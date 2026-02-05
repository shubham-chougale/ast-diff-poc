"""Complexity calculator for property file changes.

Calculates complexity based on the formula:
Properties_BlockScore = (KeyCount × 0.40) + (MaxDepth × 0.30) + (DuplicateOrOverrideCount × 0.20) + (LOC × 0.10)

Total complexity is the sum of all block scores.
"""

from typing import Dict, List, Optional, Tuple

from ..models.change_types import ChangeType
from ..models.diff_result import DiffChange


class PropertyComplexityCalculator:
    """Calculates complexity metrics for property file changes.
    
    Complexity is calculated per changed block using:
    - KeyCount: Count of keys in the block (1 for single property)
    - MaxDepth: Number of dot-separated segments in the key
    - DuplicateOrOverrideCount: Keys appearing multiple times or overrides
    - LOC: Lines of code for the block
    
    Skipped changes (no complexity contribution):
    - MOVED: Position-only change, no functional impact
    - MODIFIED without duplicates: Simple value change, no structural impact
    """

    # Weights for complexity metrics
    WEIGHT_KEYS = 0.40
    WEIGHT_DEPTH = 0.30
    WEIGHT_DUPLICATES = 0.20
    WEIGHT_LOC = 0.10

    def calculate_all_blocks_complexity(
        self, changes: List[DiffChange]
    ) -> Dict:
        """Calculate complexity for all changed blocks and sum them.
        
        Args:
            changes: List of all diff changes.
            
        Returns:
            Dictionary containing total complexity, risk level, and block details.
        """
        if not changes:
            return {
                "total_complexity": 0.0,
                "risk_level": "Low",
                "risk_interpretation": "No changes detected",
                "blocks_calculated": 0,
                "blocks_skipped": 0,
                "blocks": [],
                "skipped": [],
            }
        
        # Pre-calculate key occurrences for duplicate detection
        key_occurrences = self._count_key_occurrences(changes)
        
        block_scores = []
        block_details = []
        skipped_blocks = []
        
        for change in changes:
            # Check if this change should be skipped
            skip_reason = self._should_skip_change(change, key_occurrences)
            
            if skip_reason:
                skipped_blocks.append({
                    "key": change.key,
                    "type": change.change_type.value,
                    "reason": skip_reason,
                })
                continue
            
            # Calculate block complexity
            block_result = self._calculate_single_block_complexity(
                change, key_occurrences
            )
            
            block_scores.append(block_result["block_score"])
            block_details.append({
                "key": change.key,
                "type": change.change_type.value,
                "block_score": block_result["block_score"],
                "metrics": block_result["metrics"],
            })
        
        # Sum all block scores
        total_complexity = sum(block_scores)
        
        # Classify risk level
        risk_level, risk_interpretation = self.classify_risk_level(total_complexity)
        
        return {
            "total_complexity": round(total_complexity, 2),
            "risk_level": risk_level,
            "risk_interpretation": risk_interpretation,
            "blocks_calculated": len(block_details),
            "blocks_skipped": len(skipped_blocks),
            "blocks": block_details,
            "skipped": skipped_blocks,
        }

    def calculate_block_complexity(
        self,
        change: DiffChange,
        source_ast: Optional[object] = None,
        target_ast: Optional[object] = None,
        all_changes: Optional[List[DiffChange]] = None,
        base_complexity: Optional[Dict] = None,
    ) -> Dict:
        """Calculate complexity for a single changed block.
        
        This method maintains backward compatibility with the diff engine.

        Args:
            change: The diff change representing the changed property.
            source_ast: Source file AST (optional, kept for compatibility).
            target_ast: Target file AST (optional, kept for compatibility).
            all_changes: List of all changes for duplicate detection.
            base_complexity: Pre-computed base complexity (optional, unused in new logic).

        Returns:
            Dictionary containing complexity metrics and scores.
        """
        if all_changes is None:
            all_changes = [change]
        
        # Pre-calculate key occurrences
        key_occurrences = self._count_key_occurrences(all_changes)
        
        # Check if this change should be skipped
        skip_reason = self._should_skip_change(change, key_occurrences)
        
        if skip_reason:
            # Return zero complexity for skipped changes
            return {
                "structural_complexity": 0.0,
                "change_type_multiplier": 0.0,
                "effective_complexity": 0.0,
                "risk_level": "Skipped",
                "risk_interpretation": skip_reason,
                "metrics": {
                    "key_count": {"raw": 0, "weight": self.WEIGHT_KEYS, "weighted": 0.0},
                    "max_depth": {"raw": 0, "weight": self.WEIGHT_DEPTH, "weighted": 0.0},
                    "duplicate_count": {"raw": 0, "weight": self.WEIGHT_DUPLICATES, "weighted": 0.0},
                    "loc": {"raw": 0, "weight": self.WEIGHT_LOC, "weighted": 0.0},
                },
                "skipped": True,
                "skip_reason": skip_reason,
            }
        
        # Calculate block complexity
        block_result = self._calculate_single_block_complexity(change, key_occurrences)
        
        # Map to the expected structure for backward compatibility
        return {
            "structural_complexity": block_result["block_score"],
            "change_type_multiplier": 1.0,  # Not used in new logic
            "effective_complexity": block_result["block_score"],
            "risk_level": block_result.get("risk_level"),
            "risk_interpretation": block_result.get("risk_interpretation"),
            "metrics": block_result["metrics"],
            "skipped": False,
        }

    def _calculate_single_block_complexity(
        self, change: DiffChange, key_occurrences: Dict[str, int]
    ) -> Dict:
        """Calculate complexity score for a single block.
        
        Formula: Properties_BlockScore = (KeyCount × 0.40) + (MaxDepth × 0.30) 
                                        + (DuplicateOrOverrideCount × 0.20) + (LOC × 0.10)
        
        Args:
            change: The diff change.
            key_occurrences: Dictionary mapping keys to their occurrence counts.
            
        Returns:
            Dictionary with block_score and metrics including weighted values.
        """
        # Metric 1: KeyCount (1 for single property)
        key_count = 1
        key_count_weighted = round(key_count * self.WEIGHT_KEYS, 2)
        
        # Metric 2: MaxDepth (dot-separated segments)
        max_depth = self._calculate_key_depth(change.key)
        max_depth_weighted = round(max_depth * self.WEIGHT_DEPTH, 2)
        
        # Metric 3: DuplicateOrOverrideCount
        duplicate_count = self._calculate_duplicate_count(change, key_occurrences)
        duplicate_count_weighted = round(duplicate_count * self.WEIGHT_DUPLICATES, 2)
        
        # Metric 4: LOC (lines of code for this block)
        loc = self._calculate_loc(change)
        loc_weighted = round(loc * self.WEIGHT_LOC, 2)
        
        # Calculate weighted block score
        block_score = key_count_weighted + max_depth_weighted + duplicate_count_weighted + loc_weighted
        
        return {
            "block_score": round(block_score, 2),
            "metrics": {
                "key_count": {
                    "raw": key_count,
                    "weight": self.WEIGHT_KEYS,
                    "weighted": key_count_weighted,
                },
                "max_depth": {
                    "raw": max_depth,
                    "weight": self.WEIGHT_DEPTH,
                    "weighted": max_depth_weighted,
                },
                "duplicate_count": {
                    "raw": duplicate_count,
                    "weight": self.WEIGHT_DUPLICATES,
                    "weighted": duplicate_count_weighted,
                },
                "loc": {
                    "raw": loc,
                    "weight": self.WEIGHT_LOC,
                    "weighted": loc_weighted,
                },
            },
        }

    def _should_skip_change(
        self, change: DiffChange, key_occurrences: Dict[str, int]
    ) -> Optional[str]:
        """Determine if a change should be skipped from complexity calculation.
        
        Skip rules:
        1. MOVED: Position-only change, no functional impact
        2. MODIFIED with no duplicates: Simple value change, no structural impact
        
        Args:
            change: The diff change.
            key_occurrences: Dictionary mapping keys to their occurrence counts.
            
        Returns:
            Skip reason string if should skip, None otherwise.
        """
        # Rule 1: Skip MOVED changes
        if change.change_type == ChangeType.MOVED:
            return "Position-only change, no functional impact"
        
        # Rule 2: Skip MODIFIED with no duplicates
        if change.change_type == ChangeType.MODIFIED:
            has_duplicates = key_occurrences.get(change.key, 0) > 1
            if not has_duplicates:
                return "Simple value change, no duplicates"
        
        return None

    def _count_key_occurrences(self, changes: List[DiffChange]) -> Dict[str, int]:
        """Count occurrences of each key across all changes.
        
        Args:
            changes: List of all diff changes.
            
        Returns:
            Dictionary mapping keys to their occurrence counts.
        """
        key_counts: Dict[str, int] = {}
        for change in changes:
            if change.key:
                key_counts[change.key] = key_counts.get(change.key, 0) + 1
        return key_counts

    def _calculate_key_depth(self, key: str) -> int:
        """Calculate hierarchy depth of a key.
        
        Depth = number of dot-separated segments.
        Example: "app.database.connection.url" → 4
        
        Args:
            key: The property key.
            
        Returns:
            Depth as integer.
        """
        if not key:
            return 0
        return key.count(".") + 1

    def _calculate_duplicate_count(
        self, change: DiffChange, key_occurrences: Dict[str, int]
    ) -> int:
        """Calculate duplicate/override count for a change.
        
        Counts:
        - +1 if key appears multiple times in changes
        - +1 if this is a MODIFIED change (value override)
        
        Args:
            change: The diff change.
            key_occurrences: Dictionary mapping keys to their occurrence counts.
            
        Returns:
            Duplicate count as integer.
        """
        duplicate_count = 0
        
        # Check if key appears multiple times
        occurrences = key_occurrences.get(change.key, 0)
        if occurrences > 1:
            duplicate_count += 1
        
        # MODIFIED counts as an override (value changed)
        if change.change_type in (ChangeType.MODIFIED, ChangeType.MOVED_AND_MODIFIED):
            duplicate_count += 1
        
        return duplicate_count

    def _calculate_loc(self, change: DiffChange) -> int:
        """Calculate lines of code for a change block.
        
        For single-line properties, LOC = 1.
        For multi-line values (using \\ continuation), count all lines.
        
        Args:
            change: The diff change.
            
        Returns:
            LOC as integer.
        """
        # Use target_value for ADDED/MODIFIED, source_value for DELETED
        value = change.target_value or change.source_value
        
        if not value:
            return 1
        
        # Count newlines for multi-line values
        line_count = value.count("\n") + 1
        return max(1, line_count)

    def classify_risk_level(self, score: float) -> Tuple[str, str]:
        """Classify complexity score into risk level.

        Risk Level Ranges:
        - 0-10: Low
        - 10-20: Medium
        - 20-30: High
        - >30: Very High

        Args:
            score: Total complexity score.

        Returns:
            Tuple of (risk_level, interpretation).
        """
        if score <= 10:
            return ("Low", "Simple, stable, and easy to maintain")
        elif score <= 20:
            return ("Medium", "Moderate complexity; review recommended")
        elif score <= 30:
            return ("High", "Complex structure; refactoring advised")
        else:
            return ("Very High", "Critical complexity; high failure risk")
