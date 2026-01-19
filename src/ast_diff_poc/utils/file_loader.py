"""File loading utilities for property files."""

from pathlib import Path
from typing import Optional

from ..models.ast_node import PropertyFileAST
from ..parser.ast_parser import PropertyParser


def load_property_file(file_path: str) -> PropertyFileAST:
    """Load and parse a property file.

    Args:
        file_path: Path to the property file.

    Returns:
        PropertyFileAST representing the parsed file.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file cannot be parsed.
    """
    parser = PropertyParser(file_path=file_path)
    try:
        return parser.parse_file(file_path)
    except FileNotFoundError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to parse property file {file_path}: {str(e)}") from e
