"""Complexity calculator for property file changes.

Calculates complexity based on the formula:
Properties_BlockScore = (KeyCount × KEYS) + (MaxDepth × DEPTH) + (DuplicateOrOverrideCount × DUPLICATES) + (LOC × LOC)

Total complexity is the sum of all block scores, then normalized.
"""

from typing import Dict, List, Optional, Tuple

from ..config import METRIC_WEIGHTS, NORMALIZATION_CONFIG, RISK_THRESHOLDS, RISK_LEVELS
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
    
    Normalization:
    - Raw scores are normalized using asymptotic scaling
    - Normalized scores fit within risk thresholds defined in config
    
    Configuration is loaded from ast_diff_poc.config.complexity_config
    """

    def __init__(self):
        """Initialize the calculator with configuration values."""
        # Load weights from config
        self.weight_keys = METRIC_WEIGHTS.KEYS
        self.weight_depth = METRIC_WEIGHTS.DEPTH
        self.weight_duplicates = METRIC_WEIGHTS.DUPLICATES
        self.weight_loc = METRIC_WEIGHTS.LOC
        
        # Load normalization config
        self.norm_max_scale = NORMALIZATION_CONFIG.MAX_SCALE
        self.norm_half_point = NORMALIZATION_CONFIG.HALF_POINT
        
        # Load risk thresholds
        self.risk_low_max = RISK_THRESHOLDS.LOW_MAX
        self.risk_medium_max = RISK_THRESHOLDS.MEDIUM_MAX
        self.risk_high_max = RISK_THRESHOLDS.HIGH_MAX

    def calculate_all_blocks_complexity(
        self, changes: List[DiffChange]
    ) -> Dict:
        """Calculate complexity for all changed blocks and sum them.
        
        Args:
            changes: List of all diff changes.
            
        Returns:
            Dictionary containing total complexity (raw and normalized), risk level, and block details.
        """
        if not changes:
            return {
                "total_complexity": 0.0,
                "total_complexity_raw": 0.0,
                "risk_level": RISK_LEVELS.NO_CHANGES[0],
                "risk_interpretation": RISK_LEVELS.NO_CHANGES[1],
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
        
        # Sum all block scores (raw total)
        total_complexity_raw = sum(block_scores)
        
        # Normalize the total complexity
        total_complexity_normalized = self._normalize_complexity(total_complexity_raw)
        
        # Classify risk level based on normalized score
        risk_level, risk_interpretation = self.classify_risk_level(total_complexity_normalized)
        
        return {
            "total_complexity": total_complexity_normalized,
            "total_complexity_raw": round(total_complexity_raw, 2),
            "risk_level": risk_level,
            "risk_interpretation": risk_interpretation,
            "blocks_calculated": len(block_details),
            "blocks_skipped": len(skipped_blocks),
            "blocks": block_details,
            "skipped": skipped_blocks,
        }
    
    def _normalize_complexity(self, raw_score: float) -> float:
        """Normalize raw complexity score using asymptotic scaling.
        
        Formula: normalized = MAX_SCALE × (raw_score / (raw_score + HALF_POINT))
        
        Configuration values are loaded from complexity_config.
        
        Args:
            raw_score: The raw (un-normalized) complexity score.
            
        Returns:
            Normalized complexity score.
        """
        if raw_score <= 0:
            return 0.0
        
        normalized = self.norm_max_scale * (
            raw_score / (raw_score + self.norm_half_point)
        )
        return round(normalized, 2)

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
                "risk_level": RISK_LEVELS.SKIPPED[0],
                "risk_interpretation": skip_reason,
                "metrics": {
                    "key_count": {"raw": 0, "weight": self.weight_keys, "weighted": 0.0},
                    "max_depth": {"raw": 0, "weight": self.weight_depth, "weighted": 0.0},
                    "duplicate_count": {"raw": 0, "weight": self.weight_duplicates, "weighted": 0.0},
                    "loc": {"raw": 0, "weight": self.weight_loc, "weighted": 0.0},
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
        key_count_weighted = round(key_count * self.weight_keys, 2)
        
        # Metric 2: MaxDepth (dot-separated segments)
        max_depth = self._calculate_key_depth(change.key)
        max_depth_weighted = round(max_depth * self.weight_depth, 2)
        
        # Metric 3: DuplicateOrOverrideCount
        duplicate_count = self._calculate_duplicate_count(change, key_occurrences)
        duplicate_count_weighted = round(duplicate_count * self.weight_duplicates, 2)
        
        # Metric 4: LOC (lines of code for this block)
        loc = self._calculate_loc(change)
        loc_weighted = round(loc * self.weight_loc, 2)
        
        # Calculate weighted block score
        block_score = key_count_weighted + max_depth_weighted + duplicate_count_weighted + loc_weighted
        
        return {
            "block_score": round(block_score, 2),
            "metrics": {
                "key_count": {
                    "raw": key_count,
                    "weight": self.weight_keys,
                    "weighted": key_count_weighted,
                },
                "max_depth": {
                    "raw": max_depth,
                    "weight": self.weight_depth,
                    "weighted": max_depth_weighted,
                },
                "duplicate_count": {
                    "raw": duplicate_count,
                    "weight": self.weight_duplicates,
                    "weighted": duplicate_count_weighted,
                },
                "loc": {
                    "raw": loc,
                    "weight": self.weight_loc,
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

        Risk level thresholds are loaded from complexity_config.

        Args:
            score: Total complexity score (normalized).

        Returns:
            Tuple of (risk_level, interpretation).
        """
        if score <= self.risk_low_max:
            return RISK_LEVELS.LOW
        elif score <= self.risk_medium_max:
            return RISK_LEVELS.MEDIUM
        elif score <= self.risk_high_max:
            return RISK_LEVELS.HIGH
        else:
            return RISK_LEVELS.VERY_HIGH
