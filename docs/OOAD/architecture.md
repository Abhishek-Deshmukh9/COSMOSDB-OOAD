# COSMOSDB-OOAD — Architectural Specification

> **Project:** COSMOSDB-OOAD  
> **Status:** Architecture Proposal (Refined)  
> **Date:** 2026-11-13  
> **Author:** Antigravity (Lead Software Architect)

---

## 1. System Overview & Architectural Style

COSMOSDB-OOAD is an object-oriented system for cataloging, exploring, analyzing, and comparing astronomical star systems, stars, exoplanets, and their discovery metadata.

The system adopts a **Layered Architecture** adhering to **Clean Architecture** and **Dependency Inversion** principles. High-level domain and application layers remain entirely decoupled from concrete database drivers, HTTP frameworks, and external libraries.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   PRESENTATION LAYER (FastAPI / DTOs)                  │
│       • REST API Routers    • Request / Response DTOs   • CORS/Errors  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ invokes
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                     APPLICATION LAYER (Use Cases)                      │
│   • StarSystemCatalogService          • PlanetCatalogService           │
│   • PlanetComparisonService           • ExoplanetAnalyticsService      │
│   • PlanetManagementService           • Event / Observer Dispatcher    │
└───────────────────┬───────────────────────────────┬────────────────────┘
                    │ orchestrates                  │ depends on interfaces
                    ▼                               ▼
┌───────────────────────────────────────┐   ┌────────────────────────────┐
│             DOMAIN LAYER              │   │   REPOSITORY INTERFACES    │
│  • Aggregate Roots & Entities         │   │   • IStarSystemRepository  │
│    - StarSystem (owns Star)           │   │   • IPlanetRepository      │
│    - Planet (autonomous)              │   │   • IConstellationRepository│
│    - Constellation, Discovery         │   │   • IDiscoveryRepository   │
│  • Value Objects                      │   └─────────────▲──────────────┘
│    - CelestialCoordinates             │                 │ implements
│    - CelestialBoundingBox             │                 │
│    - ESIResult, HabitableZone         │                 │
│    - OrbitalParameters                │                 │
│  • Domain Services & Calculators      │                 │
│    - ESICalculator                    │                 │
│    - HabitableZoneCalculator          │                 │
│    - PlanetClassifier                 │                 │
│  • GoF Strategy & Builder Interfaces  │                 │
└───────────────────────────────────────┘                 │
                                                          │
┌─────────────────────────────────────────────────────────┴──────────────┐
│                    INFRASTRUCTURE LAYER (Persistence)                  │
│   • MySQLStarSystemRepository          • MySQLPlanetRepository         │
│   • MySQLConstellationRepository       • MySQLDiscoveryRepository      │
│   • Data Mappers (Entity ↔ Row)        • MySQLConnectionManager        │
│   • Analytics Cache Invalidator                                        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Aggregate Boundaries & Object Ownership

To avoid conflicting aggregate ownership and circular references, aggregate boundaries are defined based on transactional consistency and domain autonomy:

```
┌──────────────────────────────────────┐     ┌────────────────────────────────────┐
│        StarSystem Aggregate          │     │          Planet Aggregate          │
│                                      │     │                                    │
│  ┌────────────────────────────────┐  │     │  ┌──────────────────────────────┐  │
│  │ StarSystem (Aggregate Root)    │  │     │  │ Planet (Aggregate Root)      │  │
│  │ - system_id: int               │  │     │  │ - planet_id: int             │  │
│  │ - system_name: str             │  │     │  │ - planet_name: str           │  │
│  │ - coordinates: Coordinates     │  │     │  │ - system_id: int ────────────┼──┼── references by ID
│  │ - distance_ly: float           │  │     │  │ - discovery_id: int          │  │   (loose coupling)
│  │                                │  │     │  │ - physical measurements      │  │
│  │  ┌──────────────────────────┐  │  │     │  │ - orbital_params: Orbital    │  │
│  │  │ Star (Internal Entity)   │  │  │     │  └──────────────────────────────┘  │
│  │  │ - star_id: int           │  │  │     └────────────────────────────────────┘
│  │  │ - spectral_type, temp... │  │  │
│  │  └──────────────────────────┘  │  │
│  │  (1..* Stars owned via         │  │
│  │   Composition)                 │  │
│  └────────────────────────────────┘  │
└──────────────────────────────────────┘
```

