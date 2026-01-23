"""Controller for handling diff API requests."""

from typing import Optional
from fastapi import UploadFile, HTTPException, status
from ...exceptions import (
    ASTDiffException,
    DiffCalculationException,
    ParsingException,
    NormalizationException,
    TokenizationException,
)
from ...models.diff_result import DiffResult
from ...utils.logger import get_logger
from ..schemas.diff_schemas import (
    DiffRequest,
    DiffResponse,
    DiffChangeSchema,
    DiffSummarySchema,
    HealthResponse,
)
from ..services.diff_service import DiffService

logger = get_logger(__name__)


class DiffController:
    """Controller for diff-related API endpoints."""

    def __init__(self, service: Optional[DiffService] = None):
        """Initialize the diff controller.

        Args:
            service: Optional diff service. If not provided, a new one is created.
        """
        self.service = service or DiffService()

    def compute_diff_from_content(self, request: DiffRequest) -> DiffResponse:
        """Handle diff computation from content strings.

        Args:
            request: Diff request containing source and target content.

        Returns:
            DiffResponse with computed changes.

        Raises:
            HTTPException: If the request is invalid or processing fails.
        """
        try:
            logger.info(f"Computing diff from content. Source file: {request.source_file_name}, Target file: {request.target_file_name}")
            result = self.service.compute_diff_from_content(
                source_content=request.source_content,
                target_content=request.target_content,
                normalize=request.normalize,
                source_file_name=request.source_file_name,
                target_file_name=request.target_file_name,
                calculate_complexity=False,
            )

            logger.debug(f"Diff computation successful. Found {len(result.changes)} changes")
            return self._convert_to_response(result)
        except ParsingException as e:
            logger.error(f"Parsing error: {e.message}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid property file content: {e.message}" + (f" ({e.details})" if e.details else ""),
            )
        except (DiffCalculationException, NormalizationException, TokenizationException) as e:
            logger.error(f"Diff calculation error: {e.message}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error computing diff: {e.message}" + (f" ({e.details})" if e.details else ""),
            )
        except ASTDiffException as e:
            logger.error(f"AST Diff error: {e.message}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error: {e.message}" + (f" ({e.details})" if e.details else ""),
            )
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid request: {str(e)}",
            )
        except Exception as e:
            logger.error(f"Unexpected error computing diff: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal server error: {str(e)}",
            )

    async def compute_diff_from_files(
        self,
        source_file: UploadFile,
        target_file: UploadFile,
        normalize: bool = True,
        calculate_complexity: bool = False,
    ) -> DiffResponse:
        """Handle diff computation from uploaded files.

        Args:
            source_file: Uploaded source property file.
            target_file: Uploaded target property file.
            normalize: Whether to normalize ASTs before comparison.

        Returns:
            DiffResponse with computed changes.

        Raises:
            HTTPException: If the files are invalid or processing fails.
        """
        try:
            logger.info(f"Computing diff from files. Source: {source_file.filename}, Target: {target_file.filename}")
            
            # Read file contents
            source_bytes = await source_file.read()
            target_bytes = await target_file.read()
            
            logger.debug(f"Read {len(source_bytes)} bytes from source, {len(target_bytes)} bytes from target")

            # Compute diff (complexity calculation disabled for diff API)
            result = self.service.compute_diff_from_bytes(
                source_bytes=source_bytes,
                target_bytes=target_bytes,
                normalize=normalize,
                source_file_name=source_file.filename,
                target_file_name=target_file.filename,
                calculate_complexity=False,
            )

            logger.debug(f"Diff computation successful. Found {len(result.changes)} changes")
            return self._convert_to_response(result)
        except ParsingException as e:
            logger.error(f"Parsing error: {e.message}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid property file: {e.message}" + (f" ({e.details})" if e.details else ""),
            )
        except (DiffCalculationException, NormalizationException, TokenizationException) as e:
            logger.error(f"Diff calculation error: {e.message}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error computing diff: {e.message}" + (f" ({e.details})" if e.details else ""),
            )
        except ASTDiffException as e:
            logger.error(f"AST Diff error: {e.message}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error: {e.message}" + (f" ({e.details})" if e.details else ""),
            )
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid request: {str(e)}",
            )
        except Exception as e:
            logger.error(f"Unexpected error computing diff: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal server error: {str(e)}",
            )

    def get_health(self) -> HealthResponse:
        """Get API health status.

        Returns:
            HealthResponse with service status.
        """
        return HealthResponse(status="healthy", version="1.0.0")

    def _convert_to_response(self, result: DiffResult) -> DiffResponse:
        """Convert DiffResult to DiffResponse schema.

        Args:
            result: DiffResult from service.

        Returns:
            DiffResponse schema object.
            
        Raises:
            HTTPException: If conversion fails.
        """
        try:
            logger.debug("Converting DiffResult to DiffResponse schema")
            
            # Convert changes (excluding complexity field for diff API)
            changes = []
            for change in result.changes:
                try:
                    changes.append(
                        DiffChangeSchema(
                            type=change.change_type.value,
                            key=change.key,
                            source_line=change.source_line,
                            target_line=change.target_line,
                            source_value=change.source_value,
                            target_value=change.target_value,
                            keyword_changes=change.keyword_changes,
                            message=change.message,
                        )
                    )
                except Exception as e:
                    logger.warning(f"Failed to convert change for key {change.key}: {str(e)}", exc_info=True)
                    # Continue with other changes

            # Convert summary
            summary = DiffSummarySchema(
                added=result.summary.added if result.summary else 0,
                deleted=result.summary.deleted if result.summary else 0,
                modified=result.summary.modified if result.summary else 0,
                moved=result.summary.moved if result.summary else 0,
                moved_and_modified=result.summary.moved_and_modified if result.summary else 0,
            )

            return DiffResponse(
                source_file=result.source_file,
                target_file=result.target_file,
                changes=changes,
                summary=summary,
            )
        except Exception as e:
            logger.error(f"Failed to convert DiffResult to response: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error converting response: {str(e)}",
            )
