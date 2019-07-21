"""Test for the generic geojson feed entry."""
from aio_geojson_client.feed_entry import FeedEntry


def test_simple_feed_entry():
    """Test feed entry behaviour."""
    feed_entry = FeedEntry(None, None)
    assert repr(feed_entry) == "<FeedEntry(id=None)>"
    assert feed_entry.geometry is None
    assert feed_entry.coordinates is None
    assert feed_entry.title is None
    assert feed_entry.external_id is None
    assert feed_entry.attribution is None
