# COSMODB-OOAD: Developer Mental Model & Viva Defense Guide

> **Course:** Object-Oriented Analysis and Design (CSE556) — Ramaiah Institute of Technology  
> **System:** COSMODB-OOAD (Exoplanet Exploration, Classification & Comparative Planetology)  
> **Dataset Scale:** 6,154 Confirmed Exoplanets, 4,585 Star Systems, 86 Constellations  
> **Core Architecture:** 4-Layer Clean Architecture & Domain-Driven Design (DDD)  
> **Test Suite:** 28 Automated Unit Tests Passing (100% In-Memory Testable via Repository Mocks)

---

## 1. Developer Mental Model: How COSMODB-OOAD Works (2-Minute Overview)

### The Core Story (Before vs. After)
* **The Procedural Baseline (`report.txt`):** The legacy CosmosDB DBMS prototype concentrated all server logic into 4 sprawling procedural scripts (`main.py`, `crud.py`, `utils.py`, `analytics.py`). Route handlers acted as "God Objects", directly opening raw MySQL connections (`get_db()`), dynamically constructing raw SQL queries with string interpolation, mixing HTTP serialization with astronomical math, and relying on a denormalized `num_planets` column in `StarSystem` (explicitly documented in `report.txt` as a deliberate 3NF violation) that suffered constant state drift on concurrent writes.
* **The Refactored OOAD Architecture:** We decoupled the system into a strict **4-Layer Clean Architecture** (`api` $\to$ `application` $\to$ `domain` $\leftarrow$ `infrastructure`). The domain core is 100% pure Python with zero database or framework imports. Relational queries are encapsulated behind the Repository/Adapter pattern (`IPlanetRepository`), physical assembly is guarded by `PlanetBuilder`, scoring policies vary polymorphically via the Strategy pattern (`IESIScoringStrategy`), and cache invalidation is handled reactively by the Observer pattern (`CatalogEventPublisher`).

```
[Presentation Layer]  React 18 + TypeScript SPA  <--->  FastAPI Controllers (app.py)
                                                                 │
                                                                 ▼
[Application Layer]   PlanetCatalogService  /  StarSystemCatalogService  /  AnalyticsService
                      CatalogEventPublisher  ──────►  [Observers: AnalyticsCache, AuditLog]
                                │                                │ (depends on ports)
                                ▼                                ▼
[Domain Layer]        Entities: Planet, StarSystem, Star, Constellation
                      Value Objects: CelestialCoordinates, CelestialBoundingBox, ESIResult
                      Services: ESICalculator (Strategy), PlanetClassifier
                                ▲
                                │ (implements ports)
[Infrastructure]      MySQLPlanetRepository, MySQLStarSystemRepository, MySQLConstellationRepo
                      Database: Normalized MySQL 8.0 Schema (schema.sql)
```

---

### Request Lifecycle Trace

#### 1. Read Flow: Multi-Planet Comparison (`GET /api/planets/compare?planet_ids=1&planet_ids=2`)
1. **HTTP Ingestion:** `app.py::compare_planets()` receives array of `planet_ids` and delegates to `PlanetCatalogService.compare(planet_ids)`.
2. **Domain Boundary Check:** Service validates constraint ($2 \le \text{count} \le 4$ distinct IDs).
3. **Repository Adapter:** Calls `IPlanetRepository.find_by_ids(unique_ids)`. `MySQLPlanetRepository` executes parameterized `IN (%s, %s)` query via `PLANET_SELECT` join, parsing raw tabular rows into domain `Planet` entities via `PlanetBuilder`.
4. **Astrophysical Computation:** Service passes each `Planet` to `ESICalculator.calculate(planet)`:
   - Derives bulk density if missing ($\rho = \frac{M}{R^3} \times 5.51$).
   - Computes stellar luminosity ($L = R_*^2 \cdot (T_* / 5778)^4$).
   - Calculates semi-major axis via Kepler's 3rd Law ($a = \sqrt[3]{P_{yr}^2 \cdot M_*}$).
   - Evaluates Interior ($\text{ESI}_i$) and Surface ($\text{ESI}_s$) terms.
   - Evaluates habitable zone boundaries via `HabitableZoneCalculator` and scores through active `IESIScoringStrategy`.
