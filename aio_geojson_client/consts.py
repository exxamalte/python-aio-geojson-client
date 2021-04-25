"""Constants."""
from typing import TypeVar

from .feed_entry import FeedEntry
from .filter_definition import GeoJsonFeedFilterDefinition

DEFAULT_REQUEST_TIMEOUT = 10

UPDATE_OK = "OK"
UPDATE_OK_NO_DATA = "OK_NO_DATA"
UPDATE_ERROR = "ERROR"

T_FILTER_DEFINITION = TypeVar("T_FILTER_DEFINITION", bound=GeoJsonFeedFilterDefinition)
T_FEED_ENTRY = TypeVar("T_FEED_ENTRY", bound=FeedEntry)
