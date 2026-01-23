"""Core diff engine for detecting structural changes."""

import difflib
from typing import Dict, List, Optional

from ..complexity.property_complexity import PropertyComplexityCalculator
from ..exceptions import DiffCalculationException, TokenizationException, NormalizationException
from ..models.ast_node import PropertyFileAST, PropertyNode
from ..models.change_types import ChangeType
from ..models.diff_result import BlockComplexity, DiffChange, DiffResult
from ..parser.normalization import Normalizer
from ..utils.logger import get_logger
from .matcher import NodeMatcher

logger = get_logger(__name__)


class DiffEngine:
    """Engine for detecting structural differences between property files."""

    def __init__(self, normalize: bool = True, calculate_complexity: bool = True):
        """Initialize the diff engine.

        Args:
            normalize: Whether to normalize ASTs before comparison.
            calculate_complexity: Whether to calculate complexity scores for changes.
        """
        self.normalize = normalize
        self.normalizer = Normalizer() if normalize else None
        self.calculate_complexity = calculate_complexity
        self.complexity_calculator = (
            PropertyComplexityCalculator() if calculate_complexity else None
        )


    def compute_diff(
        self, source_ast: PropertyFileAST, target_ast: PropertyFileAST
    ) -> DiffResult:
        """Compute the diff between source and target ASTs.

        Args:
            source_ast: The source file AST.
            target_ast: The target file AST.

        Returns:
            DiffResult containing all detected changes.
            
        Raises:
            NormalizationException: If AST normalization fails.
            DiffCalculationException: If diff calculation fails.
        """
        try:
            logger.info(f"Computing diff between source: {source_ast.file_path or 'unknown'} and target: {target_ast.file_path or 'unknown'}")
            
            # Normalize if requested
            if self.normalize:
                try:
                    logger.debug("Normalizing source AST")
                    source_ast = self.normalizer.normalize_ast(source_ast)
                    logger.debug("Normalizing target AST")
                    target_ast = self.normalizer.normalize_ast(target_ast)
                except Exception as e:
                    logger.error(f"AST normalization failed: {str(e)}", exc_info=True)
                    raise NormalizationException(f"Failed to normalize AST: {str(e)}") from e

            # Match nodes
            logger.debug("Matching nodes between source and target ASTs")
            matcher = NodeMatcher(source_ast, target_ast)
            matching = matcher.match_nodes()

            # Detect changes
            changes: List[DiffChange] = []

            # First, identify deletions and additions to calculate line adjustments
            deletions = matcher.get_unmatched_source_nodes()
            additions = matcher.get_unmatched_target_nodes()
            
            logger.debug(f"Found {len(deletions)} deletions and {len(additions)} additions")
            
            # Create sets of deletion and addition line numbers for quick lookup
            deletion_lines = {node.line_number for node in deletions}
            addition_lines = {node.line_number for node in additions}

            # Process matched pairs
            logger.debug("Processing matched node pairs")
            for source_node, target_node in matcher.get_matched_pairs():
                try:
                    change = self._classify_change(
                        source_node, 
                        target_node,
                        deletion_lines,
                        addition_lines
                    )
                    if change:
                        changes.append(change)
                except Exception as e:
                    logger.warning(f"Failed to classify change for key {source_node.key}: {str(e)}", exc_info=True)
                    # Continue processing other changes

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
            logger.debug(f"Total changes detected: {len(changes)}")

            # Calculate complexity if requested
            if self.calculate_complexity and self.complexity_calculator:
                try:
                    logger.debug("Calculating complexity scores")
                    # Store original ASTs before normalization for complexity calculation
                    # (we need the original ASTs for context, but metrics are based on changed properties only)
                    original_source_ast = source_ast
                    original_target_ast = target_ast
                    
                    # Calculate base structural complexity from changed properties only
                    # This is computed from all changed properties, not the entire file
                    base_complexity = self.complexity_calculator._calculate_base_structural_complexity(
                        changes
                    )
                    
                    # Apply change-type multipliers for each change
                    for change in changes:
                        try:
                            complexity_data = self.complexity_calculator.calculate_block_complexity(
                                change, original_source_ast, original_target_ast, changes, base_complexity
                            )
                            change.complexity = BlockComplexity(
                                structural_complexity=complexity_data["structural_complexity"],
                                change_type_multiplier=complexity_data["change_type_multiplier"],
                                effective_complexity=complexity_data["effective_complexity"],
                                risk_level=complexity_data.get("risk_level"),
                                risk_interpretation=complexity_data.get("risk_interpretation"),
                                metrics=complexity_data["metrics"],
                            )
                        except Exception as e:
                            logger.warning(f"Failed to calculate complexity for change {change.key}: {str(e)}", exc_info=True)
                            # Continue with other changes

                    # Commented out: Calculate overall complexity
                    # overall_complexity_data = self.complexity_calculator.calculate_overall_complexity(
                    #     changes, original_source_ast, original_target_ast
                    # )
                    # overall_complexity = overall_complexity_data.get("overall_complexity")
                    # overall_risk_level = overall_complexity_data.get("risk_level")
                    # overall_risk_interpretation = overall_complexity_data.get("risk_interpretation")
                    overall_complexity = None
                    overall_risk_level = None
                    overall_risk_interpretation = None
                except Exception as e:
                    logger.error(f"Complexity calculation failed: {str(e)}", exc_info=True)
                    # Continue without complexity
                    overall_complexity = None
                    overall_risk_level = None
                    overall_risk_interpretation = None
            else:
                overall_complexity = None
                overall_risk_level = None
                overall_risk_interpretation = None

            # Create result
            result = DiffResult(
                source_file=source_ast.file_path or "source",
                target_file=target_ast.file_path or "target",
                changes=changes,
                overall_complexity=overall_complexity,
                overall_risk_level=overall_risk_level,
                overall_risk_interpretation=overall_risk_interpretation,
            )
            result.calculate_summary()

            logger.info(f"Diff calculation completed successfully. Found {len(changes)} changes")
            return result
        except (NormalizationException, TokenizationException):
            # Re-raise specific exceptions as-is
            raise
        except Exception as e:
            logger.error(f"Diff calculation failed: {str(e)}", exc_info=True)
            raise DiffCalculationException(
                f"Failed to compute diff: {str(e)}",
                source_file=source_ast.file_path if source_ast else None,
                target_file=target_ast.file_path if target_ast else None
            ) from e

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words while preserving whitespace context.
        
        Args:
            text: Input text to tokenize.
            
        Returns:
            List of tokens (words).
            
        Raises:
            TokenizationException: If tokenization fails.
        """
        try:
            if text is None:
                raise TokenizationException("Cannot tokenize None value", value=None)
            
            # Split by whitespace to get words
            # This will split on any whitespace (spaces, tabs, newlines)
            tokens = text.split()
            logger.debug(f"Tokenized text into {len(tokens)} tokens")
            return tokens
        except Exception as e:
            logger.error(f"Tokenization failed: {str(e)}", exc_info=True)
            raise TokenizationException(f"Failed to tokenize text: {str(e)}", value=text) from e

    def _calculate_keyword_changes(self, source_value: str, target_value: str) -> List[Dict]:
        """Calculate keyword/token changes with character positions.
        
        This function performs token-level diffing and calculates character positions
        for each change in the original strings.
        
        Args:
            source_value: The original value.
            target_value: The modified value.
            
        Returns:
            List of dictionaries with token changes and positions.
            
        Raises:
            TokenizationException: If tokenization fails.
            DiffCalculationException: If keyword change calculation fails.
        """
        try:
            logger.debug(f"Calculating keyword changes for source_value length: {len(source_value) if source_value else 0}, target_value length: {len(target_value) if target_value else 0}")
            
            if not source_value:
                # If source is empty, everything in target is new
                return [{
                "old_token": None,
                "new_token": target_value,
                "old_start": 0,
                "old_end": 0,
                "new_start": 0,
                "new_end": len(target_value)
            }]
            if not target_value:
                # If target is empty, everything in source was deleted
                return [{
                    "old_token": source_value,
                    "new_token": None,
                    "old_start": 0,
                    "old_end": len(source_value),
                    "new_start": 0,
                    "new_end": 0
                }]
            
            # Check if only whitespace changed
            if source_value.strip() == target_value.strip():
                # Only whitespace difference - return empty list
                return []
            
            # Tokenize both strings
            source_tokens = self._tokenize(source_value)
            target_tokens = self._tokenize(target_value)
            
            # Use difflib to find token-level differences
            diff = difflib.SequenceMatcher(None, source_tokens, target_tokens)
            
            # Build maps to find character positions of tokens
            def build_token_positions(text: str, tokens: List[str]) -> List[tuple]:
                """Build a list of (start, end) positions for each token.
                
                This function finds the actual character positions of each token
                in the original text, accounting for whitespace.
                """
                positions = []
                current_pos = 0
                text_lower = text.lower()  # For case-insensitive matching if needed
                
                for i, token in enumerate(tokens):
                    # Try to find the token starting from current_pos
                    # First try exact match
                    token_pos = text.find(token, current_pos)
                    
                    if token_pos == -1:
                        # Try case-insensitive match
                        token_pos = text_lower.find(token.lower(), current_pos)
                        if token_pos != -1:
                            # Found case-insensitive, use actual position
                            token_pos = text.find(text[token_pos:token_pos+len(token)], token_pos)
                    
                    if token_pos != -1:
                        start = token_pos
                        end = token_pos + len(token)
                        positions.append((start, end))
                        # Move past this token and any whitespace
                        current_pos = end
                        # Skip whitespace
                        while current_pos < len(text) and text[current_pos].isspace():
                            current_pos += 1
                    else:
                        # Token not found, estimate position based on previous token
                        if positions:
                            # Use end of previous token + space
                            prev_end = positions[-1][1]
                            start = prev_end + 1  # +1 for space
                        else:
                            start = current_pos
                        end = start + len(token)
                        positions.append((start, end))
                        current_pos = end
                
                return positions
            
            source_positions = build_token_positions(source_value, source_tokens)
            target_positions = build_token_positions(target_value, target_tokens)
            
            # Collect token changes with positions
            keyword_changes = []
            for tag, i1, i2, j1, j2 in diff.get_opcodes():
                if tag == 'equal':
                    # Tokens are the same, skip
                    continue
                elif tag == 'delete':
                    # Tokens deleted from source
                    old_token = ' '.join(source_tokens[i1:i2])
                    old_start = source_positions[i1][0] if i1 < len(source_positions) else len(source_value)
                    old_end = source_positions[i2-1][1] if i2 > 0 and (i2-1) < len(source_positions) else len(source_value)
                    
                    keyword_changes.append({
                        "old_token": old_token,
                        "new_token": None,
                        "old_start": old_start,
                        "old_end": old_end,
                        "new_start": 0,
                        "new_end": 0
                    })
                elif tag == 'insert':
                    # Tokens inserted in target
                    new_token = ' '.join(target_tokens[j1:j2])
                    new_start = target_positions[j1][0] if j1 < len(target_positions) else len(target_value)
                    new_end = target_positions[j2-1][1] if j2 > 0 and (j2-1) < len(target_positions) else len(target_value)
                    
                    keyword_changes.append({
                        "old_token": None,
                        "new_token": new_token,
                        "old_start": 0,
                        "old_end": 0,
                        "new_start": new_start,
                        "new_end": new_end
                    })
                elif tag == 'replace':
                    # Tokens replaced
                    old_token = ' '.join(source_tokens[i1:i2])
                    new_token = ' '.join(target_tokens[j1:j2])
                    old_start = source_positions[i1][0] if i1 < len(source_positions) else len(source_value)
                    old_end = source_positions[i2-1][1] if i2 > 0 and (i2-1) < len(source_positions) else len(source_value)
                    new_start = target_positions[j1][0] if j1 < len(target_positions) else len(target_value)
                    new_end = target_positions[j2-1][1] if j2 > 0 and (j2-1) < len(target_positions) else len(target_value)
                    
                    keyword_changes.append({
                        "old_token": old_token,
                        "new_token": new_token,
                        "old_start": old_start,
                        "old_end": old_end,
                        "new_start": new_start,
                        "new_end": new_end
                    })
            
            logger.debug(f"Calculated {len(keyword_changes)} keyword changes")
            return keyword_changes
        except TokenizationException:
            # Re-raise tokenization exceptions as-is
            raise
        except Exception as e:
            logger.error(f"Failed to calculate keyword changes: {str(e)}", exc_info=True)
            raise DiffCalculationException(
                f"Failed to calculate keyword changes: {str(e)}",
                source_file=None,
                target_file=None
            ) from e

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
                    keyword_changes = self._calculate_keyword_changes(
                        source_node.value, target_node.value
                    )
                    return DiffChange(
                        change_type=ChangeType.MODIFIED,
                        key=source_node.key,
                        source_line=source_node.line_number,
                        target_line=target_node.line_number,
                        source_value=source_node.value,
                        target_value=target_node.value,
                        keyword_changes=keyword_changes,
                    )
                else:
                    # Value changed and moved = MOVED_AND_MODIFIED
                    keyword_changes = self._calculate_keyword_changes(
                        source_node.value, target_node.value
                    )
                    return DiffChange(
                        change_type=ChangeType.MOVED_AND_MODIFIED,
                        key=source_node.key,
                        source_line=source_node.line_number,
                        target_line=target_node.line_number,
                        source_value=source_node.value,
                        target_value=target_node.value,
                        keyword_changes=keyword_changes,
                        message=f"Moved and modified as part of refactoring - check line {target_node.line_number}",
                    )
            else:
                # Value changed, same line = MODIFIED
                keyword_changes = self._calculate_keyword_changes(
                    source_node.value, target_node.value
                )
                return DiffChange(
                    change_type=ChangeType.MODIFIED,
                    key=source_node.key,
                    source_line=source_node.line_number,
                    target_line=target_node.line_number,
                    source_value=source_node.value,
                    target_value=target_node.value,
                    keyword_changes=keyword_changes,
                )

        return None