5. **Archetype Classification:** `PlanetClassifier.classify(planet)` assigns empirical taxonomy (`Sub-Earth`, `Super-Earth`, `Gas Giant`, etc.).
6. **DTO Serialization:** Returns unified comparison DTO to React frontend with zero database coupling leaked.

#### 2. Write Flow: Planet Ingestion (`POST /api/planets`)
1. **HTTP Ingestion & Schema Guard:** `app.py::create_planet()` validates payload via Pydantic `PlanetCreateRequest`.
2. **Host Existence Guard:** `PlanetCatalogService.create()` verifies `system_id` exists via `IStarSystemRepository.find_by_id()`.
3. **Builder Construction & Invariant Validation:** Feeds attributes into `PlanetBuilder`. `PlanetBuilder.build()` enforces physical bounds (e.g., $R \in [0.31, 87.21] R_\oplus$, $e \in [0, 0.95]$) and checks non-negativity.
4. **State Machine Transition:** Encapsulated in `PlanetCatalogRecord(planet, state=DRAFT)`. Calling `record.catalog()` transitions status to `CATALOGED`.
5. **Persistence Port:** `MySQLPlanetRepository.create()` executes parameterized `INSERT INTO planet`, commits transaction, and retrieves generated identity via `cursor.lastrowid`.
6. **Reactive Event Broadcast:** Service calls `CatalogEventPublisher.publish(CatalogChanged("created", planet_id))`:
   - `AnalyticsCacheObserver` immediately purges memoized aggregations (`analytics.invalidate()`).
   - `CatalogAuditLogObserver` writes timestamped audit record to logger.
7. **Dynamic Aggregation (No State Drift):** When `StarSystemCatalogService.get(system_id)` is subsequently queried, it runs `SELECT COUNT(*) FROM planet WHERE system_id = %s`, dynamically deriving `num_planets` without relational counter drift.

---

### Quick Codebase Map (Instant Live Demo Reference)

| Architectural Concept | File Path | Class / Function / Line | Viva Purpose |
|---|---|---|---|
| **FastAPI Routes & Dependency Injection** | `backend/cosmosdb/api/app.py` | `create_app()` (L59), `/compare` (L165), `/planets` (L225) | Show route controllers & exception handlers |
| **Domain Entities** | `backend/cosmosdb/domain/entities.py` | `Planet` (L70), `StarSystem` (L48), `Star` (L11) | Point out Composition (`StarSystem` $\to$ `Star`) |
| **State Machine Entity** | `backend/cosmosdb/domain/entities.py` | `PlanetCatalogRecord` (L104), `CatalogRecordState` (L97) | Defend `DRAFT` $\to$ `CATALOGED` $\to$ `REMOVED` |
| **Builder Pattern** | `backend/cosmosdb/domain/entities.py` | `PlanetBuilder` (L119), `build()` (L127) | Show centralized invariant validation & bounds |
| **Value Objects** | `backend/cosmosdb/domain/value_objects.py` | `CelestialCoordinates` (L8), `CelestialBoundingBox` (L20) | Show Cassiopeia 360°/0° wraparound math |
| **Habitable Zone VO** | `backend/cosmosdb/domain/value_objects.py` | `HabitableZone` (L45), `ESIResult` (L63) | Show immutable value objects with bounds |
| **Strategy Pattern (ESI)** | `backend/cosmosdb/domain/esi.py` | `IESIScoringStrategy` (L10), `StandardESIStrategy` (L14), `HabitabilityWeightedStrategy` (L19) | Defend Polymorphism & Open/Closed Principle |
| **ESI Domain Service** | `backend/cosmosdb/domain/esi.py` | `ESICalculator` (L34), `HabitableZoneCalculator` (L26) | Show scientific fallback derivations & ESI math |
| **Taxonomy Domain Service** | `backend/cosmosdb/domain/services/planet_classifier.py` | `PlanetClassifier.classify()` (L18) | Show radius/mass boundary classification rules |
| **Repository Ports (Interfaces)** | `backend/cosmosdb/application/ports.py` | `IPlanetRepository` (L8), `IStarSystemRepository` (L23) | Defend Dependency Inversion Principle (DIP) |
| **Application Services** | `backend/cosmosdb/application/services.py` | `PlanetCatalogService` (L19), `AnalyticsService` (L267) | Show use case orchestration & caching logic |
| **Observer Pattern** | `backend/cosmosdb/application/events.py` | `CatalogEventPublisher` (L18), `AnalyticsCacheObserver` (L30) | Defend event-driven cache invalidation |
| **MySQL Repository Adapter** | `backend/cosmosdb/infrastructure/mysql.py` | `MySQLPlanetRepository` (L97), `_planet()` mapper (L64) | Show SQL parameterization & connection pooling |
| **In-Memory Test Mocks** | `backend/tests/support.py` | `FakePlanetRepository` (L49), `planet()` fixture (L8) | Prove 100% testability without live database |
| **Automated Test Suite** | `backend/tests/` | 6 test files (`test_domain`, `test_services`, `test_api`, etc.) | Run `unittest discover` live (28/28 passing) |
| **Frontend Comparison View** | `frontend/src/app/pages/ComparePlanets.tsx` | `ComparePlanets` component (L50) | Show interactive 2–4 planet comparison matrix |

