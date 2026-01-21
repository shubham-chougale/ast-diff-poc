"""Core diff engine for detecting structural changes."""

from typing import List, Optional

from ..models.ast_node import PropertyFileAST, PropertyNode
from ..models.change_types import ChangeType
from ..models.diff_result import DiffChange, DiffResult
from ..parser.normalization import Normalizer
from .matcher import NodeMatcher


class DiffEngine:
    """Engine for detecting structural differences between property files."""

    def __init__(self, normalize: bool = True):
        """Initialize the diff engine.

        Args:
            normalize: Whether to normalize ASTs before comparison.
        """
        self.normalize = normalize
        self.normalizer = Normalizer() if normalize else None


    def compute_diff(
        self, source_ast: PropertyFileAST, target_ast: PropertyFileAST
    ) -> DiffResult:
        """Compute the diff between source and target ASTs.

        Args:
            source_ast: The source file AST.
            target_ast: The target file AST.

        Returns:
            DiffResult containing all detected changes.
        """
        # Normalize if requested
        if self.normalize:
            source_ast = self.normalizer.normalize_ast(source_ast)
            target_ast = self.normalizer.normalize_ast(target_ast)

        # Match nodes
        matcher = NodeMatcher(source_ast, target_ast)
        matching = matcher.match_nodes()

        # Detect changes
        changes: List[DiffChange] = []

        # First, identify deletions and additions to calculate line adjustments
        deletions = matcher.get_unmatched_source_nodes()
        additions = matcher.get_unmatched_target_nodes()
        
        # Create sets of deletion and addition line numbers for quick lookup
        deletion_lines = {node.line_number for node in deletions}
        addition_lines = {node.line_number for node in additions}

        # Process matched pairs
        for source_node, target_node in matcher.get_matched_pairs():
            change = self._classify_change(
                source_node, 
                target_node,
                deletion_lines,
                addition_lines
            )
            if change:
                changes.append(change)

        # Process unmatched source nodes (deletions)
        for source_node in deletions:
            changes.append(
                DiffChange(
                    change_type=ChangeType.DELETED,
                    key=source_node.key,
                    source_line=source_node.line_number,
                    source_value=source_node.value,
                )
            )

        # Process unmatched target nodes (additions)
        for target_node in additions:
            changes.append(
                DiffChange(
                    change_type=ChangeType.ADDED,
                    key=target_node.key,
                    target_line=target_node.line_number,
                    target_value=target_node.value,
                )
            )

        # Sort changes by source_line number (None values go to the end)
        changes.sort(key=lambda c: (c.source_line is None, c.source_line or 0))

        # Create result
        result = DiffResult(
            source_file=source_ast.file_path or "source",
            target_file=target_ast.file_path or "target",
            changes=changes,
        )
        result.calculate_summary()

        return result

    def _classify_change(
        self, 
        source_node: PropertyNode, 
        target_node: PropertyNode,
        deletion_lines: set = None,
        addition_lines: set = None
    ) -> Optional[DiffChange]:
        """Classify the type of change between two matched nodes.

        Args:
            source_node: The source node.
            target_node: The target node.
            deletion_lines: Set of line numbers where deletions occurred (for line adjustment).
            addition_lines: Set of line numbers where additions occurred (for line adjustment).

        """
        if deletion_lines is None:
            deletion_lines = set()
        if addition_lines is None:
            addition_lines = set()
            
        key_changed = source_node.key != target_node.key
        value_changed = source_node.value != target_node.value
        line_changed = source_node.line_number != target_node.line_number

        # Both key and value are the same
        if not key_changed and not value_changed:
            if line_changed:
                # Calculate expected target line after accounting for deletions/additions
                # Count deletions before source line
                deletions_before = sum(1 for line in deletion_lines if line < source_node.line_number)
                # Count additions before target line
                additions_before = sum(1 for line in addition_lines if line < target_node.line_number)
                
                # Expected target line = source line - deletions before + additions before
                expected_target_line = source_node.line_number - deletions_before + additions_before
                
                # If actual target line matches expected, it's just a positional shift, not a move
                if target_node.line_number == expected_target_line:
                    # This is just a positional shift due to deletions/additions above
                    return None
                else:
                    # True move - line number changed beyond what deletions/additions explain
                    return DiffChange(
                        change_type=ChangeType.MOVED,
                        key=source_node.key,
                        source_line=source_node.line_number,
                        target_line=target_node.line_number,
                        source_value=source_node.value,
                        target_value=target_node.value,
                        message=f"Moved as part of refactoring - check line {target_node.line_number}",
                    )
            else:
                # Completely unchanged
                return None

        # Key changed (shouldn't happen in normal matching, but handle it)
        if key_changed:
            # This is unusual - treat as deletion + addition
            return None  # Will be handled as separate deletion and addition

        # Value changed
        if value_changed:
            if line_changed:
                # Calculate expected target line after accounting for deletions/additions
                deletions_before = sum(1 for line in deletion_lines if line < source_node.line_number)
                additions_before = sum(1 for line in addition_lines if line < target_node.line_number)
                expected_target_line = source_node.line_number - deletions_before + additions_before
                
                # If actual target line matches expected, it's MODIFIED (not MOVED_AND_MODIFIED)
                if target_node.line_number == expected_target_line:
                    return DiffChange(
                        change_type=ChangeType.MODIFIED,
                        key=source_node.key,
                        source_line=source_node.line_number,
                        target_line=target_node.line_number,
                        source_value=source_node.value,
                        target_value=target_node.value,
                    )
                else:
                    # Value changed and moved = MOVED_AND_MODIFIED
                    return DiffChange(
                        change_type=ChangeType.MOVED_AND_MODIFIED,
                        key=source_node.key,
                        source_line=source_node.line_number,
                        target_line=target_node.line_number,
                        source_value=source_node.value,
                        target_value=target_node.value,
                        message=f"Moved and modified as part of refactoring - check line {target_node.line_number}",
                    )
            else:
                # Value changed, same line = MODIFIED
                return DiffChange(
                    change_type=ChangeType.MODIFIED,
                    key=source_node.key,
                    source_line=source_node.line_number,
                    target_line=target_node.line_number,
                    source_value=source_node.value,
                    target_value=target_node.value,
                )

        return None
