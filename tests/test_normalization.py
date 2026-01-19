"""Tests for the normalization module."""

from ast_diff_poc.parser.normalization import Normalizer
from ast_diff_poc.models.ast_node import PropertyFileAST, PropertyNode, EmptyLineNode


class TestNormalizer:
    """Test cases for Normalizer."""

    def test_normalize_key(self):
        """Test key normalization."""
        assert Normalizer.normalize_key("  key  ") == "key"
        assert Normalizer.normalize_key("key") == "key"
        assert Normalizer.normalize_key("\tkey\n") == "key"

    def test_normalize_value(self):
        """Test value normalization."""
        assert Normalizer.normalize_value("value  ") == "value"
        assert Normalizer.normalize_value("value") == "value"
        assert Normalizer.normalize_value("  value  ") == "  value"

    def test_normalize_ast(self):
        """Test AST normalization."""
        nodes = [
            PropertyNode(
                line_number=1,
                key="  key1  ",
                value="value1  ",
                raw_line="  key1  =value1  ",
            ),
            PropertyNode(
                line_number=2,
                key="key2",
                value="value2",
                raw_line="key2=value2",
            ),
        ]
        ast = PropertyFileAST(nodes=nodes, empty_lines=[], comments=[])

        normalized = Normalizer.normalize_ast(ast)

        assert normalized.nodes[0].key == "key1"
        assert normalized.nodes[0].value == "value1"
        assert normalized.nodes[1].key == "key2"
        assert normalized.nodes[1].value == "value2"

    def test_are_values_semantically_equivalent(self):
        """Test semantic equivalence checking."""
        assert Normalizer.are_values_semantically_equivalent("value", "value")
        assert Normalizer.are_values_semantically_equivalent("value  ", "value")
        assert Normalizer.are_values_semantically_equivalent("value", "value  ")
        assert not Normalizer.are_values_semantically_equivalent("value1", "value2")