---

## 2. UML Diagrams Defense Cheat Sheet (Figures 1 to 12)

Use these crisp 2-bullet talking points when the examiner asks to review any diagram:

* **Figure 1: Use Case Diagram (`use-case.puml`)**
  * *Actor Role Separation:* Distinguishes read-only public consumers (`Explorer` actor: Search, Filter, Compare Planets, Inspect 3D Orbits, View Analytics) from authenticated content managers (`Curator` actor: Create, Update, Delete Planet Records).
  * *`<<extend>>` Semantics:* Use case `View Habitable Zone Assessment` and `Compare Planetary Attributes` conditionally extend `Browse Exoplanet Catalog`, executing only when optional astrophysical parameters (luminosity, semi-major axis) or multiple selected planet identities exist.

* **Figure 2: Complete Class Diagram (`class-diagram.puml`)**
  * *Composition vs. Association:* Host star systems hold an existential **UML Composition** (`StarSystem` $1 \blacklozenge\!\!-\!\!- 1..* \text{Star}$) because a host star cannot exist in the catalog without its parent system; conversely, `Planet` holds an **Association** (`Planet` $0..* \longrightarrow 1 \text{StarSystem}$) referenced by foreign identity to allow independent lifecycles.
  * *Dependency Inversion Architecture:* Application services (`PlanetCatalogService`) depend exclusively on the abstract interface `IPlanetRepository` in `application/ports.py`; the concrete implementation `MySQLPlanetRepository` in `infrastructure/mysql.py` implements this interface, directing all arrows inward toward the domain.

* **Figure 3: Object Diagram (`object-diagram.puml`)**
  * *Concrete Runtime Snapshot:* Captures the ground-truth runtime state of the `Kepler-186` multi-planetary system, instantiating `keplerSystem:StarSystem`, its host star `keplerStar:Star` ($T=3788\text{ K}$, M1V dwarf), and the cataloged exoplanet `kepler186f:Planet` ($R=1.17 R_\oplus$, $T=188\text{ K}$, $\text{ESI}=0.61$).
  * *Value Object Linkage:* Shows how `keplerSystem` binds to immutable value objects `coords:CelestialCoordinates` ($\text{ra}=298.65^\circ, \text{dec}=44.45^\circ$) contained within the bounding boundaries of `cygnus:Constellation`.

* **Figure 4: Sequence Diagram — Compare Planets (`sequence-compare-planets.puml`)**
  * *Loop Fragment Orchestration:* Illustrates `Explorer` selecting multiple planets in the React UI; `PlanetCatalogService` iterates over the returned `Planet` list in a `loop` fragment, invoking `ESICalculator.calculate()` and `PlanetClassifier.classify()` per planet in memory.
  * *Zero Database Redundancy:* Demonstrates that comparative metrics (ESI radar terms, habitable zone classifications) are dynamically synthesized by domain services without firing repeated SQL queries or mutating database state.

* **Figure 5: Sequence Diagram — Search System (`sequence-search-system.puml`)**
  * *Dynamic Planet Count Retrieval:* When an `Explorer` searches or inspects a star system, `StarSystemCatalogService` invokes `IStarSystemRepository.find_by_id()` followed by `planet_count(system_id)`.
  * *Elimination of 3NF Violation:* Highlights that `planet_count()` fires a dynamic indexed `COUNT(*)` query, proving that the catalog completely avoids the stale counter bug present in the procedural prototype.

