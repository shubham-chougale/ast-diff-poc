"""Service for computing diffs between property files."""

from typing import Optional
from ...models.ast_node import PropertyFileAST
from ...models.diff_result import DiffResult
from ...diff.diff_engine import DiffEngine
from ..repositories.property_repository import PropertyRepository


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
    ) -> DiffResult:
        """Compute diff between two property file contents.

        Args:
            source_content: Content of the source property file.
            target_content: Content of the target property file.
            normalize: Whether to normalize ASTs before comparison.
            source_file_name: Optional source file name for reference.
            target_file_name: Optional target file name for reference.

        Returns:
            DiffResult containing all detected changes.

        Raises:
            ValueError: If either file cannot be parsed.
        """
        # Parse both files using repository
        source_ast = self.repository.parse_from_string(
            source_content, source_file_name
        )
        target_ast = self.repository.parse_from_string(
            target_content, target_file_name
        )

        # Compute diff using engine
        engine = DiffEngine(normalize=normalize)
        return engine.compute_diff(source_ast, target_ast)

    def compute_diff_from_files(
        self, source_file_path: str, target_file_path: str, normalize: bool = True
    ) -> DiffResult:
        """Compute diff between two property files on disk.

        Args:
            source_file_path: Path to the source property file.
            target_file_path: Path to the target property file.
            normalize: Whether to normalize ASTs before comparison.

        Returns:
            DiffResult containing all detected changes.

        Raises:
            FileNotFoundError: If either file does not exist.
            ValueError: If either file cannot be parsed.
        """
        # Parse both files using repository
        source_ast = self.repository.parse_from_file(source_file_path)
        target_ast = self.repository.parse_from_file(target_file_path)

        # Compute diff using engine
        engine = DiffEngine(normalize=normalize)
        return engine.compute_diff(source_ast, target_ast)

    def compute_diff_from_asts(
        self,
        source_ast: PropertyFileAST,
        target_ast: PropertyFileAST,
        normalize: bool = True,
    ) -> DiffResult:
        """Compute diff between two ASTs.

        Args:
            source_ast: Source file AST.
            target_ast: Target file AST.
            normalize: Whether to normalize ASTs before comparison.

        Returns:
            DiffResult containing all detected changes.
        """
        engine = DiffEngine(normalize=normalize)
        return engine.compute_diff(source_ast, target_ast)

    def compute_diff_from_bytes(
        self,
        source_bytes: bytes,
        target_bytes: bytes,
        normalize: bool = True,
        source_file_name: Optional[str] = None,
        target_file_name: Optional[str] = None,
        encoding: str = "utf-8",
    ) -> DiffResult:
        """Compute diff between two property file byte contents.

        Args:
            source_bytes: Source file content as bytes.
            target_bytes: Target file content as bytes.
            normalize: Whether to normalize ASTs before comparison.
            source_file_name: Optional source file name for reference.
            target_file_name: Optional target file name for reference.
            encoding: Encoding to use for decoding bytes (default: utf-8).

        Returns:
            DiffResult containing all detected changes.

        Raises:
            ValueError: If either file cannot be decoded or parsed.
        """
        # Parse both files using repository
        source_ast = self.repository.parse_from_bytes(
            source_bytes, source_file_name, encoding
        )
        target_ast = self.repository.parse_from_bytes(
            target_bytes, target_file_name, encoding
        )

        # Compute diff using engine
        engine = DiffEngine(normalize=normalize)
        return engine.compute_diff(source_ast, target_ast)
