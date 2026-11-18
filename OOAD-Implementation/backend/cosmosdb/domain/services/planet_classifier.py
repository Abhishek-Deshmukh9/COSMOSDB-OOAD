from __future__ import annotations

from enum import Enum
from math import isfinite
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cosmosdb.domain.entities import Planet


class PlanetArchetype(str, Enum):
    """Documented astronomical exoplanet archetypes based on radius and mass."""
    TERRESTRIAL = "Terrestrial / Rocky"
    SUPER_EARTH = "Super-Earth"
    MINI_NEPTUNE = "Mini-Neptune"
    GAS_GIANT = "Gas Giant"
    SUPER_JUPITER = "Super-Jupiter"
    UNKNOWN = "Unknown"


class PlanetClassifier:
    """Classifies exoplanets into canonical astronomical archetypes.
    
    Primary classification relies on planetary radius (Earth radii, R_earth).
    Secondary fallback classification relies on planetary mass (Earth masses, M_earth)
    when radius measurement is unavailable.
    """

    # Radius boundaries (R_earth)
    RADIUS_TERRESTRIAL_MAX = 1.25
    RADIUS_SUPER_EARTH_MAX = 2.0
    RADIUS_MINI_NEPTUNE_MAX = 6.0
    RADIUS_GAS_GIANT_MAX = 15.0

    # Mass boundaries (M_earth) used as fallback
    MASS_TERRESTRIAL_MAX = 2.0
    MASS_SUPER_EARTH_MAX = 10.0
    MASS_MINI_NEPTUNE_MAX = 50.0
    MASS_GAS_GIANT_MAX = 3000.0

    @classmethod
    def classify_by_measurements(
        cls,
        radius_earth: float | None,
        mass_earth: float | None = None,
    ) -> PlanetArchetype:
        """Classifies a planet given its radius and optional mass measurements."""
        if radius_earth is not None and isfinite(radius_earth) and radius_earth > 0:
            if radius_earth < cls.RADIUS_TERRESTRIAL_MAX:
                return PlanetArchetype.TERRESTRIAL
            if radius_earth < cls.RADIUS_SUPER_EARTH_MAX:
                return PlanetArchetype.SUPER_EARTH
            if radius_earth < cls.RADIUS_MINI_NEPTUNE_MAX:
                return PlanetArchetype.MINI_NEPTUNE
            if radius_earth < cls.RADIUS_GAS_GIANT_MAX:
                return PlanetArchetype.GAS_GIANT
            return PlanetArchetype.SUPER_JUPITER

        if mass_earth is not None and isfinite(mass_earth) and mass_earth > 0:
            if mass_earth < cls.MASS_TERRESTRIAL_MAX:
                return PlanetArchetype.TERRESTRIAL
            if mass_earth < cls.MASS_SUPER_EARTH_MAX:
                return PlanetArchetype.SUPER_EARTH
            if mass_earth < cls.MASS_MINI_NEPTUNE_MAX:
                return PlanetArchetype.MINI_NEPTUNE
            if mass_earth < cls.MASS_GAS_GIANT_MAX:
                return PlanetArchetype.GAS_GIANT
            return PlanetArchetype.SUPER_JUPITER

        return PlanetArchetype.UNKNOWN

    @classmethod
    def classify(cls, planet: Planet) -> PlanetArchetype:
        """Classifies a Planet domain entity."""
        return cls.classify_by_measurements(
            radius_earth=planet.radius_earth,
            mass_earth=planet.mass_earth,
        )
