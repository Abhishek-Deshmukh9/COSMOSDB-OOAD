# COSMOSDB-OOAD Design Decisions & Trade-Offs

## 1. Aggregate Boundaries and Lifecycle
- **Decision:** `StarSystem` composites `Star` ($1 \mathbin{◆\!\!-\!\!-} 1..*$). `Planet` is modeled as an independent Aggregate Root referencing `StarSystem` strictly by `system_id`.
- **Justification:** Host stars have no independent identity outside their planetary system. Conversely, exoplanets have independent lifecycles, observational histories (transits, discovery papers), and curation workflows. Modeling `Planet` independently avoids bloated monolithic aggregates and circular references.

## 2. Derivation of Planet Counts
- **Decision:** System planet count is dynamically derived via `COUNT(*)` from `IPlanetRepository` queries rather than synchronized with an Observer or stored as a drifting mutable counter column.
- **Justification:** Eliminates concurrency bugs, state drift, and race conditions during simultaneous mutations.

## 3. ESI Baseline vs. Habitability Assessment
- **Decision:** Standard ESI calculation remains the unpenalized empirical baseline. Habitable zone assessment is computed independently.
- **Justification:** The scientific literature (Schulze-Makuch et al., 2011) defines ESI based purely on physical parameters (radius, density, escape velocity, surface temperature). Conflating habitability with similarity violates scientific definition. Where an application specifically requests a penalty for non-habitable orbits, the `HabitabilityWeightedStrategy` is explicitly selected via GoF Strategy.

## 4. Constellation Spherical Wraparound & Deduplication
- **Decision:** `CelestialBoundingBox` natively models RA intervals crossing the $0^\circ/360^\circ$ meridian (`min_ra > max_ra`). The seed process merges split CSV rows (Cassiopeia, Andromeda, Pegasus, etc.) into unified constellation boundaries.
- **Justification:** Prevents artificial duplicate database rows for a single physical constellation while preserving spatial containment fidelity.

## 5. Domain Services Separation
- **Decision:** Extracted `PlanetClassifier`, `ESICalculator`, and `HabitableZoneCalculator` into dedicated domain services rather than packing all calculation methods onto the `Planet` entity.
- **Justification:** Conforms to Single Responsibility Principle (SRP) and High Cohesion. `Planet` represents the entity data; domain services own the algorithmic rules and classifications.

## 6. Minimal Stateful Lifecycle
- **Decision:** Exoplanet catalog curation follows a strict 3-state machine: `DRAFT` $\to$ `CATALOGED` $\to$ `REMOVED`.
- **Justification:** Speculative states like "TTV Verified" or "Spectroscopically Characterized" are observational classifications, not operational domain lifecycle states. The 3-state curation lifecycle matches real data operations.

## 7. Frontend Architecture (Option A: Retain & Refactor Rich UI)
- **Decision:** Retained and refactored the original rich React + TypeScript frontend with 3D canvas visualizers (`OrbitVisualizer`, `SpaceCanvas`), interactive dials (`ESIGauge`), and 9-chart ECharts dashboard (`Analytics`). Added dedicated `/compare` comparative planetology matrix.
- **Justification:** Delivers superior user experience and meets all assignment requirements without sacrificing the original visual simulations.
