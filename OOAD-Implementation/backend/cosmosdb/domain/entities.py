from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import isfinite

from .value_objects import CelestialBoundingBox, CelestialCoordinates


@dataclass(frozen=True)
class Star:
    star_id: int
    system_id: int
    name: str
    spectral_type: str | None = None
    temperature_k: float | None = None
    radius_solar: float | None = None
    mass_solar: float | None = None
    luminosity_log10: float | None = None


@dataclass(frozen=True)
class Discovery:
    discovery_id: int
    year: int | None
    method: str | None
    facility: str | None = None
    telescope: str | None = None


@dataclass(frozen=True)
class Constellation:
    name: str
    boundaries: tuple[CelestialBoundingBox, ...]
    constellation_id: int | None = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Constellation name cannot be empty.")
        if not self.boundaries:
            raise ValueError("A constellation requires at least one bounding box.")

    def contains(self, coordinates: CelestialCoordinates) -> bool:
        return any(boundary.contains(coordinates) for boundary in self.boundaries)


@dataclass(frozen=True)
class StarSystem:
    system_id: int
    name: str
    coordinates: CelestialCoordinates | None
    distance_ly: float | None
    constellation_name: str | None
    constellation_id: int | None = None
    stars: tuple[Star, ...] = ()
    planet_count: int = 0

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Star-system name cannot be empty.")
        if not self.stars:
            raise ValueError("A star system must contain at least one cataloged star.")
        if self.planet_count < 0:
            raise ValueError("Planet count cannot be negative.")
        if self.distance_ly is not None and (not isfinite(self.distance_ly) or self.distance_ly <= 0):
            raise ValueError("System distance must be finite and positive when provided.")


@dataclass(frozen=True)
class Planet:
    planet_id: int
    name: str
    system_id: int
    system_name: str
    discovery_id: int | None = None
    radius_earth: float | None = None
    mass_earth: float | None = None
    density: float | None = None
    temperature_k: float | None = None
    orbit_au: float | None = None
    orbital_period_days: float | None = None
    eccentricity: float | None = None
    insolation_flux: float | None = None
    discovery_year: int | None = None
    discovery_method: str | None = None
    constellation_name: str | None = None
    star_temperature_k: float | None = None
    star_radius_solar: float | None = None
    star_mass_solar: float | None = None
    star_luminosity_log10: float | None = None
    distance_ly: float | None = None
    discovery_facility: str | None = None
    star_spectral_type: str | None = None
    star_metallicity: float | None = None


class CatalogRecordState(str, Enum):
    DRAFT = "DRAFT"
    CATALOGED = "CATALOGED"
    REMOVED = "REMOVED"


@dataclass
class PlanetCatalogRecord:
    planet: Planet
    state: CatalogRecordState = CatalogRecordState.DRAFT

    def catalog(self) -> None:
        if self.state is not CatalogRecordState.DRAFT:
            raise ValueError("Only a draft record can be cataloged.")
        self.state = CatalogRecordState.CATALOGED

    def remove(self) -> None:
        if self.state is not CatalogRecordState.CATALOGED:
            raise ValueError("Only a cataloged record can be removed.")
        self.state = CatalogRecordState.REMOVED


class PlanetBuilder:
    def __init__(self) -> None:
        self._values: dict[str, object] = {}

    def set(self, name: str, value: object) -> PlanetBuilder:
        self._values[name] = value
        return self

    def build(self) -> Planet:
        required = ("planet_id", "name", "system_id", "system_name")
        missing = [field for field in required if field not in self._values]
        if missing:
            raise ValueError(f"Missing required planet fields: {', '.join(missing)}.")

        planet = Planet(**self._values)
        if (
            planet.planet_id < 0
            or planet.system_id <= 0
            or not planet.name.strip()
            or (planet.planet_id > 0 and not planet.system_name.strip())
        ):
            raise ValueError("Planet identity and host-system fields are invalid.")
        ranges = {
            "radius_earth": (0.3098, 87.20586985),
            "mass_earth": (0.02, 9534.85221),
            "density": (0.0051, 2000),
            "temperature_k": (34, 4050),
            "orbit_au": (0.0044, 19000),
            "orbital_period_days": (0.090706293, 402000000),
            "insolation_flux": (0.0003, 44900),
        }
        for field, (minimum, maximum) in ranges.items():
            value = getattr(planet, field)
            if value is not None and (
                not isfinite(value) or not minimum <= value <= maximum
            ):
                raise ValueError(f"{field} must be between {minimum} and {maximum}.")
        if planet.eccentricity is not None and (
            not isfinite(planet.eccentricity) or not 0 <= planet.eccentricity <= 0.95
        ):
            raise ValueError("Eccentricity must be between 0 and 0.95.")
        return planet