### 2.1 The `StarSystem` Aggregate
*   **Aggregate Root:** `StarSystem`.
*   **Internal Entities:** `Star` ($1..*$).
*   **Lifecycle & Ownership:** A `Star` cannot exist as an orphan in this astronomical catalog. A star system is physically and structurally constituted of its stellar members. Adding or mutating stars is performed strictly through the `StarSystem` aggregate root.
*   **Encapsulation:** External clients cannot mutate a `Star` directly; they invoke `StarSystem.add_star(...)` or `StarSystem.update_stellar_properties(...)`.
*   **Planet Count Derivation:** `StarSystem` does not maintain a manually synchronized counter. Its `planet_count` is derived dynamically from `len(planets)` when loaded as a full aggregate, or via `IPlanetRepository.count_by_system_id(system_id)` during paginated listings. This completely eliminates synchronization drift.

### 2.2 The `Planet` Aggregate
*   **Aggregate Root:** `Planet`.
*   **Cross-Aggregate Reference:** `Planet` references `StarSystem` **by identity (`system_id: int`)**, rather than holding an in-memory bi-directional object pointer.
*   **Justification for Autonomy:**
    1.  *Independent Query Lifecycle:* Exoplanet exploration workflows frequently query, filter, sort, and compare planets globally across unrelated star systems (e.g. ranking all 6,153 planets by ESI).
    2.  *Independent Transaction Boundary:* Updating planet observations or deleting a planet should not require loading or locking the entire `StarSystem` aggregate and all its other sibling planets.
    3.  *No Conflicting Ownership:* Treating `Planet` as an independent aggregate root with an identity reference to `StarSystem` completely resolves aggregate ownership conflicts, cyclic dependencies, and memory retention leaks.
*   **Query-Side Aggregation:** When a client requests a complete star system view (e.g. for `SystemView`), the application service (`StarSystemCatalogService`) queries `IPlanetRepository.find_by_system_id(system_id)` and constructs the combined `StarSystemDetailDTO`.

---

## 3. Reconciled UML Multiplicities & Invariants

| Relationship | UML Multiplicity | Schema & Foreign Key | Conceptual Domain Invariant (Stronger than DB) |
|---|---|---|---|
| **StarSystem ──── Constellation** | `StarSystem` $0..* \longleftrightarrow 0..1$ `Constellation` | `constellation_id INT NULL`, `ON DELETE SET NULL` | A star system may have undetermined coordinates or lie outside cataloged constellations (0..1). A constellation contains 0 or more systems. |
| **StarSystem ──── Planet** | `StarSystem` $1 \longleftrightarrow 0..*$ `Planet` | `num_planets INT DEFAULT 1 CHECK (num_planets >= 0)` | A star system can have zero planets (e.g. solitary stars). In domain logic, `planet_count` is derived dynamically (`len(planets)`), preventing counter drift. |
| **Planet ──── StarSystem** | `Planet` $0..* \longleftrightarrow 1$ `StarSystem` | `system_id INT NOT NULL`, `ON DELETE CASCADE` | Every cataloged exoplanet must belong to exactly one host star system. Orphan planets are disallowed. |
| **Planet ──── Discovery** | `Planet` $0..* \longleftrightarrow 0..1$ `Discovery` | `discovery_id INT NULL`, `ON DELETE SET NULL` | Discovery telemetry is optional. Multiple planets discovered by the same telescope campaign link to the same `Discovery` entity. |
| **StarSystem ◆──── Star** | `StarSystem` $1 \mathbin{◆\!\!-\!\!-} 1..*$ `Star` | `system_id INT NOT NULL`, `ON DELETE CASCADE` | Composition. A system must contain at least 1 star. If a system is deleted, its stars are destroyed. |
| **Constellation ◆──── BoundingBox** | `Constellation` $1 \mathbin{◆\!\!-\!\!-} 1..*$ `CelestialBoundingBox` | Ingested from CSV; normalized in domain | Composition. A constellation must own $\ge 1$ bounding box to define its spatial limits. Handles the $360^\circ/0^\circ$ wrap-around (e.g. Cassiopeia). |

