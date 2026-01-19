"""Diff result data structures."""

from dataclasses import dataclass, field
from typing import List, Optional

from .change_types import ChangeType


@dataclass
class DiffChange:
    """Represents a single change detected between source and target files."""

    change_type: ChangeType
    key: str
    source_line: Optional[int] = None  # Line number in source file (None for ADDED)
    target_line: Optional[int] = None  # Line number in target file (None for DELETED)
    source_value: Optional[str] = None  # Value in source file
    target_value: Optional[str] = None  # Value in target file
    message: Optional[str] = None  # Descriptive message about the change

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        result = {
            "type": self.change_type.value,
            "key": self.key,
            "source_line": self.source_line,
            "target_line": self.target_line,
            "source_value": self.source_value,
            "target_value": self.target_value,
        }
        if self.message:
            result["message"] = self.message
        return result

@dataclass
class DiffSummary:
    """Summary statistics of changes."""

    added: int = 0
    deleted: int = 0
    modified: int = 0
    moved: int = 0
    moved_and_modified: int = 0

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "added": self.added,
            "deleted": self.deleted,
            "modified": self.modified,
            "moved": self.moved,
            "moved_and_modified": self.moved_and_modified,
        }


@dataclass
class DiffResult:
    """Complete diff result containing all changes and summary."""

    source_file: str
    target_file: str
    changes: List[DiffChange] = field(default_factory=list)
    summary: Optional[DiffSummary] = None

    def calculate_summary(self) -> None:
        """Calculate summary statistics from changes."""
        summary = DiffSummary()
        for change in self.changes:
            if change.change_type == ChangeType.ADDED:
                summary.added += 1
            elif change.change_type == ChangeType.DELETED:
                summary.deleted += 1
            elif change.change_type == ChangeType.MODIFIED:
                summary.modified += 1
            elif change.change_type == ChangeType.MOVED:
                summary.moved += 1
            elif change.change_type == ChangeType.MOVED_AND_MODIFIED:
                summary.moved_and_modified += 1
        self.summary = summary

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        if self.summary is None:
            self.calculate_summary()
        return {
            "source_file": self.source_file,
            "target_file": self.target_file,
            "changes": [change.to_dict() for change in self.changes],
            "summary": self.summary.to_dict() if self.summary else {},
        }
