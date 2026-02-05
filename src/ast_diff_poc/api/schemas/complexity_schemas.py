"""Pydantic schemas for complexity API requests and responses."""

from typing import List, Optional
from pydantic import BaseModel, Field


class MetricDetailSchema(BaseModel):
    """Schema for a single metric with raw and weighted values."""

    raw: int = Field(..., description="Raw metric value")
    weight: float = Field(..., description="Weight applied to this metric")
    weighted: float = Field(..., description="Value after weight multiplication (raw × weight)")


class BlockMetricsSchema(BaseModel):
    """Schema for individual block metrics with weighted calculations."""

    key_count: MetricDetailSchema = Field(..., description="Number of keys metric")
    max_depth: MetricDetailSchema = Field(..., description="Hierarchy depth metric")
    duplicate_count: MetricDetailSchema = Field(..., description="Duplicate/override count metric")
    loc: MetricDetailSchema = Field(..., description="Lines of code metric")


class BlockDetailSchema(BaseModel):
    """Schema for detailed block complexity information."""

    key: str = Field(..., description="Property key")
    type: str = Field(..., description="Change type (ADDED, DELETED, MODIFIED, etc.)")
    block_score: float = Field(..., description="Complexity score for this block")
    metrics: BlockMetricsSchema = Field(..., description="Detailed metrics with weighted calculations")


class SkippedBlockSchema(BaseModel):
    """Schema for skipped blocks."""

    key: str = Field(..., description="Property key")
    type: str = Field(..., description="Change type")
    reason: str = Field(..., description="Reason for skipping")


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
    total_complexity: float = Field(..., description="Sum of all block complexity scores")
    risk_level: str = Field(..., description="Overall risk level classification")
    risk_interpretation: str = Field(..., description="Interpretation of the overall risk")
    blocks_calculated: int = Field(..., description="Number of blocks included in complexity calculation")
    blocks_skipped: int = Field(..., description="Number of blocks skipped from calculation")
    blocks: List[BlockDetailSchema] = Field(..., description="Detailed breakdown of calculated blocks")
    skipped: List[SkippedBlockSchema] = Field(..., description="List of skipped blocks with reasons")
