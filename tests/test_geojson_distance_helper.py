"""Tests for base classes."""
import unittest
from unittest.mock import MagicMock, ANY

from aio_geojson_client.geojson_distance_helper import GeoJsonDistanceHelper
from aio_geojson_client.geometries.point import Point
from aio_geojson_client.geometries.polygon import Polygon


class TestGeoJsonDistanceHelper(unittest.TestCase):
    """Tests for the GeoJSON distance helper."""

    def test_extract_coordinates_from_point(self):
        """Test extracting coordinates from point."""
        point = Point(-30.0, 151.0)
        latitude, longitude = GeoJsonDistanceHelper.\
            extract_coordinates(point)
        assert latitude == -30.0
        assert longitude == 151.0

    def test_extract_coordinates_from_polygon(self):
        """Test extracting coordinates from polygon."""
        polygon = Polygon([
            Point(-30.0, 151.0), Point(-30.0, 151.5), Point(-30.5, 151.5),
            Point(-30.5, 151.0), Point(-30.0, 151.0)
        ])
        latitude, longitude = GeoJsonDistanceHelper.\
            extract_coordinates(polygon)
        self.assertAlmostEqual(latitude, -30.2, 1)
        self.assertAlmostEqual(longitude, 151.2, 1)

    def test_extract_coordinates_from_unsupported_geometry(self):
        """Test extracting coordinates from unsupported geometry."""
        mock_unsupported_geometry = MagicMock()
        latitude, longitude = GeoJsonDistanceHelper.\
            extract_coordinates(mock_unsupported_geometry)
        self.assertIsNone(latitude)
        self.assertIsNone(longitude)

    def test_distance_to_point(self):
        """Test calculating distance to point."""
        home_coordinates = (-31.0, 150.0)
        point = Point(-30.0, 151.0)
        distance = GeoJsonDistanceHelper.\
            distance_to_geometry(home_coordinates, point)
        self.assertAlmostEqual(distance, 146.8, 1)

    def test_distance_to_polygon_1(self):
        """Test calculating distance to point."""
        home_coordinates = (-31.0, 150.0)
        polygon = Polygon([
            Point(-30.0, 151.0), Point(-30.0, 151.5), Point(-30.5, 151.5),
            Point(-30.5, 151.0), Point(-30.0, 151.0)
        ])
        distance = GeoJsonDistanceHelper.\
            distance_to_geometry(home_coordinates, polygon)
        self.assertAlmostEqual(distance, 110.6, 1)

    def test_distance_to_polygon_2(self):
        """Test calculating distance to polygon."""
        home_coordinates = (-30.2, 151.2)
        polygon = Polygon([
            Point(-30.0, 151.0), Point(-30.0, 151.5), Point(-30.5, 151.5),
            Point(-30.5, 151.0), Point(-30.0, 151.0)
        ])
        distance = GeoJsonDistanceHelper.\
            distance_to_geometry(home_coordinates, polygon)
        self.assertAlmostEqual(distance, 0.0, 1)

    def test_distance_to_polygon_3(self):
        """Test calculating distance to polygon."""
        home_coordinates = (-29.0, 151.2)
        polygon = Polygon([
            Point(-30.0, 151.0), Point(-30.0, 151.5), Point(-30.5, 151.5),
            Point(-30.5, 151.0), Point(-30.0, 151.0)
        ])
        distance = GeoJsonDistanceHelper.\
            distance_to_geometry(home_coordinates, polygon)
        self.assertAlmostEqual(distance, 111.2, 1)

    def test_distance_to_polygon_4(self):
        """Test calculating distance to polygon."""
        home_coordinates = (30.0, 151.3)
        polygon = Polygon([
            Point(30.0, 151.0), Point(30.0, 151.5), Point(30.5, 151.5),
            Point(30.5, 151.0), Point(30.0, 151.0)
        ])
        distance = GeoJsonDistanceHelper.\
            distance_to_geometry(home_coordinates, polygon)
        self.assertAlmostEqual(distance, 0.0, 1)

    def test_distance_to_polygon_5(self):
        """Test calculating distance to polygon."""
        polygon = Polygon([
            Point(30.0, 179.0), Point(30.0, -179.5), Point(30.5, -179.5),
            Point(30.5, 179.0), Point(30.0, 179.0)
        ])
        home_coordinates = (30.2, -177.0)
        distance = GeoJsonDistanceHelper.\
            distance_to_geometry(home_coordinates, polygon)
        self.assertAlmostEqual(distance, 240.3, 1)
        home_coordinates = (30.1, 178.0)
        distance = GeoJsonDistanceHelper.\
            distance_to_geometry(home_coordinates, polygon)
        self.assertAlmostEqual(distance, 96.2, 1)
        home_coordinates = (31.0, -179.8)
        distance = GeoJsonDistanceHelper.\
            distance_to_geometry(home_coordinates, polygon)
        self.assertAlmostEqual(distance, 55.6, 1)
        home_coordinates = (31.0, 179.8)
        distance = GeoJsonDistanceHelper.\
            distance_to_geometry(home_coordinates, polygon)
        self.assertAlmostEqual(distance, 55.6, 1)

    def test_distance_to_polygon_6(self):
        """Test calculating distance to polygon."""
        polygon = Polygon([
            Point(-30.0, 179.0), Point(-30.0, -179.5), Point(-29.5, -179.5),
            Point(-29.5, 179.0), Point(-30.0, 179.0)
        ])
        home_coordinates = (-29.8, -177.0)
        distance = GeoJsonDistanceHelper.\
            distance_to_geometry(home_coordinates, polygon)
        self.assertAlmostEqual(distance, 241.2, 1)
        home_coordinates = (-29.9, 178.0)
        distance = GeoJsonDistanceHelper.\
            distance_to_geometry(home_coordinates, polygon)
        self.assertAlmostEqual(distance, 96.4, 1)
        home_coordinates = (-29.0, -179.8)
        distance = GeoJsonDistanceHelper.\
            distance_to_geometry(home_coordinates, polygon)
        self.assertAlmostEqual(distance, 55.6, 1)
        home_coordinates = (-29.0, 179.8)
        distance = GeoJsonDistanceHelper.\
            distance_to_geometry(home_coordinates, polygon)
        self.assertAlmostEqual(distance, 55.6, 1)

    def test_distance_to_unsupported_geometry(self):
        """Test calculating distance to unsupported geometry."""
        home_coordinates = (-31.0, 150.0)
        mock_unsupported_geometry = MagicMock()
        distance = GeoJsonDistanceHelper.\
            distance_to_geometry(home_coordinates, mock_unsupported_geometry)
        assert distance == float("inf")

    def test_perpendicular_point_edge_case(self):
        """Test edge case when calculating perpendicular point."""
        edge = (Point(-31.0, 150.0), Point(-31.0, 150.0))
        result = GeoJsonDistanceHelper._perpendicular_point(edge, ANY)
        assert result is None
