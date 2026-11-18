# COSMOSDB-OOAD — Exoplanet Catalog & Comparative Planetology

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()
[![Tests](https://img.shields.io/badge/tests-28%2F28%20passing-success.svg)]()
[![Architecture](https://img.shields.io/badge/architecture-Clean%20%2F%20DDD%20%2F%20SOLID-blue.svg)]()
[![Frontend](https://img.shields.io/badge/frontend-React%2018%20%2B%20TypeScript%20%2B%20Vite-61dafb.svg)]()
[![Backend](https://img.shields.io/badge/backend-FastAPI%20%2B%20Python%203.11+-009688.svg)]()
[![Database](https://img.shields.io/badge/database-MySQL%208.0+-4479A1.svg)]()

An enterprise-grade, object-oriented redesign and implementation of the **COSMOSDB** exoplanet catalog and comparative planetology platform. Built strictly following **Clean Architecture**, **Domain-Driven Design (DDD)**, **SOLID principles**, and **GoF design patterns** (Strategy, Observer, Builder).

---

## 📑 Table of Contents

1. [Current Project State](#-current-project-state)
2. [Quickstart Guide (Running the App)](#-quickstart-guide-running-the-app)
3. [Troubleshooting & Common Pitfalls](#-troubleshooting--common-pitfalls)
4. [Key Features & Web Interface](#-key-features--web-interface)
5. [Architecture & GoF Design Patterns](#-architecture--gof-design-patterns)
6. [Complete REST API Specification](#-complete-rest-api-specification)
7. [Testing & Verification](#-testing--verification)
8. [UML Diagrams](#-uml-diagrams)
9. [Repository Structure](#-repository-structure)

---

## 🚀 Current Project State

The project implementation is **100% complete, fully verified, and actively passing all automated tests**:

- **Backend:** Fully operational FastAPI REST API running on Python 3.11+ with strict Clean Architecture layers (Domain $\to$ Application $\to$ Infrastructure $\to$ API Presentation).
- **Database:** Normalized MySQL 8.0 schema containing **6,154 exoplanets**, **4,585 stars**, and **86 distinct constellations** (with spatial wraparound deduplication).
- **Frontend:** Modernized React 18 + TypeScript + Vite single-page application with 3D physics-based visualizers (`Three.js`), dynamic SVG dials, and 9 interactive analytics charts (`Apache ECharts`).
- **Automated Tests:** **28 out of 28** domain, service, repository, classifier, analytics, and API integration tests passing with 0 failures and 0 errors.
- **Frontend Build:** Compiled cleanly in 8.6s with **0 TypeScript or Vite bundling errors**.
- **OOAD Specification & Diagrams:** All **9 UML diagrams** authored in PlantUML (`.puml`) and pre-rendered to scalable vector graphics (`.svg`).

---

## ⚡ Quickstart Guide (Running the App)

Running the full application requires starting **two services in parallel**: the FastAPI backend server and the Vite React frontend development server.

### Prerequisites

- **Python 3.11+** (virtual environment located at `backend/.venv`)
- **Node.js 18+** & npm
- **MySQL Server 8.0+** running as a local service (default port `3306`)

---

### Step 1: Ensure MySQL is Running

Verify that the local Windows MySQL service is active:

```powershell
Get-Service MySQL80
```

If it is stopped, start it:
```powershell
Start-Service MySQL80
```

> **Database Configuration & Verified Credentials:**
> The backend connects via [backend/.env](file:///c:/Users/abhis/Desktop/Pjts/OOAD/COSMODB-OOAD/OOAD-Implementation/backend/.env):
> ```env
> MYSQL_HOST=127.0.0.1
> MYSQL_USER=cosmos
> MYSQL_PASSWORD=cosmos123
> MYSQL_DB_NAME=cosmosdb
> MYSQL_PORT=3306
> ```
> *(If you ever need to re-seed or initialize from scratch, see [Database Setup & Seeding](#database-setup--seeding) below).*

---

### Step 2: Start the Backend API (Terminal 1)

Open a **PowerShell terminal** dedicated to the backend:

```powershell
cd c:\Users\abhis\Desktop\Pjts\OOAD\COSMODB-OOAD\OOAD-Implementation\backend
.\.venv\Scripts\python.exe -m uvicorn cosmosdb.api.app:app --host 127.0.0.1 --port 8000 --reload
```

- **API Base URL:** `http://127.0.0.1:8000`
- **Interactive Swagger Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **API Healthcheck:** [http://127.0.0.1:8000/api/analytics/summary](http://127.0.0.1:8000/api/analytics/summary)

---

### Step 3: Start the Frontend UI (Terminal 2)

Open a **second PowerShell terminal** dedicated to the frontend:

```powershell
cd c:\Users\abhis\Desktop\Pjts\OOAD\COSMODB-OOAD\OOAD-Implementation\frontend
npm run dev
```

- **Web Application URL:** [http://localhost:5173](http://localhost:5173)

Open [http://localhost:5173](http://localhost:5173) in your browser. Both the backend and frontend must remain running simultaneously in their respective terminal windows.

---

## 🛠️ Troubleshooting & Common Pitfalls

| Symptom / Error | Root Cause | Solution |
|---|---|---|
| **`ERR_CONNECTION_REFUSED` on `http://localhost:5173`** | The Vite frontend development server is not running or the terminal was closed. | Open a PowerShell terminal, navigate to `frontend`, and run `npm run dev`. Keep the terminal open. |
| **`Comparison API returned HTTP 503` or infinite spinner on `/analytics`** | The backend cannot connect to MySQL (service is stopped or credentials in `.env` are invalid). | 1. Run `Get-Service MySQL80` to verify MySQL is running.<br>2. Confirm [backend/.env](file:///c:/Users/abhis/Desktop/Pjts/OOAD/COSMODB-OOAD/OOAD-Implementation/backend/.env) has `MYSQL_USER=cosmos` and `MYSQL_PASSWORD=cosmos123`. |
| **Blank white screen on `/observatory` or `/add-planet`** | Frontend attempted to call an unhandled API endpoint or map over an empty response. | Fixed in current code: all dropdown and list renders are protected with `Array.isArray()` defensive guards, and backend route aliases (`/api/discovery_methods`, `/api/search`, `/api/crud/planets`) are wired. |
| **Port 8000 or 5173 already in use** | A previous background process did not terminate. | Run `Get-Process python` or `Get-Process node` in PowerShell and terminate the stale process (`Stop-Process -Id <PID>`). |

### Database Setup & Seeding

If setting up on a completely blank MySQL instance:

1. Create the database and user:
   ```sql
   CREATE DATABASE IF NOT EXISTS cosmosdb;
   CREATE USER IF NOT EXISTS 'cosmos'@'%' IDENTIFIED BY 'cosmos123';
   GRANT ALL PRIVILEGES ON cosmosdb.* TO 'cosmos'@'%';
   FLUSH PRIVILEGES;
   ```
2. Apply the DDL schema:
   ```powershell
   cd c:\Users\abhis\Desktop\Pjts\OOAD\COSMODB-OOAD\OOAD-Implementation
   cmd /c "mysql -u cosmos -pcosmos123 cosmosdb < database\schema.sql"
   ```
3. Run the deduplicating seed script (processes CSV data and merges spherical wraparound constellations):
   ```powershell
   cd backend
   .\.venv\Scripts\python.exe scripts\seed_database.py
   ```

---

## 🌟 Key Features & Web Interface

The frontend application provides an intuitive astronomical workspace with rich interactive visualizations:

1. **Interactive 3D Orbit Visualization (`/`):**
   - Full-screen procedural space background (`SpaceCanvas`) with drifting star particles.
   - Interactive multi-body Keplerian orbital mechanics simulation canvas (`OrbitVisualizer`).
2. **Observatory Catalog (`/observatory`):**
   - Instant search and multi-criteria filtering by discovery method and constellation.
   - Dynamic sorting by Earth Similarity Index (ESI), planetary mass, planetary radius, equilibrium temperature, and distance.
   - Responsive card and table layouts across 6,150+ confirmed exoplanet records.
3. **Dedicated Comparative Planetology Matrix (`/compare`):**
   - Direct side-by-side scientific comparison of **2 to 4 exoplanets** simultaneously.
   - Instant autocomplete planet search and multi-select tags with quick-remove chips.
   - Radial Earth Similarity Index (ESI) circular gauge dials (`ESIGauge`).
   - Categorical habitable zone determination (`HABITABLE`, `TOO_HOT`, `TOO_COLD`, `UNKNOWN`).
   - Parameter matrix: radius, mass, density, equilibrium temperature, semi-major axis, orbital period, insolation flux, eccentricity, discovery facility/year, and host star parameters.
4. **Mission Control Analytics Dashboard (`/analytics`):**
   - 9 real-time analytical datasets rendered via Apache ECharts and backed by GoF Observer cache invalidation:
     1. *Catalog Summary Cards:* Confirmed planets, multi-planet systems, cataloged constellations, top discovery facility.
     2. *Habitability Sunburst Chart:* Earth Similarity Index tier breakdown (Earth-like, Potential, Extreme, Inhospitable, Unknown).
     3. *Discovery Timeline Stacked Area Chart:* Historical discoveries by detection method from 1992 to present.
     4. *Mass-Radius Log-Log Scatter Plot:* Colored by planetary equilibrium temperature.
     5. *Stellar Spectral Types Horizontal Bar Chart:* Distribution of host stars (O, B, A, F, G, K, M).
     6. *Multi-Planet System Complexity Bar Chart:* System counts grouped by number of planets (1 to 8+).
     7. *Eccentricity vs. Orbital Period Scatter Plot:* Orbital architecture distribution.
     8. *Stellar Metallicity vs. Planet Count Scatter Plot:* [Fe/H] enrichment correlation.
     9. *Distance Distribution Log-Spaced Histogram:* Planetary distance in light-years.
5. **Planet Curation Matrix (`/add-planet`):**
   - Register new exoplanet discoveries with host system linkage and physical property validation.
   - One-click habitability presets (*Extremely Habitable*, *Moderately Habitable*, *Toxic Inferno*, *Frozen Wasteland*, *Gas Giant*).
6. **System View (`/system/:id`):**
   - Multi-planet architectural view with host star specifications and child planet orbital planes.
7. **Planet Detail (`/planet/:id`):**
   - Comprehensive astrophysical breakdown including interior vs. surface ESI terms, stellar insolation, and archetype classification.

---

## 🏛️ Architecture & GoF Design Patterns

### 1. Clean Architecture & Dependency Inversion Principle (DIP)

```text
[ Presentation Layer: FastAPI HTTP Endpoints  |  React TypeScript UI ]
                                │
                                ▼
[ Application Layer: Catalog Services, AnalyticsService, Observers ]
  - Defines: IPlanetRepository, IStarSystemRepository, IConstellationRepository
                                │
                                ▼
[ Domain Layer: Entities, Value Objects, Domain Services ]
  - Pure Python, zero framework or database dependencies
                                ▲
                                │ (implements interfaces)
[ Infrastructure Layer: MySQL Repositories & Connection Pool ]
  - Concrete SQL queries, connection pooling, and entity mapping
```

- **Strict Dependency Direction:** High-level application policies do not depend on low-level database details. Both depend on abstractions (`IPlanetRepository`, `IStarSystemRepository`, `IConstellationRepository`) defined in the application ports layer.
- **Framework Independence:** Domain logic in `cosmosdb.domain` has no imports from FastAPI, Starlette, PyMySQL, or SQLAlchemy.

### 2. DDD Aggregate Boundaries & Invariants

- **`StarSystem` (Aggregate Root):** Composites host `Star` entities ($1 \mathbin{◆\!\!-\!\!-} 1..*$). A star has no independent lifecycle outside its parent system.
- **`Planet` (Autonomous Aggregate Root):** References `StarSystem` strictly by identity (`system_id: int`), completely eliminating circular references and allowing independent planet queries, updates, and curation.
- **Dynamic Planet Count:** `StarSystem.planet_count` is derived dynamically via `COUNT(*)` from `IPlanetRepository`, eliminating state drift and concurrency race conditions.
- **Spherical Coordinate Wraparound:** `CelestialBoundingBox` supports right ascension intervals crossing the $0^\circ / 360^\circ$ meridian (`min_ra > max_ra`). The seed process merges split boxes (e.g., Cassiopeia $[345.0^\circ, 52.5^\circ]$) to ensure exactly 86 unique constellation records.

### 3. Dedicated Domain Services

- **`ESICalculator` ([backend/cosmosdb/domain/esi.py](file:///c:/Users/abhis/Desktop/Pjts/OOAD/COSMODB-OOAD/OOAD-Implementation/backend/cosmosdb/domain/esi.py)):
  Implements the standard Earth Similarity Index formulation:
  $$\text{ESI}_r = \left(1 - \left|\frac{x - x_0}{x + x_0}\right|\right)^w$$
  Computes interior similarity ($R_p, \rho_p$) and surface similarity ($v_e, T_s$) separately from habitable zone status.
- **`PlanetClassifier` ([backend/cosmosdb/domain/services/planet_classifier.py](file:///c:/Users/abhis/Desktop/Pjts/OOAD/COSMODB-OOAD/OOAD-Implementation/backend/cosmosdb/domain/services/planet_classifier.py)):
  Categorizes planets into standard astrophysical archetypes (*Terrestrial / Rocky*, *Super-Earth*, *Mini-Neptune*, *Gas Giant*, *Super-Jupiter*, *Unknown*) using planetary radius with mass fallback.
- **`HabitableZoneCalculator` ([backend/cosmosdb/domain/esi.py](file:///c:/Users/abhis/Desktop/Pjts/OOAD/COSMODB-OOAD/OOAD-Implementation/backend/cosmosdb/domain/esi.py)):
  Derives stellar luminosity ($L = R_*^2 \cdot (T_* / 5778)^4$) and calculates inner boundary ($r_{\text{in}} = \sqrt{L / 1.1}\text{ AU}$) and outer boundary ($r_{\text{out}} = \sqrt{L / 0.53}\text{ AU}$).

### 4. Three GoF Design Patterns

1. **Strategy Pattern (`IESIScoringStrategy`):**
   - **File:** [backend/cosmosdb/domain/esi.py](file:///c:/Users/abhis/Desktop/Pjts/OOAD/COSMODB-OOAD/OOAD-Implementation/backend/cosmosdb/domain/esi.py)
   - Encapsulates scoring policies without modifying `ESICalculator`.
   - `StandardESIStrategy`: Pure scientific physical score without habitable-zone penalty.
   - `HabitabilityWeightedStrategy`: Applies an explicit 90% penalty ($\times 0.1$) if the planet orbits outside the host star's habitable zone.
2. **Observer Pattern (`CatalogEventPublisher`):**
   - **File:** [backend/cosmosdb/application/events.py](file:///c:/Users/abhis/Desktop/Pjts/OOAD/COSMODB-OOAD/OOAD-Implementation/backend/cosmosdb/application/events.py)
   - Decouples catalog mutations from secondary concerns.
   - `AnalyticsCacheObserver`: Automatically invalidates the in-memory analytics cache whenever a planet is created, updated, or removed, ensuring instant cache consistency.
   - `CatalogAuditLogObserver`: Logs structured audit events for mutations.
3. **Builder Pattern (`PlanetBuilder`):**
   - **File:** [backend/cosmosdb/domain/entities.py](file:///c:/Users/abhis/Desktop/Pjts/OOAD/COSMODB-OOAD/OOAD-Implementation/backend/cosmosdb/domain/entities.py)
   - Enforces physical parameter validation (rejects non-physical measurements like negative radius or mass).
   - Computes fallback estimates (e.g. bulk density from mass & radius, semi-major axis from Kepler's 3rd Law).
   - Constructs immutable `Planet` entity instances.

---

## 📡 Complete REST API Specification

| HTTP Method | Route | Parameters / Body | Description |
|---|---|---|---|
| `GET` | `/api/systems` | `q`, `constellation`, `page`, `limit` | Paginated search and browsing of star systems |
| `GET` | `/api/systems/{id}` | `id` (path) | System detail with owned stars and child planets |
| `GET` | `/api/planets` | `q`, `constellation`, `method`, `sort_by`, `sort_dir`, `page`, `limit` | Paginated planet catalog with sorting (`esi_score`, `mass`, `radius`, `temp`, `distance`) |
| `GET` | `/api/planets/{id}` | `id` (path) | Single planet detail with full ESI metrics and archetype classification |
| `GET` | `/api/planets/{id}/details` | `id` (path) | Frontend compatibility alias for `/api/planets/{id}` |
| `GET` | `/api/planets/compare` | `planet_ids=1&planet_ids=2...` (2 to 4 IDs) | Multi-planet comparison matrix with side-by-side metrics |
| `POST` | `/api/planets` | Planet JSON payload | Create a new cataloged exoplanet record |
| `PATCH`| `/api/planets/{id}` | Partial planet JSON payload | Update existing exoplanet measurements |
| `DELETE`| `/api/planets/{id}` | `id` (path) | Remove exoplanet record from catalog |
| `GET` | `/api/crud/planets` | Same as `/api/planets` | Compatibility alias for legacy CRUD operations |
| `GET` | `/api/discovery-methods` | None | List distinct discovery methods |
| `GET` | `/api/discovery_methods` | None | Frontend compatibility alias with underscore |
| `GET` | `/api/constellations` | None | List cataloged constellations with system counts |
| `GET` | `/api/search` | `q` (query string) | Fast system autocomplete search |
| `GET` | `/api/analytics/summary` | None | Global counts (planets, systems, constellations, top facility) |
| `GET` | `/api/analytics/esi-distribution` | None | Earth Similarity Index tier counts |
| `GET` | `/api/analytics/discovery-timeline` | None | Historical discoveries by method per year |
| `GET` | `/api/analytics/mass-radius-scatter` | None | Logarithmic mass vs. radius scatter plot coordinates |
| `GET` | `/api/analytics/spectral-types` | None | Host star spectral classification counts (O, B, A, F, G, K, M) |
| `GET` | `/api/analytics/system-complexity` | None | System counts grouped by number of planets |
| `GET` | `/api/analytics/eccentricity-period` | None | Orbital period vs. eccentricity coordinates |
| `GET` | `/api/analytics/metallicity-planets` | None | Host star metallicity [Fe/H] vs. system planet count |
| `GET` | `/api/analytics/distance-histogram` | None | Log-spaced planetary distance histogram bins |

---

## 🧪 Testing & Verification

The automated test suite comprehensively exercises domain rules, value objects, domain services, repository ports, caching observers, and FastAPI endpoints.

### Run Backend Tests

From the `backend` directory:

```powershell
cd c:\Users\abhis\Desktop\Pjts\OOAD\COSMODB-OOAD\OOAD-Implementation\backend
$env:PYTHONPATH="."
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

**Test Execution Results:**
```text
test_discovery_timeline (test_analytics.AnalyticsServiceTests) ... ok
test_distance_histogram (test_analytics.AnalyticsServiceTests) ... ok
test_eccentricity_period (test_analytics.AnalyticsServiceTests) ... ok
test_esi_distribution (test_analytics.AnalyticsServiceTests) ... ok
test_mass_radius_scatter (test_analytics.AnalyticsServiceTests) ... ok
test_metallicity_planets (test_analytics.AnalyticsServiceTests) ... ok
test_mutation_invalidates_all_analytics (test_analytics.AnalyticsServiceTests) ... ok
test_spectral_types (test_analytics.AnalyticsServiceTests) ... ok
test_summary_schema_and_values (test_analytics.AnalyticsServiceTests) ... ok
test_system_complexity (test_analytics.AnalyticsServiceTests) ... ok
test_browse_and_compare_return_domain_results (test_api.CatalogApiTests) ... ok
test_catalog_constraint_conflict_is_not_reported_as_database_outage (test_api.CatalogApiTests) ... ok
test_create_requires_an_existing_host_system (test_api.CatalogApiTests) ... ok
test_invalid_page_and_missing_entities_have_api_errors (test_api.CatalogApiTests) ... ok
test_planet_mutations_invalidate_analytics (test_api.CatalogApiTests) ... ok
test_classify_entity (test_classifier.PlanetClassifierTests) ... ok
test_mass_fallback_classifications (test_classifier.PlanetClassifierTests) ... ok
test_missing_and_invalid_measurements (test_classifier.PlanetClassifierTests) ... ok
test_radius_boundary_classifications (test_classifier.PlanetClassifierTests) ... ok
test_wraparound_interval_includes_both_sides_and_meridian (test_domain.CelestialBoundingBoxTests) ... ok
test_builder_rejects_non_physical_measurement (test_domain.PlanetDomainTests) ... ok
test_catalog_record_lifecycle_rejects_invalid_transitions (test_domain.PlanetDomainTests) ... ok
test_esi_strategy_keeps_scientific_score_separate_from_habitability (test_domain.PlanetDomainTests) ... ok
test_list_parameterizes_search_and_maps_a_catalog_entity (test_mysql_repository.MySQLPlanetRepositoryTests) ... ok
test_catalog_change_invalidates_cached_analytics (test_services.AnalyticsObserverTests) ... ok
test_comparison_requires_two_to_four_distinct_existing_planets (test_services.PlanetCatalogServiceTests) ... ok
test_esi_sorting_keeps_missing_scores_last_for_both_directions (test_services.PlanetCatalogServiceTests) ... ok
test_page_and_limit_validation_is_explicit (test_services.PlanetCatalogServiceTests) ... ok

----------------------------------------------------------------------
Ran 28 tests in 0.514s
OK (28/28 tests passing, 0 failures, 0 errors, 100% pass rate)
```

### Verify Frontend Production Build

From the `frontend` directory:

```powershell
cd c:\Users\abhis\Desktop\Pjts\OOAD\COSMODB-OOAD\OOAD-Implementation\frontend
npm run build
```

*(668 modules transformed, compiled cleanly in 8.6s with 0 errors).*

---

## 📐 UML Diagrams

All UML diagrams are authored in PlantUML under `docs/OOAD/diagrams/` and pre-rendered to `.svg`:

| Diagram | PlantUML Source | Rendered Vector Image | Description |
|---|---|---|---|
| **Class Diagram** | [class-diagram.puml](file:///c:/Users/abhis/Desktop/Pjts/OOAD/COSMODB-OOAD/OOAD-Implementation/docs/OOAD/diagrams/class-diagram.puml) | [class-diagram.svg](file:///c:/Users/abhis/Desktop/Pjts/OOAD/COSMODB-OOAD/OOAD-Implementation/docs/OOAD/diagrams/class-diagram.svg) | Complete domain model, DIP ports, domain services, and GoF patterns. |
| **Object Diagram** | [object-diagram.puml](file:///c:/Users/abhis/Desktop/Pjts/OOAD/COSMODB-OOAD/OOAD-Implementation/docs/OOAD/diagrams/object-diagram.puml) | [object-diagram.svg](file:///c:/Users/abhis/Desktop/Pjts/OOAD/COSMODB-OOAD/OOAD-Implementation/docs/OOAD/diagrams/object-diagram.svg) | Real-world grounded object instance graph (Kepler-186 system & planets). |
| **Package Diagram** | [package-component.puml](file:///c:/Users/abhis/Desktop/Pjts/OOAD/COSMODB-OOAD/OOAD-Implementation/docs/OOAD/diagrams/package-component.puml) | [package-component.svg](file:///c:/Users/abhis/Desktop/Pjts/OOAD/COSMODB-OOAD/OOAD-Implementation/docs/OOAD/diagrams/package-component.svg) | Layered Clean Architecture dependency boundaries. |
| **Use Case Diagram** | [use-case.puml](file:///c:/Users/abhis/Desktop/Pjts/OOAD/COSMODB-OOAD/OOAD-Implementation/docs/OOAD/diagrams/use-case.puml) | [use-case.svg](file:///c:/Users/abhis/Desktop/Pjts/OOAD/COSMODB-OOAD/OOAD-Implementation/docs/OOAD/diagrams/use-case.svg) | Primary actors (*Astronomer*, *Catalog Curator*) and operations. |
| **Activity Diagram (Search)** | [activity-search-system.puml](file:///c:/Users/abhis/Desktop/Pjts/OOAD/COSMODB-OOAD/OOAD-Implementation/docs/OOAD/diagrams/activity-search-system.puml) | [activity-search-system.svg](file:///c:/Users/abhis/Desktop/Pjts/OOAD/COSMODB-OOAD/OOAD-Implementation/docs/OOAD/diagrams/activity-search-system.svg) | Workflow of system discovery, filtering, and detail extraction. |
| **Activity Diagram (ESI)** | [activity-esi-calculation.puml](file:///c:/Users/abhis/Desktop/Pjts/OOAD/COSMODB-OOAD/OOAD-Implementation/docs/OOAD/diagrams/activity-esi-calculation.puml) | [activity-esi-calculation.svg](file:///c:/Users/abhis/Desktop/Pjts/OOAD/COSMODB-OOAD/OOAD-Implementation/docs/OOAD/diagrams/activity-esi-calculation.svg) | Measurement validation, fallback derivation, and ESI term calculation. |
| **Sequence Diagram (Search)** | [sequence-search-system.puml](file:///c:/Users/abhis/Desktop/Pjts/OOAD/COSMODB-OOAD/OOAD-Implementation/docs/OOAD/diagrams/sequence-search-system.puml) | [sequence-search-system.svg](file:///c:/Users/abhis/Desktop/Pjts/OOAD/COSMODB-OOAD/OOAD-Implementation/docs/OOAD/diagrams/sequence-search-system.svg) | Synchronous message flow from UI controller to MySQL repository. |
| **Sequence Diagram (Compare)** | [sequence-compare-planets.puml](file:///c:/Users/abhis/Desktop/Pjts/OOAD/COSMODB-OOAD/OOAD-Implementation/docs/OOAD/diagrams/sequence-compare-planets.puml) | [sequence-compare-planets.svg](file:///c:/Users/abhis/Desktop/Pjts/OOAD/COSMODB-OOAD/OOAD-Implementation/docs/OOAD/diagrams/sequence-compare-planets.svg) | Multi-planet retrieval and comparative analytics calculation sequence. |
| **State Machine Diagram** | [state-planet-record.puml](file:///c:/Users/abhis/Desktop/Pjts/OOAD/COSMODB-OOAD/OOAD-Implementation/docs/OOAD/diagrams/state-planet-record.puml) | [state-planet-record.svg](file:///c:/Users/abhis/Desktop/Pjts/OOAD/COSMODB-OOAD/OOAD-Implementation/docs/OOAD/diagrams/state-planet-record.svg) | Exoplanet record lifecycle states (`DRAFT` $\to$ `CATALOGED` $\to$ `REMOVED`). |

To re-render all diagrams locally from PlantUML sources:
```powershell
python scripts\render_diagrams.py
```
*(Requires Java JRE and `plantuml.jar` or PlantUML CLI on PATH).*

---

## 📁 Repository Structure

```text
OOAD-Implementation/
├── backend/
│   ├── cosmosdb/
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── app.py                # FastAPI endpoints, validation & route aliases
│   │   ├── application/
│   │   │   ├── __init__.py
│   │   │   ├── events.py             # GoF Observer event publisher & listeners
│   │   │   ├── ports.py              # DIP abstract repository interfaces
│   │   │   └── services.py           # Catalog, comparison & analytics application services
│   │   ├── domain/
│   │   │   ├── __init__.py
│   │   │   ├── entities.py           # Planet, StarSystem, Star & GoF PlanetBuilder
│   │   │   ├── esi.py                # ESICalculator & GoF Strategy policies
│   │   │   ├── services/
│   │   │   │   ├── __init__.py
│   │   │   │   └── planet_classifier.py  # Planet archetype classification domain service
│   │   │   └── value_objects.py      # CelestialCoordinates, CelestialBoundingBox, HZ
│   │   └── infrastructure/
│   │       ├── __init__.py
│   │       └── mysql.py              # Concrete MySQL repository implementations & pool
│   ├── scripts/
│   │   └── seed_database.py          # Constellation deduplication & dataset seeding
│   ├── tests/
│   │   ├── support.py                # Test mocks & planet builders
│   │   ├── test_analytics.py         # Tests for all 9 analytical datasets
│   │   ├── test_api.py               # FastAPI route integration tests
│   │   ├── test_classifier.py        # Planet archetype classifier tests
│   │   ├── test_domain.py            # Domain rules & value objects tests
│   │   ├── test_mysql_repository.py  # MySQL query mapping tests
│   │   └── test_services.py          # Application services & observer tests
│   ├── .env                          # Local database connection credentials (cosmos/cosmos123)
│   └── requirements.txt              # Python dependencies
├── database/
│   └── schema.sql                    # MySQL relational schema DDL
├── docs/
│   └── OOAD/
│       ├── BASELINE_AUDIT.md         # Baseline audit report
│       ├── IMPLEMENTATION-COMPLETION-REPORT.md # Completion verification report
│       ├── architecture.md           # Clean architecture specification
│       ├── design-decisions.md       # Architectural decisions & justifications
│       └── diagrams/                 # 9 PlantUML (.puml) & rendered (.svg) diagrams
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/           # OrbitVisualizer, ESIGauge, SpaceCanvas, Navbar
│   │   │   └── pages/                # Home, Observatory, ComparePlanets, Analytics
│   │   ├── styles/                   # Tailwind CSS styling
│   │   ├── api.ts                    # Frontend API client
│   │   └── main.tsx                  # React Router root configuration
│   ├── package.json                  # Frontend dependencies
│   ├── tsconfig.json                 # TypeScript compiler configuration
│   └── vite.config.ts                # Vite bundler configuration
└── scripts/
    └── render_diagrams.py            # PlantUML SVG rendering script
```

---

## 👥 Contributors & Academic Context

- **Course:** Object-Oriented Analysis and Design (OOAD)
- **Project Name:** `COSMOSDB-OOAD`
- **Focus:** Domain-Driven Design, Clean Architecture, SOLID Principles, GoF Design Patterns, and Enterprise Web Development.
