from __future__ import annotations

from math import isfinite, sqrt
from typing import Protocol

from .entities import Planet
from .value_objects import ESIResult, HabitableZone


class IESIScoringStrategy(Protocol):
    def score(self, base_score: float | None, zone_status: str) -> float | None: ...


class StandardESIStrategy:
    def score(self, base_score: float | None, zone_status: str) -> float | None:
        return base_score


class HabitabilityWeightedStrategy:
    def score(self, base_score: float | None, zone_status: str) -> float | None:
        if base_score is None:
            return None
        return base_score if zone_status in ("HABITABLE", "UNKNOWN") else base_score * 0.1


class HabitableZoneCalculator:
    @staticmethod
    def calculate(luminosity_solar: float | None) -> HabitableZone | None:
        if luminosity_solar is None or not isfinite(luminosity_solar) or luminosity_solar <= 0:
            return None
        return HabitableZone(sqrt(luminosity_solar / 1.1), sqrt(luminosity_solar / 0.53))


class ESICalculator:
    def __init__(self, strategy: IESIScoringStrategy | None = None) -> None:
        self._strategy = strategy or StandardESIStrategy()

    def calculate(self, planet: Planet) -> ESIResult:
        radius = planet.radius_earth
        mass = planet.mass_earth
        density = planet.density
        if density is None and mass is not None and radius is not None and radius > 0:
            density = mass / radius**3 * 5.51

        luminosity = None
        if planet.star_luminosity_log10 is not None:
            luminosity = 10**planet.star_luminosity_log10
        elif planet.star_radius_solar is not None and planet.star_temperature_k is not None:
            luminosity = planet.star_radius_solar**2 * (planet.star_temperature_k / 5778) ** 4

        orbit = planet.orbit_au
        if orbit is None and planet.orbital_period_days is not None and planet.star_mass_solar:
            period_years = planet.orbital_period_days / 365.25
            orbit = ((period_years**2) * planet.star_mass_solar) ** (1 / 3)

        temperature = planet.temperature_k
        if temperature is None and luminosity is not None and orbit is not None and orbit > 0:
            temperature = 278 * (luminosity / orbit**2) ** 0.25

        escape_velocity = None
        if mass is not None and radius is not None and radius > 0:
            escape_velocity = sqrt(mass / radius) * 11.19

        interior = None
        if radius is not None and density is not None and radius + 1 > 0 and density + 5.51 > 0:
            radius_term = (1 - abs(radius - 1) / (radius + 1)) ** 0.57
            density_term = (1 - abs(density - 5.51) / (density + 5.51)) ** 1.07
            interior = sqrt(max(0, radius_term * density_term))

        surface = None
        if escape_velocity is not None and temperature is not None and temperature + 288 > 0:
            velocity_term = (1 - abs(escape_velocity - 11.19) / (escape_velocity + 11.19)) ** 0.70
            temperature_term = (1 - abs(temperature - 288) / (temperature + 288)) ** 5.58
            surface = sqrt(max(0, velocity_term * temperature_term))

        base = sqrt(interior * surface) if interior is not None and surface is not None else None
        zone = HabitableZoneCalculator.calculate(luminosity)
        status = zone.classify(orbit) if zone else "UNKNOWN"
        score = self._strategy.score(base, status)
        return ESIResult(interior, surface, base, score, density, temperature, orbit, zone, status)
