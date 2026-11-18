# COSMODB — Baseline Repository Audit

> **Audit date:** 2026-11-13  
> **Auditor:** Antigravity (lead architect)  
> **Repository:** `COSMODB-OOAD/` (local, no git history)  
> **Purpose:** Establish a factual baseline of the existing prototype before designing the new OOAD implementation.

---

## 1. Technology Stack

| Layer | Technology | Version / Notes |
|-------|-----------|-----------------|
| **Frontend** | React 18 + TypeScript | Vite 6.3.5 build tool, pnpm package manager |
| **UI Libraries** | Tailwind CSS 4, MUI 7, Radix UI, ECharts 6, Recharts 2 | Heavy dependency footprint (~60 packages) |
| **Backend** | Python + FastAPI | FastAPI 0.135.3, Uvicorn 0.43.0 |
| **Database** | MySQL | mysql-connector-python 9.6.0, DB name: `CosmosDB` |
| **Analytics** | Pandas 3.0.2, NumPy 2.4.4 | In-process caching with global `_df_cache` |
| **Configuration** | `.env` file (python-dotenv) | Variables: `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DB_NAME`, `MYSQL_PORT` |

---

## 2. Project Structure

```
COSMODB-OOAD/
├── backend/
│   ├── main.py                 # FastAPI app, core read API endpoints
│   ├── crud.py                 # Admin reset + CRUD router (create/update/delete)
│   ├── analytics.py            # Analytics dashboard endpoints (Pandas-based)
│   ├── utils.py                # ESI calculator + helper functions
│   ├── ingestConstellation.py  # CSV → Constellation table ingestion
│   ├── ingest_planets.py       # CSV → Discovery/StarSystem/Star/Planet ingestion
│   └── __pycache__/
├── data/
│   ├── Constellations.csv      # 95 constellation records
│   └── ExoplanetDataset.csv    # 6,153 exoplanet records (33 columns)
├── SQL/
│   └── schema.sql              # MySQL DDL (5 tables, constraints, FKs)
├── src/
│   ├── main.tsx                # React entry point + route definitions
│   ├── app/
│   │   ├── App.tsx             # Legacy demo component (hardcoded Kepler-452b)
│   │   ├── components/
│   │   │   ├── Navbar.tsx      # Global navigation bar + master reset button
│   │   │   ├── ESIGauge.tsx    # Circular SVG gauge for ESI score
│   │   │   ├── ZoneTracker.tsx # Habitable zone horizontal bar visualizer
│   │   │   ├── OrbitVisualizer.tsx  # Canvas-based orbit animation
│   │   │   ├── PlanetInfo.tsx  # Planet info overlay card
│   │   │   ├── SpaceCanvas.tsx # Starfield background animation
│   │   │   ├── figma/ImageWithFallback.tsx
│   │   │   └── ui/            # ~40 shadcn/Radix UI primitives (unused mostly)
│   │   └── pages/
│   │       ├── Home.tsx        # Landing page with narrative sections
│   │       ├── Gallery.tsx     # Star system browsing with search/filter
│   │       ├── SystemView.tsx  # Star system detail + orbit visualizer
│   │       ├── Observatory.tsx # Planet grid with ESI, sorting, filtering
│   │       ├── PlanetDetail.tsx # Full planet detail + inline edit/delete
│   │       ├── AddPlanet.tsx   # Create planet form (new/existing system)
│   │       └── Analytics.tsx   # 9-chart analytics dashboard (ECharts)
│   ├── imports/
│   │   └── image.png
│   └── styles/
│       ├── index.css
│       ├── tailwind.css
│       ├── fonts.css
│       └── theme.css
├── public/
│   └── favicon.ico
├── docs/OOAD/                  # Target for OOAD deliverables
├── .env.example
├── package.json
├── pnpm-lock.yaml
├── tsconfig.json
├── vite.config.ts
├── postcss.config.mjs
├── requirements.txt
├── README.md
└── (various .md/.txt reference files)
```

---

## 3. Database Schema (MySQL)

### 3.1 Tables and Columns

