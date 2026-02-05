"""Controller for handling complexity API requests."""

from typing import Optional
from fastapi import UploadFile, HTTPException, status
from ..schemas.complexity_schemas import (
    ComplexityRequest,
    ComplexityResponse,
    BlockDetailSchema,
    BlockMetricsSchema,
    MetricDetailSchema,
    SkippedBlockSchema,
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

    def _convert_to_response(self, result: dict) -> ComplexityResponse:
        """Convert service result to ComplexityResponse schema.

        Args:
            result: Dictionary result from complexity service.

        Returns:
            ComplexityResponse schema object.
        """
        # Convert blocks to schema objects with detailed metrics
        blocks = []
        for block_data in result.get("blocks", []):
            metrics_data = block_data.get("metrics", {})
            
            # Build metrics with raw, weight, and weighted values
            blocks.append(BlockDetailSchema(
                key=block_data["key"],
                type=block_data["type"],
                block_score=block_data["block_score"],
                metrics=BlockMetricsSchema(
                    key_count=MetricDetailSchema(
                        raw=metrics_data.get("key_count", {}).get("raw", 1),
                        weight=metrics_data.get("key_count", {}).get("weight", 0.40),
                        weighted=metrics_data.get("key_count", {}).get("weighted", 0.40),
                    ),
                    max_depth=MetricDetailSchema(
                        raw=metrics_data.get("max_depth", {}).get("raw", 1),
                        weight=metrics_data.get("max_depth", {}).get("weight", 0.30),
                        weighted=metrics_data.get("max_depth", {}).get("weighted", 0.30),
                    ),
                    duplicate_count=MetricDetailSchema(
                        raw=metrics_data.get("duplicate_count", {}).get("raw", 0),
                        weight=metrics_data.get("duplicate_count", {}).get("weight", 0.20),
                        weighted=metrics_data.get("duplicate_count", {}).get("weighted", 0.0),
                    ),
                    loc=MetricDetailSchema(
                        raw=metrics_data.get("loc", {}).get("raw", 1),
                        weight=metrics_data.get("loc", {}).get("weight", 0.10),
                        weighted=metrics_data.get("loc", {}).get("weighted", 0.10),
                    ),
                ),
            ))

        # Convert skipped to schema objects
        skipped = []
        for skip_data in result.get("skipped", []):
            skipped.append(SkippedBlockSchema(
                key=skip_data["key"],
                type=skip_data["type"],
                reason=skip_data["reason"],
            ))

        return ComplexityResponse(
            source_file=result["source_file"],
            target_file=result["target_file"],
            total_complexity=result["total_complexity"],
            total_complexity_raw=result["total_complexity_raw"],
            risk_level=result["risk_level"],
            risk_interpretation=result["risk_interpretation"],
            blocks_calculated=result["blocks_calculated"],
            blocks_skipped=result["blocks_skipped"],
            blocks=blocks,
            skipped=skipped,
        )
