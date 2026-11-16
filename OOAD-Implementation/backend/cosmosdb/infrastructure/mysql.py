from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Callable

import mysql.connector
from dotenv import load_dotenv

from cosmosdb.domain.entities import Planet, PlanetBuilder

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

ConnectionFactory = Callable[[], Any]


def create_connection() -> Any:
    host = os.getenv("MYSQL_HOST", "127.0.0.1")
    if host == "localhost":
        host = "127.0.0.1"
    return mysql.connector.connect(
        host=host,
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DB_NAME", "CosmosDB"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        connect_timeout=5,
    )


PLANET_SELECT = """
    SELECT p.planet_id, p.planet_name, p.system_id, s.system_name, p.discovery_id,
           p.radius_earth, p.mass_earth, p.planet_density, p.planet_temp,
           p.orbit_radius, p.orbital_period, p.eccentricity, p.insolation_flux,
           d.discovery_year, d.discovery_method, c.constellation_name,
           st.star_temp, st.star_radius, st.star_mass, st.star_luminosity
    FROM planet p
    JOIN starsystem s ON s.system_id = p.system_id
    LEFT JOIN constellation c ON c.constellation_id = s.constellation_id
    LEFT JOIN discovery d ON d.discovery_id = p.discovery_id
    LEFT JOIN (
        SELECT star_id, system_id, star_temp, star_radius, star_mass, star_luminosity,
               ROW_NUMBER() OVER (PARTITION BY system_id ORDER BY star_id) AS row_num
        FROM star
    ) st ON st.system_id = s.system_id AND st.row_num = 1
"""

PLANET_SORT_COLUMNS = {
    "name": "p.planet_name",
    "mass": "p.mass_earth",
    "radius": "p.radius_earth",
    "temperature": "p.planet_temp",
    "distance": "s.distance_ly",
}


def _number(value: Any) -> float | None:
    return float(value) if value is not None else None


def _planet(row: dict[str, Any]) -> Planet:
    values = {
        "planet_id": int(row["planet_id"]),
        "name": row["planet_name"],
        "system_id": int(row["system_id"]),
        "system_name": row["system_name"],
        "discovery_id": int(row["discovery_id"]) if row.get("discovery_id") is not None else None,
        "radius_earth": _number(row.get("radius_earth")),
        "mass_earth": _number(row.get("mass_earth")),
        "density": _number(row.get("planet_density")),
        "temperature_k": _number(row.get("planet_temp")),
        "orbit_au": _number(row.get("orbit_radius")),
        "orbital_period_days": _number(row.get("orbital_period")),
        "eccentricity": _number(row.get("eccentricity")),
        "insolation_flux": _number(row.get("insolation_flux")),
        "discovery_year": row.get("discovery_year"),
        "discovery_method": row.get("discovery_method"),
        "constellation_name": row.get("constellation_name"),
        "star_temperature_k": _number(row.get("star_temp")),
        "star_radius_solar": _number(row.get("star_radius")),
        "star_mass_solar": _number(row.get("star_mass")),
        "star_luminosity_log10": _number(row.get("star_luminosity")),
    }
    builder = PlanetBuilder()
    for field, value in values.items():
        builder.set(field, value)
    return builder.build()


