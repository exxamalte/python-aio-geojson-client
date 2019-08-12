"""
GeoJSON Feed.
"""
import logging
from datetime import datetime
from json import JSONDecodeError
from typing import Optional

import geojson
from aiohttp import ClientSession, client_exceptions

from .consts import UPDATE_OK, UPDATE_OK_NO_DATA, UPDATE_ERROR

_LOGGER = logging.getLogger(__name__)


class GeoJsonFeed:
    """Geo JSON feed base class."""

    def __init__(self, websession: ClientSession,
                 home_coordinates, url: str, filter_radius: float = None):
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

    def _new_entry(self, home_coordinates, feature, global_data):
        """Generate a new entry."""
        pass

    async def update(self):
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

    async def _fetch(self, method: str = "GET", headers=None, params=None):
        """Fetch GeoJSON data from external source."""
        try:
            async with self._websession.request(
                    method, self._url, headers=headers, params=params
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
            _LOGGER.warning("Requesting data from %s failed with %s",
                            self._url, client_error)
            return UPDATE_ERROR, None

    def _filter_entries(self, entries):
        """Filter the provided entries."""
        filtered_entries = entries
        # Always remove entries without geometry
        filtered_entries = list(
            filter(lambda entry:
                   entry.geometry is not None,
                   filtered_entries))
        # Filter by distance.
        if self._filter_radius:
            filtered_entries = list(
                filter(lambda entry:
                       entry.distance_to_home <= self._filter_radius,
                       filtered_entries))
        return filtered_entries

    def _extract_from_feed(self, feed):
        """Extract global metadata from feed."""
        return None

    def _extract_last_timestamp(self, feed_entries):
        """Determine latest (newest) entry from the filtered feed."""
        return None

    @property
    def last_timestamp(self) -> Optional[datetime]:
        """Return the last timestamp extracted from this feed."""
        return self._last_timestamp
