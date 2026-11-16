# Architecture

## Layers

1. **Presentation (`cosmosdb.api`)** validates HTTP input and invokes application services.
2. **Application (`cosmosdb.application`)** coordinates browsing, comparison, analytics and catalog management through repository ports.
3. **Domain (`cosmosdb.domain`)** owns the planet/system entities, celestial value objects, catalog lifecycle, ESI calculator and interchangeable scoring strategies.
4. **Infrastructure (`cosmosdb.infrastructure`)** implements repository ports with MySQL and maps rows to domain entities.

Dependencies point inward: application services depend on repository protocols, not concrete SQL adapters. The React UI calls the HTTP API through `frontend/src/api.ts`.

## Aggregate and relationship choices

- `StarSystem` contains its `Star` entities; the domain represents this as a tuple owned by the system.
- `Planet` is independently queried and references its host through `system_id`; system details compose a query-side response by asking the Planet repository.
- System planet count comes from `COUNT(*)` in the Planet repository.
- Constellation bounding boxes are value objects that support 0/360-degree wraparound.
- `PlanetCatalogRecord` models only Draft → Cataloged → Removed lifecycle transitions.

## Patterns implemented

- **Repository (architectural):** `IPlanetRepository` and `IStarSystemRepository` isolate persistence.
- **Strategy (GoF):** `StandardESIStrategy` and `HabitabilityWeightedStrategy` choose scoring policy without changing `ESICalculator`.
- **Observer (GoF):** catalog mutations publish events to analytics-cache and audit-log listeners.
- **Builder (GoF):** `PlanetBuilder` validates construction when records contain many optional measurements.
- No extra Facade is used: application services already coordinate use cases.

## Data flow

HTTP request → API validation → application service → repository port → MySQL adapter → mapped domain objects → service result → JSON response.

For comparison, the application service verifies two to four distinct IDs and loads the requested independent Planet aggregates. For system details it loads the system, its owned stars, and planets by `system_id`.