* **Figure 6: State Chart Diagram — Planet Catalog Record (`state-planet-record.puml`)**
  * *Finite State Machine Lifecycle:* Models the lifecycle through three explicit states: `[Draft]` $\xrightarrow{\text{catalog()}}$ `[Cataloged]` $\xrightarrow{\text{remove()}}$ `[Removed]`.
  * *Self-Transition & Mutation Guard:* Updating planet attributes triggers a self-transition on `[Cataloged]` that fires `CatalogEventPublisher.publish()`, ensuring that downstream analytics caches are invalidated without allowing invalid states (e.g., a `Removed` planet cannot be updated).

* **Figure 7: Activity Diagram — ESI & Habitable Zone Workflow (`activity-esi-calculation.puml`)**
  * *Cascading Scientific Fallbacks:* Documents decision diamonds where missing raw data is mathematically derived: deriving density from mass and radius, deriving luminosity from stellar radius and temperature ($L = R^2 T^4$), and deriving semi-major axis from orbital period via Kepler's 3rd Law.
  * *Strategy Hook:* Depicts the terminal split where the base physical score passes into the polymorphic `IESIScoringStrategy` diamond, applying habitability penalties if the planet orbits outside the calculated inner/outer boundaries.

* **Figure 8: Builder Pattern — Before vs. After Class Diagram (`pattern_builder.png`)**
  * *Before Antipattern:* Shows `crud.py::create_planet()` accepting 13 raw positional arguments prone to silent transposition (swapping mass and radius), relying on late MySQL `CHECK` exceptions that crashed the server with HTTP 500.
  * *After OO Structure:* Shows `PlanetBuilder` providing fluent `set(name, value)` methods, centralized validation guards in `build()`, and fail-fast domain invariant verification.

* **Figure 9: Repository/Adapter Pattern — Before vs. After Class Diagram (`pattern_repository.png`)**
  * *Before Antipattern:* Shows route handlers in `main.py` directly importing `mysql.connector` and composing inline SQL query strings, making the endpoint 100% untestable without a live MySQL instance.
  * *After OO Structure:* Shows `PlanetCatalogService` depending on the `IPlanetRepository` interface, while `MySQLPlanetRepository` acts as a pluggable Adapter, enabling instant testing via `FakePlanetRepository`.

* **Figure 10: Strategy Pattern — Before vs. After Class Diagram (`pattern_strategy.png`)**
  * *Before Antipattern:* Shows `utils.py::calculate_esi()` utilizing hardcoded boolean flags (`penalize_habitable_zone=True`) with nested `if-else` branches, violating the Open/Closed Principle whenever scientists proposed new weighting schemes.
  * *After OO Structure:* Shows `ESICalculator` acting as Context holding an `IESIScoringStrategy` interface, with `StandardESIStrategy` and `HabitabilityWeightedStrategy` interchangeable at runtime.

* **Figure 11: Observer Pattern — Before vs. After Class Diagram (`pattern_observer.png`)**
  * *Before Antipattern:* Shows `crud.py` executing manual counter `UPDATE` statements while `analytics.py` executed expensive aggregations across 6,154 rows on every HTTP request without caching.
  * *After OO Structure:* Shows `CatalogEventPublisher` (Subject) notifying registered `ICatalogChangeListener` observers (`AnalyticsCacheObserver` and `CatalogAuditLogObserver`), enabling automatic cache invalidation on any catalog mutation.

* **Figure 12: Layered Package & Component Architecture Diagram (`figure8_package_component.png`)**
  * *Inward Dependency Rule:* Visualizes the concentric layers of Clean Architecture: `Presentation` (`app.py`, React UI) and `Infrastructure` (`mysql.py`) point inward toward `Application` (`services.py`, `ports.py`) and `Domain` (`entities.py`, `esi.py`).
  * *Port/Adapter Decoupling:* Shows how infrastructure drivers (MySQL connector, environment configs) are isolated as outer boundary details, ensuring the domain core compiles and tests with zero external dependencies.

---

## 3. Top 15 High-Probability Viva Questions & Crisp Answers

#### Q1: Why is StarSystem to Star a Composition, while StarSystem to Planet is an Association?
**Answer:** A host star cannot exist in the astronomical catalog independently of its star system—if the star system is destroyed or dereferenced, its host star entities cease to have existential meaning, fulfilling UML Composition ($1 \blacklozenge\!\!-\!\!- 1..*$). Conversely, planets represent discovered orbital bodies cataloged over time that associate with a host system by foreign key identity ($0..* \longrightarrow 1$). Modeling planets as an association prevents cascading deletions of historical discovery records and allows independent cataloging workflows.

