"""Tests for aio-geojson-client library."""
from datetime import datetime
from typing import Optional

from aio_geojson_client.feed import GeoJsonFeed
from aio_geojson_client.feed_entry import FeedEntry

ATTR_GUID = 'guid'
ATTR_ID = 'id'
ATTR_TITLE = 'title'


class MockGeoJsonFeed(GeoJsonFeed):

    def _extract_from_feed(self, feed) -> Optional:
        return None

    def _extract_last_timestamp(self, feed_entries) -> Optional[datetime]:
        return None

    def _new_entry(self, home_coordinates, feature, global_data):
        """Generate a new entry."""
        return MockFeedEntry(home_coordinates, feature)


class MockSimpleFeedEntry(FeedEntry):

    @property
    def title(self) -> Optional[str]:
        return "mock title"

    @property
    def external_id(self) -> Optional[str]:
        return "mock id"


class MockFeedEntry(FeedEntry):
    """Generic feed entry."""

    def __init__(self, home_coordinates, feature):
        """Initialise this service."""
        super().__init__(home_coordinates, feature)

    @property
    def title(self) -> str:
        """Return the title of this entry."""
        return self._search_in_properties(ATTR_TITLE)

    @property
    def external_id(self) -> str:
        """Return the external id of this entry."""
        """Find a suitable ID for the provided entry."""
        external_id = self._search_in_feature(ATTR_ID)
        if not external_id:
            external_id = self._search_in_properties(ATTR_ID)
        if not external_id:
            external_id = self._search_in_properties(ATTR_GUID)
        if not external_id:
            external_id = self.title
        if not external_id:
            # Use geometry as ID as a fallback.
            external_id = hash(self.coordinates)
        return external_id
