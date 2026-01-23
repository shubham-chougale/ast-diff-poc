"""Complexity calculator for property file changes."""

from typing import Dict, List, Optional

from ..models.ast_node import PropertyFileAST
from ..models.change_types import ChangeType
from ..models.diff_result import DiffChange


class PropertyComplexityCalculator:
    """Calculates complexity metrics for property file changes.
    
    Complexity is calculated based on changed properties only (ADDED, MOVED, MODIFIED, 
    DELETED, MOVED_AND_MODIFIED). All metrics (keys, depth, duplicates, file size) 
    are computed from the changed properties, then normalized and weighted to produce 
    structural complexity. Each change applies its change-type multiplier to get effective complexity.
    """

    # Normalization thresholds
    MAX_KEYS_THRESHOLD = 100
    MAX_DEPTH_THRESHOLD = 15
    AVG_DEPTH_THRESHOLD = 10
    MAX_DUPLICATES_THRESHOLD = 20
    MAX_LOC_THRESHOLD = 300

    # Weights for complexity metrics
    WEIGHT_KEYS = 0.40
    WEIGHT_DEPTH = 0.30
    WEIGHT_DUPLICATES = 0.20
    WEIGHT_FILE_SIZE = 0.10

    # Change type multipliers
    CHANGE_TYPE_MULTIPLIERS = {
        ChangeType.ADDED: 1.0,
        ChangeType.MODIFIED: 1.3,
        ChangeType.MOVED: 0.6,
        ChangeType.MOVED_AND_MODIFIED: 1.6,
        ChangeType.DELETED: 0.5,
    }

    def _calculate_changed_properties_metrics(self, changes: List[DiffChange]) -> Dict[str, int]:
        """Calculate metrics from changed properties only.
        
        This computes metrics based ONLY on the changed properties (ADDED, MOVED, 
        MODIFIED, DELETED, MOVED_AND_MODIFIED), not the entire file.
        
        This computes:
        - unique_keys: Number of unique keys in changed properties
        - max_depth: Maximum hierarchy depth across changed keys
        - avg_depth: Average hierarchy depth across changed keys
        - total_duplicates: Number of duplicate key occurrences within changed properties
        - file_size: Number of changed properties (LOC)
        
        Args:
            changes: List of all diff changes.
            
        Returns:
            Dictionary with changed-properties metric values.
        """
        if not changes:
            return {
                "unique_keys": 0,
                "max_depth": 0,
                "avg_depth": 0.0,
                "total_duplicates": 0,
                "file_size": 0,
            }
        
        # Collect keys from changed properties only
        key_set = set()
        depth_list = []
        key_counts = {}
        
        for change in changes:
            if change.key:
                key_set.add(change.key)
                depth = change.key.count(".") + 1
                depth_list.append(depth)
                key_counts[change.key] = key_counts.get(change.key, 0) + 1
        
        # Calculate metrics from changed properties
        unique_keys = len(key_set)
        max_depth = max(depth_list) if depth_list else 0
        avg_depth = sum(depth_list) / len(depth_list) if depth_list else 0.0
        
        # Total duplicates = sum of (occurrences - 1) for all keys that appear more than once in changes
        total_duplicates = sum(count - 1 for count in key_counts.values() if count > 1)
        file_size = len(changes)  # Number of changed properties
        
        return {
            "unique_keys": unique_keys,
            "max_depth": max_depth,
            "avg_depth": avg_depth,
            "total_duplicates": total_duplicates,
            "file_size": file_size,
        }

    def _calculate_base_structural_complexity(self, changes: List[DiffChange]) -> Dict:
        """Calculate base structural complexity from changed properties metrics.
        
        This computes the normalized and weighted structural complexity
        based on changed properties only.
        
        Args:
            changes: List of all diff changes.
            
        Returns:
            Dictionary containing normalized metrics and structural complexity.
        """
        # Calculate metrics from changed properties only
        metrics = self._calculate_changed_properties_metrics(changes)
        
        # Normalize metrics
        keys_norm = self._normalize_keys(metrics["unique_keys"])
        # Depth score combines normalized max_depth and avg_depth
        depth_norm = self._normalize_depth(metrics["max_depth"], metrics["avg_depth"])
        duplicates_norm = self._normalize_duplicates(metrics["total_duplicates"])
        file_size_norm = self._normalize_file_size(metrics["file_size"])
        
        # Calculate structural complexity (weighted sum)
        structural_complexity = (
            (keys_norm * self.WEIGHT_KEYS)
            + (depth_norm * self.WEIGHT_DEPTH)
            + (duplicates_norm * self.WEIGHT_DUPLICATES)
            + (file_size_norm * self.WEIGHT_FILE_SIZE)
        )
        
        return {
            "structural_complexity": round(structural_complexity, 2),
            "metrics": {
                "keys": {
                    "raw": metrics["unique_keys"],
                    "normalized": round(keys_norm, 2),
                },
                "depth": {
                    "max_depth": metrics["max_depth"],
                    "avg_depth": round(metrics["avg_depth"], 2),
                    "normalized": round(depth_norm, 2),
                },
                "duplicates": {
                    "raw": metrics["total_duplicates"],
                    "normalized": round(duplicates_norm, 2),
                },
                "file_size": {
                    "raw": metrics["file_size"],
                    "normalized": round(file_size_norm, 2),
                },
            },
        }

    def calculate_block_complexity(
        self,
        change: DiffChange,
        source_ast: Optional[PropertyFileAST],
        target_ast: PropertyFileAST,
        all_changes: Optional[List[DiffChange]] = None,
        base_complexity: Optional[Dict] = None,
    ) -> Dict:
        """Calculate complexity for a single changed block (property).

        Uses changed-properties metrics to compute base structural complexity,
        then applies change-type multiplier for this specific change.

        Args:
            change: The diff change representing the changed property.
            source_ast: Source file AST (optional, for context).
            target_ast: Target file AST (optional, kept for compatibility).
            all_changes: List of all changes (required to calculate changed-properties metrics).
            base_complexity: Pre-computed base complexity (optional, computed if not provided).

        Returns:
            Dictionary containing complexity metrics and scores.
        """
        # Calculate base structural complexity from changed properties only
        if base_complexity is None:
            if all_changes is None:
                # If no changes list provided, calculate for this single change only
                all_changes = [change]
            base_complexity = self._calculate_base_structural_complexity(all_changes)
        
        structural_complexity = base_complexity["structural_complexity"]
        
        # Get change type multiplier
        change_multiplier = self.CHANGE_TYPE_MULTIPLIERS.get(
            change.change_type, 1.0
        )

        # Calculate effective complexity
        effective_complexity = structural_complexity * change_multiplier

        # Classify risk level
        risk_level, risk_interpretation = self.classify_risk_level(effective_complexity)

        return {
            "structural_complexity": structural_complexity,
            "change_type_multiplier": change_multiplier,
            "effective_complexity": round(effective_complexity, 2),
            "risk_level": risk_level,
            "risk_interpretation": risk_interpretation,
            "metrics": base_complexity["metrics"],
        }

    def _normalize_keys(self, keys: int) -> float:
        """Normalize keys metric to 0-100 scale."""
        normalized = min((keys / self.MAX_KEYS_THRESHOLD) * 100, 100)
        return normalized

    def _normalize_depth(self, max_depth: int, avg_depth: float) -> float:
        """Normalize depth metric to 0-100 scale.

        According to spec:
        - Normalized Max Depth = min((max_depth / 15) × 100, 100)
        - Normalized Avg Depth = min((avg_depth / 10) × 100, 100)
        - Depth Score = (Normalized Max + Normalized Avg) / 2

        Args:
            max_depth: Maximum hierarchy depth.
            avg_depth: Average hierarchy depth.

        Returns:
            Combined normalized depth score (0-100).
        """
        # Normalize max depth using threshold 15
        max_norm = min((max_depth / self.MAX_DEPTH_THRESHOLD) * 100, 100)
        
        # Normalize avg depth using threshold 10
        avg_norm = min((avg_depth / self.AVG_DEPTH_THRESHOLD) * 100, 100)
        
        # Combine: average of normalized max and avg
        depth_score = (max_norm + avg_norm) / 2
        
        return depth_score

    def _normalize_duplicates(self, duplicates: int) -> float:
        """Normalize duplicates metric to 0-100 scale."""
        normalized = min((duplicates / self.MAX_DUPLICATES_THRESHOLD) * 100, 100)
        return normalized

    def _normalize_file_size(self, loc: int) -> float:
        """Normalize file size (LOC) metric to 0-100 scale."""
        normalized = min((loc / self.MAX_LOC_THRESHOLD) * 100, 100)
        return normalized

    def classify_risk_level(self, score: float) -> tuple[str, str]:
        """Classify complexity score into risk level.

        Args:
            score: Complexity score (0-100 or effective complexity).

        Returns:
            Tuple of (risk_level, interpretation).
        """
        if score <= 25:
            return ("Low", "Simple, stable, and easy to maintain")
        elif score <= 50:
            return ("Medium", "Moderate complexity; review recommended")
        elif score <= 75:
            return ("High", "Complex structure; refactoring advised")
        else:
            return ("Very High", "Critical complexity; high failure risk")

    # def calculate_overall_complexity(
    #     self, changes: List[DiffChange], source_ast: Optional[PropertyFileAST], target_ast: PropertyFileAST
    # ) -> Dict:
    #     """Calculate overall change complexity using file-level metrics.
    #
    #     Overall complexity is based on:
    #     1. File-level structural complexity (computed once from entire file)
    #     2. Aggregate change-type multiplier (weighted average based on change distribution)
    #     3. Scale factor based on number of changes (to account for change volume)
    #
    #     This approach ensures complexity is file-scoped, not row-by-row additive.
    #
    #     Args:
    #         changes: List of all diff changes.
    #         source_ast: Source file AST (optional).
    #         target_ast: Target file AST.
    #
    #     Returns:
    #         Dictionary containing overall_complexity, risk_level, and risk_interpretation.
    #     """
    #     if not changes:
    #         return {
    #             "overall_complexity": 0.0,
    #             "risk_level": "Low",
    #             "risk_interpretation": "No changes detected",
    #         }
    #     
    #     # Calculate base structural complexity once (file-level)
    #     base_complexity = self._calculate_base_structural_complexity(target_ast)
    #     structural_complexity = base_complexity["structural_complexity"]
    #     
    #     # Calculate aggregate change-type multiplier
    #     # Use weighted average: sum of (multiplier × count) / total count
    #     change_type_counts = {}
    #     for change in changes:
    #         change_type = change.change_type
    #         change_type_counts[change_type] = change_type_counts.get(change_type, 0) + 1
    #     
    #     total_changes = len(changes)
    #     weighted_multiplier_sum = 0.0
    #     
    #     for change_type, count in change_type_counts.items():
    #         multiplier = self.CHANGE_TYPE_MULTIPLIERS.get(change_type, 1.0)
    #         weighted_multiplier_sum += multiplier * count
    #     
    #     aggregate_multiplier = weighted_multiplier_sum / total_changes if total_changes > 0 else 1.0
    #     
    #     # Apply scale factor for change volume
    #     # More changes = slightly higher complexity, but with diminishing returns
    #     # Formula: 1 + (num_changes / 100) * 0.1 (max 10% increase for 100+ changes)
    #     change_volume_factor = 1.0 + min((total_changes / 100.0) * 0.1, 0.1)
    #     
    #     # Overall complexity = base structural complexity × aggregate multiplier × volume factor
    #     overall_complexity = structural_complexity * aggregate_multiplier * change_volume_factor
    #     
    #     # Cap at 100 for risk classification
    #     normalized_score = min(overall_complexity, 100.0)
    #     risk_level, risk_interpretation = self.classify_risk_level(normalized_score)
    #
    #     return {
    #         "overall_complexity": round(overall_complexity, 2),
    #         "risk_level": risk_level,
    #         "risk_interpretation": risk_interpretation,
    #     }
