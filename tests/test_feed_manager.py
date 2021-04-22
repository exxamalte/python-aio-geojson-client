"""Test for the generic geojson feed manager."""
import aiohttp

import pytest
from aio_geojson_client.consts import UPDATE_OK_NO_DATA
from aio_geojson_client.feed_manager import FeedManagerBase
from asynctest import CoroutineMock, patch
from tests import MockGeoJsonFeed
from tests.utils import load_fixture


@pytest.mark.asyncio
async def test_feed_manager(aresponses, event_loop):
    """Test the feed manager."""
    home_coordinates = (-31.0, 151.0)
    aresponses.add(
        "test.url",
        "/testpath",
        "get",
        aresponses.Response(text=load_fixture('generic_feed_1.json'),
                            status=200),
    )

    async with aiohttp.ClientSession(loop=event_loop) as websession:

        feed = MockGeoJsonFeed(websession,
                               home_coordinates,
                               "http://test.url/testpath")

        # This will just record calls and keep track of external ids.
        generated_entity_external_ids = []
        updated_entity_external_ids = []
        removed_entity_external_ids = []

        async def _generate_entity(external_id):
            """Generate new entity."""
            generated_entity_external_ids.append(external_id)

        async def _update_entity(external_id):
            """Update entity."""
            updated_entity_external_ids.append(external_id)

        async def _remove_entity(external_id):
            """Remove entity."""
            removed_entity_external_ids.append(external_id)

        feed_manager = FeedManagerBase(feed, _generate_entity, _update_entity,
                                       _remove_entity)
        assert repr(feed_manager) == "<FeedManagerBase(feed=<" \
                                     "MockGeoJsonFeed(home=(-31.0, 151.0), " \
                                     "url=http://test.url/testpath, " \
                                     "radius=None)>)>"
        await feed_manager.update()
        entries = feed_manager.feed_entries
        assert entries is not None
        assert len(entries) == 5
        assert feed_manager.last_update is not None
        assert feed_manager.last_timestamp is None

        assert len(generated_entity_external_ids) == 5
        assert len(updated_entity_external_ids) == 0
        assert len(removed_entity_external_ids) == 0

        feed_entry = entries.get("3456")
        assert feed_entry.title == "Title 1"
        assert feed_entry.external_id == "3456"
        assert feed_entry.coordinates == (-37.2345, 149.1234)
        assert round(abs(feed_entry.distance_to_home - 714.4), 1) == 0
        assert repr(feed_entry) == "<MockFeedEntry(id=3456)>"

        feed_entry = entries.get("4567")
        assert feed_entry.title == "Title 2"
        assert feed_entry.external_id == "4567"

        feed_entry = entries.get("Title 3")
        assert feed_entry.title == "Title 3"
        assert feed_entry.external_id == "Title 3"

        external_id = hash((-37.8901, 149.7890))
        feed_entry = entries.get(external_id)
        assert feed_entry.title is None
        assert feed_entry.external_id == external_id

        feed_entry = entries.get("7890")
        assert feed_entry.title == "Title 5"
        assert feed_entry.external_id == "7890"

        # Simulate an update with several changes.
        generated_entity_external_ids.clear()
        updated_entity_external_ids.clear()
        removed_entity_external_ids.clear()

        aresponses.add(
            "test.url",
            "/testpath",
            "get",
            aresponses.Response(text=load_fixture('generic_feed_2.json'),
                                status=200),
        )

        await feed_manager.update()
        entries = feed_manager.feed_entries
        assert entries is not None
        assert len(entries) == 3
        assert len(generated_entity_external_ids) == 1
        assert len(updated_entity_external_ids) == 2
        assert len(removed_entity_external_ids) == 3

        feed_entry = entries.get("3456")
        assert feed_entry.title == "Title 1 UPDATED"

        feed_entry = entries.get("4567")
        assert feed_entry.title == "Title 2"

        feed_entry = entries.get("8901")
        assert feed_entry.title == "Title 6"

        # Simulate an update with no data.
        generated_entity_external_ids.clear()
        updated_entity_external_ids.clear()
        removed_entity_external_ids.clear()

        with patch("aio_geojson_client.feed.GeoJsonFeed._fetch",
                   new_callable=CoroutineMock) as mock_fetch:
            mock_fetch.return_value = (UPDATE_OK_NO_DATA, None)

            await feed_manager.update()
            entries = feed_manager.feed_entries

            assert len(entries) == 3
            assert len(generated_entity_external_ids) == 0
            assert len(updated_entity_external_ids) == 0
            assert len(removed_entity_external_ids) == 0

        # Simulate an update producing an error.
        generated_entity_external_ids.clear()
        updated_entity_external_ids.clear()
        removed_entity_external_ids.clear()

        aresponses.add(
            "test.url",
            "/testpath",
            "get",
            aresponses.Response(status=500),
        )

        await feed_manager.update()
        entries = feed_manager.feed_entries

        assert len(entries) == 0
        assert len(generated_entity_external_ids) == 0
        assert len(updated_entity_external_ids) == 0
        assert len(removed_entity_external_ids) == 3

        # Simulate an update with dynamic filter.
        generated_entity_external_ids.clear()
        updated_entity_external_ids.clear()
        removed_entity_external_ids.clear()

        aresponses.add(
            "test.url",
            "/testpath",
            "get",
            aresponses.Response(text=load_fixture('generic_feed_1.json'),
                                status=200),
        )
        await feed_manager.update(filter_overrides={'filter_radius': 750.0})
        entries = feed_manager.feed_entries
        assert entries is not None
        assert len(entries) == 2
        assert feed_manager.last_update is not None
        assert feed_manager.last_timestamp is None


