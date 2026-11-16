from __future__ import annotations

import csv
import os
from pathlib import Path
from typing import Any

from cosmosdb.infrastructure.mysql import create_connection

DATA_DIR = Path(os.getenv("COSMOSDB_DATA_DIR", Path(__file__).resolve().parents[2] / "data"))


def _number(value: str | None, integer: bool = False) -> int | float | None:
    if value is None or value.strip() == "":
        return None
    return int(float(value)) if integer else float(value)


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as source:
        return list(csv.DictReader(source))


def seed() -> None:
    constellations = _read_csv(DATA_DIR / "Constellations.csv")
    planets = _read_csv(DATA_DIR / "ExoplanetDataset.csv")
    connection = create_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM planet")
        if cursor.fetchone()[0]:
            raise RuntimeError("The planet table is not empty; refusing to duplicate seed data.")

        constellation_rows: list[tuple[Any, ...]] = []
        for row in constellations:
            cursor.execute(
                """
                INSERT INTO constellation
                    (constellation_name, min_ra, max_ra, min_dec, max_dec, description, pop_rank)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    row["constellation_name"], float(row["min_ra"]), float(row["max_ra"]),
                    float(row["min_dec"]), float(row["max_dec"]), row["description"],
                    int(row["pop_rank"]),
                ),
            )
            constellation_rows.append((
                int(cursor.lastrowid), row["constellation_name"], float(row["min_ra"]),
                float(row["max_ra"]), float(row["min_dec"]), float(row["max_dec"]),
            ))

        systems: dict[str, tuple[int, dict[str, str]]] = {}
        discovery_ids: dict[tuple[Any, ...], int] = {}
        star_names: set[str] = set()
        planet_rows: list[tuple[Any, ...]] = []

        for row in planets:
            star_name = row["star_name"].strip()
            if star_name not in systems:
                ra = _number(row["ra_deg"])
                dec = _number(row["dec_deg"])
                constellation_id = None
                if ra is not None and dec is not None:
                    normalized_ra = ra % 360
                    for cid, _, min_ra, max_ra, min_dec, max_dec in constellation_rows:
                        inside_ra = min_ra <= normalized_ra <= max_ra if min_ra <= max_ra else (
                            normalized_ra >= min_ra or normalized_ra <= max_ra
                        )
                        if inside_ra and min_dec <= dec <= max_dec:
                            constellation_id = cid
                            break
                cursor.execute(
                    """
                    INSERT INTO starsystem
                        (system_name, ra, `dec`, num_stars, num_planets, num_moons, distance_ly, constellation_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        star_name, ra, dec, _number(row["num_stars"], True) or 1,
                        _number(row["num_planets"], True) or 0,
                        _number(row["num_moons"], True) or 0,
                        (_number(row["distance_pc"]) * 3.26156) if _number(row["distance_pc"]) else None,
                        constellation_id,
                    ),
                )
                system_id = int(cursor.lastrowid)
                systems[star_name] = (system_id, row)

            system_id, first = systems[star_name]
            if star_name not in star_names:
                cursor.execute(
                    """
                    INSERT INTO star (
                        star_name, system_id, spectral_type, star_temp, star_radius, star_mass,
                        star_metallicity, star_luminosity, star_gravity, star_age, star_brightness
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        star_name, system_id, first["spectral_type"],
                        _number(first["star_temp"]), _number(first["star_radius"]),
                        _number(first["star_mass"]), _number(first["star_metallicity"]),
                        _number(first["star_luminosity"]), _number(first["star_gravity"]),
                        _number(first["star_age"]), _number(first["star_brightness"]),
                    ),
                )
                star_names.add(star_name)

            discovery_key = (
                _number(row["discovery_year"], True),
                row["discovery_method"].strip() or None,
                row["discovery_locale"].strip() or None,
                row["discovery_facility"].strip() or None,
                row["discovery_telescope"].strip() or None,
                row["discovery_instrument"].strip() or None,
            )
            if discovery_key not in discovery_ids:
                cursor.execute(
                    """
                    INSERT INTO discovery (
                        discovery_year, discovery_method, discovery_locale,
                        discovery_facility, discovery_telescope, discovery_instrument
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    discovery_key,
                )
                discovery_ids[discovery_key] = int(cursor.lastrowid)

            planet_rows.append((
                row["planet_name"], system_id, discovery_ids[discovery_key],
                bool(_number(row["is_circumbinary"], True) or 0),
                _number(row["orbital_period"]), _number(row["orbit_radius"]),
                _number(row["radius_earth"]), _number(row["mass_earth"]),
                _number(row["planet_density"]), _number(row["eccentricity"]),
                _number(row["insolation_flux"]), _number(row["planet_temp"]),
                bool(_number(row["has_transit_variations"], True) or 0),
            ))

        cursor.executemany(
            """
            INSERT INTO planet (
                planet_name, system_id, discovery_id, is_circumbinary, orbital_period,
                orbit_radius, radius_earth, mass_earth, planet_density, eccentricity,
                insolation_flux, planet_temp, ttv_obs
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            planet_rows,
        )
        connection.commit()
        print(
            f"Seeded {len(constellations)} constellation boxes, {len(systems)} systems, "
            f"{len(star_names)} stars, {len(discovery_ids)} discovery records, "
            f"and {len(planet_rows)} planets."
        )
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    seed()
