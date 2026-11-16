import unittest

from cosmosdb.application.events import AnalyticsCacheObserver, CatalogChanged, CatalogEventPublisher
from cosmosdb.application.services import AnalyticsService, NotFoundError, PlanetCatalogService
from tests.support import FakePlanetRepository


class PlanetCatalogServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repository = FakePlanetRepository()
        self.service = PlanetCatalogService(self.repository)

    def test_esi_sorting_keeps_missing_scores_last_for_both_directions(self) -> None:
        self.repository.planets[1] = self.repository.planets[1].__class__(
            **{**self.repository.planets[1].__dict__, "mass_earth": None}
        )
        ascending = self.service.browse(sort_by="esi", order="asc")
        descending = self.service.browse(sort_by="esi", order="desc")
        self.assertEqual(ascending["planets"][-1]["planet_name"], "Cold world")
        self.assertEqual(descending["planets"][-1]["planet_name"], "Cold world")

    def test_comparison_requires_two_to_four_distinct_existing_planets(self) -> None:
        with self.assertRaises(ValueError):
            self.service.compare([1, 1])
        with self.assertRaises(NotFoundError):
            self.service.compare([1, 99])

    def test_page_and_limit_validation_is_explicit(self) -> None:
        with self.assertRaisesRegex(ValueError, "limit"):
            self.service.browse(limit=101)


class AnalyticsObserverTests(unittest.TestCase):
    def test_catalog_change_invalidates_cached_analytics(self) -> None:
        repository = FakePlanetRepository()
        analytics = AnalyticsService(repository)
        events = CatalogEventPublisher()
        events.subscribe(AnalyticsCacheObserver(analytics.invalidate))
        analytics.summary()
        analytics.summary()
        self.assertEqual(repository.analytics_reads, 1)
        events.publish(CatalogChanged("updated", 1))
        analytics.summary()
        self.assertEqual(repository.analytics_reads, 2)


if __name__ == "__main__":
    unittest.main()
