import unittest
from typing import Any

from cosmosdb.infrastructure.mysql import MySQLPlanetRepository


class FakeCursor:
    def __init__(self) -> None:
        self.sql = ""
        self.parameters: list[Any] = []
        self.result: list[dict[str, Any]] = []

    def execute(self, sql: str, parameters: list[Any]) -> None:
        self.sql = sql
        self.parameters = parameters
        if "COUNT(*) AS total" in sql:
            self.result = [{"total": 1}]
        else:
            self.result = [{
                "planet_id": 7,
                "planet_name": "Earth-like",
                "system_id": 11,
                "system_name": "Host",
                "discovery_id": 9,
                "radius_earth": 1.0,
                "mass_earth": 1.0,
                "planet_density": None,
                "planet_temp": 288.0,
                "orbit_radius": 1.0,
                "orbital_period": 365.25,
                "eccentricity": 0.0,
                "insolation_flux": 1.0,
                "discovery_year": 2014,
                "discovery_method": "Transit",
                "constellation_name": "Orion",
                "star_temp": 5778.0,
                "star_radius": 1.0,
                "star_mass": 1.0,
                "star_luminosity": 0.0,
            }]

    def fetchall(self) -> list[dict[str, Any]]:
        return self.result

    def close(self) -> None:
        pass


class FakeConnection:
    def __init__(self, cursor: FakeCursor) -> None:
        self._cursor = cursor
        self.closed = False

    def cursor(self, dictionary: bool = False) -> FakeCursor:
        return self._cursor

    def close(self) -> None:
        self.closed = True


class MySQLPlanetRepositoryTests(unittest.TestCase):
    def test_list_parameterizes_search_and_maps_a_catalog_entity(self) -> None:
        cursors: list[FakeCursor] = []
        connections: list[FakeConnection] = []

        def connect() -> FakeConnection:
            cursor = FakeCursor()
            connection = FakeConnection(cursor)
            cursors.append(cursor)
            connections.append(connection)
            return connection

        repository = MySQLPlanetRepository(connect)
        planets, total = repository.list(
            query="' OR 1=1 --", constellation=None, method=None,
            sort_by="mass", order="desc", page=2, limit=10,
        )

        self.assertEqual(total, 1)
        self.assertEqual(planets[0].name, "Earth-like")
        self.assertEqual(planets[0].discovery_id, 9)
        self.assertEqual(cursors[1].parameters[:2], ["%' OR 1=1 --%", "%' OR 1=1 --%"])
        self.assertNotIn("' OR 1=1 --", cursors[1].sql)
        self.assertIn("ORDER BY p.mass_earth IS NULL, p.mass_earth DESC", cursors[1].sql)
        self.assertEqual(len(connections), 2)
        self.assertTrue(all(connection.closed for connection in connections))


if __name__ == "__main__":
    unittest.main()
