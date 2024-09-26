"""Filter definitions."""

from __future__ import annotations


class GeoJsonFeedFilterDefinition:
    """Filter definition."""

    def __init__(self, radius: float | None = None):
        """Initialise filter definition."""
        self._radius = radius

    @property
    def radius(self) -> float:
        """Return the radius."""
        return self._radius

    @radius.setter
    def radius(self, value: float):
        """Set radius."""
        self._radius = value
