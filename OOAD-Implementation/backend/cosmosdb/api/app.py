from __future__ import annotations

import logging
from typing import Any, Literal

import mysql.connector
from mysql.connector.errors import IntegrityError
from fastapi import FastAPI, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from cosmosdb.application.events import (
    AnalyticsCacheObserver,
    CatalogAuditLogObserver,
    CatalogEventPublisher,
)
from cosmosdb.application.ports import IConstellationRepository, IPlanetRepository, IStarSystemRepository
from cosmosdb.application.services import (
    AnalyticsService,
    ConstellationCatalogService,
    NotFoundError,
    PlanetCatalogService,
    StarSystemCatalogService,
)
from cosmosdb.domain.esi import ESICalculator, HabitabilityWeightedStrategy
from cosmosdb.infrastructure.mysql import (
    MySQLConstellationRepository,
    MySQLPlanetRepository,
    MySQLStarSystemRepository,
)


class PlanetCreateRequest(BaseModel):
    planet_name: str = Field(min_length=1, max_length=255)
    system_id: int = Field(gt=0)
    discovery_id: int | None = Field(default=None, gt=0)
    radius_earth: float | None = Field(default=None, gt=0)
    mass_earth: float | None = Field(default=None, gt=0)
    planet_density: float | None = Field(default=None, gt=0)
    planet_temp: float | None = Field(default=None, gt=0)
    orbit_radius: float | None = Field(default=None, gt=0)
    orbital_period: float | None = Field(default=None, gt=0)
    eccentricity: float | None = Field(default=None, ge=0, le=0.95)
    insolation_flux: float | None = Field(default=None, gt=0)


class PlanetUpdateRequest(BaseModel):
    planet_name: str | None = Field(default=None, min_length=1, max_length=255)
    radius_earth: float | None = Field(default=None, gt=0)
    mass_earth: float | None = Field(default=None, gt=0)
    planet_density: float | None = Field(default=None, gt=0)
    planet_temp: float | None = Field(default=None, gt=0)
    orbit_radius: float | None = Field(default=None, gt=0)
    orbital_period: float | None = Field(default=None, gt=0)
    eccentricity: float | None = Field(default=None, ge=0, le=0.95)
    insolation_flux: float | None = Field(default=None, gt=0)


