"""GeoJSON polygon."""
from typing import List, Optional, Tuple

from .geometry import Geometry
from .point import Point


class Polygon(Geometry):
    """Represents a polygon."""

    def __init__(self, points: List[Point]):
        """Initialise polygon."""
        self._points = points

    def __repr__(self):
        """Return string representation of this polygon."""
        return "<{}(centroid={})>".format(self.__class__.__name__, self.centroid)

    def __hash__(self) -> int:
        """Return unique hash of this polygon."""
        return hash(self.points)

    def __eq__(self, other: object) -> bool:
        """Return if this object is equal to other object."""
        return self.__class__ == other.__class__ and self.points == other.points

    @property
    def points(self) -> Optional[List]:
        """Return the points of this polygon."""
        return self._points

    @property
    def edges(self) -> List[Tuple[Point, Point]]:
        """Return all edges of this polygon."""
        edges = []
        for i in range(1, len(self.points)):
            previous = self.points[i - 1]
            current = self.points[i]
            edges.append((previous, current))
        return edges

    @property
    def centroid(self) -> Point:
        """Find the polygon's centroid as a best approximation."""
        longitudes_list = [point.longitude for point in self.points]
        latitudes_list = [point.latitude for point in self.points]
        number_of_points = len(self.points)
        longitude = sum(longitudes_list) / number_of_points
        latitude = sum(latitudes_list) / number_of_points
        return Point(latitude, longitude)

    def is_inside(self, point: Point) -> bool:
        """Check if the provided point is inside this polygon."""
        if point:
            crossings = 0
            for edge in self.edges:
                if Polygon._ray_crosses_segment(point, edge):
                    crossings += 1
            return crossings % 2 == 1
        return False

    @staticmethod
    def _ray_crosses_segment(point: Point, edge: Tuple[Point, Point]):
        """Use ray-casting algorithm to check provided point and edge."""
        a, b = edge
        px = point.longitude
        py = point.latitude
        ax = a.longitude
        ay = a.latitude
        bx = b.longitude
        by = b.latitude
        if ay > by:
            ax = b.longitude
            ay = b.latitude
            bx = a.longitude
            by = a.latitude
        # Alter longitude to cater for 180 degree crossings.
        if px < 0:
            px += 360.0
        if ax < 0:
            ax += 360.0
        if bx < 0:
            bx += 360.0

        if py == ay or py == by:
            py += 0.00000001
        if (py > by or py < ay) or (px > max(ax, bx)):
            return False
        if px < min(ax, bx):
            return True

        red = ((by - ay) / (bx - ax)) if (ax != bx) else float("inf")
        blue = ((py - ay) / (px - ax)) if (ax != px) else float("inf")
        return blue >= red