#### `Constellation`
| Column | Type | Constraints |
|--------|------|-------------|
| `constellation_id` | INT | PK, AUTO_INCREMENT |
| `constellation_name` | VARCHAR(255) | NOT NULL |
| `min_ra` | DOUBLE | NOT NULL, CHECK 0–360 |
| `max_ra` | DOUBLE | NOT NULL, CHECK 0–360 |
| `min_dec` | DOUBLE | NOT NULL, CHECK -90–90 |
| `max_dec` | DOUBLE | NOT NULL, CHECK -90–90 |
| `description` | TEXT | NOT NULL |
| `pop_rank` | INT | NOT NULL, CHECK 1–88 |

#### `StarSystem`
| Column | Type | Constraints |
|--------|------|-------------|
| `system_id` | INT | PK, AUTO_INCREMENT |
| `system_name` | VARCHAR(255) | UNIQUE, NOT NULL |
| `ra` | DOUBLE | CHECK 0–360 or NULL |
| `dec` | DOUBLE | CHECK -90–90 or NULL |
| `num_stars` | INT | DEFAULT 1, CHECK > 0 |
| `num_planets` | INT | DEFAULT 1, CHECK ≥ 0 |
| `num_moons` | INT | DEFAULT 0, CHECK ≥ 0 |
| `distance_ly` | DOUBLE | CHECK > 0 or NULL |
| `constellation_id` | INT | FK → Constellation, ON DELETE SET NULL |

#### `Discovery`
| Column | Type | Constraints |
|--------|------|-------------|
| `discovery_id` | INT | PK, AUTO_INCREMENT |
| `discovery_year` | INT | NOT NULL, CHECK 1992–2026 |
| `discovery_method` | VARCHAR(255) | NOT NULL |
| `discovery_locale` | VARCHAR(255) | NOT NULL |
| `discovery_facility` | VARCHAR(255) | NOT NULL |
| `discovery_telescope` | VARCHAR(255) | NOT NULL |
| `discovery_instrument` | VARCHAR(255) | NOT NULL |

#### `Star`
| Column | Type | Constraints |
|--------|------|-------------|
| `star_id` | INT | PK, AUTO_INCREMENT |
| `star_name` | VARCHAR(255) | NOT NULL, UNIQUE |
| `system_id` | INT | FK → StarSystem, NOT NULL, ON DELETE CASCADE |
| `spectral_type` | VARCHAR(20) | Nullable |
| `star_temp` | INT | CHECK 415–57000 or NULL |
| `star_radius` | DOUBLE | CHECK 0.0115–88.475 or NULL |
| `star_mass` | DOUBLE | CHECK 0.0094–10.94 or NULL |
| `star_metallicity` | DOUBLE | CHECK -1–0.79 or NULL |
| `star_luminosity` | DOUBLE | CHECK -6.09–3.8 or NULL (stored as log₁₀) |
| `star_gravity` | DOUBLE | CHECK 0.541–8.07 or NULL |
| `star_age` | DOUBLE | CHECK 0–16.1 or NULL |
| `star_brightness` | DOUBLE | CHECK 2.36–20.19 or NULL |

#### `Planet`
| Column | Type | Constraints |
|--------|------|-------------|
| `planet_id` | INT | PK, AUTO_INCREMENT |
| `planet_name` | VARCHAR(255) | NOT NULL, UNIQUE |
| `system_id` | INT | FK → StarSystem, NOT NULL, ON DELETE CASCADE |
| `discovery_id` | INT | FK → Discovery, ON DELETE SET NULL |
| `is_circumbinary` | BOOLEAN | NOT NULL |
| `orbital_period` | DOUBLE | CHECK range or NULL |
| `orbit_radius` | DOUBLE | CHECK range or NULL |
| `radius_earth` | DOUBLE | CHECK range or NULL |
| `mass_earth` | DOUBLE | CHECK range or NULL |
| `planet_density` | DOUBLE | CHECK range or NULL |
| `eccentricity` | DOUBLE | CHECK 0–0.95 or NULL |
| `insolation_flux` | DOUBLE | CHECK range or NULL |
| `planet_temp` | DOUBLE | CHECK 34–4050 or NULL |
| `ttv_obs` | BOOLEAN | NOT NULL |

