"""Tests for base classes."""

from unittest.mock import ANY, MagicMock

import pytest

from aio_geojson_client.geojson_distance_helper import GeoJsonDistanceHelper
from aio_geojson_client.geometries.point import Point
from aio_geojson_client.geometries.polygon import Polygon


def test_extract_coordinates_from_point():
    """Test extracting coordinates from point."""
    point = Point(-30.0, 151.0)
    latitude, longitude = GeoJsonDistanceHelper.extract_coordinates(point)
    assert latitude == -30.0
    assert longitude == 151.0


def test_extract_coordinates_from_polygon():
    """Test extracting coordinates from polygon."""
    polygon = Polygon(
        [
            Point(-30.0, 151.0),
            Point(-30.0, 151.5),
            Point(-30.5, 151.5),
            Point(-30.5, 151.0),
            Point(-30.0, 151.0),
        ]
    )
    latitude, longitude = GeoJsonDistanceHelper.extract_coordinates(polygon)
    assert latitude == pytest.approx(-30.2, 0.1)
    assert longitude == pytest.approx(151.2, 0.1)


def test_extract_coordinates_from_unsupported_geometry():
    """Test extracting coordinates from unsupported geometry."""
    mock_unsupported_geometry = MagicMock()
    latitude, longitude = GeoJsonDistanceHelper.extract_coordinates(
        mock_unsupported_geometry
    )
    assert latitude is None
    assert longitude is None


def test_distance_to_point():
    """Test calculating distance to point."""
    home_coordinates = (-31.0, 150.0)
    point = Point(-30.0, 151.0)
    distance = GeoJsonDistanceHelper.distance_to_geometry(home_coordinates, point)
    assert distance == pytest.approx(146.8, 0.1)


def test_distance_to_polygon_1():
    """Test calculating distance to point."""
    home_coordinates = (-31.0, 150.0)
    polygon = Polygon(
        [
            Point(-30.0, 151.0),
            Point(-30.0, 151.5),
            Point(-30.5, 151.5),
            Point(-30.5, 151.0),
            Point(-30.0, 151.0),
        ]
    )
    distance = GeoJsonDistanceHelper.distance_to_geometry(home_coordinates, polygon)
    assert distance == pytest.approx(110.6, 0.1)


def test_distance_to_polygon_2():
    """Test calculating distance to polygon."""
    home_coordinates = (-30.2, 151.2)
    polygon = Polygon(
        [
            Point(-30.0, 151.0),
            Point(-30.0, 151.5),
            Point(-30.5, 151.5),
            Point(-30.5, 151.0),
            Point(-30.0, 151.0),
        ]
    )
    distance = GeoJsonDistanceHelper.distance_to_geometry(home_coordinates, polygon)
    assert distance == pytest.approx(0.0, 0.1)


def test_distance_to_polygon_3():
    """Test calculating distance to polygon."""
    home_coordinates = (-29.0, 151.2)
    polygon = Polygon(
        [
            Point(-30.0, 151.0),
            Point(-30.0, 151.5),
            Point(-30.5, 151.5),
            Point(-30.5, 151.0),
            Point(-30.0, 151.0),
        ]
    )
    distance = GeoJsonDistanceHelper.distance_to_geometry(home_coordinates, polygon)
    assert distance == pytest.approx(111.2, 0.1)


def test_distance_to_polygon_4():
    """Test calculating distance to polygon."""
    home_coordinates = (30.0, 151.3)
    polygon = Polygon(
        [
            Point(30.0, 151.0),
            Point(30.0, 151.5),
            Point(30.5, 151.5),
            Point(30.5, 151.0),
            Point(30.0, 151.0),
        ]
    )
    distance = GeoJsonDistanceHelper.distance_to_geometry(home_coordinates, polygon)
    assert distance == pytest.approx(0.0, 0.1)


def test_distance_to_polygon_5():
    """Test calculating distance to polygon."""
    polygon = Polygon(
        [
            Point(30.0, 179.0),
            Point(30.0, -179.5),
            Point(30.5, -179.5),
            Point(30.5, 179.0),
            Point(30.0, 179.0),
        ]
    )
    home_coordinates = (30.2, -177.0)
    distance = GeoJsonDistanceHelper.distance_to_geometry(home_coordinates, polygon)
    assert distance == pytest.approx(240.3, 0.1)
    home_coordinates = (30.1, 178.0)
    distance = GeoJsonDistanceHelper.distance_to_geometry(home_coordinates, polygon)
    assert distance == pytest.approx(96.2, 0.1)
    home_coordinates = (31.0, -179.8)
    distance = GeoJsonDistanceHelper.distance_to_geometry(home_coordinates, polygon)
    assert distance == pytest.approx(55.6, 0.1)
    home_coordinates = (31.0, 179.8)
    distance = GeoJsonDistanceHelper.distance_to_geometry(home_coordinates, polygon)
    assert distance == pytest.approx(55.6, 0.1)


def test_distance_to_polygon_6():
    """Test calculating distance to polygon."""
    polygon = Polygon(
        [
            Point(-30.0, 179.0),
            Point(-30.0, -179.5),
            Point(-29.5, -179.5),
            Point(-29.5, 179.0),
            Point(-30.0, 179.0),
        ]
    )
    home_coordinates = (-29.8, -177.0)
    distance = GeoJsonDistanceHelper.distance_to_geometry(home_coordinates, polygon)
    assert distance == pytest.approx(241.2, 0.1)
    home_coordinates = (-29.9, 178.0)
    distance = GeoJsonDistanceHelper.distance_to_geometry(home_coordinates, polygon)
    assert distance == pytest.approx(96.4, 0.1)
    home_coordinates = (-29.0, -179.8)
    distance = GeoJsonDistanceHelper.distance_to_geometry(home_coordinates, polygon)
    assert distance == pytest.approx(55.6, 0.1)
    home_coordinates = (-29.0, 179.8)
    distance = GeoJsonDistanceHelper.distance_to_geometry(home_coordinates, polygon)
    assert distance == pytest.approx(55.6, 0.1)


def test_distance_to_unsupported_geometry():
    """Test calculating distance to unsupported geometry."""
    home_coordinates = (-31.0, 150.0)
    mock_unsupported_geometry = MagicMock()
    distance = GeoJsonDistanceHelper.distance_to_geometry(
        home_coordinates, mock_unsupported_geometry
    )
    assert distance == float("inf")


def test_perpendicular_point_edge_case():
    """Test edge case when calculating perpendicular point."""
    edge = (Point(-31.0, 150.0), Point(-31.0, 150.0))
    result = GeoJsonDistanceHelper._perpendicular_point(edge, ANY)  # noqa: SLF001
    assert result is None
