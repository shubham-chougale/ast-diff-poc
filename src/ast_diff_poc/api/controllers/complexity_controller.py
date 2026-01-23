"""Controller for handling complexity API requests."""

from typing import Optional
from fastapi import UploadFile, HTTPException, status
from ...models.diff_result import DiffResult
from ..schemas.complexity_schemas import (
    ComplexityRequest,
    ComplexityResponse,
    ComplexityChangeSchema,
    BlockComplexitySchema,
)
from ..services.complexity_service import ComplexityService


class ComplexityController:
    """Controller for complexity-related API endpoints."""

    def __init__(self, service: Optional[ComplexityService] = None):
        """Initialize the complexity controller.

        Args:
            service: Optional complexity service. If not provided, a new one is created.
        """
        self.service = service or ComplexityService()

    def compute_complexity_from_content(self, request: ComplexityRequest) -> ComplexityResponse:
        """Handle complexity computation from content strings.

        Args:
            request: Complexity request containing source and target content.

        Returns:
            ComplexityResponse with computed complexity scores.

        Raises:
            HTTPException: If the request is invalid or processing fails.
        """
        try:
            result = self.service.compute_complexity_from_content(
                source_content=request.source_content,
                target_content=request.target_content,
                normalize=request.normalize,
                source_file_name=request.source_file_name,
                target_file_name=request.target_file_name,
            )

            return self._convert_to_response(result)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid property file content: {str(e)}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error computing complexity: {str(e)}",
            )

    async def compute_complexity_from_files(
        self,
        source_file: UploadFile,
        target_file: UploadFile,
        normalize: bool = True,
    ) -> ComplexityResponse:
        """Handle complexity computation from uploaded files.

        Args:
            source_file: Uploaded source property file.
            target_file: Uploaded target property file.
            normalize: Whether to normalize ASTs before comparison.

        Returns:
            ComplexityResponse with computed complexity scores.

        Raises:
            HTTPException: If the files are invalid or processing fails.
        """
        try:
            source_bytes = await source_file.read()
            target_bytes = await target_file.read()

            result = self.service.compute_complexity_from_bytes(
                source_bytes=source_bytes,
                target_bytes=target_bytes,
                normalize=normalize,
                source_file_name=source_file.filename,
                target_file_name=target_file.filename,
            )

            return self._convert_to_response(result)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid property file: {str(e)}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error computing complexity: {str(e)}",
            )

    def _convert_to_response(self, result: DiffResult) -> ComplexityResponse:
        """Convert DiffResult to ComplexityResponse schema.

        Args:
            result: DiffResult from service with complexity data.

        Returns:
            ComplexityResponse schema object.
        """
        # Check if we have any changes with complexity data
        if not result.changes or not any(change.complexity for change in result.changes):
            raise ValueError("Complexity calculation failed - no complexity data found in changes")

        changes = [
            ComplexityChangeSchema(
                type=change.change_type.value,
                key=change.key,
                source_line=change.source_line,
                target_line=change.target_line,
                source_value=change.source_value,
                target_value=change.target_value,
                complexity=BlockComplexitySchema(**change.complexity.to_dict()),
            )
            for change in result.changes
            if change.complexity
        ]

        return ComplexityResponse(
            source_file=result.source_file,
            target_file=result.target_file,
            changes=changes,
        )
