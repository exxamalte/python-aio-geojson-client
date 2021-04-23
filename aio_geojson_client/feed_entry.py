"""Feed Entry."""
import logging
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

import geojson
from geojson import Feature

from .geojson_distance_helper import GeoJsonDistanceHelper
from .geometries import Geometry, Point, Polygon

_LOGGER = logging.getLogger(__name__)


class FeedEntry(ABC):
    """Feed entry base class."""

    def __init__(self, home_coordinates: Tuple[float, float], feature: Feature):
        """Initialise this feed entry."""
        self._home_coordinates = home_coordinates
        self._feature = feature

    def __repr__(self):
        """Return string representation of this entry."""
        return "<{}(id={})>".format(self.__class__.__name__, self.external_id)

    @property
    def geometries(self) -> Optional[List[Geometry]]:
        """Return all geometry details of this entry."""
        if self._feature:
            return FeedEntry._wrap(self._feature.geometry)
        return None

    @staticmethod
    def _wrap(geometry: geojson.geometry.Geometry) -> Optional[List[Geometry]]:
        """Wrap data of the provided GeoJSON geometry."""
        if isinstance(geometry, geojson.geometry.Point):
            return [Point(geometry.coordinates[1], geometry.coordinates[0])]
        elif isinstance(geometry, geojson.geometry.GeometryCollection):
            result = []
            for entry in geometry.geometries:
                wrapped_geometry = FeedEntry._wrap(entry)
                if wrapped_geometry:
                    result += wrapped_geometry
            return result
        elif isinstance(geometry, geojson.geometry.Polygon):
            # Currently only support polygons without a hole
            # (https://tools.ietf.org/html/rfc7946#page-23).
            return [
                Polygon(
                    [
                        Point(coordinate[1], coordinate[0])
                        for coordinate in geometry.coordinates[0]
                    ]
                )
            ]
        else:
            _LOGGER.debug("Not implemented: %s", type(geometry))
            return None

    @property
    def coordinates(self) -> Optional[Tuple[float, float]]:
        """Return the best coordinates (latitude, longitude) of this entry."""
        # This looks for the first point in the list of geometries. If there
        # is no point then return the first entry.
        if self.geometries and len(self.geometries) >= 1:
            for entry in self.geometries:
                if isinstance(entry, Point):
                    return GeoJsonDistanceHelper.extract_coordinates(entry)
            # No point found.
            return GeoJsonDistanceHelper.extract_coordinates(self.geometries[0])
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
    def distance_to_home(self) -> float:
        """Return the distance in km of this entry to the home coordinates."""
        # This goes through all geometries and reports back the closest
        # distance to any of them.
        distance = float("inf")
        if self.geometries and len(self.geometries) >= 1:
            for geometry in self.geometries:
                distance = min(
                    distance,
                    GeoJsonDistanceHelper.distance_to_geometry(
                        self._home_coordinates, geometry
                    ),
                )
        return distance

    def _search_in_feature(self, name):
        """Find an attribute in the feature object."""
        if self._feature and name in self._feature:
            return self._feature[name]
        return None

    def _search_in_properties(self, name):
        """Find an attribute in the feed entry's properties."""
        if (
            self._feature
            and self._feature.properties
            and name in self._feature.properties
        ):
            return self._feature.properties[name]
        return None