class MySQLPlanetRepository:
    def __init__(self, connection_factory: ConnectionFactory = create_connection) -> None:
        self._connection_factory = connection_factory

    def list(self, *, query: str | None, constellation: str | None, method: str | None,
             sort_by: str, order: str, page: int, limit: int) -> tuple[list[Planet], int]:
        conditions, parameters = self._filters(query, constellation, method)
        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        count = self._count(where, parameters)
        sort_column = PLANET_SORT_COLUMNS[sort_by]
        direction = "DESC" if order == "desc" else "ASC"
        sql = f"""
            {PLANET_SELECT}
            {where}
            ORDER BY {sort_column} IS NULL, {sort_column} {direction}, p.planet_id
            LIMIT %s OFFSET %s
        """
        rows = self._fetch(sql, parameters + [limit, (page - 1) * limit])
        return [_planet(row) for row in rows], count

    def list_for_esi(self, *, query: str | None, constellation: str | None,
                     method: str | None) -> tuple[list[Planet], int]:
        conditions, parameters = self._filters(query, constellation, method)
        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        rows = self._fetch(f"{PLANET_SELECT} {where} ORDER BY p.planet_id", parameters)
        return [_planet(row) for row in rows], len(rows)

    def find_by_id(self, planet_id: int) -> Planet | None:
        rows = self._fetch(f"{PLANET_SELECT} WHERE p.planet_id = %s", [planet_id])
        return _planet(rows[0]) if rows else None

    def find_by_ids(self, planet_ids: list[int]) -> list[Planet]:
        if not planet_ids:
            return []
        placeholders = ", ".join(["%s"] * len(planet_ids))
        rows = self._fetch(
            f"{PLANET_SELECT} WHERE p.planet_id IN ({placeholders})",
            planet_ids,
        )
        return [_planet(row) for row in rows]

    def find_by_ids_for_system(self, system_id: int) -> list[Planet]:
        rows = self._fetch(
            f"{PLANET_SELECT} WHERE p.system_id = %s ORDER BY p.orbital_period IS NULL, p.orbital_period",
            [system_id],
        )
        return [_planet(row) for row in rows]

    def all_for_analytics(self) -> list[Planet]:
        rows = self._fetch(f"{PLANET_SELECT} ORDER BY p.planet_id", [])
        return [_planet(row) for row in rows]

    def discovery_methods(self) -> list[str]:
        rows = self._fetch(
            "SELECT DISTINCT discovery_method FROM discovery "
            "WHERE discovery_method IS NOT NULL ORDER BY discovery_method",
            [],
        )
        return [row["discovery_method"] for row in rows]

    def create(self, planet: Planet) -> Planet:
        connection = self._connection_factory()
        cursor = connection.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO planet (
                    planet_name, system_id, discovery_id, is_circumbinary, orbital_period, orbit_radius,
                    radius_earth, mass_earth, planet_density, eccentricity, insolation_flux,
                    planet_temp, ttv_obs
                ) VALUES (%s, %s, %s, 0, %s, %s, %s, %s, %s, %s, %s, %s, 0)
                """,
                (
                    planet.name, planet.system_id, planet.discovery_id,
                    planet.orbital_period_days, planet.orbit_au,
                    planet.radius_earth, planet.mass_earth, planet.density, planet.eccentricity,
                    planet.insolation_flux, planet.temperature_k,
                ),
            )
            planet_id = int(cursor.lastrowid)
            connection.commit()
        finally:
            cursor.close()
            connection.close()
        created = self.find_by_id(planet_id)
        if created is None:
            raise RuntimeError(f"Planet {planet_id} was inserted but could not be reloaded.")
        return created

    def update(self, planet_id: int, changes: dict[str, Any]) -> Planet | None:
        columns = {
            "name": "planet_name",
            "radius_earth": "radius_earth",
            "mass_earth": "mass_earth",
            "density": "planet_density",
            "temperature_k": "planet_temp",
            "orbit_au": "orbit_radius",
            "orbital_period_days": "orbital_period",
            "eccentricity": "eccentricity",
            "insolation_flux": "insolation_flux",
        }
        updates = [(columns[key], value) for key, value in changes.items() if key in columns]
        if not updates:
            return self.find_by_id(planet_id)
        connection = self._connection_factory()
        cursor = connection.cursor()
        try:
            assignments = ", ".join(f"{column} = %s" for column, _ in updates)
            cursor.execute(
                f"UPDATE planet SET {assignments} WHERE planet_id = %s",
                [value for _, value in updates] + [planet_id],
            )
            connection.commit()
        finally:
            cursor.close()
            connection.close()
        return self.find_by_id(planet_id)

    def delete(self, planet_id: int) -> bool:
        connection = self._connection_factory()
        cursor = connection.cursor()
        try:
            cursor.execute("DELETE FROM planet WHERE planet_id = %s", [planet_id])
            deleted = cursor.rowcount > 0
            connection.commit()
            return deleted
        finally:
            cursor.close()
            connection.close()

    def _filters(self, query: str | None, constellation: str | None,
                 method: str | None) -> tuple[list[str], list[Any]]:
        conditions: list[str] = []
        parameters: list[Any] = []
        if query:
            conditions.append("(p.planet_name LIKE %s OR s.system_name LIKE %s)")
            parameters.extend([f"%{query}%", f"%{query}%"])
        if constellation:
            conditions.append("c.constellation_name = %s")
            parameters.append(constellation)
        if method:
            conditions.append("d.discovery_method = %s")
            parameters.append(method)
        return conditions, parameters

    def _count(self, where: str, parameters: list[Any]) -> int:
        rows = self._fetch(
            f"""
            SELECT COUNT(*) AS total
            FROM planet p
            JOIN starsystem s ON s.system_id = p.system_id
            LEFT JOIN constellation c ON c.constellation_id = s.constellation_id
            LEFT JOIN discovery d ON d.discovery_id = p.discovery_id
            {where}
            """,
            parameters,
        )
        return int(rows[0]["total"])

    def _fetch(self, sql: str, parameters: list[Any]) -> list[dict[str, Any]]:
        connection = self._connection_factory()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(sql, parameters)
            return list(cursor.fetchall())
        finally:
            cursor.close()
            connection.close()


class MySQLStarSystemRepository:
    def __init__(self, connection_factory: ConnectionFactory = create_connection) -> None:
        self._connection_factory = connection_factory

    def list(self, *, query: str | None, constellation: str | None,
             page: int, limit: int) -> tuple[list[dict[str, Any]], int]:
        conditions: list[str] = []
        parameters: list[Any] = []
        if query:
            conditions.append("s.system_name LIKE %s")
            parameters.append(f"%{query}%")
        if constellation:
            conditions.append("c.constellation_name = %s")
            parameters.append(constellation)
        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        count_rows = self._fetch(
            f"""
            SELECT COUNT(*) AS total FROM starsystem s
            LEFT JOIN constellation c ON c.constellation_id = s.constellation_id
            {where}
            """,
            parameters,
        )
        rows = self._fetch(
            f"""
            SELECT s.system_id, s.system_name, s.ra, s.`dec`, s.distance_ly,
                   s.constellation_id,
                   c.constellation_name,
                   (SELECT COUNT(*) FROM planet p WHERE p.system_id = s.system_id) AS num_planets
            FROM starsystem s
            LEFT JOIN constellation c ON c.constellation_id = s.constellation_id
            {where}
            ORDER BY s.system_name
            LIMIT %s OFFSET %s
            """,
            parameters + [limit, (page - 1) * limit],
        )
        return rows, int(count_rows[0]["total"])

    def find_by_id(self, system_id: int) -> dict[str, Any] | None:
        rows = self._fetch(
            """
            SELECT s.system_id, s.system_name, s.ra, s.`dec`, s.distance_ly,
                   s.constellation_id,
                   c.constellation_name
            FROM starsystem s
            LEFT JOIN constellation c ON c.constellation_id = s.constellation_id
            WHERE s.system_id = %s
            """,
            [system_id],
        )
        return rows[0] if rows else None

    def stars_by_system(self, system_id: int) -> list[dict[str, Any]]:
        return self._fetch(
            """
            SELECT star_id, star_name, spectral_type, star_temp, star_radius,
                   star_mass, star_luminosity
            FROM star WHERE system_id = %s ORDER BY star_id
            """,
            [system_id],
        )

    def planet_count(self, system_id: int) -> int:
        rows = self._fetch("SELECT COUNT(*) AS total FROM planet WHERE system_id = %s", [system_id])
        return int(rows[0]["total"])

    def count(self) -> int:
        rows = self._fetch("SELECT COUNT(*) AS total FROM starsystem", [])
        return int(rows[0]["total"])

    def _fetch(self, sql: str, parameters: list[Any]) -> list[dict[str, Any]]:
        connection = self._connection_factory()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(sql, parameters)
            return list(cursor.fetchall())
        finally:
            cursor.close()
            connection.close()


class MySQLConstellationRepository:
    def __init__(self, connection_factory: ConnectionFactory = create_connection) -> None:
        self._connection_factory = connection_factory

    def list(self) -> list[dict[str, Any]]:
        connection = self._connection_factory()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT MIN(c.constellation_id) AS constellation_id, c.constellation_name,
                       COUNT(DISTINCT s.system_id) AS system_count
                FROM constellation c
                LEFT JOIN starsystem s ON s.constellation_id = c.constellation_id
                GROUP BY c.constellation_name
                ORDER BY c.constellation_name
                """
            )
            return list(cursor.fetchall())
        finally:
            cursor.close()
            connection.close()
