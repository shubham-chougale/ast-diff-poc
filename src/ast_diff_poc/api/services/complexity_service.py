"""Service for computing complexity scores for property file changes."""

from typing import Optional
from ...models.ast_node import PropertyFileAST
from ...models.diff_result import DiffResult
from ...diff.diff_engine import DiffEngine
from ..repositories.property_repository import PropertyRepository


class ComplexityService:
    """Service for computing complexity scores for property file changes."""

    def __init__(self, repository: Optional[PropertyRepository] = None):
        """Initialize the complexity service.

        Args:
            repository: Optional property repository. If not provided, a new one is created.
        """
        self.repository = repository or PropertyRepository()

    def compute_complexity_from_content(
        self,
        source_content: str,
        target_content: str,
        normalize: bool = True,
        source_file_name: Optional[str] = None,
        target_file_name: Optional[str] = None,
    ) -> DiffResult:
        """Compute complexity for changes between two property file contents.

        Args:
            source_content: Content of the source property file.
            target_content: Content of the target property file.
            normalize: Whether to normalize ASTs before comparison.
            source_file_name: Optional source file name for reference.
            target_file_name: Optional target file name for reference.

        Returns:
            DiffResult containing all changes with complexity scores.

        Raises:
            ValueError: If either file cannot be parsed.
        """
        source_ast = self.repository.parse_from_string(source_content, source_file_name)
        target_ast = self.repository.parse_from_string(target_content, target_file_name)

        engine = DiffEngine(normalize=normalize, calculate_complexity=True)
        return engine.compute_diff(source_ast, target_ast)

    def compute_complexity_from_files(
        self,
        source_file_path: str,
        target_file_path: str,
        normalize: bool = True,
    ) -> DiffResult:
        """Compute complexity for changes between two property files on disk.

        Args:
            source_file_path: Path to the source property file.
            target_file_path: Path to the target property file.
            normalize: Whether to normalize ASTs before comparison.

        Returns:
            DiffResult containing all changes with complexity scores.

        Raises:
            FileNotFoundError: If either file does not exist.
            ValueError: If either file cannot be parsed.
        """
        source_ast = self.repository.parse_from_file(source_file_path)
        target_ast = self.repository.parse_from_file(target_file_path)

        engine = DiffEngine(normalize=normalize, calculate_complexity=True)
        return engine.compute_diff(source_ast, target_ast)

    def compute_complexity_from_bytes(
        self,
        source_bytes: bytes,
        target_bytes: bytes,
        normalize: bool = True,
        source_file_name: Optional[str] = None,
        target_file_name: Optional[str] = None,
        encoding: str = "utf-8",
    ) -> DiffResult:
        """Compute complexity for changes between two property file byte contents.

        Args:
            source_bytes: Source file content as bytes.
            target_bytes: Target file content as bytes.
            normalize: Whether to normalize ASTs before comparison.
            source_file_name: Optional source file name for reference.
            target_file_name: Optional target file name for reference.
            encoding: Encoding to use for decoding bytes (default: utf-8).

        Returns:
            DiffResult containing all changes with complexity scores.

        Raises:
            ValueError: If either file cannot be decoded or parsed.
        """
        source_ast = self.repository.parse_from_bytes(source_bytes, source_file_name, encoding, normalize=normalize)
        target_ast = self.repository.parse_from_bytes(target_bytes, target_file_name, encoding, normalize=normalize)

        engine = DiffEngine(normalize=normalize, calculate_complexity=True)
        return engine.compute_diff(source_ast, target_ast)
