# Design decisions

1. Keep the existing prototype untouched; the OOAD implementation is a separate project folder.
2. Keep `Planet` independent from `StarSystem`, reference the host by identity, and derive planet counts from the Planet repository.
3. Use standard ESI by default. Apply the 90% outside-zone penalty only through the explicit habitability-weighted strategy.
4. Model RA wraparound in `CelestialBoundingBox`; CSV split segments remain independently owned boxes of a constellation.
5. Use Builder for validated Planet creation and Observer for analytics-cache invalidation and audit logging on mutations.
6. Do not model unsupported astronomical verification states. The curation record has only Draft, Cataloged, and Removed.
7. Keep MySQL and FastAPI because they are established in the reference project; keep data access behind repository ports.
8. Use a simple React comparison workflow capped at four planets; defer authentication and complex administration.
