"""Pydantic schemas for complexity API requests and responses."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class BlockComplexitySchema(BaseModel):
    """Schema for block complexity metrics."""

    structural_complexity: float = Field(..., description="Normalized structural complexity score (0-100)")
    change_type_multiplier: float = Field(..., description="Multiplier based on change type")
    effective_complexity: float = Field(..., description="Final block complexity score")
    risk_level: Optional[str] = Field(None, description="Risk level classification (Low, Medium, High, Very High)")
    risk_interpretation: Optional[str] = Field(None, description="Interpretation of the risk level")
    metrics: Dict = Field(..., description="Raw and normalized metrics")


class ComplexityChangeSchema(BaseModel):
    """Schema for a change with complexity metrics."""

    type: str = Field(..., description="Type of change")
    key: str = Field(..., description="Property key")
    source_line: Optional[int] = Field(None, description="Line number in source file")
    target_line: Optional[int] = Field(None, description="Line number in target file")
    source_value: Optional[str] = Field(None, description="Value in source file")
    target_value: Optional[str] = Field(None, description="Value in target file")
    complexity: BlockComplexitySchema = Field(..., description="Complexity metrics for this change")


class ComplexityRequest(BaseModel):
    """Request schema for computing complexity from content strings."""

    source_content: str = Field(..., description="Content of the source property file")
    target_content: str = Field(..., description="Content of the target property file")
    normalize: bool = Field(True, description="Whether to normalize ASTs before comparison")
    source_file_name: Optional[str] = Field(None, description="Optional source file name for reference")
    target_file_name: Optional[str] = Field(None, description="Optional target file name for reference")


class ComplexityResponse(BaseModel):
    """Response schema for complexity computation."""

    source_file: str = Field(..., description="Source file path or identifier")
    target_file: str = Field(..., description="Target file path or identifier")
    changes: List[ComplexityChangeSchema] = Field(..., description="List of changes with complexity metrics")
