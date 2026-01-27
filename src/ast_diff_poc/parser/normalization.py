"""Normalization module for converting AST to unified internal format."""

import re
from typing import Dict, List, Tuple

from ..exceptions import NormalizationException
from ..models.ast_node import PropertyFileAST, PropertyNode
from ..utils.logger import get_logger

logger = get_logger(__name__)


class Normalizer:
    """Normalizes AST nodes to a unified internal format for comparison.
    
    Normalization rules for .properties files:
    1. Trim whitespace around keys, =, and values
    2. Ignore empty lines
    3. Ignore comment-only lines (#, !)
    4. Normalize line endings (CRLF → LF)
    5. Preserve original key order (no sorting)
    6. Preserve values as-is (HTML, special chars, escaped entities, numbers, case)
    """

    @staticmethod
    def normalize_content(content: str) -> str:
        """Normalize raw file content before parsing.
        
        This applies:
        - Line ending normalization (CRLF → LF)
        - Whitespace trimming around keys and values
        - Filtering empty lines and comments
        - Preserving original key order (no sorting)
        
        Args:
            content: Raw file content.
            
        Returns:
            Normalized content string.
            
        Raises:
            NormalizationException: If normalization fails.
        """
        try:
            logger.debug(f"Normalizing content (length: {len(content)})")
            
            # Step 1: Normalize line endings (CRLF → LF)
            content = content.replace('\r\n', '\n').replace('\r', '\n')
            
            # Step 2: Split into lines and process
            lines = content.split('\n')
            key_value_pairs: List[Tuple[str, str]] = []
            
            for line in lines:
                # Step 3: Strip the line
                stripped = line.strip()
                
                # Step 4: Ignore empty lines
                if not stripped:
                    continue
                
                # Step 5: Ignore comment-only lines (# or !)
                if stripped.startswith('#') or stripped.startswith('!'):
                    continue
                
                # Step 6: Parse key=value (handle both = and : as separators)
                # Trim whitespace around separator
                if '=' in stripped:
                    parts = stripped.split('=', 1)
                    key = parts[0].strip()
                    value = parts[1].strip() if len(parts) > 1 else ""
                elif ':' in stripped:
                    parts = stripped.split(':', 1)
                    key = parts[0].strip()
                    value = parts[1].strip() if len(parts) > 1 else ""
                else:
                    # Skip lines without separator
                    logger.warning(f"Skipping line without separator: {stripped[:50]}")
                    continue
                
                # Skip if key is empty
                if not key:
                    continue
                
                # Step 7: Preserve value as-is (no modification to HTML, special chars, etc.)
                key_value_pairs.append((key, value))
            
            # Step 8: Preserve original key order (no sorting)
            logger.debug(f"Normalized to {len(key_value_pairs)} key-value pairs, preserving original order")
            
            # Step 9: Rebuild normalized content
            normalized_lines = [f"{key}={value}" for key, value in key_value_pairs]
            normalized_content = '\n'.join(normalized_lines)
            
            return normalized_content
        except Exception as e:
            logger.error(f"Content normalization failed: {str(e)}", exc_info=True)
            raise NormalizationException(f"Failed to normalize content: {str(e)}") from e

    @staticmethod
    def normalize_ast(ast: PropertyFileAST) -> PropertyFileAST:
        """Normalize an AST to a canonical form using comprehensive normalization rules.

        Normalization flow:
        1. Extract all key-value pairs from AST
        2. Filter out empty lines and comments (already done by parser, but ensure)
        3. Trim whitespace around keys, separators, and values
        4. Preserve original key order (no sorting)
        5. Rebuild normalized AST

        Args:
            ast: The AST to normalize.

        Returns:
            A new normalized AST with keys in original order.

        Raises:
            NormalizationException: If normalization fails.
        """
        try:
            logger.debug(f"Normalizing AST with {len(ast.nodes)} property nodes")
            
            # Extract key-value pairs with original line numbers, filtering out empty lines and comments
            key_value_pairs: List[Tuple[str, str, int]] = []
            
            for node in ast.nodes:
                # Normalize key: trim whitespace
                normalized_key = node.key.strip()
                
                # Normalize value: trim whitespace around = but preserve value content
                # Values are preserved as-is (HTML, special chars, etc.)
                normalized_value = node.value.strip() if node.value else ""
                
                # Skip if key is empty (shouldn't happen, but safety check)
                if not normalized_key:
                    logger.warning(f"Skipping node with empty key at line {node.line_number}")
                    continue
                
                # Store original line number along with key-value pair
                key_value_pairs.append((normalized_key, normalized_value, node.line_number))
            
            # Preserve original key order (no sorting)
            logger.debug(f"Normalized to {len(key_value_pairs)} key-value pairs, preserving original order")
            
            # Rebuild normalized nodes preserving original line numbers
            normalized_nodes: List[PropertyNode] = []
            for key, value, original_line_num in key_value_pairs:
                # Create normalized node with standard format: key=value
                # Preserve original line number for accurate diff reporting
                normalized_node = PropertyNode(
                    line_number=original_line_num,
                    key=key,
                    value=value,
                    raw_line=f"{key}={value}",
                    leading_whitespace="",
                    separator="=",
                    trailing_whitespace_before_value="",
                    trailing_whitespace_after_value="",
                )
                normalized_nodes.append(normalized_node)

            # Return normalized AST (empty lines and comments are filtered out)
            return PropertyFileAST(
                nodes=normalized_nodes,
                empty_lines=[],  # Empty lines are ignored in normalization
                comments=[],  # Comments are ignored in normalization
                file_path=ast.file_path,
            )
        except Exception as e:
            logger.error(f"AST normalization failed: {str(e)}", exc_info=True)
            raise NormalizationException(f"Failed to normalize AST: {str(e)}") from e

    @staticmethod
    def normalize_key(key: str) -> str:
        """Normalize a property key for comparison.

        Args:
            key: The key to normalize.

        Returns:
            Normalized key.
        """
        return key.strip()

    @staticmethod
    def normalize_value(value: str) -> str:
        """Normalize a property value for comparison.

        According to normalization rules, values should be preserved as-is.
        However, for comparison purposes, we trim whitespace around the value
        (but preserve content like HTML, special chars, etc.).

        Args:
            value: The value to normalize.

        Returns:
            Normalized value (trimmed but content preserved).
        """
        # Trim whitespace but preserve value content as-is
        # (HTML, special chars, escaped entities, numbers, case are all preserved)
        return value.strip()

    @staticmethod
    def are_values_semantically_equivalent(value1: str, value2: str) -> bool:
        """Check if two values are semantically equivalent.

        This checks if values are the same after normalization,
        which handles cases like trailing whitespace differences.

        Args:
            value1: First value to compare.
            value2: Second value to compare.

        Returns:
            True if values are semantically equivalent.
        """
        return Normalizer.normalize_value(value1) == Normalizer.normalize_value(value2)
