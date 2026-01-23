"""Route definitions for complexity API endpoints."""

from fastapi import APIRouter, UploadFile, File, Form
from ..controllers.complexity_controller import ComplexityController
from ..schemas.complexity_schemas import (
    ComplexityRequest,
    ComplexityResponse,
)

router = APIRouter(prefix="/api", tags=["complexity"])

# Initialize controller
controller = ComplexityController()


@router.post(
    "/complexity",
    response_model=ComplexityResponse,
    summary="Compute complexity from content",
    description="Compute complexity scores for changes between two property file contents.",
)
async def compute_complexity_from_content(request: ComplexityRequest) -> ComplexityResponse:
    """Compute complexity scores for changes between two property file contents.

    Args:
        request: Complexity request containing source and target content.

    Returns:
        ComplexityResponse with computed complexity scores.
    """
    return controller.compute_complexity_from_content(request)


@router.post(
    "/complexity/files",
    response_model=ComplexityResponse,
    summary="Compute complexity from uploaded files",
    description="Compute complexity scores for changes between two uploaded property files.",
)
async def compute_complexity_from_files(
    source_file: UploadFile = File(..., description="Source property file"),
    target_file: UploadFile = File(..., description="Target property file"),
    normalize: bool = Form(True, description="Whether to normalize ASTs before comparison"),
) -> ComplexityResponse:
    """Compute complexity scores for changes between two uploaded property files.

    Args:
        source_file: Uploaded source property file.
        target_file: Uploaded target property file.
        normalize: Whether to normalize ASTs before comparison.

    Returns:
        ComplexityResponse with computed complexity scores.
    """
    return await controller.compute_complexity_from_files(
        source_file, target_file, normalize
    )