@pytest.mark.asyncio
async def test_feed_manager_with_status_callback(aresponses, event_loop):
    """Test the feed manager."""
    home_coordinates = (-31.0, 151.0)
    aresponses.add(
        "test.url",
        "/testpath",
        "get",
        aresponses.Response(text=load_fixture('generic_feed_1.json'),
                            status=200),
    )

    async with aiohttp.ClientSession(loop=event_loop) as websession:

        feed = MockGeoJsonFeed(websession,
                               home_coordinates,
                               "http://test.url/testpath")

        # This will just record calls and keep track of external ids.
        generated_entity_external_ids = []
        updated_entity_external_ids = []
        removed_entity_external_ids = []
        status_update = []

        async def _generate_entity(external_id):
            """Generate new entity."""
            generated_entity_external_ids.append(external_id)

        async def _update_entity(external_id):
            """Update entity."""
            updated_entity_external_ids.append(external_id)

        async def _remove_entity(external_id):
            """Remove entity."""
            removed_entity_external_ids.append(external_id)

        async def _status(status_details):
            """Capture status update details."""
            status_update.append(status_details)

        feed_manager = FeedManagerBase(feed, _generate_entity, _update_entity,
                                       _remove_entity, _status)
        assert repr(feed_manager) == "<FeedManagerBase(feed=<" \
                                     "MockGeoJsonFeed(home=(-31.0, 151.0), " \
                                     "url=http://test.url/testpath, " \
                                     "radius=None)>)>"
        await feed_manager.update()
        entries = feed_manager.feed_entries
        assert entries is not None
        assert len(entries) == 5
        assert feed_manager.last_update is not None
        assert feed_manager.last_timestamp is None

        assert len(generated_entity_external_ids) == 5
        assert len(updated_entity_external_ids) == 0
        assert len(removed_entity_external_ids) == 0

        assert status_update[0].status == "OK"
        assert status_update[0].last_update is not None
        last_update_successful = status_update[0].last_update_successful
        assert status_update[0].last_update == last_update_successful
        assert status_update[0].last_timestamp is None
        assert status_update[0].total == 5
        assert status_update[0].created == 5
        assert status_update[0].updated == 0
        assert status_update[0].removed == 0
        assert repr(status_update[0]) == f"<StatusUpdate(" \
            f"OK@{status_update[0].last_update})>"

        # Simulate an update with no data.
        generated_entity_external_ids.clear()
        updated_entity_external_ids.clear()
        removed_entity_external_ids.clear()
        status_update.clear()

        aresponses.add(
            "test.url",
            "/testpath",
            "get",
            aresponses.Response(status=500),
        )

        await feed_manager.update()
        entries = feed_manager.feed_entries

        assert len(entries) == 0
        assert len(generated_entity_external_ids) == 0
        assert len(updated_entity_external_ids) == 0
        assert len(removed_entity_external_ids) == 5

        assert status_update[0].status == "ERROR"
        assert status_update[0].last_update is not None
        assert status_update[0].last_update_successful is not None
        assert status_update[0].last_update_successful == \
            last_update_successful
        assert status_update[0].total == 0
