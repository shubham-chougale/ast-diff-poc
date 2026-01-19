"""Tests for the property file parser."""

import pytest
from pathlib import Path

from ast_diff_poc.parser.ast_parser import PropertyParser
from ast_diff_poc.models.ast_node import PropertyNode


class TestPropertyParser:
    """Test cases for PropertyParser."""

    def test_parse_simple_property(self):
        """Test parsing a simple key-value pair."""
        content = "key=value"
        parser = PropertyParser()
        ast = parser.parse_string(content)

        assert len(ast.nodes) == 1
        assert ast.nodes[0].key == "key"
        assert ast.nodes[0].value == "value"
        assert ast.nodes[0].line_number == 1

    def test_parse_multiple_properties(self):
        """Test parsing multiple key-value pairs."""
        content = "key1=value1\nkey2=value2\nkey3=value3"
        parser = PropertyParser()
        ast = parser.parse_string(content)

        assert len(ast.nodes) == 3
        assert ast.nodes[0].key == "key1"
        assert ast.nodes[1].key == "key2"
        assert ast.nodes[2].key == "key3"

    def test_parse_with_empty_lines(self):
        """Test parsing with empty lines."""
        content = "key1=value1\n\nkey2=value2"
        parser = PropertyParser()
        ast = parser.parse_string(content)

        assert len(ast.nodes) == 2
        assert len(ast.empty_lines) == 1
        assert ast.empty_lines[0].line_number == 2

    def test_parse_with_whitespace(self):
        """Test parsing with whitespace around separator."""
        content = "key = value"
        parser = PropertyParser()
        ast = parser.parse_string(content)

        assert len(ast.nodes) == 1
        assert ast.nodes[0].key == "key"
        assert ast.nodes[0].value == "value"

    def test_parse_with_colon_separator(self):
        """Test parsing with colon separator."""
        content = "key:value"
        parser = PropertyParser()
        ast = parser.parse_string(content)

        assert len(ast.nodes) == 1
        assert ast.nodes[0].key == "key"
        assert ast.nodes[0].value == "value"
        assert ast.nodes[0].separator == ":"

    def test_parse_escaped_characters(self):
        """Test parsing escaped characters."""
        content = "key=value\\nwith\\tnewline"
        parser = PropertyParser()
        ast = parser.parse_string(content)

        assert len(ast.nodes) == 1
        assert "\n" in ast.nodes[0].value
        assert "\t" in ast.nodes[0].value

    def test_parse_unicode(self):
        """Test parsing Unicode characters."""
        content = "key=value with unicode: 测试"
        parser = PropertyParser()
        ast = parser.parse_string(content)

        assert len(ast.nodes) == 1
        assert "测试" in ast.nodes[0].value

    def test_parse_file(self, tmp_path):
        """Test parsing from a file."""
        test_file = tmp_path / "test.properties"
        test_file.write_text("key1=value1\nkey2=value2", encoding="utf-8")

        parser = PropertyParser()
        ast = parser.parse_file(str(test_file))

        assert len(ast.nodes) == 2
        assert ast.file_path == str(test_file)

    def test_parse_file_not_found(self):
        """Test parsing a non-existent file."""
        parser = PropertyParser()
        with pytest.raises(FileNotFoundError):
            parser.parse_file("nonexistent.properties")

    def test_line_number_preservation(self):
        """Test that line numbers are preserved correctly."""
        content = "line1=value1\nline2=value2\n\nline4=value4"
        parser = PropertyParser()
        ast = parser.parse_string(content)

        assert ast.nodes[0].line_number == 1
        assert ast.nodes[1].line_number == 2
        assert ast.nodes[2].line_number == 4
