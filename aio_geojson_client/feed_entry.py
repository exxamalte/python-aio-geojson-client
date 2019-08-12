"""
Feed Entry.
"""
from abc import abstractmethod, ABC
from typing import Optional

from .geojson_distance_helper import GeoJsonDistanceHelper


class FeedEntry(ABC):
    """Feed entry base class."""

    def __init__(self, home_coordinates, feature):
        """Initialise this feed entry."""
        self._home_coordinates = home_coordinates
        self._feature = feature

    def __repr__(self):
        """Return string representation of this entry."""
        return '<{}(id={})>'.format(self.__class__.__name__, self.external_id)

    @property
    def geometry(self):
        """Return all geometry details of this entry."""
        if self._feature:
            return self._feature.geometry
        return None

    @property
    def coordinates(self):
        """Return the best coordinates (latitude, longitude) of this entry."""
        if self.geometry:
            return GeoJsonDistanceHelper.extract_coordinates(self.geometry)
        return None

    @property
    @abstractmethod
    def title(self) -> Optional[str]:
        """Return the title of this entry."""
        return None

    @property
    @abstractmethod
    def external_id(self) -> Optional[str]:
        """Return the external id of this entry."""
        return None

    @property
    def attribution(self) -> Optional[str]:
        """Return the attribution of this entry."""
        return None

    @property
    def distance_to_home(self) -> Optional[float]:
        """Return the distance in km of this entry to the home coordinates."""
        return GeoJsonDistanceHelper.distance_to_geometry(
            self._home_coordinates, self.geometry)

    def _search_in_feature(self, name):
        """Find an attribute in the feature object."""
        if self._feature and name in self._feature:
            return self._feature[name]
        return None

    def _search_in_properties(self, name):
        """Find an attribute in the feed entry's properties."""
        if self._feature and self._feature.properties \
                and name in self._feature.properties:
            return self._feature.properties[name]
        return None