### 3.2 Relationships (ER Summary)

```
Constellation  1 ──── 0..* StarSystem    (optional association; SET NULL on delete)
StarSystem     1 ──── 1..* Star          (composition; CASCADE on delete)
StarSystem     1 ──── 1..* Planet        (composition; CASCADE on delete)
Discovery      1 ──── 0..* Planet        (optional association; SET NULL on delete)
```

**Key observations:**
- Star → StarSystem is mandatory (NOT NULL FK); Planet → StarSystem is also mandatory.
- Planet → Discovery is optional (nullable FK).
- StarSystem → Constellation is optional (nullable FK).
- Discovery is a standalone entity — not tied to a system, only to individual planets.
- There is **no direct Star–Planet relationship**; both relate to StarSystem independently.

### 3.3 Data Volumes

| Table | Estimated Records | Source |
|-------|------------------|--------|
| Constellation | ~88 unique (95 CSV rows, includes duplicates like Cassiopeia split across RA ranges) | `Constellations.csv` |
| StarSystem | ~4,000+ | Derived from unique `star_name` in exoplanet CSV |
| Star | ~4,000+ (1 per system typically) | Same derivation |
| Discovery | ~2,500+ (unique method/facility/instrument combos) | Deduplicated from CSV |
| Planet | ~6,153 | `ExoplanetDataset.csv` |

---

## 4. Backend API Inventory

### 4.1 Core Read Endpoints (`main.py`)

| Method | Route | Purpose |
|--------|-------|---------|
| GET | `/api/systems` | Paginated star system list; optional `constellation` filter |
| GET | `/api/systems/{system_id}` | System detail with nested stars and planets |
| GET | `/api/constellations` | All constellations with system count |
| GET | `/api/search?q=` | System name search (LIKE, limit 30) |
| GET | `/api/planets` | Paginated planet list with ESI, sorting (6 fields), filtering (constellation, method, name) |
| GET | `/api/planets/{planet_id}/details` | Full planet detail joined with star, system, constellation, discovery + ESI |
| GET | `/api/discovery_methods` | Distinct discovery methods for filter dropdowns |

### 4.2 Analytics Endpoints (`analytics.py`)

| Method | Route | Purpose |
|--------|-------|---------|
| GET | `/api/analytics/summary` | Aggregate stats (total planets, multi-planet systems, etc.) |
| GET | `/api/analytics/esi-distribution` | ESI tier counts (Earth-like / Potential / Extreme / Inhospitable / Unknown) |
| GET | `/api/analytics/discovery-timeline` | Discoveries per year grouped by method |
| GET | `/api/analytics/mass-radius-scatter` | Mass vs radius scatter data |
| GET | `/api/analytics/spectral-types` | Star spectral class distribution (O/B/A/F/G/K/M) |
| GET | `/api/analytics/system-complexity` | Systems grouped by planet count |
| GET | `/api/analytics/eccentricity-period` | Eccentricity vs orbital period scatter |
| GET | `/api/analytics/metallicity-planets` | Star metallicity vs planet count |
| GET | `/api/analytics/distance-histogram` | Log-spaced distance distribution |

### 4.3 CRUD / Admin Endpoints (`crud.py`)

| Method | Route | Purpose |
|--------|-------|---------|
| POST | `/api/admin/reset` | Truncate all tables + re-run ingestion scripts |
| POST | `/api/crud/planets` | Create planet (with new or existing system) |
| PUT | `/api/crud/planets/{planet_id}` | Update planet attributes |
| PUT | `/api/crud/stars/{star_id}` | Update star attributes |
| PUT | `/api/crud/systems/{system_id}` | Update system attributes |
| DELETE | `/api/crud/planets/{planet_id}` | Delete planet (cascades system deletion if no planets remain) |

---

## 5. Frontend Pages and Routes

