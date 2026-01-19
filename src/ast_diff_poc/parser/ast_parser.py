"""Custom AST parser for Java-style .properties files."""

import re
from pathlib import Path
from typing import List, Optional

from ..models.ast_node import (
    CommentNode,
    EmptyLineNode,
    PropertyFileAST,
    PropertyNode,
)


class PropertyParser:
    """Parser for Java-style .properties files that preserves line numbers and structure."""

    # Pattern to match key-value pairs: key = value or key: value
    # Handles escaped characters and Unicode
    PROPERTY_PATTERN = re.compile(
        r"^(\s*)([^=:\s#!][^=:]*?)(\s*)([=:])(\s*)(.*?)(\s*)$", re.UNICODE
    )

    # Pattern to match comments (# or !)
    COMMENT_PATTERN = re.compile(r"^\s*([#!])(.*)$")

    def __init__(self, file_path: Optional[str] = None):
        """Initialize the parser.

        Args:
            file_path: Optional path to the property file being parsed.
        """
        self.file_path = file_path

    def parse_file(self, file_path: str) -> PropertyFileAST:
        """Parse a property file from disk.

        Args:
            file_path: Path to the property file.

        Returns:
            PropertyFileAST containing all parsed nodes.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Property file not found: {file_path}")

        # Try UTF-8 first, fall back to ISO-8859-1 (common for Java properties)
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = path.read_text(encoding="iso-8859-1")

        return self.parse_string(content, file_path)

    def parse_string(self, content: str, file_path: Optional[str] = None) -> PropertyFileAST:
        """Parse a property file from a string.

        Args:
            content: Content of the property file.
            file_path: Optional path for reference.

        Returns:
            PropertyFileAST containing all parsed nodes.
        """
        lines = content.splitlines(keepends=False)
        nodes: List[PropertyNode] = []
        empty_lines: List[EmptyLineNode] = []
        comments: List[CommentNode] = []

        # Track continuation lines (lines ending with \)
        continuation_buffer: List[str] = []
        continuation_line_start = 0

        for line_num, line in enumerate(lines, start=1):
            original_line = line
            stripped = line.strip()

            # Handle continuation lines
            if continuation_buffer:
                if line.endswith("\\"):
                    # Continue building the value
                    continuation_buffer.append(line.rstrip("\\").rstrip())
                    continue
                else:
                    # End of continuation, reconstruct the full line
                    full_key_part = continuation_buffer[0]
                    full_value_part = " ".join(continuation_buffer[1:]) + " " + line
                    line = full_key_part + "=" + full_value_part
                    line_num = continuation_line_start
                    continuation_buffer = []

            # Check for empty lines
            if not stripped:
                empty_lines.append(EmptyLineNode(line_number=line_num))
                continue

            # Check for comments
            comment_match = self.COMMENT_PATTERN.match(line)
            if comment_match:
                comments.append(
                    CommentNode(line_number=line_num, content=comment_match.group(2).strip())
                )
                continue

            # Check for continuation marker
            if line.rstrip().endswith("\\"):
                if not continuation_buffer:
                    continuation_line_start = line_num
                continuation_buffer.append(line.rstrip("\\").rstrip())
                continue

            # Try to match property pattern
            match = self.PROPERTY_PATTERN.match(line)
            if match:
                (
                    leading_ws,
                    key,
                    ws_before_sep,
                    separator,
                    ws_after_sep,
                    value,
                    trailing_ws,
                ) = match.groups()

                # Unescape the key and value
                key = self._unescape(key.strip())
                value = self._unescape(value)

                node = PropertyNode(
                    line_number=line_num,
                    key=key,
                    value=value,
                    raw_line=original_line,
                    leading_whitespace=leading_ws,
                    separator=separator,
                    trailing_whitespace_before_value=ws_after_sep,
                    trailing_whitespace_after_value=trailing_ws,
                )
                nodes.append(node)
            else:
                # Try to handle malformed lines (key without value)
                # Some properties files have keys without values
                if "=" in line or ":" in line:
                    # Split on first = or :
                    sep = "=" if "=" in line else ":"
                    parts = line.split(sep, 1)
                    key = self._unescape(parts[0].strip())
                    value = self._unescape(parts[1].strip() if len(parts) > 1 else "")

                    node = PropertyNode(
                        line_number=line_num,
                        key=key,
                        value=value,
                        raw_line=original_line,
                        separator=sep,
                    )
                    nodes.append(node)

        return PropertyFileAST(
            nodes=nodes,
            empty_lines=empty_lines,
            comments=comments,
            file_path=file_path or self.file_path,
        )

    @staticmethod
    def _unescape(text: str) -> str:
        r"""Unescape Java property file escape sequences.

        Handles:
        - \\ -> \
        - \n -> newline
        - \t -> tab
        - \r -> carriage return
        - \uXXXX -> Unicode character
        - \xXX -> hex character
        """
        if not text:
            return text

        result = []
        i = 0
        while i < len(text):
            if text[i] == "\\" and i + 1 < len(text):
                next_char = text[i + 1]
                if next_char == "\\":
                    result.append("\\")
                    i += 2
                elif next_char == "n":
                    result.append("\n")
                    i += 2
                elif next_char == "t":
                    result.append("\t")
                    i += 2
                elif next_char == "r":
                    result.append("\r")
                    i += 2
                elif next_char == "u" and i + 5 < len(text):
                    # Unicode escape \uXXXX
                    hex_str = text[i + 2 : i + 6]
                    try:
                        code_point = int(hex_str, 16)
                        result.append(chr(code_point))
                        i += 6
                    except ValueError:
                        result.append("\\u")
                        i += 2
                elif next_char == "x" and i + 3 < len(text):
                    # Hex escape \xXX
                    hex_str = text[i + 2 : i + 4]
                    try:
                        code_point = int(hex_str, 16)
                        result.append(chr(code_point))
                        i += 4
                    except ValueError:
                        result.append("\\x")
                        i += 2
                else:
                    result.append(text[i])
                    i += 1
            else:
                result.append(text[i])
                i += 1

        return "".join(result)
