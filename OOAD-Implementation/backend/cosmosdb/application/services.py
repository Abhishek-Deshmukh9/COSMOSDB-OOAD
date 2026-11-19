from __future__ import annotations

from collections import Counter, defaultdict
import math
from typing import Any

from cosmosdb.application.events import CatalogChanged, CatalogEventPublisher
from cosmosdb.domain.entities import Planet, PlanetBuilder, PlanetCatalogRecord, Star, StarSystem
from cosmosdb.domain.esi import ESICalculator
from cosmosdb.domain.services.planet_classifier import PlanetClassifier
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
        if sort_by == "esi_score":
            sort_by = "esi"
        elif sort_by == "temp":
            sort_by = "temperature"
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
        serialized = [self._serialize(planet) for planet in planets]
        return {
            "items": serialized,
            "planets": serialized,
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
        archetype = PlanetClassifier.classify(planet)
        return {
            "planet_id": planet.planet_id,
            "planet_name": planet.name,
            "planet_type": archetype.value,
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
            "star_id": planet.system_id,
            "star_name": planet.system_name,
            "star_temp": planet.star_temperature_k,
            "star_radius": planet.star_radius_solar,
            "star_mass": planet.star_mass_solar,
            "star_luminosity": planet.star_luminosity_log10,
            "star_spectral_type": planet.star_spectral_type,
            "distance_ly": planet.distance_ly,
            "discovery_facility": planet.discovery_facility,
            "num_stars": 1,
            "num_planets": 1,
            "num_moons": 0,
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
        return {"systems": rows, "items": rows, "total": total, "page": page, "limit": limit,
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

    def create_or_ensure_system(
        self,
        system_name: str,
        constellation_id: int | None = None,
        distance_ly: float | None = None,
        num_stars: int = 1,
        num_moons: int = 0,
        star_name: str | None = None,
        star_data: dict[str, Any] | None = None,
    ) -> int:
        if hasattr(self._systems, "create_system"):
            return self._systems.create_system(
                system_name=system_name,
                constellation_id=constellation_id,
                distance_ly=distance_ly,
                num_stars=num_stars,
                num_moons=num_moons,
                star_name=star_name,
                star_data=star_data,
            )
        first = self._systems.find_by_id(101) or self._systems.find_by_id(1)
        return int(first["system_id"]) if first else 1

    def update_star(self, star_id: int, star_data: dict[str, Any]) -> bool:
        if hasattr(self._systems, "update_star"):
            return self._systems.update_star(star_id, star_data)
        return True

    def update_system(self, system_id: int, system_data: dict[str, Any]) -> bool:
        if hasattr(self._systems, "update_system"):
            return self._systems.update_system(system_id, system_data)
        return True


class ConstellationCatalogService:
    def __init__(self, repository: IConstellationRepository) -> None:
        self._repository = repository

    def list(self) -> list[dict[str, Any]]:
        return self._repository.list()


class AnalyticsService:
    def __init__(self, planets: IPlanetRepository, systems: IStarSystemRepository | None = None) -> None:
        self._planets = planets
        self._systems = systems
        self._cache: dict[str, Any] = {}
        self._cached_planets: list[Planet] | None = None

    def _get_planets(self) -> list[Planet]:
        if self._cached_planets is None:
            self._cached_planets = self._planets.all_for_analytics()
        return self._cached_planets

    def summary(self) -> dict[str, Any]:
        if "summary" in self._cache:
            return dict(self._cache["summary"])
        planets = self._get_planets()
        scores = [score for planet in planets if (score := ESICalculator().calculate(planet).score) is not None]
        methods = Counter(planet.discovery_method for planet in planets if planet.discovery_method)
        facilities = Counter(planet.discovery_facility for planet in planets if planet.discovery_facility)

        system_planet_counts = Counter(planet.system_id for planet in planets)
        multi_planet_count = sum(1 for count in system_planet_counts.values() if count > 1)
        constellation_names = {planet.constellation_name for planet in planets if planet.constellation_name}
        unique_stars = len({planet.system_id for planet in planets})

        top_fac_name, top_fac_count = facilities.most_common(1)[0] if facilities else ("N/A", 0)
        total_planets = len(planets)
        system_count = (
            self._systems.count()
            if self._systems is not None
            else len(system_planet_counts)
        )
        avg_esi = sum(scores) / len(scores) if scores else None

        self._cache["summary"] = {
            "planet_count": total_planets,
            "system_count": system_count,
            "average_esi": avg_esi,
            "scored_planet_count": len(scores),
            "top_discovery_method": methods.most_common(1)[0][0] if methods else None,
            "total_planets": total_planets,
            "multi_planet_systems": multi_planet_count,
            "constellations_cataloged": len(constellation_names),
            "unique_stars": unique_stars,
            "discovery_methods": len(methods),
            "top_discovery_facility": {
                "name": top_fac_name,
                "count": top_fac_count,
            },
        }
        return dict(self._cache["summary"])

    def esi_distribution(self) -> list[dict[str, Any]]:
        if "esi_distribution" in self._cache:
            return list(self._cache["esi_distribution"])
        planets = self._get_planets()
        tier_counts = {"Earth-like": 0, "Potential": 0, "Extreme": 0, "Inhospitable": 0, "Unknown": 0}
        for planet in planets:
            score = ESICalculator().calculate(planet).score
            if score is None:
                tier_counts["Unknown"] += 1
            elif score >= 0.8:
                tier_counts["Earth-like"] += 1
            elif score >= 0.6:
                tier_counts["Potential"] += 1
            elif score >= 0.4:
                tier_counts["Extreme"] += 1
            else:
                tier_counts["Inhospitable"] += 1
        result = [{"tier": tier, "count": count} for tier, count in tier_counts.items()]
        self._cache["esi_distribution"] = result
        return result

    def discovery_timeline(self) -> dict[str, Any]:
        if "discovery_timeline" in self._cache:
            return dict(self._cache["discovery_timeline"])
        planets = self._get_planets()
        pairs = [
            (int(planet.discovery_year), str(planet.discovery_method))
            for planet in planets
            if planet.discovery_year is not None and planet.discovery_method
        ]
        if not pairs:
            result = {"years": [], "methods": [], "series": {}}
        else:
            years = sorted(list({year for year, _ in pairs}))
            methods = sorted(list({method for _, method in pairs}))
            counts_map = Counter(pairs)
            series = {
                method: [counts_map.get((year, method), 0) for year in years]
                for method in methods
            }
            result = {"years": years, "methods": methods, "series": series}
        self._cache["discovery_timeline"] = result
        return result

    def mass_radius_scatter(self) -> list[dict[str, Any]]:
        if "mass_radius_scatter" in self._cache:
            return list(self._cache["mass_radius_scatter"])
        planets = self._get_planets()
        result = [
            {
                "mass": float(p.mass_earth),
                "radius": float(p.radius_earth),
                "temp": float(p.temperature_k) if p.temperature_k is not None else None,
                "name": p.name,
            }
            for p in planets
            if p.mass_earth is not None and p.radius_earth is not None
        ]
        self._cache["mass_radius_scatter"] = result
        return result

    def spectral_types(self) -> list[dict[str, Any]]:
        if "spectral_types" in self._cache:
            return list(self._cache["spectral_types"])
        planets = self._get_planets()
        seen_systems: set[int] = set()
        counts: dict[str, int] = defaultdict(int)
        for p in planets:
            if p.system_id in seen_systems:
                continue
            seen_systems.add(p.system_id)
            st = p.star_spectral_type
            if not st or not isinstance(st, str) or not st.strip():
                counts["Unknown"] += 1
            else:
                first = st.strip()[0].upper()
                if first in "OBAFGKM":
                    counts[first] += 1
                else:
                    counts["Other"] += 1
        order = ["O", "B", "A", "F", "G", "K", "M", "Other", "Unknown"]
        result = [{"type": s, "count": counts[s]} for s in order if s in counts]
        self._cache["spectral_types"] = result
        return result

    def system_complexity(self) -> list[dict[str, Any]]:
        if "system_complexity" in self._cache:
            return list(self._cache["system_complexity"])
        planets = self._get_planets()
        system_counts = Counter(p.system_id for p in planets)
        planet_num_to_systems = Counter(system_counts.values())
        result: list[dict[str, Any]] = []
        for n in range(1, 9):
            result.append({"planet_count": n, "systems": planet_num_to_systems.get(n, 0)})
        over8 = sum(count for n, count in planet_num_to_systems.items() if n >= 9)
        if over8 > 0:
            result.append({"planet_count": "8+", "systems": over8})
        self._cache["system_complexity"] = result
        return result

    def eccentricity_period(self) -> list[dict[str, Any]]:
        if "eccentricity_period" in self._cache:
            return list(self._cache["eccentricity_period"])
        planets = self._get_planets()
        result = [
            {
                "period": float(p.orbital_period_days),
                "eccentricity": float(p.eccentricity),
                "name": p.name,
            }
            for p in planets
            if p.orbital_period_days is not None and p.eccentricity is not None
        ]
        self._cache["eccentricity_period"] = result
        return result

    def metallicity_planets(self) -> list[dict[str, Any]]:
        if "metallicity_planets" in self._cache:
            return list(self._cache["metallicity_planets"])
        planets = self._get_planets()
        system_planet_counts = Counter(p.system_id for p in planets)
        seen_systems: set[int] = set()
        points: list[dict[str, Any]] = []
        for p in planets:
            if p.system_id in seen_systems:
                continue
            seen_systems.add(p.system_id)
            if p.star_metallicity is not None:
                points.append({
                    "metallicity": float(p.star_metallicity),
                    "num_planets": system_planet_counts[p.system_id],
                    "system": p.system_name,
                })
        self._cache["metallicity_planets"] = points
        return points

    def distance_histogram(self) -> dict[str, Any]:
        if "distance_histogram" in self._cache:
            return dict(self._cache["distance_histogram"])
        planets = self._get_planets()
        distances = [float(p.distance_ly) for p in planets if p.distance_ly is not None and p.distance_ly > 0]
        if not distances:
            result = {"bins": [], "counts": [], "bin_edges": []}
        else:
            min_d = max(min(distances), 0.1)
            max_d = max(distances)
            if min_d == max_d:
                max_d = min_d * 10
            num_edges = 30
            log_min = math.log10(min_d)
            log_max = math.log10(max_d)
            step = (log_max - log_min) / (num_edges - 1)
            edges = [10 ** (log_min + i * step) for i in range(num_edges)]
            counts = [0] * (num_edges - 1)
            for d in distances:
                placed = False
                for i in range(len(counts)):
                    if edges[i] <= d < edges[i + 1] or (i == len(counts) - 1 and d == edges[i + 1]):
                        counts[i] += 1
                        placed = True
                        break
                if not placed:
                    if d < edges[0]:
                        counts[0] += 1
                    elif d > edges[-1]:
                        counts[-1] += 1
            bins = [round(b, 2) for b in edges[:-1]]
            bin_edges = [round(b, 2) for b in edges]
            result = {"bins": bins, "counts": counts, "bin_edges": bin_edges}
        self._cache["distance_histogram"] = result
        return result

    def invalidate(self) -> None:
        self._cache.clear()
        self._cached_planets = None