| Route | Component | Description |
|-------|-----------|-------------|
| `/` | `Home.tsx` | Landing page — narrative about exoplanets, CTA to observatory |
| `/observatory` | `Observatory.tsx` | Planet card grid with ESI gauges, search, sort (6 fields), filter by constellation/method, pagination |
| `/analytics` | `Analytics.tsx` | 9-chart dashboard (ECharts): stat cards, ESI sunburst, timeline, mass-radius scatter, distance histogram, spectral types, system complexity, eccentricity-period, metallicity-planets |
| `/add-planet` | `AddPlanet.tsx` | Create planet form with two modes (new system / existing system), habitability presets |
| `/galaxy` | `Gallery.tsx` | Star system card grid with search and constellation filter |
| `/system/:id` | `SystemView.tsx` | Full-screen system view with orbit visualizer, planet selector, planet info panel |
| `/planet/:id` | `PlanetDetail.tsx` | Detailed planet view with ESI breakdown (interior/surface/final), habitable zone tracker, inline edit/delete for planet/star/system |

### 5.1 Key UI Components

| Component | Purpose |
|-----------|---------|
| `Navbar` | Fixed top nav with Home/Observatory/Analytics/Add Planet tabs + Master Reset button |
| `ESIGauge` | SVG circular arc gauge — red (<0.3), amber (0.3–0.7), emerald (>0.7) |
| `ZoneTracker` | Horizontal bar showing habitable zone bounds and planet orbit position |
| `OrbitVisualizer` | Canvas animation of planetary orbit around star(s) |
| `PlanetInfo` | Left-panel overlay showing key planet facts |
| `SpaceCanvas` | Animated starfield background |
| `ui/` | ~40 shadcn/Radix UI primitive components (accordion, dialog, tabs, etc.) — **largely unused** |

---

## 6. Domain Logic and Business Rules

### 6.1 Earth Similarity Index (ESI) — `utils.py`

The ESI calculator is the **most significant piece of domain logic**. It computes a 0–1 similarity score comparing an exoplanet to Earth across four parameters:

**Inputs** (with fallback computation chains):
1. **Star Luminosity (L):** From DB log₁₀ value → 10^raw_lum; fallback: R²star × (Tstar/5778)⁴
2. **Orbit Distance (d):** From `orbit_radius`; fallback via Kepler's 3rd Law from orbital period and star mass
3. **Planet Density (D):** From DB; fallback: (mass/radius³) × 5.51
4. **Surface Temperature (T):** From `planet_temp`; fallback: 278 × (L/d²)^0.25
5. **Escape Velocity (V):** Computed: √(mass/radius) × 11.19

**ESI Formula:**
- **ESI_interior** = √(r_term × d_term) where:
  - r_term = (1 - |R-1|/(R+1))^0.57
  - d_term = (1 - |D-5.51|/(D+5.51))^1.07
- **ESI_surface** = √(v_term × t_term) where:
  - v_term = (1 - |V-11.19|/(V+11.19))^0.70
  - t_term = (1 - |T-288|/(T+288))^5.58
- **Final ESI** = √(ESI_interior × ESI_surface)

**Habitable Zone (Goldilocks):**
- HZ_inner = √(L/1.1)
- HZ_outer = √(L/0.53)
- Planet is habitable if HZ_inner ≤ orbit_distance ≤ HZ_outer

**ESI Tier Classification:**
| Tier | ESI Range |
|------|-----------|
| Earth-like | ≥ 0.8 |
| Potential | 0.6 – 0.8 |
| Extreme | 0.4 – 0.6 |
| Inhospitable | < 0.4 |
| Unknown | NULL/NaN |

> **Note:** The plan mentions a "Goldilocks penalty" (90% reduction for planets outside HZ), but the current implementation does **not** apply this penalty — `final_esi = base_esi` unconditionally.

### 6.2 Planet Type Classification (`SystemView.tsx`)

Frontend-only classification by Earth radius:
| Radius (R⊕) | Classification |
|-------------|---------------|
| < 1.25 | Rocky (Terrestrial) |
| 1.25 – 2.0 | Super-Earth |
| 2.0 – 6.0 | Mini-Neptune |
| 6.0 – 15.0 | Gas Giant |
| ≥ 15.0 | Super-Jupiter |

