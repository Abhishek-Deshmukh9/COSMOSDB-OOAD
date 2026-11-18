from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class CelestialCoordinates:
    ra: float
    dec: float

    def __post_init__(self) -> None:
        if not isfinite(self.ra) or not 0 <= self.ra <= 360:
            raise ValueError("Right ascension must be between 0 and 360 degrees.")
        if not isfinite(self.dec) or not -90 <= self.dec <= 90:
            raise ValueError("Declination must be between -90 and 90 degrees.")


@dataclass(frozen=True)
class CelestialBoundingBox:
    min_ra: float
    max_ra: float
    min_dec: float
    max_dec: float

    def __post_init__(self) -> None:
        if not all(isfinite(value) for value in (self.min_ra, self.max_ra, self.min_dec, self.max_dec)):
            raise ValueError("Bounding-box coordinates must be finite.")
        if not (0 <= self.min_ra <= 360 and 0 <= self.max_ra <= 360):
            raise ValueError("Right ascension bounds must be between 0 and 360 degrees.")
        if not (-90 <= self.min_dec <= self.max_dec <= 90):
            raise ValueError("Declination bounds must be ordered within -90 and 90 degrees.")

    def contains(self, coordinates: CelestialCoordinates) -> bool:
        ra = coordinates.ra % 360
        inside_ra = (
            self.min_ra <= ra <= self.max_ra
            if self.min_ra <= self.max_ra
            else ra >= self.min_ra or ra <= self.max_ra
        )
        return inside_ra and self.min_dec <= coordinates.dec <= self.max_dec


@dataclass(frozen=True)
class HabitableZone:
    inner_au: float
    outer_au: float

    def __post_init__(self) -> None:
        if not (isfinite(self.inner_au) and isfinite(self.outer_au) and 0 < self.inner_au <= self.outer_au):
            raise ValueError("Habitable-zone boundaries must be finite, positive, and ordered.")

    def classify(self, orbit_au: float | None) -> str:
        if orbit_au is None:
            return "UNKNOWN"
        if orbit_au < self.inner_au:
            return "TOO_HOT"
        if orbit_au > self.outer_au:
            return "TOO_COLD"
        return "HABITABLE"


@dataclass(frozen=True)
class ESIResult:
    interior: float | None
    surface: float | None
    base: float | None
    score: float | None
    density: float | None
    surface_temperature: float | None
    orbit_distance: float | None
    habitable_zone: HabitableZone | None
    zone_status: str
