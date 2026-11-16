from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Callable, Protocol


@dataclass(frozen=True)
class CatalogChanged:
    action: str
    planet_id: int


class ICatalogChangeListener(Protocol):
    def on_catalog_changed(self, event: CatalogChanged) -> None: ...


class CatalogEventPublisher:
    def __init__(self) -> None:
        self._listeners: list[ICatalogChangeListener] = []

    def subscribe(self, listener: ICatalogChangeListener) -> None:
        self._listeners.append(listener)

    def publish(self, event: CatalogChanged) -> None:
        for listener in self._listeners:
            listener.on_catalog_changed(event)


class AnalyticsCacheObserver:
    def __init__(self, invalidate: Callable[[], None]) -> None:
        self._invalidate = invalidate

    def on_catalog_changed(self, event: CatalogChanged) -> None:
        self._invalidate()


class CatalogAuditLogObserver:
    def on_catalog_changed(self, event: CatalogChanged) -> None:
        logging.getLogger("cosmosdb.catalog").info(
            "Planet catalog changed: action=%s planet_id=%s", event.action, event.planet_id
        )
