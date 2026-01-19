"""Change type enumeration for diff results."""

from enum import Enum


class ChangeType(str, Enum):
    """Enumeration of possible change types in a diff."""

    ADDED = "ADDED"
    DELETED = "DELETED"
    MODIFIED = "MODIFIED"
    MOVED = "MOVED"
    MOVED_AND_MODIFIED = "MOVED_AND_MODIFIED"