### 6.3 ESI Duplication

The ESI calculation is **duplicated** between backend (`utils.py → calculate_esi()`) and frontend (`PlanetDetail.tsx → calculateESIFrontEnd()`). Both implement the same algorithm. This is a **code smell** — domain logic should live in one authoritative place.

### 6.4 Spectral Class Extraction (`analytics.py`)

Extracts the first letter of `spectral_type` and maps to OBAFGKM classification; anything else → "Other", missing → "Unknown".

---

## 7. Data Ingestion Pipeline

### 7.1 Constellation Ingestion (`ingestConstellation.py`)
- Reads `data/Constellations.csv` (95 rows, 7 columns)
- Direct INSERT via `cursor.executemany()`
- No deduplication or cleanup — relies on clean CSV
- Note: Cassiopeia spans two RA ranges and appears as **two rows** (pop_rank=3 for both)

### 7.2 Planet Ingestion (`ingest_planets.py`)
- Reads `data/ExoplanetDataset.csv` (6,153 rows, 33 columns)
- **Truncates** all four data tables before ingesting
- Three-phase ingestion:
  1. **Discovery cache:** Deduplicate unique (year, method, locale, facility, telescope, instrument) tuples → Discovery table
  2. **Constellation spatial mapping:** Match (RA, Dec) to constellation bounding boxes
  3. **Row processing:** For each CSV row:
     - Create or reuse StarSystem (keyed by `star_name`)
     - Create Star (one per system, keyed by `star_name`)
     - Create Planet with FK references
- Distance conversion: parsecs → light-years (× 3.26156)
- Range validation with CHECK-compatible bounds
- Boolean parsing with multiple format handling
- Single commit at end of batch

---

## 8. Architectural Issues for OOAD Redesign

### 8.1 No Layered Architecture
The current backend is a **flat module structure**. All files sit in `backend/` with no separation between:
- API/routing concerns
- Business/domain logic
- Data access/persistence
- DTOs/serialization

Every endpoint function directly creates a DB connection, writes raw SQL, processes results, and returns them. There are **no domain classes, no service layer, no repository abstractions**.

### 8.2 Duplicated Database Connection Logic
`get_db()` is **defined three times** independently — in `main.py`, `crud.py`, and `analytics.py` — with identical logic. No connection pooling or dependency injection.

### 8.3 Raw SQL Everywhere
All data access is via string-formatted SQL queries embedded directly in route handler functions. There are no ORMs, no query builders, and no data mapper classes.

### 8.4 Business Logic in Route Handlers
ESI computation, pagination arithmetic, sorting logic, and planet count maintenance are all embedded directly within FastAPI endpoint functions rather than in dedicated service or domain classes.

### 8.5 No Domain Model
There are **no Python classes representing domain entities**. Data flows as raw dictionaries from MySQL cursor through to JSON response. The only Pydantic models are `PlanetPayload`, `PlanetUpdate`, `StarUpdate`, `SystemUpdate` — used purely as request DTOs, not as domain objects.

### 8.6 Frontend Business Logic Leakage
- ESI is recalculated in the frontend (`PlanetDetail.tsx`)
- Planet type classification happens only in the frontend (`SystemView.tsx`)
- Habitable zone logic is computed on both sides

### 8.7 Global Mutable State
`analytics.py` uses a global `_df_cache` variable for the Pandas DataFrame. No invalidation mechanism — stale after CRUD operations until server restart.

### 8.8 No Error Handling Strategy
Bare `try/except Exception` blocks with generic HTTP 500 responses. No domain-specific exceptions or validation error classes.

### 8.9 No Tests
Zero test files exist in the repository. No unit tests, integration tests, or API tests.

### 8.10 Bloated Frontend Dependencies
The `package.json` includes ~60 dependencies. Many shadcn/Radix UI primitives in `src/app/components/ui/` (~40 files) appear **unused** by the actual pages.

---

## 9. What to Retain vs. Redesign

### 9.1 RETAIN (conceptually reuse)

