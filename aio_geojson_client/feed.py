"""GeoJSON Feed."""

from __future__ import annotations

from abc import ABC, abstractmethod
import asyncio
from collections.abc import Callable
from datetime import datetime
import logging
from typing import Generic

import aiohttp
from aiohttp import ClientSession, client_exceptions
import geojson
from geojson import Feature, FeatureCollection

from .consts import (
    DEFAULT_REQUEST_TIMEOUT,
    T_FEED_ENTRY,
    T_FILTER_DEFINITION,
    UPDATE_ERROR,
    UPDATE_OK,
    UPDATE_OK_NO_DATA,
)

_LOGGER = logging.getLogger(__name__)


class GeoJsonFeed(Generic[T_FEED_ENTRY], ABC):
    """Geo JSON feed base class."""

    def __init__(
        self,
        websession: ClientSession,
        home_coordinates: tuple[float, float],
        url: str,
        filter_radius: float | None = None,
    ):
        """Initialise this service."""
        self._websession = websession
        self._home_coordinates = home_coordinates
        self._filter_radius = filter_radius
        self._url = url
        self._last_timestamp = None

    def __repr__(self):
        """Return string representation of this feed."""
        return f"<{self.__class__.__name__}(home={self._home_coordinates}, url={self._url}, radius={self._filter_radius})>"

    @abstractmethod
    def _new_entry(
        self, home_coordinates: tuple[float, float], feature, global_data: dict
    ) -> T_FEED_ENTRY:
        """Generate a new entry."""

    def _client_session_timeout(self) -> int:
        """Define client session timeout in seconds. Override if necessary."""
        return DEFAULT_REQUEST_TIMEOUT

    async def _update_internal(
        self, filter_function: Callable[[list[T_FEED_ENTRY]], list[T_FEED_ENTRY]]
    ) -> tuple[str, list[T_FEED_ENTRY] | None]:
        """Update from external source and return filtered entries."""
        status, data = await self._fetch()
        if status == UPDATE_OK:
            if data:
                entries: list = []
                global_data = self._extract_from_feed(data)
                # Extract data from feed entries.
                if type(data) is Feature:
                    entries.append(
                        self._new_entry(self._home_coordinates, data, global_data)
                    )
                elif type(data) is FeatureCollection:
                    entries = [
                        self._new_entry(self._home_coordinates, feature, global_data)
                        for feature in data.features
                    ]
                else:
                    _LOGGER.warning("Unsupported GeoJSON object found: %s", type(data))
                filtered_entries = filter_function(entries)
                self._last_timestamp = self._extract_last_timestamp(filtered_entries)
                return UPDATE_OK, filtered_entries
            # Should not happen.
            return UPDATE_OK, None
        if status == UPDATE_OK_NO_DATA:
            # Happens for example if the server returns 304
            return UPDATE_OK_NO_DATA, None
        # Error happened while fetching the feed.
        self._last_timestamp = None
        return UPDATE_ERROR, None

    async def update(self) -> tuple[str, list[T_FEED_ENTRY] | None]:
        """Update from external source and return filtered entries."""
        return await self._update_internal(
            lambda entries: self._filter_entries(entries)
        )

    async def update_override(
        self, filter_overrides: T_FILTER_DEFINITION = None
    ) -> tuple[str, list[T_FEED_ENTRY] | None]:
        """Update from external source and return filtered entries with ability to override filter conditions."""
        return await self._update_internal(
            lambda entries: self._filter_entries_override(
                entries, filter_overrides=filter_overrides
            )
        )

    async def _fetch(
        self, method: str = "GET", headers=None, params=None
    ) -> tuple[str, FeatureCollection | None]:
        """Fetch GeoJSON data from external source."""
        try:
            timeout = aiohttp.ClientTimeout(total=self._client_session_timeout())
            async with self._websession.request(
                method, self._url, headers=headers, params=params, timeout=timeout
            ) as response:
                try:
                    response.raise_for_status()
                    text = await response.text()
                    feature_collection = geojson.loads(text)
                    return UPDATE_OK, feature_collection
                except client_exceptions.ClientError as client_error:
                    _LOGGER.warning(
                        "Fetching data from %s failed with %s", self._url, client_error
                    )
                    return UPDATE_ERROR, None
                except ValueError as value_ex:
                    _LOGGER.warning(
                        "Unable to parse JSON from %s: %s", self._url, value_ex
                    )
                    return UPDATE_ERROR, None
        except client_exceptions.ClientError as client_error:
            _LOGGER.warning(
                "Requesting data from %s failed with " "client error: %s",
                self._url,
                client_error,
            )
            return UPDATE_ERROR, None
        except asyncio.TimeoutError:
            _LOGGER.warning(
                "Requesting data from %s failed with " "timeout error", self._url
            )
            return UPDATE_ERROR, None

    def _filter_entries(self, entries: list[T_FEED_ENTRY]) -> list[T_FEED_ENTRY]:
        """Filter the provided entries (for backwards-compatibility)."""
        return self._filter_entries_override(entries, None)

    def _filter_entries_override(
        self, entries: list[T_FEED_ENTRY], filter_overrides: T_FILTER_DEFINITION = None
    ) -> list[T_FEED_ENTRY]:
        """Filter the provided entries with ability to override filter definitions."""
        filtered_entries = entries
        _LOGGER.debug("Entries before filtering %s", filtered_entries)
        # Always remove entries without geometry
        filtered_entries = list(
            filter(
                lambda entry: entry.geometries is not None
                and len(entry.geometries) >= 1,
                filtered_entries,
            )
        )
        # Filter by distance.
        filter_radius = (
            filter_overrides.radius
            if filter_overrides and filter_overrides.radius
            else self._filter_radius
        )
        if filter_radius:
            filtered_entries = list(
                filter(
                    lambda entry: entry.distance_to_home <= filter_radius,
                    filtered_entries,
                )
            )
        _LOGGER.debug("Entries after filtering %s", filtered_entries)
        return filtered_entries

    @abstractmethod
    def _extract_from_feed(self, feed: FeatureCollection) -> dict | None:
        """Extract global metadata from feed."""
        return None

    @abstractmethod
    def _extract_last_timestamp(
        self, feed_entries: list[T_FEED_ENTRY]
    ) -> datetime | None:
        """Determine latest (newest) entry from the filtered feed."""
        return None

    @property
    def last_timestamp(self) -> datetime | None:
        """Return the last timestamp extracted from this feed."""
        return self._last_timestamp
