# COSMODB-OOAD demonstration

1. Start MySQL and load the documented schema and sample data.
2. Open **Star systems**, search for `Kepler-186`, and open the result. Point out the system's constellation, dynamically counted planets, host star, and planet list.
3. Open **Planets**; filter by a discovery method and sort by ESI. Open a planet profile and explain that the score is only available when measurements support the calculation.
4. Select two to four planets and use **Compare worlds**. Discuss the uniform comparison fields and independent planet aggregate IDs.
5. Open **Analytics** and explain the catalog counts, supported ESI average, and top discovery method.
6. In the API docs, show invalid input/not-found responses and the optional create/update/delete endpoints.
7. Explain the domain/application/infrastructure/API boundary, ESI Strategy, PlanetBuilder, and catalog-change Observer.
8. Open `docs/OOAD/diagrams` and compare the editable UML sources with the implemented classes and flow.
