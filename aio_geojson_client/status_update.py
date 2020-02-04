"""Status Update."""
from datetime import datetime
from typing import Optional


class StatusUpdate:
    """Status Update class."""

    def __init__(self,
                 status: str,
                 last_update: Optional[datetime],
                 last_update_successful: Optional[datetime],
                 last_timestamp: Optional[datetime],
                 total: int,
                 created: int,
                 updated: int,
                 removed: int):
        """Initialise this status update."""
        self._status = status
        self._last_update = last_update
        self._last_update_successful = last_update_successful
        self._last_timestamp = last_timestamp
        self._total = total
        self._created = created
        self._updated = updated
        self._removed = removed

    def __repr__(self):
        """Return string representation of this entry."""
        return '<{}({}@{})>'.format(self.__class__.__name__,
                                    self.status,
                                    self.last_update)

    @property
    def status(self) -> str:
        """Return the status."""
        return self._status

    @property
    def last_update(self) -> Optional[datetime]:
        """Return the time when the feed was last updated."""
        return self._last_update

    @property
    def last_update_successful(self) -> Optional[datetime]:
        """Return the time when the feed was last updated successfully."""
        return self._last_update_successful

    @property
    def last_timestamp(self) -> Optional[datetime]:
        """Return the timestamp the latest entry in the feed."""
        return self._last_timestamp

    @property
    def total(self) -> int:
        """Return the total number of managed entries."""
        return self._total

    @property
    def created(self) -> int:
        """Return the number of created entries."""
        return self._created

    @property
    def updated(self) -> int:
        """Return the number of updated entries."""
        return self._updated

    @property
    def removed(self) -> int:
        """Return the number of removed entries."""
        return self._removed
