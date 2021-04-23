"""Filter definitions."""


class GeoJsonFeedFilterDefinition:
    def __init__(self, radius: float = None):
        self._radius = radius

    @property
    def radius(self) -> float:
        """Return the radius."""
        return self._radius

    @radius.setter
    def radius(self, value: float):
        """Set radius."""
        self._radius = value