---

## 4. GoF Design Patterns vs. Architectural Patterns

To adhere to academic rigor and viva evaluation, patterns are strictly categorized:

### 4.1 Architectural & DDD Patterns (Structural Foundations)
*   **Repository Pattern (Fowler / Evans):** `IPlanetRepository`, `IStarSystemRepository`. Decouples domain logic from persistence mechanisms.
*   **Data Mapper Pattern (Fowler):** `PlanetDataMapper`, `StarSystemDataMapper`. Isolates relational SQL schemas from domain entity structures.
*   **Value Object Pattern (Evans):** `CelestialCoordinates`, `CelestialBoundingBox`, `ESIResult`, `HabitableZone`, `OrbitalParameters`. Ensures immutability, self-validation, and eliminates primitive obsession.
*   **Layered / Clean Architecture:** Clear unidirectional dependency flow.

### 4.2 Three Genuine GoF Patterns (Micro-Level Design)

#### 1. Strategy Pattern (GoF Behavioral)
*   **Context:** `ESICalculator`.
*   **Strategy Interface:** `IESIScoringStrategy`.
*   **Concrete Strategies:**
    *   `StandardESIStrategy`: Computes unpenalized Earth Similarity Index (Schulze-Makuch et al., 2011 baseline).
    *   `HabitabilityWeightedStrategy`: Evaluates ESI and applies a 90% penalty if the planet's orbit lies outside the host star's liquid-water habitable zone.
*   **Justification:** Solves the exact scientific trade-off between strict physical similarity and habitability weighting without branching or modifying the core calculator (Open/Closed Principle).

#### 2. Observer Pattern (GoF Behavioral)
*   **Subject:** `PlanetManagementService` (or `CatalogEventPublisher`).
*   **Observer Interface:** `ICatalogChangeListener`.
*   **Concrete Observers:**
    *   `AnalyticsCacheObserver`: Automatically invalidates the cached Pandas/NumPy analytics DataFrame whenever a planet is created, updated, or deleted.
    *   `CatalogAuditLogObserver`: Logs administrative catalog changes for auditing and tracking data modifications.
*   **Justification:** Solves the cache-staleness bug identified in the Baseline Audit without coupling CRUD management to analytics caching. (Note: System planet count synchronization is deliberately excluded here because `StarSystem.planet_count` is derived directly from the Planet repository, eliminating dual-write race conditions).

