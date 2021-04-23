"""GeoJSON point."""
from typing import Optional

from .geometry import Geometry


class Point(Geometry):
    """Represents a point."""

    def __init__(self, latitude: float, longitude: float):
        """Initialise point."""
        self._latitude = latitude
        self._longitude = longitude

    def __repr__(self):
        """Return string representation of this point."""
        return "<{}(latitude={}, longitude={})>".format(
            self.__class__.__name__, self.latitude, self.longitude
        )

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
    def latitude(self) -> Optional[float]:
        """Return the latitude of this point."""
        return self._latitude

    @property
    def longitude(self) -> Optional[float]:
        """Return the longitude of this point."""
        return self._longitude
