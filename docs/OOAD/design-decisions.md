# COSMOSDB-OOAD — Design Decisions Log

> **Project:** COSMOSDB-OOAD  
> **Status:** Active Reference Document  
> **Date:** 2026-11-13  
> **Author:** Antigravity (Lead Software Architect)

This document records the architectural and design decisions made for the COSMOSDB-OOAD system, detailing the context, alternatives considered, the chosen decision, and the justification for the evaluation viva.

---

## Decision 1: Aggregate Boundaries for `StarSystem` and `Planet`

### Context
In the relational schema, `Planet` and `Star` both have foreign keys referencing `StarSystem` with `ON DELETE CASCADE`. In early analysis, one could naively assume that `StarSystem` should be a monolithic Aggregate Root that encapsulates both `Star` and `Planet` as subordinate child entities.

### Alternatives Considered
1.  **Monolithic Aggregate (`StarSystem` owns `Star` and `Planet`):**  
    *   *Pros:* Direct reflection of MySQL `ON DELETE CASCADE`.
    *   *Cons:* Severe performance and concurrency bottlenecks. Querying, paginating, sorting, or comparing planets globally (e.g. ranking all 6,153 exoplanets by ESI) would require loading entire star system aggregates. Mutating a single planet would lock the whole system and all sibling planets.
2.  **Autonomous Aggregates (`StarSystem` owns `Star`; `Planet` is an autonomous Aggregate Root):**  
    *   *Pros:* Matches domain reality. Planets have independent scientific identities, distinct discovery publications, independent global query lifecycles, and separate comparison workflows. `Planet` references `StarSystem` by foreign identity (`system_id: int`), conforming to standard Domain-Driven Design (DDD) rules for cross-aggregate references.
    *   *Cons:* Cross-aggregate hydration must be handled by application services.

### Decision
**Adopt Alternative 2.**  
`StarSystem` is the aggregate root for `Star` (modeled as **UML Composition**).  
`Planet` is an autonomous aggregate root that holds an **Association** to `StarSystem` via its `system_id`. When complete system views are needed, `StarSystemCatalogService` coordinates both repositories.  
Furthermore, `StarSystem.planet_count` is dynamically derived from `IPlanetRepository.count_by_system_id(system_id)` or `len(planets)` rather than maintaining a dual-write synchronized counter column, eliminating synchronization drift.

---

## Decision 2: UML Multiplicities vs. Database Constraints

### Context
Relational database column constraints (such as `NOT NULL`, foreign keys, and `CHECK` constraints) do not automatically equate to object-oriented multiplicities and domain invariants.

### Decision & Reconciled Multiplicities
1.  **`StarSystem` to `Constellation` ($0..* \longleftrightarrow 0..1$):**  
    *   *Schema:* `constellation_id INT NULL`, `ON DELETE SET NULL`.  
    *   *OO Justification:* A star system may have unresolved celestial coordinates or lie outside cataloged constellations.
2.  **`StarSystem` to `Planet` ($1 \longleftrightarrow 0..*$):**  
    *   *Schema:* `num_planets INT DEFAULT 1 CHECK (num_planets >= 0)`.  
    *   *OO Justification:* A star system can exist with zero cataloged planets (e.g. newly discovered stellar hosts or solitary field stars). In the domain model, `num_planets` is an invariant property derived dynamically from the count of associated planets to avoid data drift.
3.  **`Planet` to `StarSystem` ($0..* \longleftrightarrow 1$):**  
    *   *Schema:* `system_id INT NOT NULL`.  
    *   *OO Justification:* An exoplanet is gravitationally bound to a host system; orphan planets are invalid in this catalog.
4.  **`Planet` to `Discovery` ($0..* \longleftrightarrow 0..1$):**  
    *   *Schema:* `discovery_id INT NULL`, `ON DELETE SET NULL`.  
    *   *OO Justification:* Multiple planets share telescope discovery telemetry. Discovery records exist independently.
5.  **`Constellation` to `CelestialBoundingBox` ($1 \mathbin{◆\!\!-\!\!-} 1..*$):**  
    *   *OO Justification:* Composition. A constellation owns one or more spatial bounding boxes, cleanly resolving the $360^\circ/0^\circ$ Right Ascension wrap-around (e.g. Cassiopeia) without duplicating the `Constellation` entity.

---

## Decision 3: Separation of ESI Scoring from Habitable Zone Assessment

### Context
The original project plan mentioned a 90% penalty to ESI for planets outside the liquid-water habitable zone. However, in scientific literature (Schulze-Makuch et al., 2011), the Earth Similarity Index is strictly an index of physical and thermal similarity to Earth, independent of the host star's thermodynamic habitable zone (Kopparapu et al., 2013). Applying an arbitrary 90% penalty unconditionally muddles the domain logic and invalidates published ESI reference scores.

### Decision
1.  **Separation of Concerns:**  
    *   `ESICalculator` produces standard, authoritative `ESIResult` (interior, surface, and base ESI).
    *   `HabitableZoneCalculator` produces `HabitableZone` boundaries and evaluates whether a planet's orbit is `TOO_HOT`, `HABITABLE`, or `TOO_COLD`.
2.  **Application of the Strategy Pattern (GoF):**  
    *   Introduce `IESIScoringStrategy` with two implementations:
        *   `StandardESIStrategy`: Default authoritative baseline (unpenalized).
        *   `HabitabilityWeightedStrategy`: Applies the 90% penalty for planets outside the habitable zone.
    *   This provides a clean, explainable GoF design pattern and allows runtime algorithm selection without modifying domain entities (Open/Closed Principle).

