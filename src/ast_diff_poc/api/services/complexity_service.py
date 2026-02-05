"""Service for computing complexity scores for property file changes."""

from typing import Dict, Optional

from ...complexity.property_complexity import PropertyComplexityCalculator
from ...diff.diff_engine import DiffEngine
from ...models.diff_result import DiffResult
from ..repositories.property_repository import PropertyRepository


class ComplexityService:
    """Service for computing complexity scores for property file changes."""

    def __init__(self, repository: Optional[PropertyRepository] = None):
        """Initialize the complexity service.

        Args:
            repository: Optional property repository. If not provided, a new one is created.
        """
        self.repository = repository or PropertyRepository()
        self.complexity_calculator = PropertyComplexityCalculator()

    def compute_complexity_from_content(
        self,
        source_content: str,
        target_content: str,
        normalize: bool = True,
        source_file_name: Optional[str] = None,
        target_file_name: Optional[str] = None,
    ) -> Dict:
        """Compute complexity for changes between two property file contents.

        Args:
            source_content: Content of the source property file.
            target_content: Content of the target property file.
            normalize: Whether to normalize ASTs before comparison.
            source_file_name: Optional source file name for reference.
            target_file_name: Optional target file name for reference.

        Returns:
            Dictionary containing complexity results with total score, blocks, and changes.

        Raises:
            ValueError: If either file cannot be parsed.
        """
        # Parse the files
        source_ast = self.repository.parse_from_string(source_content, source_file_name)
        target_ast = self.repository.parse_from_string(target_content, target_file_name)

        # Compute diff (without complexity calculation - we'll do it ourselves)
        engine = DiffEngine(normalize=normalize, calculate_complexity=False)
        diff_result = engine.compute_diff(source_ast, target_ast)

        # Calculate complexity using new logic
        return self._compute_complexity_for_changes(diff_result)

    def compute_complexity_from_files(
        self,
        source_file_path: str,
        target_file_path: str,
        normalize: bool = True,
    ) -> Dict:
        """Compute complexity for changes between two property files on disk.

        Args:
            source_file_path: Path to the source property file.
            target_file_path: Path to the target property file.
            normalize: Whether to normalize ASTs before comparison.

        Returns:
            Dictionary containing complexity results.

        Raises:
            FileNotFoundError: If either file does not exist.
            ValueError: If either file cannot be parsed.
        """
        source_ast = self.repository.parse_from_file(source_file_path)
        target_ast = self.repository.parse_from_file(target_file_path)

        engine = DiffEngine(normalize=normalize, calculate_complexity=False)
        diff_result = engine.compute_diff(source_ast, target_ast)

        return self._compute_complexity_for_changes(diff_result)

    def compute_complexity_from_bytes(
        self,
        source_bytes: bytes,
        target_bytes: bytes,
        normalize: bool = True,
        source_file_name: Optional[str] = None,
        target_file_name: Optional[str] = None,
        encoding: str = "utf-8",
    ) -> Dict:
        """Compute complexity for changes between two property file byte contents.

        Args:
            source_bytes: Source file content as bytes.
            target_bytes: Target file content as bytes.
            normalize: Whether to normalize ASTs before comparison.
            source_file_name: Optional source file name for reference.
            target_file_name: Optional target file name for reference.
            encoding: Encoding to use for decoding bytes (default: utf-8).

        Returns:
            Dictionary containing complexity results.

        Raises:
            ValueError: If either file cannot be decoded or parsed.
        """
        source_ast = self.repository.parse_from_bytes(
            source_bytes, source_file_name, encoding, normalize=normalize
        )
        target_ast = self.repository.parse_from_bytes(
            target_bytes, target_file_name, encoding, normalize=normalize
        )

        engine = DiffEngine(normalize=normalize, calculate_complexity=False)
        diff_result = engine.compute_diff(source_ast, target_ast)

        return self._compute_complexity_for_changes(diff_result)

    def _compute_complexity_for_changes(self, diff_result: DiffResult) -> Dict:
        """Compute complexity for all changes in a diff result.

        Args:
            diff_result: The diff result containing changes.

        Returns:
            Dictionary with complexity data including total score and blocks.
        """
        changes = diff_result.changes

        # Calculate complexity for all blocks
        complexity_result = self.complexity_calculator.calculate_all_blocks_complexity(changes)

        return {
            "source_file": diff_result.source_file,
            "target_file": diff_result.target_file,
            "total_complexity": complexity_result["total_complexity"],
            "total_complexity_raw": complexity_result["total_complexity_raw"],
            "risk_level": complexity_result["risk_level"],
            "risk_interpretation": complexity_result["risk_interpretation"],
            "blocks_calculated": complexity_result["blocks_calculated"],
            "blocks_skipped": complexity_result["blocks_skipped"],
            "blocks": complexity_result["blocks"],
            "skipped": complexity_result["skipped"],
        }
