"""Pydantic schemas for diff API requests and responses."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class DiffChangeSchema(BaseModel):
    """Schema for a single diff change."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "type": "MODIFIED",
                "key": "app.version",
                "source_line": 5,
                "target_line": 5,
                "source_value": "1.0.0",
                "target_value": "2.0.0",
                "keyword_changes": [
                    {
                        "old_token": "1.0.0",
                        "new_token": "2.0.0",
                        "old_start": 0,
                        "old_end": 5,
                        "new_start": 0,
                        "new_end": 5
                    }
                ]
            }
        },
    )

    type: str = Field(..., description="Type of change")
    key: str = Field(..., description="Property key")
    source_line: Optional[int] = Field(None, description="Line number in source file")
    target_line: Optional[int] = Field(None, description="Line number in target file")
    source_value: Optional[str] = Field(None, description="Value in source file")
    target_value: Optional[str] = Field(None, description="Value in target file")
    keyword_changes: Optional[List[Dict]] = Field(None, description="Keyword/token changes with positions (only for MODIFIED and MOVED_AND_MODIFIED types)")
    message: Optional[str] = Field(None, description="Additional message about the change")


class DiffSummarySchema(BaseModel):
    """Schema for diff summary statistics."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "added": 5,
                "deleted": 2,
                "modified": 3,
                "moved": 4,
                "moved_and_modified": 1,
            }
        }
    )

    added: int = Field(..., description="Number of added properties")
    deleted: int = Field(..., description="Number of deleted properties")
    modified: int = Field(..., description="Number of modified properties")
    moved: int = Field(..., description="Number of moved properties")
    moved_and_modified: int = Field(..., description="Number of moved and modified properties")


class DiffRequest(BaseModel):
    """Request schema for computing diff from content strings."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "source_content": "key1=value1\nkey2=value2",
                "target_content": "key1=value1\nkey2=value3",
                "normalize": True,
            }
        }
    )

    source_content: str = Field(..., description="Content of the source property file")
    target_content: str = Field(..., description="Content of the target property file")
    normalize: bool = Field(
        True, description="Whether to normalize ASTs before comparison"
    )
    source_file_name: Optional[str] = Field(
        None, description="Optional source file name for reference"
    )
    target_file_name: Optional[str] = Field(
        None, description="Optional target file name for reference"
    )


class DiffResponse(BaseModel):
    """Response schema for diff computation."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "source_file": "source.properties",
                "target_file": "target.properties",
                "changes": [],
                "summary": {
                    "added": 0,
                    "deleted": 0,
                    "modified": 0,
                    "moved": 0,
                    "moved_and_modified": 0,
                },
            }
        }
    )

    source_file: str = Field(..., description="Source file path or identifier")
    target_file: str = Field(..., description="Target file path or identifier")
    changes: List[DiffChangeSchema] = Field(..., description="List of detected changes")
    summary: DiffSummarySchema = Field(..., description="Summary statistics")


class DiffFileRequest(BaseModel):
    """Request schema for file upload diff computation."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "normalize": True,
            }
        }
    )

    normalize: bool = Field(
        True, description="Whether to normalize ASTs before comparison"
    )


class HealthResponse(BaseModel):
    """Health check response schema."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "healthy",
                "version": "1.0.0",
            }
        }
    )

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")