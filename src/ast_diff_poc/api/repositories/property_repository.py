"""Repository for property file data access operations."""

from typing import Optional
from ...exceptions import NormalizationException, ParsingException
from ...models.ast_node import PropertyFileAST
from ...parser.ast_parser import PropertyParser
from ...parser.normalization import Normalizer
from ...utils.logger import get_logger

logger = get_logger(__name__)


class PropertyRepository:
    """Repository for accessing and parsing property files."""

    def __init__(self):
        """Initialize the repository."""
        self.parser = PropertyParser()

    def parse_from_file(self, file_path: str, normalize: bool = True) -> PropertyFileAST:
        """Parse a property file from disk.

        Normalization is applied before parsing:
        1. Normalize line endings (CRLF → LF)
        2. Trim whitespace around keys, =, and values
        3. Filter out empty lines and comments
        4. Sort keys alphabetically
        5. Preserve values as-is

        Args:
            file_path: Path to the property file.
            normalize: Whether to normalize content before parsing (default: True).

        Returns:
            PropertyFileAST representing the parsed file.

        Raises:
            FileNotFoundError: If the file does not exist.
            ParsingException: If the file cannot be parsed.
            NormalizationException: If normalization fails.
        """
        try:
            # Read file content first
            from pathlib import Path
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"Property file not found: {file_path}")
            
            # Try UTF-8 first, fall back to ISO-8859-1
            try:
                content = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                content = path.read_text(encoding="iso-8859-1")
            
            # Parse with normalization
            return self.parse_from_string(content, file_path, normalize=normalize)
        except FileNotFoundError:
            raise
        except (NormalizationException, ParsingException):
            # Re-raise specific exceptions
            raise
        except Exception as e:
            logger.error(f"Failed to parse property file {file_path}: {str(e)}", exc_info=True)
            raise ParsingException(
                f"Failed to parse property file: {str(e)}",
                file_path=file_path
            ) from e

    def parse_from_string(
        self, content: str, file_path: Optional[str] = None, normalize: bool = True
    ) -> PropertyFileAST:
        """Parse a property file from a string.

        Normalization is applied before parsing:
        1. Normalize line endings (CRLF → LF)
        2. Trim whitespace around keys, =, and values
        3. Filter out empty lines and comments
        4. Sort keys alphabetically
        5. Preserve values as-is

        Args:
            content: Content of the property file.
            file_path: Optional file path for reference.
            normalize: Whether to normalize content before parsing (default: True).

        Returns:
            PropertyFileAST representing the parsed file.

        Raises:
            ParsingException: If the content cannot be parsed.
            NormalizationException: If normalization fails.
        """
        try:
            # Apply normalization before parsing
            if normalize:
                try:
                    logger.debug(f"Normalizing content before parsing (file: {file_path})")
                    normalized_content = Normalizer.normalize_content(content)
                    logger.debug(f"Content normalized, parsing normalized content")
                    return self.parser.parse_string(normalized_content, file_path)
                except NormalizationException:
                    # Re-raise normalization exceptions
                    raise
                except Exception as e:
                    logger.error(f"Normalization failed: {str(e)}", exc_info=True)
                    raise NormalizationException(f"Failed to normalize content: {str(e)}") from e
            else:
                # Parse without normalization
                return self.parser.parse_string(content, file_path)
        except (NormalizationException, ParsingException):
            # Re-raise specific exceptions
            raise
        except Exception as e:
            logger.error(f"Failed to parse property file content: {str(e)}", exc_info=True)
            raise ParsingException(
                f"Failed to parse property file content: {str(e)}",
                file_path=file_path
            ) from e

    def parse_from_bytes(
        self, content: bytes, file_path: Optional[str] = None, encoding: str = "utf-8", normalize: bool = True
    ) -> PropertyFileAST:
        """Parse a property file from bytes.

        Normalization is applied before parsing:
        1. Normalize line endings (CRLF → LF)
        2. Trim whitespace around keys, =, and values
        3. Filter out empty lines and comments
        4. Sort keys alphabetically
        5. Preserve values as-is

        Args:
            content: Content of the property file as bytes.
            file_path: Optional file path for reference.
            encoding: Encoding to use for decoding bytes (default: utf-8).
            normalize: Whether to normalize content before parsing (default: True).

        Returns:
            PropertyFileAST representing the parsed file.

        Raises:
            ParsingException: If the content cannot be decoded or parsed.
            NormalizationException: If normalization fails.
        """
        try:
            # Try specified encoding first
            try:
                text_content = content.decode(encoding)
            except UnicodeDecodeError:
                # Fall back to ISO-8859-1 (common for Java properties)
                logger.debug(f"UTF-8 decode failed, trying ISO-8859-1")
                text_content = content.decode("iso-8859-1")

            return self.parse_from_string(text_content, file_path, normalize=normalize)
        except (NormalizationException, ParsingException):
            # Re-raise specific exceptions
            raise
        except Exception as e:
            logger.error(f"Failed to parse property file from bytes: {str(e)}", exc_info=True)
            raise ParsingException(
                f"Failed to parse property file from bytes: {str(e)}",
                file_path=file_path
            ) from e
