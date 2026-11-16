# COSMOSDB-OOAD Architecture Specification

## 1. Architectural Layers & Dependency Inversion

The platform strictly follows Clean Architecture and Domain-Driven Design (DDD):

```
+-------------------------------------------------------------+
| Presentation Layer (FastAPI API + React Frontend)            |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
| Application Layer (Catalog Services, Analytics, Observers)  |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
| Domain Layer (Entities, Value Objects, Domain Services)     |
+-------------------------------------------------------------+
                              ^
                              | (implements ports)
+-------------------------------------------------------------+
| Infrastructure Layer (MySQL Repositories & Connection Pool)  |
+-------------------------------------------------------------+
```

1. **Presentation (`cosmosdb.api` & `frontend`):**
   - FastAPI endpoints handle HTTP protocol concerns, deserialization, Pydantic request validation, and status code mapping.
   - React + TypeScript client provides visual exploration: 3D orbit simulation canvas (`OrbitVisualizer`), space canvas background (`SpaceCanvas`), ESI dials (`ESIGauge`), habitable zone tracker (`ZoneTracker`), 9 ECharts analytics dashboards, and the dedicated Comparative Planetology matrix (`/compare`).
2. **Application (`cosmosdb.application`):**
   - Coordinates use-case workflows: `PlanetCatalogService`, `StarSystemCatalogService`, `ConstellationCatalogService`, and `AnalyticsService`.
   - Depends solely on abstract repository protocols (`IPlanetRepository`, `IStarSystemRepository`, `IConstellationRepository`), satisfying the Dependency Inversion Principle (DIP).
   - Manages asynchronous event publishing via `CatalogEventPublisher`.
3. **Domain (`cosmosdb.domain`):**
   - Contains pure business logic, invariants, domain entities, value objects, and domain services.
   - Zero dependencies on frameworks, databases, or third-party I/O libraries.
   - Houses `ESICalculator`, `IESIScoringStrategy`, `PlanetClassifier`, and value objects `CelestialCoordinates`, `CelestialBoundingBox`, and `HabitableZone`.
4. **Infrastructure (`cosmosdb.infrastructure`):**
   - Concrete implementations of application ports: `MySQLPlanetRepository`, `MySQLStarSystemRepository`, `MySQLConstellationRepository`.
   - Maps raw relational rows to immutable domain entities using `PlanetBuilder`.

---

## 2. Domain Entities & DDD Aggregate Boundaries

### StarSystem (Aggregate Root)
- Represents a physical star system containing host stars.
- **Composition Relationship ($1 \mathbin{◆\!\!-\!\!-} 1..*$):** `StarSystem` composites `Star` entities (`stars: tuple[Star, ...]`). A star's lifecycle is strictly owned by its parent star system; deleting a system cascades to its constituent stars.
- **Dynamic Planet Count:** To prevent state drift and redundancy, `num_planets` is derived dynamically via `COUNT(*)` from `IPlanetRepository.planet_count(system_id)` rather than maintaining a duplicated counter column.

### Planet (Autonomous Aggregate Root)
- Represents an individual exoplanet.
- **Identity Reference ($N \mathbin{-\!\!-} 1$):** `Planet` references `StarSystem` strictly by foreign identity (`system_id: int`), completely eliminating cyclical object graphs and decoupling query/mutation boundaries.
- Owns all physical measurements (radius, mass, density, equilibrium temperature, semi-major axis, orbital period, eccentricity, insolation flux).

### Discovery & Constellation
- `Discovery` captures historical observational context (method, facility, telescope, year).
- `Constellation` groups celestial coordinates using spherical bounding boxes (`CelestialBoundingBox`).

---

## 3. Domain Services

### ESICalculator
Calculates planetary Earth Similarity Index according to the established scientific formulation:
$$\text{ESI}_r = \left(1 - \left|\frac{x - x_0}{x + x_0}\right|\right)^w$$
- **Interior ESI:** Radius ($w=0.57$) and Bulk Density ($w=1.07$).
- **Surface ESI:** Escape Velocity ($w=0.70$) and Surface Temperature ($w=5.58$).
- **Global Base ESI:** Geometric mean of interior and surface metrics.
- Separates physical similarity scoring from habitable zone status assessment.

### PlanetClassifier
Categorizes exoplanets into canonical astrophysical archetypes based on planetary radius (with mass fallback):
- **Terrestrial / Rocky:** $R_p \le 1.25\,R_\oplus$ (or $M_p \le 2.0\,M_\oplus$)
- **Super-Earth:** $1.25\,R_\oplus < R_p \le 2.0\,R_\oplus$ (or $2.0 < M_p \le 10.0\,M_\oplus$)
- **Mini-Neptune:** $2.0\,R_\oplus < R_p \le 4.0\,R_\oplus$ (or $10.0 < M_p \le 50.0\,M_\oplus$)
- **Gas Giant:** $4.0\,R_\oplus < R_p \le 15.0\,R_\oplus$ (or $50.0 < M_p \le 500.0\,M_\oplus$)
- **Super-Jupiter:** $R_p > 15.0\,R_\oplus$ (or $M_p > 500.0\,M_\oplus$)
- **Unknown:** When required physical measurements are unavailable.

---

## 4. GoF Design Patterns

### 1. Strategy Pattern (`IESIScoringStrategy`)
- **Intent:** Define a family of scoring algorithms, encapsulate each one, and make them interchangeable without modifying `ESICalculator`.
- **Implementations:**
  - `StandardESIStrategy`: Calculates the standard empirical scientific ESI without modifying or penalizing the score for habitable zone status.
  - `HabitabilityWeightedStrategy`: Applies an explicit 90% penalty ($\times 0.1$) to planets situated outside the host star's habitable zone (`TOO_HOT` or `TOO_COLD`).

### 2. Observer Pattern (`CatalogEventPublisher`)
- **Intent:** Define a one-to-many dependency between objects so that when one object changes state, all its dependents are notified automatically.
- **Implementations:**
  - `AnalyticsCacheObserver`: Automatically invalidates the in-memory cache of all 9 analytics pre-aggregated datasets whenever a planet is created, updated, or deleted.
  - `CatalogAuditLogObserver`: Logs structured audit events whenever catalog mutations occur.

### 3. Builder Pattern (`PlanetBuilder`)
- **Intent:** Separate the construction of a complex object from its representation, allowing the same construction process to create various representations.
- **Usage:** Validates physical bounds (rejecting non-physical measurements like negative radius or mass), executes fallback computations (e.g. bulk density estimation from mass and radius, semi-major axis estimation via Kepler's 3rd Law), and constructs immutable `Planet` entities.

---

## 5. Spherical Coordinate System & Constellation Deduplication

- `CelestialBoundingBox` supports right ascension intervals crossing the $0^\circ/360^\circ$ celestial meridian. When $\min\text{RA} > \max\text{RA}$, containment evaluates:
  $$\text{inside\_ra} = (\text{ra} \ge \min\text{RA}) \lor (\text{ra} \le \max\text{RA})$$
- Ingestion logic merges split CSV records (such as Cassiopeia $[345.0^\circ, 360.0^\circ]$ and $[0.0^\circ, 52.5^\circ]$) into a single constellation row with interval $[345.0^\circ, 52.5^\circ]$, ensuring exactly 86 unique constellation records rather than duplicate split entries.