| Asset | Reason |
|-------|--------|
| **Database schema design** | The 5-table relational model (Constellation → StarSystem → Star/Planet, Discovery → Planet) is sound and captures the domain well. Column names, types, and constraints are well-designed. |
| **ESI calculation algorithm** | Core domain logic with astrophysical basis. Should be encapsulated in a proper domain class. |
| **Habitable zone formula** | Useful domain rule; should move to a domain value object. |
| **Planet type classification** | Useful domain logic; should move from frontend to backend domain layer. |
| **Spectral class extraction** | Simple but useful; belongs in Star domain entity. |
| **Data files** | `ExoplanetDataset.csv` and `Constellations.csv` are valuable seed data. |
| **API route structure** | The URL patterns (`/api/systems`, `/api/planets`, `/api/search`) are reasonable and RESTful. |
| **ESI tier classification** | The tier boundaries and naming are sensible domain policy. |
| **Core user journeys** | Browse systems → view system → view planet → search/filter → analytics. These map well to OOAD use cases. |

### 9.2 REDESIGN (must change for OOAD)

| Current State | OOAD Target |
|---------------|-------------|
| Flat `backend/` with 4 files | Layered: `api/`, `application/`, `domain/`, `infrastructure/` |
| No domain classes | Proper entity classes: `Planet`, `Star`, `StarSystem`, `Constellation`, `Discovery` with attributes, methods, visibility |
| Raw SQL in handlers | Repository pattern: `PlanetRepository`, `StarSystemRepository`, etc. with interface/implementation split |
| ESI in utility function | Domain service or value object: `ESICalculator` with strategy potential |
| Duplicated `get_db()` | Single infrastructure concern with dependency injection |
| No service layer | Application services: `StarSystemService`, `PlanetService`, `SearchService`, `AnalyticsService` |
| Dict-based data flow | DTOs for API layer, domain entities for business logic |
| No validation classes | Domain validation in entity constructors/methods |
| Frontend ESI duplication | Single backend source of truth; remove frontend recalculation |
| No tests | Unit tests for domain logic, service tests, API tests |
| Global DataFrame cache | Proper caching strategy in analytics service |

---

## 10. Proposed MVP Use Cases

Based on the plan and current functionality, the MVP should cover:

| # | Use Case | Actor | Priority |
|---|----------|-------|----------|
| UC-1 | Browse/search star systems | Explorer | Core |
| UC-2 | View star system details (star + planets) | Explorer | Core |
| UC-3 | Browse/search/filter planets | Explorer | Core |
| UC-4 | View planet details with ESI breakdown | Explorer | Core |
| UC-5 | Compare planets (side-by-side) | Explorer | Core |
| UC-6 | View analytics dashboard | Explorer | Core |
| UC-7 | Add a new planet (with system) | Admin | Optional |
| UC-8 | Edit planet/star/system data | Admin | Optional |
| UC-9 | Delete a planet | Admin | Optional |

### Actors
- **Explorer:** Browses, searches, filters, and analyzes exoplanet data. Primary actor.
- **Admin:** Manages data — creates, updates, and deletes records. Secondary actor.

---

## 11. Candidate Domain Entities and Relationships

Based on the schema and domain analysis:

```
┌──────────────┐       0..1 ┌──────────────────┐ 1      ┌──────────┐
│ Constellation│◄───────────│   StarSystem      │───────▶│   Star   │
│              │            │                   │  1..*  │          │
│ - name       │            │ - name (unique)   │        │ - name   │
│ - ra bounds  │            │ - ra, dec         │        │ - temp   │
│ - dec bounds │            │ - numStars        │        │ - radius │
│ - description│            │ - numPlanets      │        │ - mass   │
│ - popRank    │            │ - numMoons        │        │ - ...    │
└──────────────┘            │ - distance_ly     │        └──────────┘
                            └──────────┬────────┘
                                 1     │
                                       │ 1..*
                              ┌────────▼────────┐
                              │     Planet       │
                              │                  │   0..1  ┌───────────┐
                              │ - name (unique)  │────────▶│ Discovery │
                              │ - radius, mass   │         │           │
                              │ - temp, density  │         │ - year    │
                              │ - orbitalPeriod  │         │ - method  │
                              │ - eccentricity   │         │ - facility│
                              │ - ...            │         │ - ...     │
                              │ + computeESI()   │         └───────────┘
                              │ + classifyType() │
                              │ + isHabitable()  │
                              └─────────────────┘
```

