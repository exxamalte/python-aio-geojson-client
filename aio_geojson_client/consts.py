"""Constants."""
from typing import TypeVar

from .filter import GeoJsonFeedFilterDefinition

DEFAULT_REQUEST_TIMEOUT = 10

UPDATE_OK = 'OK'
UPDATE_OK_NO_DATA = 'OK_NO_DATA'
UPDATE_ERROR = 'ERROR'

T_FILTER_DEFINITION = TypeVar("T_FILTER_DEFINITION", bound=GeoJsonFeedFilterDefinition)
