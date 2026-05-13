from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import UUID
from backend.models.database import SourceType, ItemType, Difficulty


class DocumentCreate(BaseModel):
    title: str
    source_type: SourceType
    file_path: str
    authors: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    source_type: SourceType
    file_path: str
    authors: Optional[List[str]] = None
    created_at: datetime
    metadata: Optional[Dict[str, Any]] = None


class ContentItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    document_id: UUID
    parent_id: Optional[UUID] = None
    item_type: ItemType
    title: Optional[str] = None
    content: str
    sequence_order: int
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime


class TopicResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    category: Optional[str] = None
    description: Optional[str] = None


class ContentTopicResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    topic: TopicResponse
    relevance_score: float
    coverage_depth: int


class ContentMetadataResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    frameworks: Optional[List[str]] = None
    difficulty: Optional[Difficulty] = None
    audience: Optional[str] = None
    duration_minutes: Optional[int] = None


class SearchRequest(BaseModel):
    query: str
    limit: int = Field(default=10, ge=1, le=100)
    source_types: Optional[List[SourceType]] = None
    topics: Optional[List[str]] = None
    difficulty: Optional[Difficulty] = None


class SearchResult(BaseModel):
    content_item: ContentItemResponse
    similarity_score: float
    topics: List[ContentTopicResponse] = []
    metadata: Optional[ContentMetadataResponse] = None


class SearchResponse(BaseModel):
    results: List[SearchResult]
    total: int


class TopicSearchRequest(BaseModel):
    topic_names: List[str]
    min_coverage_depth: int = Field(default=1, ge=1, le=10)
    limit: int = Field(default=10, ge=1, le=100)


class TopicStatsResponse(BaseModel):
    topic: TopicResponse
    total_mentions: int
    avg_coverage_depth: float
    content_count: int


class UploadResponse(BaseModel):
    document_id: UUID
    message: str


class ProcessingStatus(BaseModel):
    document_id: UUID
    status: str
    message: Optional[str] = None
    content_items_created: Optional[int] = None
    topics_extracted: Optional[int] = None
