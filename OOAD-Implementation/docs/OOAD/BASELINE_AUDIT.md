# COSMODB-OOAD baseline audit

## Reference implementation

The adjacent project is a React + TypeScript + Vite UI backed by FastAPI and MySQL. Its SQL schema models `Constellation`, `StarSystem`, `Discovery`, `Star`, and `Planet`; its CSV dataset contains 6,153 exoplanet rows and the constellation data contains segmented right-ascension intervals. Existing routes support system browsing, planet browsing, ESI, analytics, and planet CRUD. Most backend behavior is concentrated in procedural modules and direct SQL calls; analytics cache invalidation is not coordinated with CRUD changes.

## Scope decisions

- Keep the reference prototype intact and build this implementation in its own folder.
- Reuse the reference domain vocabulary, MySQL schema concepts, and adjacent CSV data.
- MVP includes system browsing/details, planet browse/search/filter/details, comparison, and explainable ESI analytics.
- Admin CRUD is included as API support; no authentication is added because it is a local academic demonstration.
- Planet counts are queried from the Planet repository instead of trusting the legacy denormalized count.
- Database integration tests require a configured MySQL database; the domain, application, and API tests use fake repositories.

## Risks and assumptions

- The seed script needs MySQL 8+, database creation privileges, and a clean Planet table.
- Right ascension may cross 0/360 degrees; the domain bounding box normalizes coordinates and supports wraparound.
- ESI is only returned when source or supported fallback measurements are sufficient. It is not a probability of life.
- The source CSVs remain adjacent to this subproject by default. Set `COSMOSDB_DATA_DIR` to use another copy.
