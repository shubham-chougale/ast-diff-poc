"""Tests for the node matcher."""

from ast_diff_poc.diff.matcher import NodeMatcher
from ast_diff_poc.models.ast_node import PropertyFileAST, PropertyNode


class TestNodeMatcher:
    """Test cases for NodeMatcher."""

    def test_match_exact_nodes(self):
        """Test matching nodes with exact key and value."""
        source_nodes = [
            PropertyNode(1, "key1", "value1", "key1=value1"),
            PropertyNode(2, "key2", "value2", "key2=value2"),
        ]
        target_nodes = [
            PropertyNode(3, "key1", "value1", "key1=value1"),
            PropertyNode(4, "key2", "value2", "key2=value2"),
        ]

        source_ast = PropertyFileAST(nodes=source_nodes, empty_lines=[], comments=[])
        target_ast = PropertyFileAST(nodes=target_nodes, empty_lines=[], comments=[])

        matcher = NodeMatcher(source_ast, target_ast)
        matching = matcher.match_nodes()

        assert len(matching) == 2
        assert source_nodes[0] in matching
        assert source_nodes[1] in matching

    def test_match_by_key_only(self):
        """Test matching nodes by key when values differ."""
        source_nodes = [
            PropertyNode(1, "key1", "value1", "key1=value1"),
        ]
        target_nodes = [
            PropertyNode(2, "key1", "value2", "key1=value2"),
        ]

        source_ast = PropertyFileAST(nodes=source_nodes, empty_lines=[], comments=[])
        target_ast = PropertyFileAST(nodes=target_nodes, empty_lines=[], comments=[])

        matcher = NodeMatcher(source_ast, target_ast)
        matching = matcher.match_nodes()

        assert len(matching) == 1
        assert source_nodes[0] in matching

    def test_unmatched_source_nodes(self):
        """Test detecting unmatched source nodes."""
        source_nodes = [
            PropertyNode(1, "key1", "value1", "key1=value1"),
            PropertyNode(2, "key2", "value2", "key2=value2"),
        ]
        target_nodes = [
            PropertyNode(3, "key1", "value1", "key1=value1"),
        ]

        source_ast = PropertyFileAST(nodes=source_nodes, empty_lines=[], comments=[])
        target_ast = PropertyFileAST(nodes=target_nodes, empty_lines=[], comments=[])

        matcher = NodeMatcher(source_ast, target_ast)
        matcher.match_nodes()

        unmatched = matcher.get_unmatched_source_nodes()
        assert len(unmatched) == 1
        assert unmatched[0].key == "key2"

    def test_unmatched_target_nodes(self):
        """Test detecting unmatched target nodes."""
        source_nodes = [
            PropertyNode(1, "key1", "value1", "key1=value1"),
        ]
        target_nodes = [
            PropertyNode(2, "key1", "value1", "key1=value1"),
            PropertyNode(3, "key2", "value2", "key2=value2"),
        ]

        source_ast = PropertyFileAST(nodes=source_nodes, empty_lines=[], comments=[])
        target_ast = PropertyFileAST(nodes=target_nodes, empty_lines=[], comments=[])

        matcher = NodeMatcher(source_ast, target_ast)
        matcher.match_nodes()

        unmatched = matcher.get_unmatched_target_nodes()
        assert len(unmatched) == 1
        assert unmatched[0].key == "key2"
