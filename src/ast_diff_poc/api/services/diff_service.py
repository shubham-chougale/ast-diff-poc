"""Service for computing diffs between property files."""

from typing import Optional
from ...exceptions import ParsingException, DiffCalculationException
from ...models.ast_node import PropertyFileAST
from ...models.diff_result import DiffResult
from ...diff.diff_engine import DiffEngine
from ...utils.logger import get_logger
from ..repositories.property_repository import PropertyRepository

logger = get_logger(__name__)


class DiffService:
    """Service for computing diffs between property files."""

    def __init__(self, repository: Optional[PropertyRepository] = None):
        """Initialize the diff service.

        Args:
            repository: Optional property repository. If not provided, a new one is created.
        """
        self.repository = repository or PropertyRepository()

    def compute_diff_from_content(
        self,
        source_content: str,
        target_content: str,
        normalize: bool = True,
        source_file_name: Optional[str] = None,
        target_file_name: Optional[str] = None,
        calculate_complexity: bool = False,
    ) -> DiffResult:
        """Compute diff between two property file contents.

        Args:
            source_content: Content of the source property file.
            target_content: Content of the target property file.
            normalize: Whether to normalize ASTs before comparison.
            source_file_name: Optional source file name for reference.
            target_file_name: Optional target file name for reference.
            calculate_complexity: Whether to calculate complexity scores.

        Returns:
            DiffResult containing all detected changes.

        Raises:
            ParsingException: If either file cannot be parsed.
            DiffCalculationException: If diff calculation fails.
        """
        try:
            logger.info(f"Computing diff from content. Source: {source_file_name}, Target: {target_file_name}")
            
            # Parse both files using repository
            try:
                logger.debug(f"Parsing source content (length: {len(source_content)})")
                source_ast = self.repository.parse_from_string(
                    source_content, source_file_name
                )
            except Exception as e:
                logger.error(f"Failed to parse source content: {str(e)}", exc_info=True)
                raise ParsingException(
                    f"Failed to parse source content: {str(e)}",
                    file_path=source_file_name
                ) from e
            
            try:
                logger.debug(f"Parsing target content (length: {len(target_content)})")
                target_ast = self.repository.parse_from_string(
                    target_content, target_file_name
                )
            except Exception as e:
                logger.error(f"Failed to parse target content: {str(e)}", exc_info=True)
                raise ParsingException(
                    f"Failed to parse target content: {str(e)}",
                    file_path=target_file_name
                ) from e

            # Compute diff using engine
            logger.debug("Computing diff using DiffEngine")
            engine = DiffEngine(normalize=normalize, calculate_complexity=calculate_complexity)
            result = engine.compute_diff(source_ast, target_ast)
            logger.info(f"Diff computation completed. Found {len(result.changes)} changes")
            return result
        except (ParsingException, DiffCalculationException):
            # Re-raise specific exceptions
            raise
        except Exception as e:
            logger.error(f"Unexpected error in compute_diff_from_content: {str(e)}", exc_info=True)
            raise DiffCalculationException(
                f"Unexpected error computing diff: {str(e)}",
                source_file=source_file_name,
                target_file=target_file_name
            ) from e

    def compute_diff_from_files(
        self,
        source_file_path: str,
        target_file_path: str,
        normalize: bool = True,
        calculate_complexity: bool = False,
    ) -> DiffResult:
        """Compute diff between two property files on disk.

        Args:
            source_file_path: Path to the source property file.
            target_file_path: Path to the target property file.
            normalize: Whether to normalize ASTs before comparison.
            calculate_complexity: Whether to calculate complexity scores.

        Returns:
            DiffResult containing all detected changes.

        Raises:
            FileNotFoundError: If either file does not exist.
            ParsingException: If either file cannot be parsed.
            DiffCalculationException: If diff calculation fails.
        """
        try:
            logger.info(f"Computing diff from files. Source: {source_file_path}, Target: {target_file_path}")
            
            # Parse both files using repository
            try:
                logger.debug(f"Parsing source file: {source_file_path}")
                source_ast = self.repository.parse_from_file(source_file_path)
            except FileNotFoundError:
                logger.error(f"Source file not found: {source_file_path}")
                raise
            except Exception as e:
                logger.error(f"Failed to parse source file {source_file_path}: {str(e)}", exc_info=True)
                raise ParsingException(
                    f"Failed to parse source file: {str(e)}",
                    file_path=source_file_path
                ) from e
            
            try:
                logger.debug(f"Parsing target file: {target_file_path}")
                target_ast = self.repository.parse_from_file(target_file_path)
            except FileNotFoundError:
                logger.error(f"Target file not found: {target_file_path}")
                raise
            except Exception as e:
                logger.error(f"Failed to parse target file {target_file_path}: {str(e)}", exc_info=True)
                raise ParsingException(
                    f"Failed to parse target file: {str(e)}",
                    file_path=target_file_path
                ) from e

            # Compute diff using engine
            logger.debug("Computing diff using DiffEngine")
            engine = DiffEngine(normalize=normalize, calculate_complexity=calculate_complexity)
            result = engine.compute_diff(source_ast, target_ast)
            logger.info(f"Diff computation completed. Found {len(result.changes)} changes")
            return result
        except (FileNotFoundError, ParsingException, DiffCalculationException):
            # Re-raise specific exceptions
            raise
        except Exception as e:
            logger.error(f"Unexpected error in compute_diff_from_files: {str(e)}", exc_info=True)
            raise DiffCalculationException(
                f"Unexpected error computing diff: {str(e)}",
                source_file=source_file_path,
                target_file=target_file_path
            ) from e

    def compute_diff_from_asts(
        self,
        source_ast: PropertyFileAST,
        target_ast: PropertyFileAST,
        normalize: bool = True,
        calculate_complexity: bool = False,
    ) -> DiffResult:
        """Compute diff between two ASTs.

        Args:
            source_ast: Source file AST.
            target_ast: Target file AST.
            normalize: Whether to normalize ASTs before comparison.
            calculate_complexity: Whether to calculate complexity scores.

        Returns:
            DiffResult containing all detected changes.
            
        Raises:
            DiffCalculationException: If diff calculation fails.
        """
        try:
            logger.debug("Computing diff from ASTs")
            engine = DiffEngine(normalize=normalize, calculate_complexity=calculate_complexity)
            result = engine.compute_diff(source_ast, target_ast)
            logger.debug(f"Diff computation completed. Found {len(result.changes)} changes")
            return result
        except DiffCalculationException:
            # Re-raise as-is
            raise
        except Exception as e:
            logger.error(f"Unexpected error in compute_diff_from_asts: {str(e)}", exc_info=True)
            raise DiffCalculationException(
                f"Unexpected error computing diff: {str(e)}",
                source_file=source_ast.file_path if source_ast else None,
                target_file=target_ast.file_path if target_ast else None
            ) from e

    def compute_diff_from_bytes(
        self,
        source_bytes: bytes,
        target_bytes: bytes,
        normalize: bool = True,
        source_file_name: Optional[str] = None,
        target_file_name: Optional[str] = None,
        encoding: str = "utf-8",
        calculate_complexity: bool = False,
    ) -> DiffResult:
        """Compute diff between two property file byte contents.

        Args:
            source_bytes: Source file content as bytes.
            target_bytes: Target file content as bytes.
            normalize: Whether to normalize ASTs before comparison.
            source_file_name: Optional source file name for reference.
            target_file_name: Optional target file name for reference.
            encoding: Encoding to use for decoding bytes (default: utf-8).
            calculate_complexity: Whether to calculate complexity scores.

        Returns:
            DiffResult containing all detected changes.

        Raises:
            ParsingException: If either file cannot be decoded or parsed.
            DiffCalculationException: If diff calculation fails.
        """
        try:
            logger.info(f"Computing diff from bytes. Source: {source_file_name}, Target: {target_file_name}, Encoding: {encoding}")
            
            # Parse both files using repository
            try:
                logger.debug(f"Parsing source bytes (length: {len(source_bytes)})")
                source_ast = self.repository.parse_from_bytes(
                    source_bytes, source_file_name, encoding
                )
            except UnicodeDecodeError as e:
                logger.error(f"Failed to decode source bytes with encoding {encoding}: {str(e)}", exc_info=True)
                raise ParsingException(
                    f"Failed to decode source content with encoding {encoding}: {str(e)}",
                    file_path=source_file_name
                ) from e
            except Exception as e:
                logger.error(f"Failed to parse source bytes: {str(e)}", exc_info=True)
                raise ParsingException(
                    f"Failed to parse source content: {str(e)}",
                    file_path=source_file_name
                ) from e
            
            try:
                logger.debug(f"Parsing target bytes (length: {len(target_bytes)})")
                target_ast = self.repository.parse_from_bytes(
                    target_bytes, target_file_name, encoding
                )
            except UnicodeDecodeError as e:
                logger.error(f"Failed to decode target bytes with encoding {encoding}: {str(e)}", exc_info=True)
                raise ParsingException(
                    f"Failed to decode target content with encoding {encoding}: {str(e)}",
                    file_path=target_file_name
                ) from e
            except Exception as e:
                logger.error(f"Failed to parse target bytes: {str(e)}", exc_info=True)
                raise ParsingException(
                    f"Failed to parse target content: {str(e)}",
                    file_path=target_file_name
                ) from e

            # Compute diff using engine
            logger.debug("Computing diff using DiffEngine")
            engine = DiffEngine(normalize=normalize, calculate_complexity=calculate_complexity)
            result = engine.compute_diff(source_ast, target_ast)
            logger.info(f"Diff computation completed. Found {len(result.changes)} changes")
            return result
        except (ParsingException, DiffCalculationException):
            # Re-raise specific exceptions
            raise
        except Exception as e:
            logger.error(f"Unexpected error in compute_diff_from_bytes: {str(e)}", exc_info=True)
            raise DiffCalculationException(
                f"Unexpected error computing diff: {str(e)}",
                source_file=source_file_name,
                target_file=target_file_name
            ) from e
