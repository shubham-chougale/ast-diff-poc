"""Normalization module for converting AST to unified internal format."""

from typing import List

from ..models.ast_node import PropertyFileAST, PropertyNode


class Normalizer:
    """Normalizes AST nodes to a unified internal format for comparison."""

    @staticmethod
    def normalize_ast(ast: PropertyFileAST) -> PropertyFileAST:
        """Normalize an AST to a canonical form.

        This includes:
        - Normalizing whitespace in keys and values
        - Standardizing separators
        - Removing leading/trailing whitespace from values

        Args:
            ast: The AST to normalize.

        Returns:
            A new normalized AST.
        """
        normalized_nodes: List[PropertyNode] = []

        for node in ast.nodes:
            # Normalize key: trim whitespace
            normalized_key = node.key.strip()

            # Normalize value: trim trailing whitespace (but preserve leading if intentional)
            # For comparison purposes, we typically want to ignore trailing whitespace
            normalized_value = node.value.rstrip()

            # Create normalized node (preserve line numbers for diff tracking)
            normalized_node = PropertyNode(
                line_number=node.line_number,
                key=normalized_key,
                value=normalized_value,
                raw_line=node.raw_line,
                leading_whitespace=node.leading_whitespace,
                separator=node.separator,
                trailing_whitespace_before_value=node.trailing_whitespace_before_value,
                trailing_whitespace_after_value=node.trailing_whitespace_after_value,
            )
            normalized_nodes.append(normalized_node)

        return PropertyFileAST(
            nodes=normalized_nodes,
            empty_lines=ast.empty_lines,
            comments=ast.comments,
            file_path=ast.file_path,
        )

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

        Args:
            value: The value to normalize.

        Returns:
            Normalized value.
        """
        # Remove trailing whitespace but preserve leading whitespace
        # (leading whitespace might be intentional in some cases)
        return value.rstrip()

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
