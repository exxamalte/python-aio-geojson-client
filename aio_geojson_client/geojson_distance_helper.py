"""GeoJSON distance helper."""
import logging
from typing import Optional, Tuple

from haversine import haversine

from .geometries import Geometry, Point, Polygon

_LOGGER = logging.getLogger(__name__)


class GeoJsonDistanceHelper:
    """Helper to calculate distances between GeoJSON geometries."""

    def __init__(self):
        """Initialize the geo distance helper."""
        pass

    @staticmethod
    def extract_coordinates(geometry: Geometry) -> Optional[Tuple[float, float]]:
        """Extract the best coordinates from the feature for display."""
        latitude = longitude = None
        if isinstance(geometry, Point):
            # Just extract latitude and longitude directly.
            latitude, longitude = geometry.latitude, geometry.longitude
        elif isinstance(geometry, Polygon):
            centroid = geometry.centroid
            latitude, longitude = centroid.latitude, centroid.longitude
            _LOGGER.debug("Centroid of %s is %s", geometry, (latitude, longitude))
        else:
            _LOGGER.debug("Not implemented: %s", type(geometry))
        return latitude, longitude

    @staticmethod
    def distance_to_geometry(
        coordinates: Tuple[float, float], geometry: Geometry
    ) -> float:
        """Calculate the distance between coordinates and geometry."""
        distance = float("inf")
        if isinstance(geometry, Point):
            distance = GeoJsonDistanceHelper._distance_to_point(coordinates, geometry)
        elif isinstance(geometry, Polygon):
            distance = GeoJsonDistanceHelper._distance_to_polygon(coordinates, geometry)
        else:
            _LOGGER.debug("Not implemented: %s", type(geometry))
        return distance

    @staticmethod
    def _distance_to_point(coordinates: Tuple[float, float], point: Point) -> float:
        """Calculate the distance between coordinates and the point."""
        # Swap coordinates to match: (latitude, longitude).
        return GeoJsonDistanceHelper._distance_to_coordinates(
            coordinates, (point.latitude, point.longitude)
        )

    @staticmethod
    def _distance_to_polygon(
        coordinates: Tuple[float, float], polygon: Polygon
    ) -> float:
        """Calculate the distance between coordinates and the polygon."""
        distance = float("inf")
        # Check if coordinates are inside the polygon.
        if polygon.is_inside(Point(coordinates[0], coordinates[1])):
            return 0.0
        # Calculate distance from polygon by calculating the distance
        # to each point of the polygon.
        for polygon_point in polygon.points:
            distance = min(
                distance,
                GeoJsonDistanceHelper._distance_to_point(coordinates, polygon_point),
            )
        # Next calculate the distance to each edge of the polygon.
        for edge in polygon.edges:
            distance = min(
                distance, GeoJsonDistanceHelper._distance_to_edge(coordinates, edge)
            )
        _LOGGER.debug("Distance between %s and %s: %s", coordinates, polygon, distance)
        return distance

    @staticmethod
    def _distance_to_coordinates(
        coordinates1: Tuple[float, float], coordinates2: Tuple[float, float]
    ) -> float:
        """Calculate the distance between two coordinates tuples.."""
        # Expecting coordinates in format: (latitude, longitude).
        return haversine(coordinates2, coordinates1)

    @staticmethod
    def _distance_to_edge(
        coordinates: Tuple[float, float], edge: Tuple[Point, Point]
    ) -> float:
        """Calculate distance between coordinates and provided edge."""
        perpendicular_point = GeoJsonDistanceHelper._perpendicular_point(
            edge, Point(coordinates[0], coordinates[1])
        )
        # If there is a perpendicular point on the edge -> calculate distance.
        # If there isn't, then the distance to the end points of the edge will
        # need to be considered separately.
        if perpendicular_point:
            distance = GeoJsonDistanceHelper._distance_to_point(
                coordinates, perpendicular_point
            )
            _LOGGER.debug("Distance between %s and %s: %s", coordinates, edge, distance)
            return distance
        return float("inf")

    @staticmethod
    def _perpendicular_point(
        edge: Tuple[Point, Point], point: Point
    ) -> Optional[Point]:
        """Find a perpendicular point on the edge to the provided point."""
        a, b = edge
        # Safety check: a and b can't be an edge if they are the same point.
        if a == b:
            return None
        px = point.longitude
        py = point.latitude
        ax = a.longitude
        ay = a.latitude
        bx = b.longitude
        by = b.latitude
        # Alter longitude to cater for 180 degree crossings.
        if px < 0:
            px += 360.0
        if ax < 0:
            ax += 360.0
        if bx < 0:
            bx += 360.0
        if ay > by or ax > bx:
            ax, ay, bx, by = bx, by, ax, ay
        dx = abs(bx - ax)
        dy = abs(by - ay)
        shortest_length = ((dx * (px - ax)) + (dy * (py - ay))) / (
            (dx * dx) + (dy * dy)
        )
        rx = ax + dx * shortest_length
        ry = ay + dy * shortest_length
        if bx >= rx >= ax and by >= ry >= ay:
            if rx > 180:
                # Correct longitude.
                rx -= 360.0
            return Point(ry, rx)
        return None
