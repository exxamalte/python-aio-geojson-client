"""GeoJSON Feed."""
import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from json import JSONDecodeError
from typing import Dict, Generic, List, Optional, Tuple, TypeVar

import aiohttp
import geojson
from aiohttp import ClientSession, client_exceptions
from geojson import FeatureCollection

from .consts import (DEFAULT_REQUEST_TIMEOUT, UPDATE_ERROR, UPDATE_OK,
                     UPDATE_OK_NO_DATA)
from .feed_entry import FeedEntry

_LOGGER = logging.getLogger(__name__)

T_FEED_ENTRY = TypeVar("T_FEED_ENTRY", bound=FeedEntry)


class GeoJsonFeed(Generic[T_FEED_ENTRY], ABC):
    """Geo JSON feed base class."""

    def __init__(self,
                 websession: ClientSession,
                 home_coordinates: Tuple[float, float],
                 url: str,
                 filter_radius: float = None):
        """Initialise this service."""
        self._websession = websession
        self._home_coordinates = home_coordinates
        self._filter_radius = filter_radius
        self._url = url
        self._last_timestamp = None

    def __repr__(self):
        """Return string representation of this feed."""
        return '<{}(home={}, url={}, radius={})>'.format(
            self.__class__.__name__, self._home_coordinates, self._url,
            self._filter_radius)

    @abstractmethod
    def _new_entry(self,
                   home_coordinates: Tuple[float, float],
                   feature,
                   global_data: Dict) -> T_FEED_ENTRY:
        """Generate a new entry."""
        pass

    def _client_session_timeout(self) -> int:
        """Define client session timeout in seconds. Override if necessary."""
        return DEFAULT_REQUEST_TIMEOUT

    async def update(self) -> Tuple[str, Optional[List[T_FEED_ENTRY]]]:
        """Update from external source and return filtered entries."""
        status, data = await self._fetch()
        if status == UPDATE_OK:
            if data:
                entries = []
                global_data = self._extract_from_feed(data)
                # Extract data from feed entries.
                for feature in data.features:
                    entries.append(self._new_entry(self._home_coordinates,
                                                   feature, global_data))
                filtered_entries = self._filter_entries(entries)
                self._last_timestamp = self._extract_last_timestamp(
                    filtered_entries)
                return UPDATE_OK, filtered_entries
            else:
                # Should not happen.
                return UPDATE_OK, None
        elif status == UPDATE_OK_NO_DATA:
            # Happens for example if the server returns 304
            return UPDATE_OK_NO_DATA, None
        else:
            # Error happened while fetching the feed.
            self._last_timestamp = None
            return UPDATE_ERROR, None

    async def _fetch(self,
                     method: str = "GET",
                     headers=None,
                     params=None) -> Tuple[str, Optional[FeatureCollection]]:
        """Fetch GeoJSON data from external source."""
        try:
            timeout = aiohttp.ClientTimeout(
                total=self._client_session_timeout())
            async with self._websession.request(
                    method, self._url, headers=headers, params=params,
                    timeout=timeout
            ) as response:
                try:
                    response.raise_for_status()
                    text = await response.text()
                    feature_collection = geojson.loads(text)
                    return UPDATE_OK, feature_collection
                except client_exceptions.ClientError as client_error:
                    _LOGGER.warning("Fetching data from %s failed with %s",
                                    self._url, client_error)
                    return UPDATE_ERROR, None
                except JSONDecodeError as decode_ex:
                    _LOGGER.warning("Unable to parse JSON from %s: %s",
                                    self._url, decode_ex)
                    return UPDATE_ERROR, None
        except client_exceptions.ClientError as client_error:
            _LOGGER.warning("Requesting data from %s failed with "
                            "client error: %s",
                            self._url, client_error)
            return UPDATE_ERROR, None
        except asyncio.TimeoutError:
            _LOGGER.warning("Requesting data from %s failed with "
                            "timeout error", self._url)
            return UPDATE_ERROR, None

    def _filter_entries(self,
                        entries: List[T_FEED_ENTRY]) -> List[T_FEED_ENTRY]:
        """Filter the provided entries."""
        filtered_entries = entries
        _LOGGER.debug("Entries before filtering %s", filtered_entries)
        # Always remove entries without geometry
        filtered_entries = list(
            filter(lambda entry:
                   entry.geometries is not None and len(entry.geometries) >= 1,
                   filtered_entries))
        # Filter by distance.
        if self._filter_radius:
            filtered_entries = list(
                filter(lambda entry:
                       entry.distance_to_home <= self._filter_radius,
                       filtered_entries))
        _LOGGER.debug("Entries after filtering %s", filtered_entries)
        return filtered_entries

    @abstractmethod
    def _extract_from_feed(self, feed: FeatureCollection) -> Optional[Dict]:
        """Extract global metadata from feed."""
        return None

    @abstractmethod
    def _extract_last_timestamp(
            self, feed_entries: List[T_FEED_ENTRY]) -> Optional[datetime]:
        """Determine latest (newest) entry from the filtered feed."""
        return None

    @property
    def last_timestamp(self) -> Optional[datetime]:
        """Return the last timestamp extracted from this feed."""
        return self._last_timestamp
