"""GeoJSON point."""

from __future__ import annotations

from .geometry import Geometry


class Point(Geometry):
    """Represents a point."""

    def __init__(self, latitude: float, longitude: float):
        """Initialise point."""
        self._latitude = latitude
        self._longitude = longitude

    def __repr__(self):
        """Return string representation of this point."""
        return f"<{self.__class__.__name__}(latitude={self.latitude}, longitude={self.longitude})>"

    def __hash__(self) -> int:
        """Return unique hash of this point."""
        return hash((self.latitude, self.longitude))

    def __eq__(self, other: object) -> bool:
        """Return if this object is equal to other object."""
        return (
            self.__class__ == other.__class__
            and self.latitude == other.latitude
            and self.longitude == other.longitude
        )

    @property
    def latitude(self) -> float | None:
        """Return the latitude of this point."""
        return self._latitude

    @property
    def longitude(self) -> float | None:
        """Return the longitude of this point."""
        return self._longitude
