"""Node matching algorithm for diff engine."""

from typing import Dict, List, Optional, Set, Tuple

from ..models.ast_node import PropertyFileAST, PropertyNode


class NodeMatcher:
    """Matches nodes between source and target ASTs."""

    def __init__(self, source_ast: PropertyFileAST, target_ast: PropertyFileAST):
        """Initialize the matcher with source and target ASTs.

        Args:
            source_ast: The source file AST.
            target_ast: The target file AST.
        """
        self.source_ast = source_ast
        self.target_ast = target_ast
        self._matching: Dict[PropertyNode, PropertyNode] = {}
        self._reverse_matching: Dict[PropertyNode, PropertyNode] = {}

    def match_nodes(self) -> Dict[PropertyNode, PropertyNode]:
        """Match nodes between source and target ASTs.

        Returns:
            Dictionary mapping source nodes to target nodes.
        """
        # Reset matching
        self._matching = {}
        self._reverse_matching = {}

        # First pass: exact matches (same key and value)
        self._match_exact()

        # Second pass: match by key only (for modified values)
        self._match_by_key()

        return self._matching

    def _match_exact(self) -> None:
        """Match nodes with exact key and value matches."""
        source_matched: Set[PropertyNode] = set()
        target_matched: Set[PropertyNode] = set()

        for source_node in self.source_ast.nodes:
            if source_node in source_matched:
                continue

            # Find exact match in target
            for target_node in self.target_ast.nodes:
                if target_node in target_matched:
                    continue

                if (
                    source_node.key == target_node.key
                    and source_node.value == target_node.value
                ):
                    self._matching[source_node] = target_node
                    self._reverse_matching[target_node] = source_node
                    source_matched.add(source_node)
                    target_matched.add(target_node)
                    break

    def _match_by_key(self) -> None:
        """Match remaining nodes by key only (for modified values)."""
        source_unmatched = [
            node 
            for node in self.source_ast.nodes 
            if node not in self._matching
        ]
        target_unmatched = [
            node
            for node in self.target_ast.nodes
            if node not in self._reverse_matching
        ]

        # Create key-based matching
        source_by_key: Dict[str, List[PropertyNode]] = {}
        for node in source_unmatched:
            if node.key not in source_by_key:
                source_by_key[node.key] = []
            source_by_key[node.key].append(node)

        target_by_key: Dict[str, List[PropertyNode]] = {}
        for node in target_unmatched:
            if node.key not in target_by_key:
                target_by_key[node.key] = []
            target_by_key[node.key].append(node)

        # Match nodes with same key
        for key in source_by_key:
            if key in target_by_key:
                source_nodes = source_by_key[key]
                target_nodes = target_by_key[key]

                # Match by position similarity (closest line numbers)
                # This helps with moves
                for source_node in source_nodes:
                    if source_node in self._matching:
                        continue

                    # Find best match (closest line number, or first available)
                    best_match: Optional[PropertyNode] = None
                    min_distance = float("inf")

                    for target_node in target_nodes:
                        if target_node in self._reverse_matching:
                            continue

                        # Calculate distance (prefer closer line numbers)
                        distance = abs(source_node.line_number - target_node.line_number)
                        if distance < min_distance:
                            min_distance = distance
                            best_match = target_node

                    if best_match:
                        self._matching[source_node] = best_match
                        self._reverse_matching[best_match] = source_node

    def get_unmatched_source_nodes(self) -> List[PropertyNode]:
        """Get source nodes that were not matched.

        Returns:
            List of unmatched source nodes (deletions).
        """
        return [
            node for node in self.source_ast.nodes if node not in self._matching
        ]

    def get_unmatched_target_nodes(self) -> List[PropertyNode]:
        """Get target nodes that were not matched.

        Returns:
            List of unmatched target nodes (additions).
        """
        return [
            node
            for node in self.target_ast.nodes
            if node not in self._reverse_matching
        ]

    def get_matched_pairs(self) -> List[Tuple[PropertyNode, PropertyNode]]:
        """Get all matched node pairs.

        Returns:
            List of (source_node, target_node) tuples.
        """
        return list(self._matching.items())