def create_app(
    planet_repository: IPlanetRepository | None = None,
    system_repository: IStarSystemRepository | None = None,
    constellation_repository: IConstellationRepository | None = None,
) -> FastAPI:
    planet_repository = planet_repository or MySQLPlanetRepository()
    system_repository = system_repository or MySQLStarSystemRepository()
    constellation_repository = constellation_repository or MySQLConstellationRepository()
    events = CatalogEventPublisher()
    analytics = AnalyticsService(planet_repository, system_repository)
    events.subscribe(AnalyticsCacheObserver(analytics.invalidate))
    events.subscribe(CatalogAuditLogObserver())

    standard_planets = PlanetCatalogService(
        planet_repository, ESICalculator(), events, system_repository
    )
    weighted_planets = PlanetCatalogService(
        planet_repository, ESICalculator(HabitabilityWeightedStrategy()), events, system_repository
    )
    systems = StarSystemCatalogService(system_repository, planet_repository)
    constellations = ConstellationCatalogService(constellation_repository)

    app = FastAPI(title="COSMODB-OOAD API", version="1.0.0")
    app.state.services = {
        "planets": standard_planets,
        "weighted_planets": weighted_planets,
        "systems": systems,
        "constellations": constellations,
        "analytics": analytics,
    }
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
        ],
        allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:[0-9]+)?$",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(NotFoundError)
    async def not_found_handler(_request: Any, error: NotFoundError) -> Response:
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=404, content={"detail": str(error)})

    @app.exception_handler(ValueError)
    async def invalid_input_handler(_request: Any, error: ValueError) -> Response:
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=422, content={"detail": str(error)})

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(_request: Any, error: IntegrityError) -> Response:
        from fastapi.responses import JSONResponse
        err_msg = str(error)
        logging.getLogger("cosmosdb.api").warning("Catalog constraint rejected a mutation: %s", err_msg)
        if "Duplicate entry" in err_msg:
            if "planet_name" in err_msg:
                detail = "A planet with this name already exists in the catalog. Please choose a unique name."
            elif "system_name" in err_msg:
                detail = "A star system with this name already exists. Please choose a different system name or select the existing system."
            elif "star_name" in err_msg:
                detail = "A star with this name already exists in the catalog."
            else:
                detail = f"Catalog unique constraint conflict: duplicate entry."
        elif "foreign key constraint" in err_msg.lower():
            detail = "Referenced catalog entity does not exist."
        else:
            detail = "Catalog constraint conflict."
        return JSONResponse(status_code=409, content={"detail": detail})

    @app.exception_handler(mysql.connector.Error)
    async def database_error_handler(_request: Any, error: mysql.connector.Error) -> Response:
        from fastapi.responses import JSONResponse
        logging.getLogger("cosmosdb.api").error(
            "Database operation failed",
            exc_info=(type(error), error, error.__traceback__),
        )
        return JSONResponse(status_code=503, content={"detail": "Catalog database is unavailable."})

    @app.get("/api/constellations")
    def list_constellations() -> list[dict[str, Any]]:
        return constellations.list()

    @app.get("/api/systems")
    def list_systems(
        page: int = Query(1, ge=1),
        limit: int = Query(20, ge=1, le=100),
        q: str | None = Query(None, max_length=100),
        constellation: str | None = Query(None, max_length=100),
    ) -> dict[str, Any]:
        return systems.browse(query=q, constellation=constellation, page=page, limit=limit)

    @app.get("/api/systems/{system_id}")
    def get_system(system_id: int) -> dict[str, Any]:
        return systems.get(system_id)

    @app.get("/api/planets")
    def list_planets(
        page: int = Query(1, ge=1),
        limit: int = Query(50, ge=1, le=100),
        q: str | None = Query(None, max_length=100),
        constellation: str | None = Query(None, max_length=100),
        method: str | None = Query(None, max_length=100),
        filter_constellation: str | None = Query(None, max_length=100),
        filter_method: str | None = Query(None, max_length=100),
        sort_by: str = "name",
        order: Literal["asc", "desc"] = "asc",
        scoring: Literal["standard", "habitability"] = "standard",
    ) -> dict[str, Any]:
        c = constellation or filter_constellation
        m = method or filter_method
        service = weighted_planets if scoring == "habitability" else standard_planets
        return service.browse(
            query=q, constellation=c, method=m,
            sort_by=sort_by, order=order, page=page, limit=limit,
        )

    @app.get("/api/discovery-methods")
    @app.get("/api/discovery_methods")
    def list_discovery_methods() -> list[str]:
        return standard_planets.discovery_methods()

    @app.get("/api/planets/compare")
    def compare_planets(planet_ids: list[int] = Query(...)) -> list[dict[str, Any]]:
        return standard_planets.compare(planet_ids)

    @app.get("/api/planets/{planet_id}")
    @app.get("/api/planets/{planet_id}/details")
    def get_planet(planet_id: int) -> dict[str, Any]:
        return standard_planets.get(planet_id)

    @app.get("/api/search")
    def search_systems_alias(q: str = Query(...)) -> list[dict[str, Any]]:
        res = systems.browse(query=q, page=1, limit=20)
        return res.get("items", [])

    @app.post("/api/crud/planets", status_code=201)
    def create_planet_crud_alias(request: dict[str, Any]) -> dict[str, Any]:
        raw_name = request.get("planet_name") or request.get("name")
        if not raw_name or not str(raw_name).strip():
            raise ValueError("Target planet name is required.")
        name = str(raw_name).strip()

        mode = request.get("mode", "existing")
        sys_id = request.get("system_id")

        if mode == "new" or not sys_id:
            raw_sys_name = request.get("system_name")
            sys_name = str(raw_sys_name).strip() if raw_sys_name and str(raw_sys_name).strip() else f"{name} System"
            constellation_id = request.get("constellation_id")
            if constellation_id is not None and constellation_id != "":
                try:
                    constellation_id = int(constellation_id)
                except (ValueError, TypeError):
                    constellation_id = None
            else:
                constellation_id = None

            distance_ly = request.get("distance_ly")
            if distance_ly is not None and distance_ly != "":
                try:
                    distance_ly = float(distance_ly)
                except (ValueError, TypeError):
                    distance_ly = None
            else:
                distance_ly = None

            star_data = {
                "spectral_type": request.get("spectral_type") or "G",
                "star_temp": request.get("star_temp"),
                "star_radius": request.get("star_radius"),
                "star_mass": request.get("star_mass"),
                "star_metallicity": request.get("star_metallicity"),
                "star_luminosity": request.get("star_luminosity"),
                "star_gravity": request.get("star_gravity"),
                "star_age": request.get("star_age"),
                "star_brightness": request.get("star_brightness"),
            }
            sys_id = systems.create_or_ensure_system(
                system_name=sys_name,
                constellation_id=constellation_id,
                distance_ly=distance_ly,
                num_stars=int(request.get("num_stars") or 1),
                num_moons=int(request.get("num_moons") or 0),
                star_name=request.get("star_name") or sys_name,
                star_data=star_data,
            )
        else:
            sys_id = int(sys_id)

        field_map = {
            "radius_earth": "radius_earth",
            "mass_earth": "mass_earth",
            "planet_density": "density",
            "density": "density",
            "planet_temp": "temperature_k",
            "temperature_k": "temperature_k",
            "orbit_radius": "orbit_au",
            "orbit_au": "orbit_au",
            "orbital_period": "orbital_period_days",
            "orbital_period_days": "orbital_period_days",
            "eccentricity": "eccentricity",
            "insolation_flux": "insolation_flux",
        }
        values: dict[str, Any] = {
            "name": name,
            "system_id": sys_id,
        }
        for src, target in field_map.items():
            val = request.get(src)
            if val is not None and val != "":
                try:
                    values[target] = float(val)
                except (ValueError, TypeError):
                    continue

        return standard_planets.create(values)

    @app.put("/api/crud/planets/{planet_id}")
    def update_planet_crud_alias(planet_id: int, request: dict[str, Any]) -> dict[str, Any]:
        name_map = {
            "planet_name": "name",
            "name": "name",
            "planet_density": "density",
            "density": "density",
            "planet_temp": "temperature_k",
            "temperature_k": "temperature_k",
            "orbit_radius": "orbit_au",
            "orbit_au": "orbit_au",
            "orbital_period": "orbital_period_days",
            "orbital_period_days": "orbital_period_days",
            "radius_earth": "radius_earth",
            "mass_earth": "mass_earth",
            "eccentricity": "eccentricity",
            "insolation_flux": "insolation_flux",
        }
        clean: dict[str, Any] = {}
        for src, target in name_map.items():
            if src in request:
                val = request[src]
                if val is not None and val != "":
                    if target == "name":
                        clean[target] = str(val).strip()
                    else:
                        try:
                            clean[target] = float(val)
                        except (ValueError, TypeError):
                            continue

        return standard_planets.update(planet_id, clean) if clean else standard_planets.get(planet_id)

    @app.delete("/api/crud/planets/{planet_id}")
    def delete_planet_crud_alias(planet_id: int) -> dict[str, Any]:
        standard_planets.delete(planet_id)
        return {"status": "success"}

    @app.put("/api/crud/stars/{star_id}")
    def update_star_crud_alias(star_id: int, request: dict[str, Any]) -> dict[str, Any]:
        systems.update_star(star_id, request)
        return {"status": "success", "star_id": star_id}

    @app.put("/api/crud/systems/{system_id}")
    def update_system_crud_alias(system_id: int, request: dict[str, Any]) -> dict[str, Any]:
        systems.update_system(system_id, request)
        return {"status": "success", "system_id": system_id}

    @app.post("/api/admin/reset")
    def admin_reset_alias() -> dict[str, Any]:
        return {"status": "ok"}

    @app.post("/api/planets", status_code=201)
    def create_planet(request: PlanetCreateRequest) -> dict[str, Any]:
        values = request.model_dump()
        values["name"] = values.pop("planet_name")
        values["density"] = values.pop("planet_density")
        values["temperature_k"] = values.pop("planet_temp")
        values["orbit_au"] = values.pop("orbit_radius")
        values["orbital_period_days"] = values.pop("orbital_period")
        return standard_planets.create(values)

    @app.patch("/api/planets/{planet_id}")
    def update_planet(planet_id: int, request: PlanetUpdateRequest) -> dict[str, Any]:
        values = request.model_dump(exclude_unset=True)
        if not values:
            raise ValueError("Provide at least one planet field to update.")
        name_map = {
            "planet_name": "name",
            "planet_density": "density",
            "planet_temp": "temperature_k",
            "orbit_radius": "orbit_au",
            "orbital_period": "orbital_period_days",
        }
        return standard_planets.update(
            planet_id, {name_map.get(name, name): value for name, value in values.items()}
        )

    @app.delete("/api/planets/{planet_id}", status_code=204)
    def delete_planet(planet_id: int) -> Response:
        standard_planets.delete(planet_id)
        return Response(status_code=204)

    @app.get("/api/analytics/summary")
    def analytics_summary() -> dict[str, Any]:
        return analytics.summary()

    @app.get("/api/analytics/esi-distribution")
    def analytics_esi_distribution() -> list[dict[str, Any]]:
        return analytics.esi_distribution()

    @app.get("/api/analytics/discovery-timeline")
    def analytics_discovery_timeline() -> dict[str, Any]:
        return analytics.discovery_timeline()

    @app.get("/api/analytics/mass-radius-scatter")
    def analytics_mass_radius_scatter() -> list[dict[str, Any]]:
        return analytics.mass_radius_scatter()

    @app.get("/api/analytics/spectral-types")
    def analytics_spectral_types() -> list[dict[str, Any]]:
        return analytics.spectral_types()

    @app.get("/api/analytics/system-complexity")
    def analytics_system_complexity() -> list[dict[str, Any]]:
        return analytics.system_complexity()

    @app.get("/api/analytics/eccentricity-period")
    def analytics_eccentricity_period() -> list[dict[str, Any]]:
        return analytics.eccentricity_period()

    @app.get("/api/analytics/metallicity-planets")
    def analytics_metallicity_planets() -> list[dict[str, Any]]:
        return analytics.metallicity_planets()

    @app.get("/api/analytics/distance-histogram")
    def analytics_distance_histogram() -> dict[str, Any]:
        return analytics.distance_histogram()

    return app


app = create_app()
