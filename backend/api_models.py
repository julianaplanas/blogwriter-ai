"""
FastAPI-specific models that avoid conflicts with the config/models.py
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ImageMetadata(BaseModel):
    """Image metadata schema"""
    url: str = Field(..., description="Direct URL to the image")
    alt_text: str = Field(..., description="Alt text description for the image")
    photographer: str = Field(..., description="Name of the photographer")
    source_url: str = Field(..., description="URL to the source page")
    width: int = Field(0, description="Image width in pixels")
    height: int = Field(0, description="Image height in pixels")


class GenerateRequest(BaseModel):
    """Request schema for blog post generation"""
    topic: str = Field(..., description="Blog topic to write about", min_length=3, max_length=200)
    provider: str = Field("groq", description="LLM provider to use")
    model: Optional[str] = Field(None, description="Specific model to use (auto-selected if not specified)")
    research_count: int = Field(5, description="Number of articles to research", ge=1, le=10)
    include_images: bool = Field(True, description="Whether to fetch and include images")
    image_count: int = Field(3, description="Number of images to fetch", ge=1, le=5)
    embed_images: bool = Field(True, description="Whether to embed images in the content")


class EditRequest(BaseModel):
    """Request schema for blog post editing"""
    markdown: str = Field(..., description="Existing blog post content in Markdown", min_length=10)
    instruction: str = Field(..., description="Natural language editing instruction", min_length=5, max_length=500)
    provider: str = Field("groq", description="LLM provider to use")
    model: Optional[str] = Field(None, description="Specific model to use")


class EnhancedEditRequest(BaseModel):
    """Enhanced request schema for blog post editing with advanced features"""
    markdown: str = Field(..., description="Existing blog post content in Markdown", min_length=10)
    instruction: str = Field(..., description="Natural language editing instruction", min_length=5, max_length=500)
    provider: str = Field("groq", description="LLM provider to use")
    model: Optional[str] = Field(None, description="Specific model to use")
    temperature: float = Field(0.3, description="LLM temperature (0.0-1.0)", ge=0.0, le=1.0)
    max_tokens: int = Field(4000, description="Maximum tokens to generate", gt=0, le=8000)
    track_version: bool = Field(True, description="Whether to track this edit in version history")
    export_diff: bool = Field(False, description="Whether to include diff information in response")


class EditResponse(BaseModel):
    """Enhanced response schema for blog post editing"""
    markdown: str = Field(..., description="Edited blog content")
    instruction_applied: str = Field(..., description="The instruction that was applied")
    edited_at: str = Field(..., description="Timestamp when edit was completed")
    success: bool = Field(..., description="Whether the edit was successful")
    changes_summary: Optional[str] = Field(None, description="Summary of changes made")
    diff_text: Optional[str] = Field(None, description="Text diff of changes")
    model_used: str = Field(..., description="Model used for editing")
    provider_used: str = Field(..., description="Provider used for editing")
    error_message: Optional[str] = Field(None, description="Error message if edit failed")


class BlogResponse(BaseModel):
    """Response schema for generated blog posts"""
    id: str = Field(..., description="Unique blog post identifier")
    markdown: str = Field(..., description="Generated blog content in Markdown")
    references: List[Dict[str, Any]] = Field(..., description="Research sources used")
    images: List[ImageMetadata] = Field(..., description="Image metadata")
    metadata: Dict[str, Any] = Field(..., description="Additional metadata about the generation")


class VersionHistoryResponse(BaseModel):
    """Response schema for version history"""
    versions: List[Dict[str, Any]] = Field(..., description="List of version history entries")
    current_version: Optional[str] = Field(None, description="Current version identifier")


class BlogPost(BaseModel):
    """Database model for stored blog posts"""
    id: str = Field(..., description="Unique identifier")
    topic: str = Field(..., description="Blog topic")
    content: str = Field(..., description="Blog content in Markdown")
    word_count: int = Field(0, description="Word count of the content")
    sources: List[str] = Field(default_factory=list, description="URLs of research sources")
    images: List[Dict[str, Any]] = Field(default_factory=list, description="Image metadata")
    provider: str = Field("groq", description="LLM provider used")
    model: str = Field("auto", description="Model used for generation")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")

    class Config:
        """Pydantic configuration"""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ErrorResponse(BaseModel):
    """Error response schema"""
    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Specific error code")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")


class HealthResponse(BaseModel):
    """Health check response schema"""
    status: str = Field(..., description="Overall health status")
    timestamp: datetime = Field(..., description="Check timestamp")
    agents: Dict[str, bool] = Field(..., description="Status of each AI agent")


class ListPostsResponse(BaseModel):
    """Response for listing blog posts"""
    posts: List[Dict[str, Any]] = Field(..., description="List of blog post summaries")
    total: int = Field(..., description="Total number of posts")
    limit: int = Field(..., description="Limit used for pagination")
    offset: int = Field(..., description="Offset used for pagination")
