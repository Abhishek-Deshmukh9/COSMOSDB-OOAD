import unittest

from cosmosdb.domain.entities import PlanetBuilder
from cosmosdb.domain.services.planet_classifier import PlanetArchetype, PlanetClassifier


class PlanetClassifierTests(unittest.TestCase):
    def test_radius_boundary_classifications(self) -> None:
        test_cases = [
            (0.5, PlanetArchetype.TERRESTRIAL),
            (1.0, PlanetArchetype.TERRESTRIAL),
            (1.249, PlanetArchetype.TERRESTRIAL),
            (1.25, PlanetArchetype.SUPER_EARTH),
            (1.6, PlanetArchetype.SUPER_EARTH),
            (1.99, PlanetArchetype.SUPER_EARTH),
            (2.0, PlanetArchetype.MINI_NEPTUNE),
            (4.0, PlanetArchetype.MINI_NEPTUNE),
            (5.99, PlanetArchetype.MINI_NEPTUNE),
            (6.0, PlanetArchetype.GAS_GIANT),
            (11.0, PlanetArchetype.GAS_GIANT),
            (14.99, PlanetArchetype.GAS_GIANT),
            (15.0, PlanetArchetype.SUPER_JUPITER),
            (22.0, PlanetArchetype.SUPER_JUPITER),
        ]
        for radius, expected in test_cases:
            with self.subTest(radius=radius):
                self.assertEqual(
                    PlanetClassifier.classify_by_measurements(radius_earth=radius),
                    expected,
                )

    def test_mass_fallback_classifications(self) -> None:
        test_cases = [
            (0.8, PlanetArchetype.TERRESTRIAL),
            (1.99, PlanetArchetype.TERRESTRIAL),
            (2.0, PlanetArchetype.SUPER_EARTH),
            (5.5, PlanetArchetype.SUPER_EARTH),
            (9.99, PlanetArchetype.SUPER_EARTH),
            (10.0, PlanetArchetype.MINI_NEPTUNE),
            (30.0, PlanetArchetype.MINI_NEPTUNE),
            (49.9, PlanetArchetype.MINI_NEPTUNE),
            (50.0, PlanetArchetype.GAS_GIANT),
            (318.0, PlanetArchetype.GAS_GIANT),
            (2999.0, PlanetArchetype.GAS_GIANT),
            (3000.0, PlanetArchetype.SUPER_JUPITER),
            (5000.0, PlanetArchetype.SUPER_JUPITER),
        ]
        for mass, expected in test_cases:
            with self.subTest(mass=mass):
                self.assertEqual(
                    PlanetClassifier.classify_by_measurements(radius_earth=None, mass_earth=mass),
                    expected,
                )

    def test_missing_and_invalid_measurements(self) -> None:
        self.assertEqual(
            PlanetClassifier.classify_by_measurements(radius_earth=None, mass_earth=None),
            PlanetArchetype.UNKNOWN,
        )
        self.assertEqual(
            PlanetClassifier.classify_by_measurements(radius_earth=0.0, mass_earth=None),
            PlanetArchetype.UNKNOWN,
        )
        self.assertEqual(
            PlanetClassifier.classify_by_measurements(radius_earth=-1.5, mass_earth=None),
            PlanetArchetype.UNKNOWN,
        )
        self.assertEqual(
            PlanetClassifier.classify_by_measurements(radius_earth=float("nan"), mass_earth=None),
            PlanetArchetype.UNKNOWN,
        )

    def test_classify_entity(self) -> None:
        planet = (
            PlanetBuilder()
            .set("planet_id", 101)
            .set("name", "Kepler-452 b")
            .set("system_id", 10)
            .set("system_name", "Kepler-452")
            .set("radius_earth", 1.63)
            .set("mass_earth", 5.0)
            .build()
        )
        self.assertEqual(PlanetClassifier.classify(planet), PlanetArchetype.SUPER_EARTH)


if __name__ == "__main__":
    unittest.main()
