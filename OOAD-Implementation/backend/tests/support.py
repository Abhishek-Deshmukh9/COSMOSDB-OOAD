from __future__ import annotations

from typing import Any

from cosmosdb.domain.entities import Planet, PlanetBuilder


def planet(
    planet_id: int,
    name: str,
    *,
    orbit: float | None = 1.0,
    mass: float | None = 1.0,
    discovery_year: int | None = 2020,
    discovery_method: str | None = "Transit",
    discovery_facility: str | None = "Kepler",
    spectral_type: str | None = "G2V",
    distance_ly: float | None = 100.0,
    metallicity: float | None = 0.05,
    period: float | None = 365.25,
    eccentricity: float | None = 0.02,
) -> Planet:
    return (
        PlanetBuilder()
        .set("planet_id", planet_id)
        .set("name", name)
        .set("system_id", planet_id + 100)
        .set("system_name", f"System {planet_id}")
        .set("radius_earth", 1.0)
        .set("mass_earth", mass)
        .set("temperature_k", 288.0)
        .set("orbit_au", orbit)
        .set("orbital_period_days", period)
        .set("eccentricity", eccentricity)
        .set("star_temperature_k", 5778.0)
        .set("star_radius_solar", 1.0)
        .set("star_mass_solar", 1.0)
        .set("star_luminosity_log10", 0.0)
        .set("discovery_year", discovery_year)
        .set("discovery_method", discovery_method)
        .set("discovery_facility", discovery_facility)
        .set("star_spectral_type", spectral_type)
        .set("distance_ly", distance_ly)
        .set("star_metallicity", metallicity)
        .build()
    )


class FakePlanetRepository:
    def __init__(self, planets: list[Planet] | None = None) -> None:
        self.planets = planets or [planet(1, "Earth-like"), planet(2, "Cold world", orbit=4.0)]
        self.analytics_reads = 0

    def list(self, *, query: str | None, constellation: str | None, method: str | None,
             sort_by: str, order: str, page: int, limit: int) -> tuple[list[Planet], int]:
        selected = self._filter(query, constellation, method)
        key_map = {"name": lambda p: p.name.lower(), "mass": lambda p: p.mass_earth or 0,
                   "radius": lambda p: p.radius_earth or 0, "temperature": lambda p: p.temperature_k or 0,
                   "distance": lambda p: p.planet_id}
        selected.sort(key=key_map[sort_by], reverse=order == "desc")
        total = len(selected)
        offset = (page - 1) * limit
        return selected[offset:offset + limit], total

    def list_for_esi(self, *, query: str | None, constellation: str | None,
                     method: str | None) -> tuple[list[Planet], int]:
        selected = self._filter(query, constellation, method)
        return selected, len(selected)

    def find_by_id(self, planet_id: int) -> Planet | None:
        return next((entry for entry in self.planets if entry.planet_id == planet_id), None)

    def find_by_ids(self, planet_ids: list[int]) -> list[Planet]:
        return [entry for entry in self.planets if entry.planet_id in planet_ids]

    def find_by_ids_for_system(self, system_id: int) -> list[Planet]:
        return [entry for entry in self.planets if entry.system_id == system_id]

    def all_for_analytics(self) -> list[Planet]:
        self.analytics_reads += 1
        return list(self.planets)

    def discovery_methods(self) -> list[str]:
        return ["Transit"]

    def create(self, entry: Planet) -> Planet:
        saved = PlanetBuilder()
        for key, value in {**entry.__dict__, "planet_id": max(p.planet_id for p in self.planets) + 1,
                           "system_name": "Created System"}.items():
            saved.set(key, value)
        result = saved.build()
        self.planets.append(result)
        return result

    def update(self, planet_id: int, changes: dict[str, Any]) -> Planet | None:
        current = self.find_by_id(planet_id)
        if current is None:
            return None
        builder = PlanetBuilder()
        for name, value in {**current.__dict__, **changes}.items():
            builder.set(name, value)
        updated = builder.build()
        self.planets = [updated if p.planet_id == planet_id else p for p in self.planets]
        return updated

    def delete(self, planet_id: int) -> bool:
        before = len(self.planets)
        self.planets = [entry for entry in self.planets if entry.planet_id != planet_id]
        return len(self.planets) < before

    def _filter(self, query: str | None, constellation: str | None, method: str | None) -> list[Planet]:
        selected = self.planets
        if query:
            selected = [entry for entry in selected if query.casefold() in entry.name.casefold()
                        or query.casefold() in entry.system_name.casefold()]
        if constellation:
            selected = [entry for entry in selected if entry.constellation_name == constellation]
        if method:
            selected = [entry for entry in selected if entry.discovery_method == method]
        return list(selected)


class FakeSystemRepository:
    def list(self, *, query: str | None, constellation: str | None, page: int,
             limit: int) -> tuple[list[dict[str, Any]], int]:
        rows = [{"system_id": 101, "system_name": "System 1", "ra": 10.0, "dec": 20.0,
                 "distance_ly": 4.2, "constellation_name": "Orion", "num_planets": 1}]
        return rows, len(rows)

    def find_by_id(self, system_id: int) -> dict[str, Any] | None:
        if system_id != 101:
            return None
        return {"system_id": 101, "system_name": "System 1", "ra": 10.0, "dec": 20.0,
                "distance_ly": 4.2, "constellation_name": "Orion"}

    def stars_by_system(self, system_id: int) -> list[dict[str, Any]]:
        return [{"star_id": 1, "star_name": "System 1", "star_temp": 5778.0,
                 "star_radius": 1.0, "star_mass": 1.0, "star_luminosity": 0.0}]

    def planet_count(self, system_id: int) -> int:
        return 1

    def count(self) -> int:
        return 2


class FakeConstellationRepository:
    def list(self) -> list[dict[str, Any]]:
        return [{"constellation_name": "Orion", "system_count": 1}]
