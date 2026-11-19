import asyncio
import unittest

import httpx
from mysql.connector.errors import IntegrityError

from cosmosdb.api.app import create_app
from tests.support import (
    FakeConstellationRepository,
    FakePlanetRepository,
    FakeSystemRepository,
)


class CatalogApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.planets = FakePlanetRepository()
        self.app = create_app(
            planet_repository=self.planets,
            system_repository=FakeSystemRepository(),
            constellation_repository=FakeConstellationRepository(),
        )

    def request(self, method: str, path: str, **kwargs: object) -> httpx.Response:
        async def send() -> httpx.Response:
            transport = httpx.ASGITransport(app=self.app)
            async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
                return await client.request(method, path, **kwargs)

        return asyncio.run(send())

    def test_browse_and_compare_return_domain_results(self) -> None:
        response = self.request("GET", "/api/planets", params={"q": "Earth"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total"], 1)
        self.assertEqual(response.json()["planets"][0]["planet_name"], "Earth-like")

        comparison = self.request(
            "GET", "/api/planets/compare", params=[("planet_ids", 1), ("planet_ids", 2)]
        )
        self.assertEqual(comparison.status_code, 200)
        self.assertEqual(len(comparison.json()), 2)

    def test_invalid_page_and_missing_entities_have_api_errors(self) -> None:
        self.assertEqual(self.request("GET", "/api/planets", params={"limit": 0}).status_code, 422)
        self.assertEqual(self.request("GET", "/api/planets/999").status_code, 404)
        self.assertEqual(self.request("GET", "/api/systems/999").status_code, 404)

    def test_planet_mutations_invalidate_analytics(self) -> None:
        self.request("GET", "/api/analytics/summary")
        self.assertEqual(self.planets.analytics_reads, 1)

        created = self.request(
            "POST", "/api/planets", json={"planet_name": "New world", "system_id": 101}
        )
        self.assertEqual(created.status_code, 201)
        planet_id = created.json()["planet_id"]
        self.request("GET", "/api/analytics/summary")
        self.assertEqual(self.planets.analytics_reads, 2)

        updated = self.request("PATCH", f"/api/planets/{planet_id}", json={"planet_name": "Updated world"})
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.json()["planet_name"], "Updated world")
        self.assertEqual(self.request("DELETE", f"/api/planets/{planet_id}").status_code, 204)

    def test_create_requires_an_existing_host_system(self) -> None:
        response = self.request(
            "POST", "/api/planets", json={"planet_name": "Orphan", "system_id": 999}
        )
        self.assertEqual(response.status_code, 404)

    def test_catalog_constraint_conflict_is_not_reported_as_database_outage(self) -> None:
        class ConflictingRepository(FakePlanetRepository):
            def create(self, entry: object) -> object:
                raise IntegrityError("duplicate planet name")

        app = create_app(
            planet_repository=ConflictingRepository(),
            system_repository=FakeSystemRepository(),
            constellation_repository=FakeConstellationRepository(),
        )

        async def send() -> httpx.Response:
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
                return await client.post(
                    "/api/planets", json={"planet_name": "Duplicate", "system_id": 101}
                )

        response = asyncio.run(send())
        self.assertEqual(response.status_code, 409)

    def test_crud_aliases_and_cors_preflight(self) -> None:
        # 1. Test CORS preflight for PUT
        cors_res = self.request(
            "OPTIONS",
            "/api/crud/planets/1",
            headers={
                "Origin": "http://127.0.0.1:5173",
                "Access-Control-Request-Method": "PUT",
                "Access-Control-Request-Headers": "content-type",
            },
        )
        self.assertEqual(cors_res.status_code, 200)
        self.assertIn("access-control-allow-origin", cors_res.headers)

        # 2. Test POST /api/crud/planets with empty name returns 422
        bad_create = self.request("POST", "/api/crud/planets", json={"planet_name": ""})
        self.assertEqual(bad_create.status_code, 422)

        # 3. Test POST /api/crud/planets with valid data
        good_create = self.request(
            "POST",
            "/api/crud/planets",
            json={
                "mode": "new",
                "planet_name": "Kepler-999 b",
                "system_name": "Kepler-999",
                "radius_earth": 1.2,
                "mass_earth": 1.5,
            },
        )
        self.assertEqual(good_create.status_code, 201)
        created_id = good_create.json()["planet_id"]

        # 4. Test PUT /api/crud/planets/{id} update (System Edit mode save)
        update_res = self.request(
            "PUT",
            f"/api/crud/planets/{created_id}",
            json={
                "planet_name": "teegarden x",
                "radius_earth": 1.25,
                "mass_earth": 1.55,
                "num_stars": 4,  # Extra fields in form must be ignored cleanly
            },
        )
        self.assertEqual(update_res.status_code, 200)
        self.assertEqual(update_res.json()["planet_name"], "teegarden x")

        # 5. Test PUT /api/crud/stars and /api/crud/systems
        self.assertEqual(
            self.request("PUT", "/api/crud/stars/1", json={"star_name": "New Star"}).status_code,
            200,
        )
        self.assertEqual(
            self.request("PUT", "/api/crud/systems/101", json={"system_name": "New System"}).status_code,
            200,
        )


if __name__ == "__main__":
    unittest.main()
