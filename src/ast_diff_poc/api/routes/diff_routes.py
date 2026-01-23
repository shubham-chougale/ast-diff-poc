"""Route definitions for diff API endpoints."""

from fastapi import APIRouter, UploadFile, File, Form
from ..controllers.diff_controller import DiffController
from ..schemas.diff_schemas import (
    DiffRequest,
    DiffResponse,
    HealthResponse,
)

router = APIRouter(prefix="/api", tags=["diff"])

# Initialize controller
controller = DiffController()


@router.get("/health", response_model=HealthResponse, summary="Health check")
async def health_check():
    """Check API health status.

    Returns:
        HealthResponse with service status and version.
    """
    return controller.get_health()


@router.post(
    "/diff",
    response_model=DiffResponse,
    summary="Compute diff from content",
    description="Compute AST-based diff between two property file contents provided as strings.",
)
async def compute_diff_from_content(request: DiffRequest) -> DiffResponse:
    """Compute diff between two property file contents.

    Args:
        request: Diff request containing source and target content.

    Returns:
        DiffResponse with computed changes and summary.
    """
    return controller.compute_diff_from_content(request)


@router.post(
    "/diff/files",
    response_model=DiffResponse,
    summary="Compute diff from uploaded files",
    description="Compute AST-based diff between two uploaded property files.",
)
async def compute_diff_from_files(
    source_file: UploadFile = File(..., description="Source property file"),
    target_file: UploadFile = File(..., description="Target property file"),
    normalize: bool = Form(True, description="Whether to normalize ASTs before comparison"),
    calculate_complexity: bool = Form(False, description="Whether to calculate complexity scores for changes"),
) -> DiffResponse:
    """Compute diff between two uploaded property files.

    Args:
        source_file: Uploaded source property file.
        target_file: Uploaded target property file.
        normalize: Whether to normalize ASTs before comparison.
        calculate_complexity: Whether to calculate complexity scores for changes.

    Returns:
        DiffResponse with computed changes and summary.
    """
    return await controller.compute_diff_from_files(
        source_file, target_file, normalize, calculate_complexity
    )
