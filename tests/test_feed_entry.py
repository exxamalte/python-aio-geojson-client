"""Test for the generic geojson feed entry."""
from tests import MockSimpleFeedEntry


def test_simple_feed_entry():
    """Test feed entry behaviour."""
    feed_entry = MockSimpleFeedEntry(None, None)
    assert repr(feed_entry) == "<MockSimpleFeedEntry(id=mock id)>"
    assert feed_entry.geometries is None
    assert feed_entry.coordinates is None
    assert feed_entry.title == "mock title"
    assert feed_entry.external_id == "mock id"
    assert feed_entry.attribution is None
