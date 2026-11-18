from __future__ import annotations

import unittest
from typing import Any

from fastapi.testclient import TestClient

from cosmosdb.api.app import create_app
from tests.support import FakeConstellationRepository, FakePlanetRepository, FakeSystemRepository, planet


class AnalyticsServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.planets = FakePlanetRepository([
            planet(1, "Earth-like", orbit=1.0, mass=1.0, discovery_year=2015, discovery_method="Transit", discovery_facility="Kepler", spectral_type="G2V", distance_ly=50.0, metallicity=0.02, period=365.0, eccentricity=0.01),
            planet(2, "Cold World", orbit=5.0, mass=10.0, discovery_year=2018, discovery_method="Radial Velocity", discovery_facility="HARPS", spectral_type="M3V", distance_ly=150.0, metallicity=-0.1, period=1200.0, eccentricity=0.25),
        ])
        self.systems = FakeSystemRepository()
        self.constellations = FakeConstellationRepository()
        self.app = create_app(self.planets, self.systems, self.constellations)
        self.client = TestClient(self.app)

    def test_summary_schema_and_values(self) -> None:
        response = self.client.get("/api/analytics/summary")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("total_planets", data)
        self.assertIn("multi_planet_systems", data)
        self.assertIn("constellations_cataloged", data)
        self.assertIn("unique_stars", data)
        self.assertIn("discovery_methods", data)
        self.assertIn("top_discovery_facility", data)
        self.assertEqual(data["total_planets"], 2)
        self.assertIn(data["top_discovery_facility"]["name"], {"Kepler", "HARPS"})

    def test_esi_distribution(self) -> None:
        response = self.client.get("/api/analytics/esi-distribution")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        tiers = {item["tier"]: item["count"] for item in data}
        for expected in ("Earth-like", "Potential", "Extreme", "Inhospitable", "Unknown"):
            self.assertIn(expected, tiers)
        self.assertEqual(sum(tiers.values()), 2)

    def test_discovery_timeline(self) -> None:
        response = self.client.get("/api/analytics/discovery-timeline")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("years", data)
        self.assertIn("methods", data)
        self.assertIn("series", data)
        self.assertEqual(data["years"], [2015, 2018])
        self.assertIn("Transit", data["methods"])
        self.assertIn("Radial Velocity", data["methods"])

    def test_mass_radius_scatter(self) -> None:
        response = self.client.get("/api/analytics/mass-radius-scatter")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)
        self.assertIn("mass", data[0])
        self.assertIn("radius", data[0])
        self.assertIn("name", data[0])

    def test_spectral_types(self) -> None:
        response = self.client.get("/api/analytics/spectral-types")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        types = {item["type"] for item in data}
        self.assertTrue("G" in types or "M" in types)

    def test_system_complexity(self) -> None:
        response = self.client.get("/api/analytics/system-complexity")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertTrue(any(item["planet_count"] == 1 for item in data))

    def test_eccentricity_period(self) -> None:
        response = self.client.get("/api/analytics/eccentricity-period")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)
        self.assertIn("period", data[0])
        self.assertIn("eccentricity", data[0])

    def test_metallicity_planets(self) -> None:
        response = self.client.get("/api/analytics/metallicity-planets")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)
        self.assertIn("metallicity", data[0])
        self.assertIn("num_planets", data[0])
        self.assertIn("system", data[0])

    def test_distance_histogram(self) -> None:
        response = self.client.get("/api/analytics/distance-histogram")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("bins", data)
        self.assertIn("counts", data)
        self.assertIn("bin_edges", data)
        self.assertEqual(sum(data["counts"]), 2)

    def test_mutation_invalidates_all_analytics(self) -> None:
        self.client.get("/api/analytics/summary")
        self.assertEqual(self.planets.analytics_reads, 1)

        # Mutate via create
        create_res = self.client.post("/api/planets", json={
            "planet_name": "New Planet",
            "system_id": 101,
            "radius_earth": 1.2,
        })
        self.assertEqual(create_res.status_code, 201)

        # Next call to analytics re-reads
        self.client.get("/api/analytics/summary")
        self.assertEqual(self.planets.analytics_reads, 2)


if __name__ == "__main__":
    unittest.main()
