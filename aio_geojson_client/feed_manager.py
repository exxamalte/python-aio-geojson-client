"""Base class for the feed manager. This allows managing feeds and their entries throughout their life-cycle."""
import logging
from datetime import datetime
from typing import Awaitable, Callable, List, Optional, Set

from .consts import T_FEED_ENTRY, T_FILTER_DEFINITION, UPDATE_OK, UPDATE_OK_NO_DATA
from .feed import GeoJsonFeed
from .feed_entry import FeedEntry
from .status_update import StatusUpdate

_LOGGER = logging.getLogger(__name__)


class FeedManagerBase:
    """Generic Feed manager."""

    def __init__(
        self,
        feed: GeoJsonFeed,
        generate_async_callback: Callable[[str], Awaitable[None]],
        update_async_callback: Callable[[str], Awaitable[None]],
        remove_async_callback: Callable[[str], Awaitable[None]],
        status_async_callback: Callable[[StatusUpdate], Awaitable[None]] = None,
    ):
        """Initialise feed manager."""
        self._feed = feed
        self.feed_entries = {}
        self._managed_external_ids = set()
        self._last_update = None
        self._last_update_successful = None
        self._generate_async_callback = generate_async_callback
        self._update_async_callback = update_async_callback
        self._remove_async_callback = remove_async_callback
        self._status_async_callback = status_async_callback

    def __repr__(self):
        """Return string representation of this feed."""
        return "<{}(feed={})>".format(self.__class__.__name__, self._feed)

    async def _update_internal(
        self, status: str, feed_entries: Optional[List[T_FEED_ENTRY]]
    ):
        """Update the feed and then update connected entities."""
        # Record current time of update.
        self._last_update = datetime.now()
        count_created = 0
        count_updated = 0
        count_removed = 0
        await self._store_feed_entries(status, feed_entries)
        if status == UPDATE_OK:
            _LOGGER.debug("Data retrieved %s", feed_entries)
            # Record current time of update.
            self._last_update_successful = self._last_update
            # For entity management the external ids from the feed are used.
            feed_external_ids = set([entry.external_id for entry in feed_entries])
            count_removed = await self._update_feed_remove_entries(feed_external_ids)
            count_updated = await self._update_feed_update_entries(feed_external_ids)
            count_created = await self._update_feed_create_entries(feed_external_ids)
        elif status == UPDATE_OK_NO_DATA:
            _LOGGER.debug("Update successful, but no data received from %s", self._feed)
            # Record current time of update.
            self._last_update_successful = self._last_update
        else:
            _LOGGER.warning(
                "Update not successful, no data received from %s", self._feed
            )
            # Remove all entities.
            count_removed = await self._update_feed_remove_entries(set())
        # Send status update to subscriber.
        await self._status_update(status, count_created, count_updated, count_removed)

    async def update(self):
        """Update the feed and then update connected entities."""
        status, feed_entries = await self._feed.update()
        await self._update_internal(status, feed_entries)

    async def update_override(self, filter_overrides: T_FILTER_DEFINITION = None):
        """Update the feed and then update connected entities."""
        status, feed_entries = await self._feed.update_override(
            filter_overrides=filter_overrides
        )
        await self._update_internal(status, feed_entries)

    async def _store_feed_entries(
        self, status: str, feed_entries: Optional[List[FeedEntry]]
    ):
        """Keep a copy of all feed entries for future lookups."""
        if feed_entries or status == UPDATE_OK_NO_DATA:
            if status == UPDATE_OK:
                self.feed_entries = {entry.external_id: entry for entry in feed_entries}
        else:
            self.feed_entries.clear()

    async def _update_feed_create_entries(self, feed_external_ids: Set[str]) -> int:
        """Create entities after feed update."""
        create_external_ids = feed_external_ids.difference(self._managed_external_ids)
        count_created = len(create_external_ids)
        await self._generate_new_entities(create_external_ids)
        return count_created

    async def _update_feed_update_entries(self, feed_external_ids: Set[str]) -> int:
        """Update entities after feed update."""
        update_external_ids = self._managed_external_ids.intersection(feed_external_ids)
        count_updated = len(update_external_ids)
        await self._update_entities(update_external_ids)
        return count_updated

    async def _update_feed_remove_entries(self, feed_external_ids: Set[str]) -> int:
        """Remove entities after feed update."""
        remove_external_ids = self._managed_external_ids.difference(feed_external_ids)
        count_removed = len(remove_external_ids)
        await self._remove_entities(remove_external_ids)
        return count_removed

    async def _generate_new_entities(self, external_ids: Set[str]):
        """Generate new entities for events using callback."""
        for external_id in external_ids:
            await self._generate_async_callback(external_id)
            _LOGGER.debug("New entity added %s", external_id)
            self._managed_external_ids.add(external_id)

    async def _update_entities(self, external_ids: Set[str]):
        """Update entities using callback."""
        for external_id in external_ids:
            _LOGGER.debug("Existing entity found %s", external_id)
            await self._update_async_callback(external_id)

    async def _remove_entities(self, external_ids: Set[str]):
        """Remove entities using callback."""
        for external_id in external_ids:
            _LOGGER.debug("Entity not current anymore %s", external_id)
            self._managed_external_ids.remove(external_id)
            await self._remove_async_callback(external_id)

    async def _status_update(
        self, status: str, count_created: int, count_updated: int, count_removed: int
    ):
        """Provide status update."""
        if self._status_async_callback:
            await self._status_async_callback(
                StatusUpdate(
                    status,
                    self.last_update,
                    self.last_update_successful,
                    self.last_timestamp,
                    len(self.feed_entries),
                    count_created,
                    count_updated,
                    count_removed,
                )
            )

    @property
    def last_timestamp(self) -> Optional[datetime]:
        """Return the last timestamp extracted from this feed."""
        return self._feed.last_timestamp

    @property
    def last_update(self) -> Optional[datetime]:
        """Return the last update of this feed."""
        return self._last_update

    @property
    def last_update_successful(self) -> Optional[datetime]:
        """Return the last successful update of this feed."""
        return self._last_update_successful