#### Q2: Why did you remove the denormalized `num_planets` counter from the original DBMS project?
**Answer:** In the procedural codebase (`report.txt`, Section 10), `num_planets` was an explicitly admitted 3NF violation that required manual `UPDATE StarSystem SET num_planets = num_planets - 1` statements inside delete and insert endpoints. In practice, concurrent transactions, partial ingestion failures, and direct SQL imports caused severe relational state drift where systems with 5 planets reported `num_planets = 1`. In our refactored OO architecture, the planet count is dynamically derived via `IStarSystemRepository.planet_count()` using an indexed `COUNT(*)` query, guaranteeing absolute referential integrity.

#### Q3: How does your project demonstrate Polymorphism and the Open/Closed Principle?
**Answer:** We implemented the GoF Strategy pattern via `IESIScoringStrategy`, which defines the polymorphic contract `score(base_score, zone_status)`. The `StandardESIStrategy` returns the purely physical terrestrial similarity score, while `HabitabilityWeightedStrategy` applies a 90% penalty if the planet orbits outside the calculated circumstellar habitable zone. The calculation engine (`ESICalculator`) is closed for modification but open for extension—new astrophysical scoring policies can be introduced simply by implementing the strategy protocol without altering a single line of calculation math.

#### Q4: Why use the Builder pattern (`PlanetBuilder`) instead of a Python `__init__` or Factory Method?
**Answer:** Exoplanet catalog records involve 24 distinct physical, stellar, and telemetry parameters, many of which are optional or discovered in stages across different telescope missions. Telescoping constructors or long positional parameter lists (as seen in `crud.py`'s 13-argument function) lead to catastrophic transposition bugs, such as swapping orbital radius and period. `PlanetBuilder` provides a fluent, named `set()` interface with centralized invariant validation in `build()`, ensuring that non-physical measurements (e.g., negative mass or radius) fail fast before an immutable `Planet` entity is ever instantiated.

#### Q5: How does the Observer pattern work during planet creation or deletion?
**Answer:** We implemented `CatalogEventPublisher` as the Subject and `ICatalogChangeListener` as the Observer protocol. When `PlanetCatalogService.create()` or `delete()` executes successfully, it publishes a `CatalogChanged` event. The registered `AnalyticsCacheObserver` intercepts this notification and invokes `analytics.invalidate()`, wiping the memoized statistical distributions, while `CatalogAuditLogObserver` writes an audit trail. This completely decouples catalog mutation logic from the analytics caching infrastructure.

#### Q6: Explain Dependency Inversion—how do you test `PlanetCatalogService` without MySQL?
**Answer:** High-level application services (`PlanetCatalogService`) depend strictly on abstractions (`IPlanetRepository` protocol defined in `application/ports.py`), not on the low-level database driver (`MySQLPlanetRepository`). For automated testing, we created `FakePlanetRepository` in `tests/support.py` that implements `IPlanetRepository` using in-memory Python lists. This architectural decoupling allows our entire 28-test suite to execute and verify complex catalog operations, pagination, sorting, and error handling in just 1.3 seconds without a running MySQL instance.

#### Q7: How does `CelestialBoundingBox` handle Right Ascension meridian wraparounds?
**Answer:** Right Ascension is a circular spherical coordinate ranging from $0^\circ$ to $360^\circ$ ($0\text{h}$ to $24\text{h}$). Constellations straddling the vernal equinox meridian (such as Cassiopeia, spanning $345^\circ$ through $52.5^\circ$) have $\text{min\_ra} > \text{max\_ra}$. The procedural code used naive linear checks (`min <= ra <= max`), misclassifying coordinates as null. Our `CelestialBoundingBox.contains()` value object explicitly evaluates:
```python
inside_ra = (self.min_ra <= ra <= self.max_ra if self.min_ra <= self.max_ra else ra >= self.min_ra or ra <= self.max_ra)
```
This correctly handles equatorial wraparound across all spherical boundary conditions.

#### Q8: Which Bahrami design corollaries did the old DBMS code violate, and how did you fix them?
**Answer:** The procedural codebase violated Corollary 1 (uncoupled design) by embedding SQL cursors directly inside HTTP presentation routes; we resolved this by introducing clean repository ports. It violated Corollary 2 (single purpose classes) through 78-line functions in `crud.py` that handled parsing, SQL insertion, counter updates, and orphan cleanup simultaneously; we decomposed these into specialized single-responsibility classes. It also violated Corollary 6 (designing with inheritance and polymorphism) by using boolean flags in `utils.py` instead of polymorphic strategy hierarchies.

#### Q9: Why did you reject the Command and Decorator patterns?
**Answer:** We evaluated Command and Decorator during our architecture review and deliberately rejected them to avoid speculative over-engineering. Command (encapsulating mutations as standalone execution objects with undo stacks) was rejected because catalog curation requires atomic, persistent ACID database transactions managed via MySQL row locks, not ephemeral in-memory command replay. Decorator was rejected because adding dynamic behavior to `Planet` entities at runtime would break data immutability (`@dataclass(frozen=True)`) and complicate Pydantic serialization.

#### Q10: What happens mathematically inside `ESICalculator` and `HabitableZoneCalculator`?
**Answer:** `ESICalculator` evaluates planetary similarity to Earth ($R_\oplus=1.0, \rho_\oplus=5.51, v_{e\oplus}=11.19, T_\oplus=288\text{ K}$) using a two-tier formulation:
$$\text{ESI}_i = \sqrt{\left(1 - \left|\frac{R - 1}{R + 1}\right|\right)^{0.57} \left(1 - \left|\frac{\rho - 5.51}{\rho + 5.51}\right|\right)^{1.07}}, \quad \text{ESI}_s = \sqrt{\left(1 - \left|\frac{v_e - 11.19}{v_e + 11.19}\right|\right)^{0.70} \left(1 - \left|\frac{T - 288}{T + 288}\right|\right)^{5.58}}$$
The base score is $\sqrt{\text{ESI}_i \cdot \text{ESI}_s}$. Concurrently, `HabitableZoneCalculator` determines stellar luminosity ($L = R_*^2 (T_* / 5778)^4$) and computes runaway greenhouse inner and maximum greenhouse outer boundaries ($r_{\text{in}} = \sqrt{L / 1.1}, r_{\text{out}} = \sqrt{L / 0.53}$).

#### Q11: How do you prevent SQL injection in `MySQLPlanetRepository`?
**Answer:** In the legacy code (`report.txt`), queries were composed using dynamic string formatting. In `MySQLPlanetRepository`, all SQL operations utilize strictly parameterized prepared statements with positional `%s` placeholders (e.g., `cursor.execute("SELECT * FROM planet WHERE planet_id = %s", (planet_id,))`). Dynamic filter conditions sanitize user inputs by binding values exclusively through the database connector's parameter tuple, ensuring that malicious inputs cannot alter SQL syntax.

#### Q12: What is the difference between an Entity, a Value Object, and a DTO in your code?
**Answer:** 
* **Entity (`Planet`, `StarSystem`):** Defined by a persistent, mutable conceptual identity (`planet_id`, `system_id`) that remains constant even if physical properties (mass, radius) change.
* **Value Object (`CelestialCoordinates`, `HabitableZone`, `ESIResult`):** Immutable (`frozen=True`) structures defined entirely by their attribute values, with no identity; two coordinate objects with the same RA and Dec are completely interchangeable.
* **DTO (Data Transfer Object):** Plain serialized dictionaries or Pydantic models (`PlanetCreateRequest`, JSON comparison outputs) designed strictly for transporting structured data across process boundaries without behavior.

#### Q13: How does `PlanetCatalogRecord` enforce valid state transitions?
**Answer:** `PlanetCatalogRecord` implements a formal State machine containing an internal `CatalogRecordState` enum (`DRAFT`, `CATALOGED`, `REMOVED`). An exoplanet record is initialized as `DRAFT`. Calling `catalog()` transitions it to `CATALOGED`; calling `remove()` transitions it to `REMOVED`. If a client attempts an illegal state transition—such as invoking `remove()` on an uncataloged `DRAFT` or trying to re-catalog a `REMOVED` planet—the record raises an explicit `ValueError`, guarding lifecycle invariants.

#### Q14: What trade-offs did Clean Architecture introduce compared to the procedural code?
**Answer:** Clean Architecture introduced higher initial ceremony: decomposing 4 procedural files resulted in 14 specialized classes, abstract interfaces, domain value objects, and separate mapping logic. However, this trade-off dramatically reduced maintenance risk: it eliminated tight coupling to the database driver, eradicated relational state drift on `num_planets`, cut defect reproduction time through in-memory testing, and allowed frontend features (like the `/compare` matrix) to be implemented without modifying underlying database schemas.

#### Q15: Walk through how you run the backend, frontend, and test suite from scratch.
**Answer:**
1. **Database:** Ensure local MySQL service `MySQL80` is running on port 3306 with the `cosmosdb` schema loaded.
2. **Backend API:** Navigate to `OOAD-Implementation/backend`, activate `.venv`, and start FastAPI via `python -m uvicorn cosmosdb.api.app:app --host 127.0.0.1 --port 8000 --reload` (Swagger UI at `/docs`).
3. **Frontend SPA:** Navigate to `OOAD-Implementation/frontend` and run `npm run dev` (Vite dev server at `localhost:5173`).
4. **Verification Suite:** From `OOAD-Implementation/backend`, execute `python -m unittest discover -s tests -v`, running all 28 automated tests across domain, service, API, and repository layers in ~1.3 seconds.

---

## 4. Synchronized Two-Person Presentation & Live Demo Script (7–8 Minutes)

* **Speaker 1 (Abhishek):** System Architecture, Clean Architecture Layers, Domain Model, Builder & Strategy Patterns.  
* **Speaker 2 (Teammate):** OO Analysis, Use Cases, Observer Pattern, Caching, Live UI Demo & Evaluation Metrics.  

---

### Part 1 (0:00–1:30) — Problem Context & Architectural Transformation
* **Speaker 1 (Abhishek):**  
  *"Good morning respected examiners. Today we are presenting **COSMODB-OOAD**, an enterprise-grade object-oriented system for exoplanet cataloging, astrophysical classification, and comparative planetology. Our system manages a real-world dataset of 6,154 confirmed exoplanets, 4,585 star systems, and 86 constellations."*  
  `[Point to Title Slide & Report Cover]`  
  *"To truly understand our design, we must examine the baseline we inherited. In our original DBMS coursework prototype—documented in our baseline audit—the backend was written as 4 procedural scripts: `main.py`, `crud.py`, `utils.py`, and `analytics.py`. In that legacy design, route handlers were God Objects: a single function composed raw SQL queries, handled HTTP requests, managed transactions, and manually synchronized a denormalized `num_planets` counter."*

* **Speaker 2 (Teammate):**  
  *"That denormalized counter was an acknowledged 3NF violation that caused constant state drift whenever planets were added or deleted. Furthermore, business logic was hardcoded against the MySQL connector, making unit testing impossible without a live database. To eliminate these critical structural flaws, we refactored the entire application into a 4-Layer Clean Architecture governed by Ali Bahrami's design corollaries and the SOLID principles."*  
  `[Point to Figure 12: Layered Package & Component Diagram]`  
  *"Notice our package diagram: dependencies point strictly inward. Our presentation and database infrastructure layers depend inward on application ports, keeping our domain core 100% pure Python and completely testable in memory."*

---

### Part 2 (1:30–3:30) — OO Analysis & UML Modeling Defense
* **Speaker 2 (Teammate):**  
  *"Beginning with Unit III Object-Oriented Analysis, we conducted a rigorous noun-phrase analysis extracting 22 candidate classes and identifying two core actor roles."*  
  `[Point to Figure 1: Use Case Diagram]`  
  *"The `Explorer` actor performs read-only operations: searching systems, browsing planets, inspecting 3D orbits, and comparing worlds. The `Curator` actor manages catalog curation: creating, updating, and removing planetary records. Notice the `<<extend>>` relationship on our comparison and habitable zone use cases—they execute conditionally when optional astrophysical telemetry is present."*

* **Speaker 1 (Abhishek):**  
  `[Point to Figure 2: Complete Class Diagram]`  
  *"In our Class Diagram, I want to highlight two vital structural distinctions:  
  First, look at `StarSystem` to `Star`. We modeled this as a strict **UML Composition** (`StarSystem` $1 \blacklozenge\!\!-\!\!- 1..* \text{Star}$) because a host star cannot exist in the catalog without its host system. If a system is purged, its stars are physically destroyed.  
  Second, look at `Planet` to `StarSystem`. This is an **Association**, not composition, allowing planets to be cataloged, re-assigned, or removed without destroying the underlying host system hierarchy."*  
  `[Point to Figure 3 & Figure 6: Object Diagram & State Chart]`  
  *"Our Object Diagram shows the Kepler-186 system snapshot with its M1 host star and Kepler-186f planet. In Figure 6, our State Chart captures the lifecycle of `PlanetCatalogRecord` through `Draft`, `Cataloged`, and `Removed` states, ensuring no illegal updates occur on decommissioned records."*

---

### Part 3 (3:30–5:30) — Refactoring & GoF Design Patterns
* **Speaker 1 (Abhishek):**  
  *"In Unit V, we implemented four genuine Gang of Four design patterns to eliminate specific architectural antipatterns from the legacy DBMS codebase."*  
  `[Point to Figure 8: Builder Pattern Before/After]`  
  *"First is the **Builder Pattern** (`PlanetBuilder`). In the legacy `crud.py`, adding a planet required a 13-argument positional function. If a developer accidentally swapped mass and radius, the database accepted the corrupted data until a late SQL check failed. `PlanetBuilder` provides fluent named setters and encapsulates centralized invariant validation, ensuring non-physical measurements fail fast before instantiation."*  
  `[Point to Figure 10: Strategy Pattern Before/After]`  
  *"Second is the **Strategy Pattern** for the Earth Similarity Index. In the legacy `utils.py`, ESI calculation relied on hardcoded boolean flags with nested `if-else` branches. We refactored this into `IESIScoringStrategy`, supporting `StandardESIStrategy` and `HabitabilityWeightedStrategy`. This achieves full Open/Closed compliance—new scientific scoring models can be introduced without modifying calculation math."*

* **Speaker 2 (Teammate):**  
  `[Point to Figure 9: Repository Pattern & Figure 11: Observer Pattern]`  
  *"Third, we applied the **Repository / Adapter Pattern**. Application services depend on `IPlanetRepository`, while `MySQLPlanetRepository` acts as the concrete database adapter.  
  Fourth is the **Observer Pattern**. In the procedural system, `analytics.py` re-queried 6,154 planets on every page load because it had no notification mechanism. We introduced `CatalogEventPublisher` and `AnalyticsCacheObserver`. Whenever a curator inserts, updates, or deletes a planet, an event fires and automatically invalidates the analytics cache, decoupling the catalog service from caching infrastructure."*

---

### Part 4 (5:30–7:30) — Live System Demo, Automated Tests & Conclusion
* **Speaker 2 (Teammate):**  
  `[Screen Action: Open Browser to http://localhost:5173/observatory]`  
  *"Now let's demonstrate the live working application. Here is our Observatory page. The UI dynamically loads over 6,100 exoplanets. Notice each card displays an interactive radial ESI gauge and habitable zone badge, rendered using our domain calculations."*  
  `[Screen Action: Click on Kepler-186 to open 3D System Visualizer]`  
  *"Clicking on Kepler-186 launches our interactive 3D Orbit Visualizer, modeling orbital radii and stellar illumination in real time."*  
  `[Screen Action: Navigate to /compare page, search and select Kepler-452 b and Proxima Centauri b]`  
  *"Here is our dedicated **Exoplanet Comparison Matrix** (`/compare`), implementing the use case from Figure 4. We can select 2 to 4 worlds side by side to contrast physical density, equilibrium temperature, semi-major axis, and Earth similarity index."*

* **Speaker 1 (Abhishek):**  
  `[Screen Action: Navigate to /add-planet, submit a new test planet, then open /analytics]`  
  *"Now watch our Observer pattern in action. When we ingest a new exoplanet on `/add-planet`, the backend executes `PlanetBuilder`, writes to MySQL, and publishes a `CatalogChanged` event. When we immediately switch to `/analytics`, the dashboard reflects freshly computed aggregates—proving our automated cache invalidation works seamlessly."*  
  `[Screen Action: Switch to Terminal, execute: python -m unittest discover -s tests -v]`  
  *"Finally, let's run our automated test suite. In just 1.3 seconds, all 28 unit tests pass with 100% success—verifying our domain entities, strategy policies, celestial coordinate meridian wraparound, and service workflows using in-memory mock repositories without requiring MySQL."*

* **Speaker 2 (Teammate):**  
  *"In conclusion, our OOAD case study transformed a fragile procedural SQL prototype into a maintainable, high-cohesion, low-coupling system adhering strictly to Clean Architecture, GoF patterns, and academic software engineering standards. Thank you, and we welcome your questions."*
