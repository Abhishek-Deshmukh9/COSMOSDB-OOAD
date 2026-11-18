# Requirements and use cases

## Actors

- **Explorer:** browses systems and planets, opens details, filters the catalog, and compares selected planets.
- **Catalog curator:** creates, edits, or removes a planet catalog record through the API.

## MVP use cases

1. Search for a star system and inspect its known stars and planets.
2. Search and filter planets by name, host system, and discovery method.
3. Open a planet profile with available physical, orbital, and discovery attributes.
4. Compare two to four distinct planets using consistent fields.
5. View a catalog summary and standard ESI when sufficient data exists.
6. Create, update, and delete a cataloged planet record.

## Functional requirements

- System and planet lists are paginated and input limits are validated.
- Planet list sorting is restricted to supported fields; missing ESI values remain at the end for either sort direction.
- A system response includes its stars and independently queried planets.
- ESI scoring and habitable-zone classification are separate; standard ESI is the default.
- Comparison rejects fewer than two, more than four, duplicate, or missing planet IDs.
- A planet mutation emits a catalog-change event so observers can invalidate analytics and record the action.
- API not-found, invalid-input, integrity-conflict, and database failures are returned explicitly.

## Quality requirements

- Domain and application services do not depend on FastAPI or MySQL.
- Repository ports isolate SQL from use cases.
- Unit tests cover celestial wraparound, ESI strategies, lifecycle transitions, service behavior, observer invalidation, and API status cases.
- The source of each UML diagram is editable PlantUML and diagram content matches implemented classes and flows.
