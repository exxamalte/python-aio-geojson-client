"""Test for the generic geojson feed."""

import asyncio
from http import HTTPStatus
from unittest.mock import MagicMock

import aiohttp
from aiohttp import ClientOSError
import pytest

from aio_geojson_client.consts import UPDATE_ERROR, UPDATE_OK
from aio_geojson_client.filter_definition import GeoJsonFeedFilterDefinition
from aio_geojson_client.geometries.point import Point
from aio_geojson_client.geometries.polygon import Polygon
from tests import MockGeoJsonFeed
from tests.utils import load_fixture


@pytest.mark.asyncio
async def test_update_ok(mock_aioresponse):
    """Test updating feed is ok."""
    home_coordinates = (-31.0, 151.0)
    mock_aioresponse.get(
        "http://test.url/testpath",
        status=HTTPStatus.OK,
        body=load_fixture("generic_feed_1.json"),
    )

    async with aiohttp.ClientSession(loop=asyncio.get_running_loop()) as websession:
        feed = MockGeoJsonFeed(websession, home_coordinates, "http://test.url/testpath")
        assert (
            repr(feed) == "<MockGeoJsonFeed(home=(-31.0, 151.0), "
            "url=http://test.url/testpath, radius=None)>"
        )
        status, entries = await feed.update()
        assert status == UPDATE_OK
        assert entries is not None
        assert len(entries) == 5

        feed_entry = entries[0]
        assert feed_entry is not None
        assert feed_entry.title == "Title 1"
        assert feed_entry.external_id == "3456"
        assert feed_entry.coordinates == (-37.2345, 149.1234)
        assert round(abs(feed_entry.distance_to_home - 714.4), 1) == 0
        assert repr(feed_entry) == "<MockFeedEntry(id=3456)>"

        feed_entry = entries[1]
        assert feed_entry is not None
        assert feed_entry.title == "Title 2"
        assert feed_entry.external_id == "4567"

        feed_entry = entries[2]
        assert feed_entry is not None
        assert feed_entry.title == "Title 3"
        assert feed_entry.external_id == "Title 3"

        feed_entry = entries[3]
        assert feed_entry is not None
        assert feed_entry.title is None
        assert feed_entry.external_id == hash(feed_entry.coordinates)

        feed_entry = entries[4]
        assert feed_entry is not None
        assert feed_entry.title == "Title 5"
        assert feed_entry.external_id == "7890"


@pytest.mark.asyncio
async def test_update_ok_with_filtering(mock_aioresponse):
    """Test updating feed is ok."""
    home_coordinates = (-37.0, 150.0)
    mock_aioresponse.get(
        "http://test.url/testpath",
        status=HTTPStatus.OK,
        body=load_fixture("generic_feed_1.json"),
    )

    async with aiohttp.ClientSession(loop=asyncio.get_running_loop()) as websession:
        feed = MockGeoJsonFeed(
            websession, home_coordinates, "http://test.url/testpath", filter_radius=90.0
        )
        status, entries = await feed.update()
        assert status == UPDATE_OK
        assert entries is not None
        assert len(entries) == 4
        assert round(abs(entries[0].distance_to_home - 82.0), 1) == 0
        assert round(abs(entries[1].distance_to_home - 77.0), 1) == 0
        assert round(abs(entries[2].distance_to_home - 84.6), 1) == 0


@pytest.mark.asyncio
async def test_update_ok_with_filter_override(mock_aioresponse):
    """Test updating feed is ok."""
    home_coordinates = (-37.0, 150.0)
    mock_aioresponse.get(
        "http://test.url/testpath",
        status=HTTPStatus.OK,
        body=load_fixture("generic_feed_1.json"),
    )

    async with aiohttp.ClientSession(loop=asyncio.get_running_loop()) as websession:
        feed = MockGeoJsonFeed(
            websession, home_coordinates, "http://test.url/testpath", filter_radius=60.0
        )
        status, entries = await feed.update_override(
            filter_overrides=GeoJsonFeedFilterDefinition(radius=90.0)
        )
        assert status == UPDATE_OK
        assert entries is not None
        assert len(entries) == 4
        assert round(abs(entries[0].distance_to_home - 82.0), 1) == 0
        assert round(abs(entries[1].distance_to_home - 77.0), 1) == 0
        assert round(abs(entries[2].distance_to_home - 84.6), 1) == 0


@pytest.mark.asyncio
async def test_update_geometries(mock_aioresponse):
    """Test updating feed is ok."""
    home_coordinates = (-31.0, 151.0)
    mock_aioresponse.get(
        "http://test.url/testpath",
        status=HTTPStatus.OK,
        body=load_fixture("generic_feed_3.json"),
    )

    async with aiohttp.ClientSession(loop=asyncio.get_running_loop()) as websession:
        feed = MockGeoJsonFeed(websession, home_coordinates, "http://test.url/testpath")
        assert (
            repr(feed) == "<MockGeoJsonFeed(home=(-31.0, 151.0), "
            "url=http://test.url/testpath, radius=None)>"
        )
        status, entries = await feed.update()
        assert status == UPDATE_OK
        assert entries is not None
        assert len(entries) == 3

        feed_entry = entries[0]
        assert feed_entry is not None
        assert feed_entry.title == "Title 1"
        assert feed_entry.external_id == "1234"
        assert isinstance(feed_entry.geometries[0], Point)
        assert feed_entry.coordinates == (-35.5, 150.5)
        assert round(abs(feed_entry.distance_to_home - 502.5), 1) == 0
        assert repr(feed_entry) == "<MockFeedEntry(id=1234)>"

        feed_entry = entries[1]
        assert feed_entry is not None
        assert feed_entry.title == "Title 2"
        assert feed_entry.external_id == "2345"
        assert isinstance(feed_entry.geometries[0], Polygon)
        assert feed_entry.coordinates == (-28.0, 152.0)

        feed_entry = entries[2]
        assert feed_entry is not None
        assert feed_entry.title == "Title 3"
        assert feed_entry.external_id == "3456"
        assert isinstance(feed_entry.geometries[0], Point)
        assert isinstance(feed_entry.geometries[1], Polygon)
        assert feed_entry.coordinates == (-35.5, 150.5)


