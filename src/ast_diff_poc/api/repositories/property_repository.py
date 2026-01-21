"""Repository for property file data access operations."""

from typing import Optional
from ...models.ast_node import PropertyFileAST
from ...parser.ast_parser import PropertyParser


class PropertyRepository:
    """Repository for accessing and parsing property files."""

    def __init__(self):
        """Initialize the repository."""
        self.parser = PropertyParser()

    def parse_from_file(self, file_path: str) -> PropertyFileAST:
        """Parse a property file from disk.

        Args:
            file_path: Path to the property file.

        Returns:
            PropertyFileAST representing the parsed file.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file cannot be parsed.
        """
        try:
            return self.parser.parse_file(file_path)
        except FileNotFoundError:
            raise
        except Exception as e:
            raise ValueError(f"Failed to parse property file {file_path}: {str(e)}") from e

    def parse_from_string(
        self, content: str, file_path: Optional[str] = None
    ) -> PropertyFileAST:
        """Parse a property file from a string.

        Args:
            content: Content of the property file.
            file_path: Optional file path for reference.

        Returns:
            PropertyFileAST representing the parsed file.

        Raises:
            ValueError: If the content cannot be parsed.
        """
        try:
            return self.parser.parse_string(content, file_path)
        except Exception as e:
            raise ValueError(f"Failed to parse property file content: {str(e)}") from e

    def parse_from_bytes(
        self, content: bytes, file_path: Optional[str] = None, encoding: str = "utf-8"
    ) -> PropertyFileAST:
        """Parse a property file from bytes.

        Args:
            content: Content of the property file as bytes.
            file_path: Optional file path for reference.
            encoding: Encoding to use for decoding bytes (default: utf-8).

        Returns:
            PropertyFileAST representing the parsed file.

        Raises:
            ValueError: If the content cannot be decoded or parsed.
        """
        try:
            # Try specified encoding first
            try:
                text_content = content.decode(encoding)
            except UnicodeDecodeError:
                # Fall back to ISO-8859-1 (common for Java properties)
                text_content = content.decode("iso-8859-1")

            return self.parse_from_string(text_content, file_path)
        except Exception as e:
            raise ValueError(
                f"Failed to parse property file from bytes: {str(e)}"
            ) from e
