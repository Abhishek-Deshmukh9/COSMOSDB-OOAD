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
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_methods=["GET", "POST", "PATCH", "DELETE"],
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
        logging.getLogger("cosmosdb.api").warning("Catalog constraint rejected a mutation: %s", error)
        return JSONResponse(status_code=409, content={"detail": "Catalog constraint conflict."})

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
        sort_by: Literal["name", "mass", "radius", "temperature", "distance", "esi"] = "name",
        order: Literal["asc", "desc"] = "asc",
        scoring: Literal["standard", "habitability"] = "standard",
    ) -> dict[str, Any]:
        service = weighted_planets if scoring == "habitability" else standard_planets
        return service.browse(
            query=q, constellation=constellation, method=method,
            sort_by=sort_by, order=order, page=page, limit=limit,
        )

    @app.get("/api/discovery-methods")
    def list_discovery_methods() -> list[str]:
        return standard_planets.discovery_methods()

    @app.get("/api/planets/compare")
    def compare_planets(planet_ids: list[int] = Query(...)) -> list[dict[str, Any]]:
        return standard_planets.compare(planet_ids)

    @app.get("/api/planets/{planet_id}")
    def get_planet(planet_id: int) -> dict[str, Any]:
        return standard_planets.get(planet_id)

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

    return app


app = create_app()