@pytest.mark.asyncio
async def test_update_with_client_exception():
    """Test updating feed results in error."""
    home_coordinates = (-31.0, 151.0)

    async with aiohttp.ClientSession(loop=asyncio.get_running_loop()):
        mock_websession = MagicMock()
        mock_websession.request.side_effect = ClientOSError
        feed = MockGeoJsonFeed(
            mock_websession, home_coordinates, "http://test.url/badpath"
        )
        status, entries = await feed.update()
        assert status == UPDATE_ERROR
        assert feed.last_timestamp is None


@pytest.mark.asyncio
async def test_update_with_request_exception(mock_aioresponse):
    """Test updating feed results in error."""
    home_coordinates = (-31.0, 151.0)
    mock_aioresponse.get("http://test.url/testpath", status=HTTPStatus.NOT_FOUND)

    async with aiohttp.ClientSession(loop=asyncio.get_running_loop()) as websession:
        feed = MockGeoJsonFeed(websession, home_coordinates, "http://test.url/badpath")
        status, entries = await feed.update()
        assert status == UPDATE_ERROR
        assert feed.last_timestamp is None


@pytest.mark.asyncio
async def test_update_with_json_decode_error(mock_aioresponse):
    """Test updating feed raises exception."""
    home_coordinates = (-31.0, 151.0)
    mock_aioresponse.get(
        "http://test.url/badjson", status=HTTPStatus.OK, body="NOT JSON"
    )

    async with aiohttp.ClientSession(loop=asyncio.get_running_loop()) as websession:
        feed = MockGeoJsonFeed(websession, home_coordinates, "http://test.url/badjson")
        status, entries = await feed.update()
        assert status == UPDATE_ERROR
        assert entries is None


@pytest.mark.asyncio
async def test_update_with_timeout_error():
    """Test updating feed results in timeout error."""
    home_coordinates = (-31.0, 151.0)

    async with aiohttp.ClientSession(loop=asyncio.get_running_loop()):
        mock_websession = MagicMock()
        mock_websession.request.side_effect = asyncio.TimeoutError
        feed = MockGeoJsonFeed(
            mock_websession, home_coordinates, "http://test.url/goodpath"
        )
        status, entries = await feed.update()
        assert status == UPDATE_ERROR
        assert feed.last_timestamp is None


@pytest.mark.asyncio
async def test_update_ok_feed_feature(mock_aioresponse):
    """Test updating feed is ok."""
    home_coordinates = (-31.0, 151.0)
    mock_aioresponse.get(
        "http://test.url/testpath",
        status=HTTPStatus.OK,
        body=load_fixture("generic_feed_4.json"),
    )

    async with aiohttp.ClientSession(loop=asyncio.get_running_loop()) as websession:
        feed = MockGeoJsonFeed(websession, home_coordinates, "http://test.url/testpath")
        assert (
            repr(feed) == "<MockGeoJsonFeed(home=(-31.0, 151.0), "
            "url=http://test.url/testpath, radius=None)>"
        )
        status, entries = await feed.update()
        assert status == UPDATE_OK
        assert entries is not None
        assert len(entries) == 1

        feed_entry = entries[0]
        assert feed_entry is not None
        assert feed_entry.title == "Title 1"
        assert feed_entry.external_id == "3456"
        assert feed_entry.coordinates == (-37.2345, 149.1234)
        assert round(abs(feed_entry.distance_to_home - 714.4), 1) == 0
        assert repr(feed_entry) == "<MockFeedEntry(id=3456)>"


@pytest.mark.asyncio
async def test_unsupported_object(mock_aioresponse, caplog):
    """Test updating feed is ok."""
    home_coordinates = (-31.0, 151.0)
    mock_aioresponse.get(
        "http://test.url/testpath",
        status=HTTPStatus.OK,
        body=load_fixture("generic_feed_5.json"),
    )

    async with aiohttp.ClientSession(loop=asyncio.get_running_loop()) as websession:
        feed = MockGeoJsonFeed(websession, home_coordinates, "http://test.url/testpath")
        assert (
            repr(feed) == "<MockGeoJsonFeed(home=(-31.0, 151.0), "
            "url=http://test.url/testpath, radius=None)>"
        )
        status, entries = await feed.update()
        assert status == UPDATE_OK
        assert entries is not None
        assert len(entries) == 0

        assert (
            "Unsupported GeoJSON object found: <class 'geojson.geometry.Point'>"
            in caplog.text
        )
