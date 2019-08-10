"""
Status Update.
"""


class StatusUpdate:
    """Status Update class."""

    def __init__(self, status, last_update, last_update_successful,
                 last_timestamp, created, updated, removed):
        """Initialise this status update."""
        self._status = status
        self._last_update = last_update
        self._last_update_successful = last_update_successful
        self._last_timestamp = last_timestamp
        self._created = created
        self._updated = updated
        self._removed = removed

    def __repr__(self):
        """Return string representation of this entry."""
        return '<{}({}@{})>'.format(self.__class__.__name__,
                                    self.status,
                                    self.last_update)

    @property
    def status(self):
        """Return the status."""
        return self._status

    @property
    def last_update(self):
        """Return the time when the feed was last updated."""
        return self._last_update

    @property
    def last_update_successful(self):
        """Return the time when the feed was last updated successfully."""
        return self._last_update_successful

    @property
    def last_timestamp(self):
        """Return the timestamp the latest entry in the feed."""
        return self._last_timestamp

    @property
    def created(self):
        """Return the number of created entries."""
        return self._created

    @property
    def updated(self):
        """Return the number of updated entries."""
        return self._updated

    @property
    def removed(self):
        """Return the number of removed entries."""
        return self._removed
