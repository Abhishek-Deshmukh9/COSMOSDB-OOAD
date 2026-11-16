# COSMOSDB-OOAD

An OOAD-focused implementation of the COSMOSDB exoplanet catalog and comparative planetology platform. This project lives beside the original prototype and maintains strict adherence to SOLID, clean architecture, Domain-Driven Design (DDD), and GoF design patterns.

## Features & Capabilities

- **Star System & Planet Exploration:** Search, browse, and explore systems with their host stars and independent planet aggregates.
- **Dedicated Comparative Planetology (`/compare`):** Side-by-side scientific comparison of up to 4 exoplanets with Earth Similarity Index gauges, habitable zone status, physical parameters, and comparative metrics.
- **Domain Services:**
  - `ESICalculator`: Modular calculation of interior, surface, and global Earth Similarity Index.
  - `PlanetClassifier`: Radius and mass-fallback classification into canonical archetypes (*Terrestrial / Rocky*, *Super-Earth*, *Mini-Neptune*, *Gas Giant*, *Super-Jupiter*).
  - Habitable Zone assessment with inner/outer boundaries based on stellar luminosity.
- **Pre-Aggregated Analytics Dashboard (`/analytics`):** 9 real-time analytical datasets powered by GoF Observer cache invalidation:
  1. Overview Summary Stats
  2. Earth Similarity Index (ESI) Sunburst Tier Distribution
  3. Discovery Methods Timeline
  4. Mass-Radius Logarithmic Scatter Plot
  5. Stellar Spectral Type Distribution (O, B, A, F, G, K, M, Other)
  6. Multi-Planet System Complexity
  7. Orbital Period vs. Eccentricity Scatter Plot
  8. Stellar Metallicity vs. Planet Count
  9. Distance Distribution Log-Spaced Histogram
- **Interactive 3D Visualizations:** Orbital simulation canvas (`OrbitVisualizer`), space canvas background (`SpaceCanvas`), dynamic ESI gauge dials (`ESIGauge`), and habitable zone trackers (`ZoneTracker`).

---

## Architectural Principles & GoF Patterns

1. **Dependency Inversion Principle (DIP):** Presentation and application layers depend solely on repository protocols (`IPlanetRepository`, `IStarSystemRepository`, `IConstellationRepository`), never on concrete database drivers.
2. **DDD Aggregate Boundaries:**
   - `StarSystem` is an Aggregate Root compositing its cataloged `Star` entities ($1 \mathbin{◆\!\!-\!\!-} 1..*$).
   - `Planet` is an autonomous Aggregate Root referencing its host system strictly by identity (`system_id: int`), completely eliminating cyclical dependencies.
   - `StarSystem.planet_count` is derived dynamically from `COUNT(*)` in the Planet repository, preventing drifting state.
3. **Spherical Coordinate Wraparound:** `CelestialBoundingBox` natively supports interval wraparound across the $0^\circ/360^\circ$ meridian (`min_ra > max_ra`). Database seeding deduplicates multi-box constellations (e.g., Cassiopeia) into a single entity.
4. **Design Patterns:**
   - **Strategy (GoF):** `IESIScoringStrategy` allows switching between `StandardESIStrategy` (authoritative baseline) and `HabitabilityWeightedStrategy` (applies a 90% penalty to planets outside the habitable zone).
   - **Observer (GoF):** `CatalogEventPublisher` notifies `AnalyticsCacheObserver` to invalidate cached analytics and `CatalogAuditLogObserver` to record mutations upon any catalog changes.
   - **Builder (GoF):** `PlanetBuilder` validates domain constraints (e.g. non-physical measurements) and safely constructs immutable `Planet` aggregates with optional measurements and fallback estimates.

---

## Windows Quickstart

### 1. Database and Seed Data

Execute `database\schema.sql` with MySQL:

```powershell
cmd /c "mysql -u root -p < database\schema.sql"
```

Configure local credentials in `backend\.env` (see `.env.example`).
Run the deduplicated seed script:

```powershell
Set-Location backend
.\.venv\Scripts\python.exe scripts\seed_database.py
```

### 2. Backend API Service

```powershell
Set-Location backend
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m uvicorn cosmosdb.api.app:app --host 127.0.0.1 --port 8000 --reload
```

Interactive OpenAPI documentation is available at `http://127.0.0.1:8000/docs`.

### 3. Frontend Web Application

```powershell
Set-Location frontend
npm install --legacy-peer-deps
npm run dev
```

Open `http://127.0.0.1:5173` in your browser.

---

## Complete API Specification

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/systems` | Paginated search of star systems |
| `GET` | `/api/systems/{id}` | System detail with owned stars and child planets |
| `GET` | `/api/planets` | Paginated planet catalog with filtering & ESI sorting |
| `GET` | `/api/planets/{id}` | Planet detail with ESI terms and archetype |
| `GET` | `/api/planets/compare` | Multi-planet comparison matrix (2 to 4 planets) |
| `POST` | `/api/planets` | Create a new cataloged exoplanet |
| `PATCH`| `/api/planets/{id}` | Update existing exoplanet measurements |
| `DELETE`| `/api/planets/{id}` | Remove exoplanet from catalog |
| `GET` | `/api/discovery-methods` | List distinct discovery methods |
| `GET` | `/api/constellations` | List cataloged constellations with system counts |
| `GET` | `/api/analytics/summary` | Global counts, multi-planet systems, top facility |
| `GET` | `/api/analytics/esi-distribution`| ESI tier breakdown (Earth-like, Potential, etc.) |
| `GET` | `/api/analytics/discovery-timeline`| Historical discovery counts by method per year |
| `GET` | `/api/analytics/mass-radius-scatter`| Logarithmic mass-radius coordinates |
| `GET` | `/api/analytics/spectral-types` | Host star spectral classification counts |
| `GET` | `/api/analytics/system-complexity`| System counts grouped by planet quantity |
| `GET` | `/api/analytics/eccentricity-period`| Orbital period vs. eccentricity distribution |
| `GET` | `/api/analytics/metallicity-planets`| Host star metallicity vs. system planet count |
| `GET` | `/api/analytics/distance-histogram`| Log-spaced distance distribution bins |

---

## UML Diagrams

All UML diagrams are authored in PlantUML under `docs/OOAD/diagrams/` with rendered SVGs:

1. `class-diagram.puml` / `class-diagram.svg` — Complete domain, application, and infrastructure model.
2. `object-diagram.puml` / `object-diagram.svg` — Grounded instance graph (Kepler-186 system).
3. `package-component.puml` / `package-component.svg` — Layered architectural package structure.
4. `use-case.puml` / `use-case.svg` — Use case model for astronomer/explorer interactions.
5. `activity-search-system.puml` / `activity-search-system.svg` — System search & detail workflow.
6. `activity-esi-calculation.puml` / `activity-esi-calculation.svg` — Parameter fallbacks, ESI & HZ workflow.
7. `sequence-search-system.puml` / `sequence-search-system.svg` — Interaction sequence for system browsing.
8. `sequence-compare-planets.puml` / `sequence-compare-planets.svg` — Interaction sequence for planet comparison.
9. `state-planet-record.puml` / `state-planet-record.svg` — Planet catalog curation lifecycle states.
