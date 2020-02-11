"""GeoJSON geometry collection."""
import logging
from typing import List, Optional

from aio_geojson_client.geometries.geometry import Geometry

_LOGGER = logging.getLogger(__name__)


class GeometryCollection(Geometry):
    """Represents a geometry collection."""

    def __init__(self, geometries: List[Geometry]):
        """Initialise point."""
        self._geometries = geometries

    def __repr__(self):
        """Return string representation of this point."""
        return '<{}(geometries={})>'.format(
            self.__class__.__name__, self.geometries)

    def __hash__(self) -> int:
        """Return unique hash of this geometry collection."""
        return hash(self.geometries)

    def __eq__(self, other: object) -> bool:
        """Return if this object is equal to other object."""
        return (
             self.__class__ == other.__class__ and
             self.geometries == other.geometries
         )

    @property
    def geometries(self) -> Optional[List[Geometry]]:
        """Return the geometries of this collection."""
        return self._geometries
