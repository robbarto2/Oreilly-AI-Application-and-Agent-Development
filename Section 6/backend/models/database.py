from sqlalchemy import Column, String, Integer, Float, Text, TIMESTAMP, ForeignKey, Enum, ARRAY, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
import uuid
import enum
from datetime import datetime

Base = declarative_base()


class SourceType(str, enum.Enum):
    PPTX = "pptx"
    DOCX = "docx"
    PDF = "pdf"
    MARKDOWN = "markdown"
    GITHUB = "github"


class ItemType(str, enum.Enum):
    SECTION = "section"
    SLIDE = "slide"
    PARAGRAPH = "paragraph"
    CODE_BLOCK = "code_block"
    TABLE = "table"
    LIST = "list"


class Difficulty(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(Text, nullable=False)
    source_type = Column(Enum(SourceType), nullable=False)
    file_path = Column(Text, nullable=False)
    authors = Column(ARRAY(Text), nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    metadata = Column(JSONB, nullable=True)

    # Relationships
    content_items = relationship("ContentItem", back_populates="document", cascade="all, delete-orphan")


class ContentItem(Base):
    __tablename__ = "content_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("content_items.id"), nullable=True)
    item_type = Column(Enum(ItemType), nullable=False)
    title = Column(Text, nullable=True)
    content = Column(Text, nullable=False)
    sequence_order = Column(Integer, nullable=False, default=0)
    metadata = Column(JSONB, nullable=True)
    embedding = Column(Vector(1024), nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)

    # Relationships
    document = relationship("Document", back_populates="content_items")
    parent = relationship("ContentItem", remote_side=[id], backref="children")
    topics = relationship("ContentTopic", back_populates="content_item", cascade="all, delete-orphan")
    content_metadata = relationship("ContentMetadata", back_populates="content_item", uselist=False, cascade="all, delete-orphan")


class Topic(Base):
    __tablename__ = "topics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False, unique=True)
    category = Column(Text, nullable=True)
    description = Column(Text, nullable=True)

    # Relationships
    content_topics = relationship("ContentTopic", back_populates="topic", cascade="all, delete-orphan")


class ContentTopic(Base):
    __tablename__ = "content_topics"

    content_item_id = Column(UUID(as_uuid=True), ForeignKey("content_items.id"), primary_key=True)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("topics.id"), primary_key=True)
    relevance_score = Column(Float, nullable=False, default=0.0)
    coverage_depth = Column(Integer, nullable=False, default=1)

    # Relationships
    content_item = relationship("ContentItem", back_populates="topics")
    topic = relationship("Topic", back_populates="content_topics")


class ContentMetadata(Base):
    __tablename__ = "content_metadata"

    content_item_id = Column(UUID(as_uuid=True), ForeignKey("content_items.id"), primary_key=True)
    frameworks = Column(ARRAY(Text), nullable=True)
    difficulty = Column(Enum(Difficulty), nullable=True)
    audience = Column(Text, nullable=True)
    duration_minutes = Column(Integer, nullable=True)

    # Relationships
    content_item = relationship("ContentItem", back_populates="content_metadata")
