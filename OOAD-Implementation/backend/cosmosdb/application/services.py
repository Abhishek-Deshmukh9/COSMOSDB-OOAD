from __future__ import annotations

from collections import Counter
from typing import Any

from cosmosdb.application.events import CatalogChanged, CatalogEventPublisher
from cosmosdb.domain.entities import Planet, PlanetBuilder, PlanetCatalogRecord, Star, StarSystem
from cosmosdb.domain.esi import ESICalculator
from cosmosdb.domain.value_objects import CelestialCoordinates
from .ports import IConstellationRepository, IPlanetRepository, IStarSystemRepository


class NotFoundError(LookupError):
    pass


class PlanetCatalogService:
    def __init__(self, repository: IPlanetRepository, calculator: ESICalculator | None = None,
                 events: CatalogEventPublisher | None = None,
                 systems: IStarSystemRepository | None = None) -> None:
        self._repository = repository
        self._calculator = calculator or ESICalculator()
        self._events = events
        self._systems = systems

    def browse(self, *, query: str | None = None, constellation: str | None = None,
               method: str | None = None, sort_by: str = "name", order: str = "asc",
               page: int = 1, limit: int = 50) -> dict[str, Any]:
        if sort_by not in {"name", "mass", "radius", "temperature", "distance", "esi"}:
            raise ValueError("Unsupported planet sort field.")
        if order not in {"asc", "desc"}:
            raise ValueError("Sort order must be 'asc' or 'desc'.")
        if page < 1 or limit < 1 or limit > 100:
            raise ValueError("Page must be positive and limit must be between 1 and 100.")
        if sort_by == "esi":
            planets, total = self._repository.list_for_esi(
                query=query, constellation=constellation, method=method,
            )
            scores = {planet.planet_id: self._calculator.calculate(planet).score for planet in planets}
            planets.sort(key=lambda planet: (
                scores[planet.planet_id] is None,
                (scores[planet.planet_id] or 0) * (-1 if order == "desc" else 1),
            ))
            offset = (page - 1) * limit
            planets = planets[offset:offset + limit]
        else:
            planets, total = self._repository.list(
                query=query, constellation=constellation, method=method,
                sort_by=sort_by, order=order, page=page, limit=limit,
            )
        return {
            "planets": [self._serialize(planet) for planet in planets],
            "total": total,
            "page": page,
            "limit": limit,
            "pages": max(1, (total + limit - 1) // limit),
        }

    def get(self, planet_id: int) -> dict[str, Any]:
        planet = self._repository.find_by_id(planet_id)
        if planet is None:
            raise NotFoundError(f"Planet {planet_id} was not found.")
        return self._serialize(planet)

    def discovery_methods(self) -> list[str]:
        return self._repository.discovery_methods()

    def compare(self, planet_ids: list[int]) -> list[dict[str, Any]]:
        unique_ids = list(dict.fromkeys(planet_ids))
        if not 2 <= len(unique_ids) <= 4:
            raise ValueError("Select between two and four distinct planets to compare.")
        planets = self._repository.find_by_ids(unique_ids)
        by_id = {planet.planet_id: planet for planet in planets}
        missing = [planet_id for planet_id in unique_ids if planet_id not in by_id]
        if missing:
            raise NotFoundError(f"Planets not found: {', '.join(map(str, missing))}.")
        return [self._serialize(by_id[planet_id]) for planet_id in unique_ids]

    def create(self, values: dict[str, Any]) -> dict[str, Any]:
        system_id = values.get("system_id")
        if self._systems is not None:
            if not isinstance(system_id, int) or self._systems.find_by_id(system_id) is None:
                raise NotFoundError(f"Star system {system_id} was not found.")
        planet = PlanetBuilder().set("planet_id", 0).set("system_name", "")
        for name, value in values.items():
            planet.set(name, value)
        record = PlanetCatalogRecord(planet.build())
        created = self._repository.create(record.planet)
        record.planet = created
        record.catalog()
        if self._events:
            self._events.publish(CatalogChanged("created", created.planet_id))
        return self._serialize(created)

    def update(self, planet_id: int, changes: dict[str, Any]) -> dict[str, Any]:
        current = self._repository.find_by_id(planet_id)
        if current is None:
            raise NotFoundError(f"Planet {planet_id} was not found.")
        record = PlanetCatalogRecord(current)
        record.catalog()
        permitted = {
            "name", "radius_earth", "mass_earth", "density", "temperature_k",
            "orbit_au", "orbital_period_days", "eccentricity", "insolation_flux",
        }
        unknown = set(changes) - permitted
        if unknown:
            raise ValueError(f"Unsupported planet fields: {', '.join(sorted(unknown))}.")
        candidate = PlanetBuilder()
        for name, value in {**current.__dict__, **changes}.items():
            candidate.set(name, value)
        candidate.build()
        updated = self._repository.update(planet_id, changes)
        if updated is None:
            raise NotFoundError(f"Planet {planet_id} was not found.")
        record.planet = updated
        if self._events:
            self._events.publish(CatalogChanged("updated", planet_id))
        return self._serialize(updated)

    def delete(self, planet_id: int) -> None:
        current = self._repository.find_by_id(planet_id)
        if current is None:
            raise NotFoundError(f"Planet {planet_id} was not found.")
        record = PlanetCatalogRecord(current)
        record.catalog()
        if not self._repository.delete(planet_id):
            raise NotFoundError(f"Planet {planet_id} was not found.")
        record.remove()
        if self._events:
            self._events.publish(CatalogChanged("deleted", planet_id))

    def _serialize(self, planet: Planet) -> dict[str, Any]:
        esi = self._calculator.calculate(planet)
        return {
            "planet_id": planet.planet_id,
            "planet_name": planet.name,
            "system_id": planet.system_id,
            "system_name": planet.system_name,
            "discovery_id": planet.discovery_id,
            "radius_earth": planet.radius_earth,
            "mass_earth": planet.mass_earth,
            "planet_density": planet.density,
            "planet_temp": planet.temperature_k,
            "orbit_radius": planet.orbit_au,
            "orbital_period": planet.orbital_period_days,
            "eccentricity": planet.eccentricity,
            "insolation_flux": planet.insolation_flux,
            "discovery_year": planet.discovery_year,
            "discovery_method": planet.discovery_method,
            "constellation_name": planet.constellation_name,
            "esi_score": esi.score,
            "esi": {
                "interior": esi.interior,
                "surface": esi.surface,
                "base": esi.base,
                "score": esi.score,
                "zone_status": esi.zone_status,
                "hz_inner": esi.habitable_zone.inner_au if esi.habitable_zone else None,
                "hz_outer": esi.habitable_zone.outer_au if esi.habitable_zone else None,
            },
        }


class StarSystemCatalogService:
    def __init__(self, systems: IStarSystemRepository, planets: IPlanetRepository) -> None:
        self._systems = systems
        self._planets = planets

    def browse(self, *, query: str | None = None, constellation: str | None = None,
               page: int = 1, limit: int = 20) -> dict[str, Any]:
        if page < 1 or limit < 1 or limit > 100:
            raise ValueError("Page must be positive and limit must be between 1 and 100.")
        rows, total = self._systems.list(query=query, constellation=constellation, page=page, limit=limit)
        return {"systems": rows, "total": total, "page": page, "limit": limit,
                "pages": max(1, (total + limit - 1) // limit)}

    def get(self, system_id: int) -> dict[str, Any]:
        row = self._systems.find_by_id(system_id)
        if row is None:
            raise NotFoundError(f"Star system {system_id} was not found.")
        coordinates = None
        if row.get("ra") is not None and row.get("dec") is not None:
            coordinates = CelestialCoordinates(float(row["ra"]), float(row["dec"]))
        stars = tuple(
            Star(
                star_id=int(star["star_id"]),
                system_id=system_id,
                name=star["star_name"],
                spectral_type=star.get("spectral_type"),
                temperature_k=float(star["star_temp"]) if star.get("star_temp") is not None else None,
                radius_solar=float(star["star_radius"]) if star.get("star_radius") is not None else None,
                mass_solar=float(star["star_mass"]) if star.get("star_mass") is not None else None,
                luminosity_log10=float(star["star_luminosity"]) if star.get("star_luminosity") is not None else None,
            )
            for star in self._systems.stars_by_system(system_id)
        )
        entity = StarSystem(
            system_id=system_id,
            name=row["system_name"],
            coordinates=coordinates,
            distance_ly=float(row["distance_ly"]) if row.get("distance_ly") is not None else None,
            constellation_name=row.get("constellation_name"),
            constellation_id=(
                int(row["constellation_id"]) if row.get("constellation_id") is not None else None
            ),
            stars=stars,
            planet_count=self._systems.planet_count(system_id),
        )
        return {
            "system_id": entity.system_id,
            "system_name": entity.name,
            "ra": entity.coordinates.ra if entity.coordinates else None,
            "dec": entity.coordinates.dec if entity.coordinates else None,
            "distance_ly": entity.distance_ly,
            "constellation_name": entity.constellation_name,
            "constellation_id": entity.constellation_id,
            "num_planets": entity.planet_count,
            "stars": [
                {
                    "star_id": star.star_id,
                    "star_name": star.name,
                    "spectral_type": star.spectral_type,
                    "star_temp": star.temperature_k,
                    "star_radius": star.radius_solar,
                    "star_mass": star.mass_solar,
                    "star_luminosity": star.luminosity_log10,
                }
                for star in entity.stars
            ],
            "planets": [
            PlanetCatalogService(self._planets)._serialize(planet)
            for planet in self._planets.find_by_ids_for_system(system_id)
            ],
        }


class ConstellationCatalogService:
    def __init__(self, repository: IConstellationRepository) -> None:
        self._repository = repository

    def list(self) -> list[dict[str, Any]]:
        return self._repository.list()


class AnalyticsService:
    def __init__(self, planets: IPlanetRepository, systems: IStarSystemRepository | None = None) -> None:
        self._planets = planets
        self._systems = systems
        self._cached_summary: dict[str, Any] | None = None

    def summary(self) -> dict[str, Any]:
        if self._cached_summary is not None:
            return dict(self._cached_summary)
        planets = self._planets.all_for_analytics()
        scores = [score for planet in planets if (score := ESICalculator().calculate(planet).score) is not None]
        methods = Counter(planet.discovery_method for planet in planets if planet.discovery_method)
        self._cached_summary = {
            "planet_count": len(planets),
            "system_count": (
                self._systems.count()
                if self._systems is not None
                else len({planet.system_id for planet in planets})
            ),
            "average_esi": sum(scores) / len(scores) if scores else None,
            "scored_planet_count": len(scores),
            "top_discovery_method": methods.most_common(1)[0][0] if methods else None,
        }
        return dict(self._cached_summary)

    def invalidate(self) -> None:
        self._cached_summary = None
