# COSMODB-OOAD

An OOAD-focused implementation of the COSMODB exoplanet catalog. This project lives beside the original prototype and does not modify it.

## MVP

- Search and browse star systems; open a system with its stars and planets.
- Search and filter planets by discovery method; inspect planet properties.
- Compare two to four planets.
- Review a small analytics summary and the standard Earth Similarity Index (ESI).
- Add, update, and remove planet records through the API.

The standard ESI remains independent from the habitable-zone assessment. The API also supports an explicitly selected `habitability` scoring strategy.

## Stack and boundaries

- `backend/cosmosdb/domain`: entities, value objects, catalog lifecycle and ESI policies.
- `backend/cosmosdb/application`: use-case services, repository ports, and catalog-change observers.
- `backend/cosmosdb/infrastructure`: MySQL repositories and database connection configuration.
- `backend/cosmosdb/api`: FastAPI endpoints and request validation.
- `frontend`: independent React + TypeScript + Vite catalog UI.
- `database`: MySQL schema. The seed script reads the existing CSVs from the adjacent `data` folder, or `COSMOSDB_DATA_DIR`.
- `docs/OOAD/diagrams`: editable PlantUML and rendered SVGs.

The application computes planet counts from `Planet` rows; it does not rely on the legacy `StarSystem.num_planets` value.

## Windows setup

### 1. Database and seed data

From this directory, execute `database\schema.sql` with the MySQL command-line client:

```powershell
cmd /c "mysql -u root -p < database\schema.sql"
```

Copy `.env.example` to `backend\.env` and set your local MySQL credentials. The adjacent `data\ExoplanetDataset.csv` and `data\Constellations.csv` are used by default. To place them elsewhere, set `COSMOSDB_DATA_DIR` in `backend\.env`.

### 2. Backend

```powershell
Set-Location backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts\seed_database.py
python -m unittest discover -s tests -v
uvicorn main:app --reload
```

The API is available at `http://127.0.0.1:8000`; interactive API documentation is at `/docs`. The seed script refuses to run when the Planet table already contains records.

### 3. Frontend

In another terminal:

```powershell
Set-Location frontend
npm install
npm run dev
```

Open the Vite URL (by default `http://127.0.0.1:5173`). Override the API URL with `VITE_API_BASE_URL` if the backend is hosted elsewhere.

## API overview

| Endpoint | Purpose |
|---|---|
| `GET /api/systems` | Search and page through star systems |
| `GET /api/systems/{system_id}` | Retrieve a system with its stars and planets |
| `GET /api/planets` | Search, filter, sort, and page through planets |
| `GET /api/planets/{planet_id}` | Retrieve a planet and ESI details |
| `GET /api/planets/compare?planet_ids=1&planet_ids=2` | Compare two to four planets |
| `POST/PATCH/DELETE /api/planets` | Manage catalog records |
| `GET /api/analytics/summary` | Return catalog counts and mean available ESI |

Database failures are reported as `503`; invalid input, missing records, and catalog constraint conflicts return `422`, `404`, and `409`.

## Tests and UML

Run backend domain, service, and API tests with `python -m unittest discover -s tests -v` from `backend`.

The `.puml` files in `docs/OOAD/diagrams` are the editable sources. Render them with:

```powershell
python scripts\render_diagrams.py
```

The renderer uses a local PlantUML installation or `PLANTUML_JAR`; see the script's diagnostic if Java or the renderer is unavailable. Update diagrams whenever implementation changes affect their content.
