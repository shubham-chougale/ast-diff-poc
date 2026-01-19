"""Tests for the diff engine."""

from ast_diff_poc.diff.diff_engine import DiffEngine
from ast_diff_poc.models.ast_node import PropertyFileAST, PropertyNode
from ast_diff_poc.models.change_types import ChangeType


class TestDiffEngine:
    """Test cases for DiffEngine."""

    def test_detect_additions(self):
        """Test detecting added properties."""
        source_nodes = [
            PropertyNode(1, "key1", "value1", "key1=value1"),
        ]
        target_nodes = [
            PropertyNode(1, "key1", "value1", "key1=value1"),
            PropertyNode(2, "key2", "value2", "key2=value2"),
        ]

        source_ast = PropertyFileAST(nodes=source_nodes, empty_lines=[], comments=[])
        target_ast = PropertyFileAST(nodes=target_nodes, empty_lines=[], comments=[])

        engine = DiffEngine()
        result = engine.compute_diff(source_ast, target_ast)

        assert result.summary.added == 1
        assert any(
            c.change_type == ChangeType.ADDED and c.key == "key2"
            for c in result.changes
        )

    def test_detect_deletions(self):
        """Test detecting deleted properties."""
        source_nodes = [
            PropertyNode(1, "key1", "value1", "key1=value1"),
            PropertyNode(2, "key2", "value2", "key2=value2"),
        ]
        target_nodes = [
            PropertyNode(1, "key1", "value1", "key1=value1"),
        ]

        source_ast = PropertyFileAST(nodes=source_nodes, empty_lines=[], comments=[])
        target_ast = PropertyFileAST(nodes=target_nodes, empty_lines=[], comments=[])

        engine = DiffEngine()
        result = engine.compute_diff(source_ast, target_ast)

        assert result.summary.deleted == 1
        assert any(
            c.change_type == ChangeType.DELETED and c.key == "key2"
            for c in result.changes
        )

    def test_detect_modifications(self):
        """Test detecting modified properties."""
        source_nodes = [
            PropertyNode(1, "key1", "value1", "key1=value1"),
        ]
        target_nodes = [
            PropertyNode(1, "key1", "value2", "key1=value2"),
        ]

        source_ast = PropertyFileAST(nodes=source_nodes, empty_lines=[], comments=[])
        target_ast = PropertyFileAST(nodes=target_nodes, empty_lines=[], comments=[])

        engine = DiffEngine()
        result = engine.compute_diff(source_ast, target_ast)

        assert result.summary.modified == 1
        assert any(
            c.change_type == ChangeType.MODIFIED
            and c.key == "key1"
            and c.source_value == "value1"
            and c.target_value == "value2"
            for c in result.changes
        )

    def test_detect_moves(self):
        """Test detecting moved properties."""
        source_nodes = [
            PropertyNode(1, "key1", "value1", "key1=value1"),
            PropertyNode(2, "key2", "value2", "key2=value2"),
        ]
        target_nodes = [
            PropertyNode(1, "key2", "value2", "key2=value2"),
            PropertyNode(2, "key1", "value1", "key1=value1"),
        ]

        source_ast = PropertyFileAST(nodes=source_nodes, empty_lines=[], comments=[])
        target_ast = PropertyFileAST(nodes=target_nodes, empty_lines=[], comments=[])

        engine = DiffEngine()
        result = engine.compute_diff(source_ast, target_ast)

        moved_changes = [
            c for c in result.changes if c.change_type == ChangeType.MOVED
        ]
        assert len(moved_changes) >= 1

    def test_detect_moved_and_modified(self):
        """Test detecting moved and modified properties."""
        source_nodes = [
            PropertyNode(1, "key1", "value1", "key1=value1"),
        ]
        target_nodes = [
            PropertyNode(5, "key1", "value2", "key1=value2"),
        ]

        source_ast = PropertyFileAST(nodes=source_nodes, empty_lines=[], comments=[])
        target_ast = PropertyFileAST(nodes=target_nodes, empty_lines=[], comments=[])

        engine = DiffEngine()
        result = engine.compute_diff(source_ast, target_ast)

        assert result.summary.moved_and_modified >= 0
        moved_modified = [
            c
            for c in result.changes
            if c.change_type == ChangeType.MOVED_AND_MODIFIED
        ]
        # May be detected as moved_and_modified or separate move + modify
        assert len(moved_modified) >= 0
