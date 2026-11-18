import unittest

from cosmosdb.domain.entities import CatalogRecordState, PlanetBuilder, PlanetCatalogRecord
from cosmosdb.domain.esi import (
    ESICalculator,
    HabitabilityWeightedStrategy,
    StandardESIStrategy,
)
from cosmosdb.domain.value_objects import CelestialBoundingBox, CelestialCoordinates
from tests.support import planet


class CelestialBoundingBoxTests(unittest.TestCase):
    def test_wraparound_interval_includes_both_sides_and_meridian(self) -> None:
        box = CelestialBoundingBox(345.0, 52.5, 46.0, 78.0)
        for ra in (0.0, 10.0, 345.0, 350.0, 360.0, 52.5):
            with self.subTest(ra=ra):
                self.assertTrue(box.contains(CelestialCoordinates(ra, 60.0)))
        self.assertFalse(box.contains(CelestialCoordinates(180.0, 60.0)))
        self.assertFalse(box.contains(CelestialCoordinates(350.0, 20.0)))


class PlanetDomainTests(unittest.TestCase):
    def test_builder_rejects_non_physical_measurement(self) -> None:
        with self.assertRaisesRegex(ValueError, "radius_earth"):
            (PlanetBuilder().set("planet_id", 1).set("name", "Bad")
             .set("system_id", 1).set("system_name", "Host")
             .set("radius_earth", 0).build())

    def test_catalog_record_lifecycle_rejects_invalid_transitions(self) -> None:
        record = PlanetCatalogRecord(planet(1, "Earth"))
        with self.assertRaises(ValueError):
            record.remove()
        record.catalog()
        self.assertIs(record.state, CatalogRecordState.CATALOGED)
        record.remove()
        self.assertIs(record.state, CatalogRecordState.REMOVED)

    def test_esi_strategy_keeps_scientific_score_separate_from_habitability(self) -> None:
        standard = ESICalculator(StandardESIStrategy()).calculate(planet(1, "Earth"))
        weighted = ESICalculator(HabitabilityWeightedStrategy()).calculate(
            planet(2, "Distant", orbit=4.0)
        )
        self.assertAlmostEqual(standard.score, 1.0)
        self.assertEqual(weighted.zone_status, "TOO_COLD")
        self.assertAlmostEqual(weighted.score, weighted.base * 0.1)


if __name__ == "__main__":
    unittest.main()
