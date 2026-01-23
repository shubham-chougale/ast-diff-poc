"""Diff result data structures."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

from .change_types import ChangeType


@dataclass
class BlockComplexity:
    """Complexity metrics for a single changed block."""

    structural_complexity: float  # Normalized structural score (0-100)
    change_type_multiplier: float  # Multiplier based on change type
    effective_complexity: float  # Final block complexity score
    risk_level: Optional[str] = None  # Risk level classification (Low, Medium, High, Very High)
    risk_interpretation: Optional[str] = None  # Interpretation of the risk level
    metrics: Dict = field(default_factory=dict)  # Dictionary of raw and normalized metrics

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        result = {
            "structural_complexity": self.structural_complexity,
            "change_type_multiplier": self.change_type_multiplier,
            "effective_complexity": self.effective_complexity,
            "metrics": self.metrics or {},
        }
        if self.risk_level:
            result["risk_level"] = self.risk_level
        if self.risk_interpretation:
            result["risk_interpretation"] = self.risk_interpretation
        return result


@dataclass
class DiffChange:
    """Represents a single change detected between source and target files."""

    change_type: ChangeType
    key: str
    source_line: Optional[int] = None  # Line number in source file (None for ADDED)
    target_line: Optional[int] = None  # Line number in target file (None for DELETED)
    source_value: Optional[str] = None  # Value in source file
    target_value: Optional[str] = None  # Value in target file
    keyword_changes: Optional[List[Dict[str, Any]]] = None  # Keyword/token changes with positions (only for MODIFIED and MOVED_AND_MODIFIED)
    message: Optional[str] = None  # Descriptive message about the change
    complexity: Optional[BlockComplexity] = None  # Complexity metrics for this change

    def to_dict(self, exclude_complexity: bool = False) -> dict:
        """Convert to dictionary for JSON serialization.
        
        Args:
            exclude_complexity: If True, exclude complexity field from output.
        """
        result = {
            "type": self.change_type.value,
            "key": self.key,
            "source_line": self.source_line,
            "target_line": self.target_line,
            "source_value": self.source_value,
            "target_value": self.target_value,
        }
        # Add keyword_changes only for MODIFIED and MOVED_AND_MODIFIED types
        if self.keyword_changes is not None and self.change_type in (ChangeType.MODIFIED, ChangeType.MOVED_AND_MODIFIED):
            result["keyword_changes"] = self.keyword_changes
        if self.message:
            result["message"] = self.message
        if self.complexity and not exclude_complexity:
            result["complexity"] = self.complexity.to_dict()
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
    overall_complexity: Optional[float] = None  # Overall change complexity score
    overall_risk_level: Optional[str] = None  # Overall risk level classification
    overall_risk_interpretation: Optional[str] = None  # Overall risk interpretation

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

    def to_dict(self, exclude_complexity: bool = False) -> dict:
        """Convert to dictionary for JSON serialization.
        
        Args:
            exclude_complexity: If True, exclude complexity fields from output.
        """
        if self.summary is None:
            self.calculate_summary()
        result = {
            "source_file": self.source_file,
            "target_file": self.target_file,
            "changes": [change.to_dict(exclude_complexity=exclude_complexity) for change in self.changes],
            "summary": self.summary.to_dict() if self.summary else {},
        }
        if not exclude_complexity:
            if self.overall_complexity is not None:
                result["overall_complexity"] = self.overall_complexity
            if self.overall_risk_level:
                result["overall_risk_level"] = self.overall_risk_level
            if self.overall_risk_interpretation:
                result["overall_risk_interpretation"] = self.overall_risk_interpretation
        return result