### Value Object Candidates
- **CelestialCoordinates** (ra, dec) — shared by StarSystem/Constellation bounds
- **ESIResult** (interior, surface, final, tier, isHabitable, hzInner, hzOuter) — returned by ESI computation
- **HabitableZone** (inner AU, outer AU) — computed from star luminosity

---

## 12. Proposed Layered Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Presentation / API Layer                │
│  FastAPI routers, request/response DTOs, error mapping  │
├─────────────────────────────────────────────────────────┤
│                  Application Layer                       │
│  StarSystemService, PlanetService, SearchService,       │
│  AnalyticsService, ComparisonService                    │
├─────────────────────────────────────────────────────────┤
│                  Domain Layer                            │
│  Planet, Star, StarSystem, Constellation, Discovery     │
│  ESICalculator, PlanetClassifier, HabitableZone         │
│  Repository interfaces (abstract)                       │
├─────────────────────────────────────────────────────────┤
│                  Infrastructure Layer                    │
│  MySQL repository implementations, DB connection pool,  │
│  data mappers, CSV ingestion utilities                  │
└─────────────────────────────────────────────────────────┘
```

---

## 13. Risks and Uncertainties

| # | Risk / Question | Impact | Recommendation |
|---|-----------------|--------|----------------|
| R1 | The Goldilocks penalty described in the plan is **not implemented** in the current code. Should it be? | Affects ESI scores for many planets | Clarify with team whether to implement the 90% penalty or keep current behavior |
| R2 | Constellation CSV has duplicate entries (Cassiopeia appears twice for different RA ranges). Schema doesn't handle this. | Minor data issue | Handle in ingestion; consider composite key or merging |
| R3 | The `num_planets` counter on StarSystem is maintained manually (incremented on create, decremented on delete). | Denormalized; can drift | Consider computing from COUNT or adding domain invariant enforcement |
| R4 | Analytics cache (`_df_cache`) is never invalidated after CRUD. | Stale dashboard data | Implement cache invalidation or TTL in the new architecture |
| R5 | `star_luminosity` is stored as log₁₀(L/L☉) but the field name doesn't indicate this. | Potential confusion | Document clearly in domain entity; consider a value object |
| R6 | No authentication or authorization exists. | Security | Out of scope per plan; document as explicit non-goal |
| R7 | 40+ unused UI component files bloat the frontend. | Maintenance burden | Strip to actually-used components in OOAD implementation |
| R8 | Planet comparison feature (UC-5) has **no existing implementation**. | New development needed | Design from scratch as part of MVP |
| R9 | The frontend hardcodes `http://localhost:8000` as the API URL in every page file. | Not configurable | Centralize in a config/environment variable |

---

## 14. Summary

The existing COSMODB prototype is a **feature-rich but architecturally flat** application. It successfully demonstrates the exoplanet exploration domain with a comprehensive dataset, working API, and polished UI. However, it has:

- ❌ No domain classes or object-oriented structure
- ❌ No separation of concerns (everything in route handlers)
- ❌ No tests
- ❌ Duplicated logic across backend and frontend
- ❌ No abstractions or interfaces

The OOAD redesign should:
- ✅ Preserve the domain model (5 entities, their relationships, ESI logic)
- ✅ Preserve the API contract and user journeys
- ✅ Preserve the seed data
- ✅ Introduce clear layered architecture with domain entities, services, and repositories
- ✅ Add the missing planet comparison feature
- ✅ Consolidate all business logic in the backend domain layer
- ✅ Add meaningful tests for domain rules

**Next step:** Await team approval of this audit, then proceed to Phase 1 — Requirements and Use Case documentation.

---

*End of baseline audit.*

