"""
GeoJSON distance helper.
"""
import logging

from geojson import Point, GeometryCollection, Polygon
from haversine import haversine

_LOGGER = logging.getLogger(__name__)


class GeoJsonDistanceHelper:
    """Helper to calculate distances between GeoJSON geometries."""

    def __init__(self):
        """Initialize the geo distance helper."""
        pass

    @staticmethod
    def extract_coordinates(geometry):
        """Extract the best coordinates from the feature for display."""
        latitude = longitude = None
        if isinstance(geometry, Point):
            # Just extract latitude and longitude directly.
            latitude, longitude = geometry.coordinates[1], \
                                  geometry.coordinates[0]
        elif isinstance(geometry, GeometryCollection):
            # Go through the collection, and extract the first suitable
            # geometry.
            for entry in geometry.geometries:
                latitude, longitude = \
                    GeoJsonDistanceHelper.extract_coordinates(entry)
                if latitude is not None and longitude is not None:
                    break
        elif isinstance(geometry, Polygon):
            # Find the polygon's centroid as a best approximation for the map.
            longitudes_list = [point[0] for point in geometry.coordinates[0]]
            latitudes_list = [point[1] for point in geometry.coordinates[0]]
            number_of_points = len(geometry.coordinates[0])
            longitude = sum(longitudes_list) / number_of_points
            latitude = sum(latitudes_list) / number_of_points
            _LOGGER.debug("Centroid of %s is %s", geometry.coordinates[0],
                          (latitude, longitude))
        else:
            _LOGGER.debug("Not implemented: %s", type(geometry))
        return latitude, longitude

    @staticmethod
    def distance_to_geometry(home_coordinates, geometry):
        """Calculate the distance between home coordinates and geometry."""
        distance = float("inf")
        if isinstance(geometry, Point):
            distance = GeoJsonDistanceHelper._distance_to_point(
                home_coordinates, geometry)
        elif isinstance(geometry, GeometryCollection):
            distance = GeoJsonDistanceHelper._distance_to_geometry_collection(
                home_coordinates, geometry)
        elif isinstance(geometry, Polygon):
            distance = GeoJsonDistanceHelper._distance_to_polygon(
                home_coordinates, geometry.coordinates[0])
        else:
            _LOGGER.debug("Not implemented: %s", type(geometry))
        return distance

    @staticmethod
    def _distance_to_point(home_coordinates, point):
        """Calculate the distance between home coordinates and the point."""
        # Swap coordinates to match: (latitude, longitude).
        return GeoJsonDistanceHelper._distance_to_coordinates(
            home_coordinates, (point.coordinates[1], point.coordinates[0]))

    @staticmethod
    def _distance_to_geometry_collection(home_coordinates,
                                         geometry_collection):
        """Calculate the distance between home coordinates and the geometry
        collection."""
        distance = float("inf")
        for geometry in geometry_collection.geometries:
            distance = min(distance,
                           GeoJsonDistanceHelper.distance_to_geometry(
                               home_coordinates, geometry))
        return distance

    @staticmethod
    def _distance_to_polygon(home_coordinates, polygon):
        """Calculate the distance between home coordinates and the polygon."""
        distance = float("inf")
        # Calculate distance from polygon by calculating the distance
        # to each point of the polygon but not to each edge of the
        # polygon; should be good enough
        for polygon_point in polygon:
            distance = min(distance,
                           GeoJsonDistanceHelper._distance_to_coordinates(
                               home_coordinates,
                               (polygon_point[1], polygon_point[0])))
        return distance

    @staticmethod
    def _distance_to_coordinates(home_coordinates, coordinates):
        """Calculate the distance between home coordinates and the
        coordinates."""
        # Expecting coordinates in format: (latitude, longitude).
        return haversine(coordinates, home_coordinates)