#### 3. Builder Pattern (GoF Creational)
*   **Builder:** `PlanetBuilder`.
*   **Target:** `Planet` Entity.
*   **Justification:** An exoplanet record contains over 15 physical and orbital parameters (period, radius, mass, temperature, insolation, eccentricity, circumbinary flag, TTV flag). `PlanetBuilder` encapsulates multi-step assembly, computes astrophysically sound fallbacks during construction (e.g. Kepler's 3rd Law for distance, density from mass/radius), enforces domain invariants, and outputs a valid, immutable-ready entity.

> **Design Decision on Facade:**  
> In our layered architecture, `StarSystemCatalogService` already coordinates subsystem repositories and calculators for the presentation layer. Introducing an extra `SystemExplorationFacade` is redundant. Application Services natively serve as use-case facades.

---

## 5. State Chart & Workflow Analysis

### 5.1 Dataset Limitation Investigation
An exhaustive audit of `data/ExoplanetDataset.csv` (6,153 records) confirms:
*   There is **no status column** (e.g. no "candidate", "false-positive", or "confirmed" disposition tags).
*   All rows represent already-confirmed exoplanets.
*   Therefore, inventing astronomical verification states (such as "TTV Verified" or "Spectroscopically Characterized") on the `Planet` entity is **unsupported by data and academically indefensible**.
*   Furthermore, labels like `Modifying` or `Purged` are transient operations or terminal transitions, not persistent resting states of a domain entity.

### 5.2 Defensible Stateful Workflow: `PlanetCatalogRecord` Curation Lifecycle
For the required UML State Chart, we model the **minimal, genuine resting states of a planet record within the COSMOSDB-OOAD catalog management workflow**:

```
        [*] (New Ingestion / Create Request)
         │
         │ create()
         ▼
    ┌───────────┐
    │   Draft   │ ──[validation failure]──▶ [*] (Aborted)
    └─────┬─────┘
          │
          │ validate() [invariants satisfied & coordinates resolved]
          │ / persist to repository & notify observers
          ▼
    ┌───────────┐
    │           │ ──update() [invariants valid] / apply changes & notify observers──┐
    │ Cataloged │ ◀─────────────────────────────────────────────────────────────────┘
    │           │
    └─────┬─────┘
          │
          │ delete() / remove from repository & notify observers
          ▼
         [*] (Destroyed / Removed)
```

*   **Draft:** In-memory object constructed by `PlanetBuilder`, undergoing invariant checking and coordinate boundary matching.
*   **Cataloged:** Fully persisted in MySQL, queryable in Observatory, indexed in Analytics, and eligible for multi-planet comparisons. Updating an existing planet is an operational self-transition on `Cataloged` with attribute re-validation and cache invalidation.
*   **Terminal (`[*]`):** The record is deleted and removed from the persistence store; observers are notified to clear caches.

### 5.3 Interactive Workflow Alternative: `PlanetComparisonSession`
As an additional behavioral state model for UI interaction, `PlanetComparisonSession` demonstrates a rich user journey:
*   **Empty:** No planets selected ($0$).
*   **PendingSelection:** 1 planet selected (insufficient for comparison; comparison action disabled).
*   **Comparable:** 2 to 4 planets selected (comparison matrix active and rendered).
*   **Full:** 4 planets selected (capacity reached; further additions blocked).

---

## 6. Spatial Boundaries & RA Wraparound (Cassiopeia 360°/0°)

### 6.1 The Mathematical Problem
Right Ascension ($\alpha$) is a periodic angular coordinate on the celestial sphere:
$$\alpha \in [0.0^\circ, 360.0^\circ) \quad (\text{or } 0\text{h to } 24\text{h})$$
For constellations that cross the $0^\circ$ celestial prime meridian (such as **Cassiopeia**, spanning roughly $345^\circ \to 52.5^\circ$), a naive bounding check $\min(\alpha) \le \alpha \le \max(\alpha)$ fails because $345^\circ > 52.5^\circ$.

### 6.2 Dual-Representation Strategy in `CelestialBoundingBox`
The domain model provides two complementary layers of protection:

1.  **Segmented Bounding Boxes (`Constellation 1 ◆── 1..* CelestialBoundingBox`):**  
    In `data/Constellations.csv`, Cassiopeia is cataloged as two segments:
    *   Box 1: $\min\text{RA} = 345.0^\circ, \max\text{RA} = 360.0^\circ, \text{Dec} \in [46.0^\circ, 78.0^\circ]$
    *   Box 2: $\min\text{RA} = 0.0^\circ, \max\text{RA} = 52.5^\circ, \text{Dec} \in [46.0^\circ, 78.0^\circ]$  
    The `Constellation` entity aggregates both boxes:
    $$\text{contains}(\text{coords}) = \bigvee_{b \in \text{boundaries}} b.\text{contains}(\text{coords})$$

2.  **Wraparound-Aware `CelestialBoundingBox`:**  
    A single `CelestialBoundingBox` also natively supports crossing the meridian when $\min\text{RA} > \max\text{RA}$:
    ```python
    class CelestialBoundingBox:
        min_ra: float
        max_ra: float
        min_dec: float
        max_dec: float

        def contains(self, coords: CelestialCoordinates) -> bool:
            # 1. Check Declination bounds
            if not (self.min_dec <= coords.dec <= self.max_dec):
                return False

            # 2. Check Right Ascension bounds
            ra = coords.ra % 360.0
            if self.min_ra <= self.max_ra:
                # Standard interval (does not cross 0°)
                return self.min_ra <= ra <= self.max_ra
            else:
                # Wraparound interval (crosses 360°/0° meridian)
                return ra >= self.min_ra or ra <= self.max_ra
    ```

### 6.3 Required Boundary Test Cases
The unit test suite (`tests/domain/test_celestial_coordinates.py`) will assert the following boundary conditions for a wraparound box $[345.0^\circ, 52.5^\circ], \text{Dec} \in [46.0^\circ, 78.0^\circ]$:
1.  **Inside high interval:** $\text{RA} = 350.0^\circ, \text{Dec} = 60.0^\circ \implies \text{True}$.
2.  **Inside low interval:** $\text{RA} = 10.0^\circ, \text{Dec} = 60.0^\circ \implies \text{True}$.
3.  **Exact minimum bound:** $\text{RA} = 345.0^\circ, \text{Dec} = 60.0^\circ \implies \text{True}$.
4.  **Exact maximum bound:** $\text{RA} = 52.5^\circ, \text{Dec} = 60.0^\circ \implies \text{True}$.
5.  **Meridian crossings:** $\text{RA} = 0.0^\circ \implies \text{True}$; $\text{RA} = 360.0^\circ \implies \text{True}$ (modulo normalization).
6.  **Outside RA gap:** $\text{RA} = 180.0^\circ, \text{Dec} = 60.0^\circ \implies \text{False}$.
7.  **Outside Declination bounds:** $\text{RA} = 350.0^\circ, \text{Dec} = 20.0^\circ \implies \text{False}$.

---

## 7. Verified Concrete Snapshot for Object Diagram (Kepler-186)

The snapshot data has been verified against `data/ExoplanetDataset.csv` and `data/Constellations.csv`:

```
┌────────────────────────────────────────────────────────┐
│               Cygnus : Constellation                   │
├────────────────────────────────────────────────────────┤
│ constellation_id = 9                                   │
│ name = "Cygnus"                                        │
│ description = "Swan / Northern Cross"                  │
│ pop_rank = 9                                           │
└───────────────────────────┬────────────────────────────┘
                            │ contains
                            ▼
┌────────────────────────────────────────────────────────┐
│              Kepler-186 : StarSystem                   │
├────────────────────────────────────────────────────────┤
│ system_id = 3299                                       │
│ name = "Kepler-186"                                    │
│ distance_ly = 579.24                                   │
│ num_stars_cataloged = 1                                │
│ num_planets = 5                                        │
│ coordinates = (ra=298.6527°, dec=43.9550°)             │
└─────────────┬────────────────────────────┬─────────────┘
              │ 1 ◆ (owns)                 │ 1
              ▼                            ▼
┌──────────────────────────────┐ ┌──────────────────────────────────────┐
│     Kepler-186 : Star        │ │       Kepler-186 f : Planet          │
├──────────────────────────────┤ ├──────────────────────────────────────┤
│ star_id = 3299               │ │ planet_id = 3299                     │
│ name = "Kepler-186"          │ │ name = "Kepler-186 f"                │
│ spectral_type = "M1"         │ │ radius_earth = 1.17 R⊕               │
│ temperature_k = 3755 K       │ │ mass_earth = 1.71 M⊕                 │
│ radius_solar = 0.523 R☉      │ │ density = 5.87 g/cm³                 │
│ mass_solar = 0.544 M☉        │ │ temperature_k = 177 K                │
│ luminosity_log10 = -1.26     │ │ insolation_flux = 0.30 S⊕            │
│ age_gyr = 4.0 Gyr            │ │ orbital_period = 129.94 days         │
│ brightness_mag = 14.60       │ │ orbit_radius = 0.432 AU              │
└──────────────────────────────┘ │ eccentricity = 0.04                  │
                                 └──────────────────┬───────────────────┘
                                                    │ 0..*
                                                    ▼ 0..1
                                 ┌──────────────────────────────────────┐
                                 │          Kepler : Discovery          │
                                 ├──────────────────────────────────────┤
                                 │ discovery_year = 2014                │
                                 │ method = "Transit"                   │
                                 │ locale = "Space"                     │
                                 │ facility = "Kepler"                  │
                                 │ telescope = "0.95 m Kepler Telescope"│
                                 │ instrument = "Kepler CCD Array"      │
                                 └──────────────────────────────────────┘
```

---

## 7. Next Actions

Following user review and approval:
1. Initialize layered packages in `backend/` (`domain`, `application`, `infrastructure`, `api`).
2. Implement Domain Entities, Value Objects, Domain Services, and GoF Patterns.
3. Write comprehensive unit test suites for domain and services.
4. Implement Infrastructure repositories and Application services.
5. Generate editable PlantUML sources and render diagrams under `docs/OOAD/diagrams/`.