---

## Decision 4: Selection of Three GoF Design Patterns

### Context
The evaluation rubric rewards sound object-oriented design and defensible GoF patterns. We must avoid "pattern bloat" or introducing artificial classes that have no real problem to solve.

### Analysis of Candidates
*   **Facade Pattern:** Originally proposed as `SystemExplorationFacade`.  
    *   *Evaluation:* In our layered architecture, `StarSystemCatalogService` already fulfills the role of coordinating repositories and domain services for the API routers. Adding another `Facade` class on top of an Application Service creates artificial layering.  
    *   *Verdict:* **Discarded as redundant.**
*   **Strategy Pattern (GoF Behavioral):**  
    *   *Verdict:* **Adopted.** `IESIScoringStrategy` solves the scientific trade-off between standard ESI and habitability-penalized ESI.
*   **Observer Pattern (GoF Behavioral):**  
    *   *Verdict:* **Adopted.** Solves the concrete cache-invalidation problem identified in the Baseline Audit. When a planet is added, updated, or removed, `AnalyticsCacheObserver` invalidates the in-memory Pandas DataFrame. A companion `CatalogAuditLogObserver` logs modifications for operational auditing. Counter synchronization on `StarSystem` is deliberately removed because planet count is derived directly from the Planet repository, eliminating dual-write race conditions.
*   **Builder Pattern (GoF Creational):**  
    *   *Verdict:* **Adopted.** `PlanetBuilder` manages the complex construction of `Planet` entities containing over 15 optional parameters, calculates missing fallbacks (Kepler's 3rd Law, density), validates physical invariants, and packages value objects (`OrbitalParameters`).

---

## Decision 5: Genuine Stateful Workflow for State Chart

### Context
A State Chart diagram is required by the rubric. An earlier draft proposed astrophysical states such as "TTV Verified" or "Spectroscopically Characterized".

### Investigation & Verdict
Inspection of `data/ExoplanetDataset.csv` confirmed that all 6,153 records are already confirmed exoplanets with no historical disposition column. Modeling physical verification states is scientifically ungrounded in this dataset. Furthermore, terms like `Modifying` or `Purged` are transient operations or terminal actions, not resting entity states.

Instead, we model the **`PlanetCatalogRecord` Curation Lifecycle** (minimal resting states):
*   `Draft` $\xrightarrow{\text{validate \& persist}}$ `Cataloged (Active)` $\xrightarrow{\text{delete}}$ `[*]` (Destroyed).  
*   `update()` is modeled as an operational self-transition on `Cataloged` with attribute re-validation and cache invalidation.  
*   Additionally, a UI-level **`PlanetComparisonSession`** state machine (`Empty` $\to$ `PendingSelection` $\to$ `Comparable` $\to$ `Full`) provides an alternative interactive workflow for demonstration.

---

## Decision 6: Verified Snapshot for UML Object Diagram

### Context
The Object Diagram must represent a concrete, factual snapshot of domain objects and their links, not synthetic or imagined data.

### Verification
The **Kepler-186** system was verified in `data/ExoplanetDataset.csv` and `data/Constellations.csv`:
*   `StarSystem`: `Kepler-186` (RA: 298.6527°, Dec: 43.9550°, Dist: 579.24 ly, 5 planets, 1 star)
*   `Star`: `Kepler-186` (Spectral: M1, Temp: 3755 K, Mass: 0.544 $M_\odot$, Radius: 0.523 $R_\odot$)
*   `Planet`: `Kepler-186 f` (Period: 129.94 d, Semi-major axis: 0.432 AU, Mass: 1.71 $M_\oplus$, Radius: 1.17 $R_\oplus$, Density: 5.87 $\text{g/cm}^3$, Temp: 177 K)
*   `Discovery`: Kepler Mission (Year: 2014, Method: Transit, Telescope: 0.95 m Kepler Telescope)
*   `Constellation`: `Cygnus` (RA: 286.5° to 330.0°, Dec: 27.7° to 61.6°, Pop Rank: 9)

---

## Decision 7: Consistent Naming Convention

Across all code, documentation, test suites, and diagrams, the project will be referred to as **COSMOSDB-OOAD** consistently.

---

## Decision 8: Cassiopeia RA Wraparound Representation

### Context
Right Ascension wraps around at $360^\circ \equiv 0^\circ$. Constellations like Cassiopeia cross this meridian ($345^\circ \to 52.5^\circ$), causing split rows in raw CSV data and broken single-interval comparisons.

### Decision
Support dual protection:
1.  `Constellation` aggregates $1..*$ `CelestialBoundingBox` value objects (directly matching the two segments in `Constellations.csv`).
2.  `CelestialBoundingBox` natively supports wraparound intervals where $\min\text{RA} > \max\text{RA}$, evaluating containment as `(ra >= min_ra or ra <= max_ra)`.
3.  Comprehensive boundary-condition unit tests verify strict interval edges ($345.0^\circ$, $52.5^\circ$, $0.0^\circ$, $360.0^\circ$).

---

## Decision 9: Frontend & PlantUML Tooling Strategy

1.  **Frontend:** Retain and refactor the existing React + TypeScript + Vite frontend. Add a dedicated `/compare` page for multi-planet comparison.
2.  **PlantUML:** Editable `.puml` files stored in `docs/OOAD/diagrams/` are the definitive source of truth. A lightweight Python runner (`scripts/render_diagrams.py`) will check local Java/Graphviz availability, render SVG/PNG outputs, and provide clear fallback instructions if dependencies are missing.

