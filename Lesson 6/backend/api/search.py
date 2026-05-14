from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from backend.database.connection import get_session
from backend.models.database import ContentItem, Topic, ContentTopic, ContentMetadata, Document
from backend.models.schemas import (
    SearchRequest,
    SearchResponse,
    SearchResult,
    ContentItemResponse,
    TopicSearchRequest,
    TopicResponse,
    TopicStatsResponse,
    ContentTopicResponse,
    ContentMetadataResponse,
)
from backend.embeddings.generator import EmbeddingGenerator
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/search/semantic", response_model=SearchResponse)
async def semantic_search(
    request: SearchRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    Semantic search using pgvector cosine similarity.

    Combines vector similarity with metadata filtering for precise results.
    """
    try:
        # Generate embedding for query
        embedding_gen = EmbeddingGenerator()
        query_embedding = await embedding_gen.generate_embedding(request.query)

        # Build base query
        query = select(ContentItem)

        # Apply source type filter if provided
        if request.source_types:
            query = query.join(Document).where(
                Document.source_type.in_(request.source_types)
            )

        # Apply topic filter if provided
        if request.topics:
            query = query.join(ContentTopic).join(Topic).where(
                Topic.name.in_(request.topics)
            )

        # Apply difficulty filter if provided (requires ContentMetadata join)
        if request.difficulty:
            query = query.join(ContentMetadata).where(
                ContentMetadata.difficulty == request.difficulty
            )

        # Add vector similarity ordering
        # pgvector uses <=> operator for cosine distance (1 - cosine similarity)
        query = query.where(ContentItem.embedding.isnot(None))
        query = query.order_by(ContentItem.embedding.cosine_distance(query_embedding))
        query = query.limit(request.limit)

        # Execute query
        result = await session.execute(query)
        content_items = result.scalars().all()

        # Build search results with similarity scores and metadata
        search_results = []
        for item in content_items:
            # Calculate similarity score (1 - distance)
            # Note: This is a simplified calculation; in practice, you'd use the distance from the query
            similarity = 1.0  # Placeholder - actual similarity would come from the vector distance

            # Load topics for this item
            topics_result = await session.execute(
                select(ContentTopic, Topic)
                .join(Topic)
                .where(ContentTopic.content_item_id == item.id)
            )
            topics_data = topics_result.all()

            topics = [
                ContentTopicResponse(
                    topic=TopicResponse.model_validate(topic),
                    relevance_score=ct.relevance_score,
                    coverage_depth=ct.coverage_depth,
                )
                for ct, topic in topics_data
            ]

            # Load metadata
            metadata_result = await session.execute(
                select(ContentMetadata).where(ContentMetadata.content_item_id == item.id)
            )
            metadata = metadata_result.scalar_one_or_none()
            metadata_response = (
                ContentMetadataResponse.model_validate(metadata) if metadata else None
            )

            search_results.append(
                SearchResult(
                    content_item=ContentItemResponse.model_validate(item),
                    similarity_score=similarity,
                    topics=topics,
                    metadata=metadata_response,
                )
            )

        logger.info(f"Semantic search returned {len(search_results)} results for query: {request.query[:50]}")

        return SearchResponse(
            results=search_results,
            total=len(search_results),
        )

    except Exception as e:
        logger.error(f"Error in semantic search: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search/topics", response_model=SearchResponse)
async def topic_search(
    request: TopicSearchRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    Search content by topics and coverage depth.

    Returns content that mentions specified topics with minimum coverage depth.
    """
    try:
        # Query content items with matching topics
        query = (
            select(ContentItem)
            .join(ContentTopic)
            .join(Topic)
            .where(
                and_(
                    Topic.name.in_(request.topic_names),
                    ContentTopic.coverage_depth >= request.min_coverage_depth,
                )
            )
            .order_by(ContentTopic.coverage_depth.desc())
            .limit(request.limit)
        )

        result = await session.execute(query)
        content_items = result.scalars().all()

        # Build search results
        search_results = []
        for item in content_items:
            # Load topics for this item
            topics_result = await session.execute(
                select(ContentTopic, Topic)
                .join(Topic)
                .where(ContentTopic.content_item_id == item.id)
            )
            topics_data = topics_result.all()

            topics = [
                ContentTopicResponse(
                    topic=TopicResponse.model_validate(topic),
                    relevance_score=ct.relevance_score,
                    coverage_depth=ct.coverage_depth,
                )
                for ct, topic in topics_data
            ]

            # Load metadata
            metadata_result = await session.execute(
                select(ContentMetadata).where(ContentMetadata.content_item_id == item.id)
            )
            metadata = metadata_result.scalar_one_or_none()
            metadata_response = (
                ContentMetadataResponse.model_validate(metadata) if metadata else None
            )

            # Use coverage depth as similarity score
            max_coverage = max(
                (t.coverage_depth for t in topics if t.topic.name in request.topic_names),
                default=0,
            )
            similarity = max_coverage / 10.0  # Normalize to 0-1

            search_results.append(
                SearchResult(
                    content_item=ContentItemResponse.model_validate(item),
                    similarity_score=similarity,
                    topics=topics,
                    metadata=metadata_response,
                )
            )

        logger.info(f"Topic search returned {len(search_results)} results")

        return SearchResponse(
            results=search_results,
            total=len(search_results),
        )

    except Exception as e:
        logger.error(f"Error in topic search: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/topics", response_model=List[TopicStatsResponse])
async def list_topics(
    session: AsyncSession = Depends(get_session),
):
    """
    List all extracted topics with statistics.

    Shows topic frequency, average coverage depth, and content count.
    """
    try:
        # Query topics with aggregated statistics
        query = (
            select(
                Topic,
                func.count(ContentTopic.content_item_id).label("content_count"),
                func.avg(ContentTopic.coverage_depth).label("avg_coverage_depth"),
            )
            .join(ContentTopic)
            .group_by(Topic.id)
            .order_by(func.count(ContentTopic.content_item_id).desc())
        )

        result = await session.execute(query)
        topics_data = result.all()

        topic_stats = [
            TopicStatsResponse(
                topic=TopicResponse.model_validate(topic),
                total_mentions=content_count,
                avg_coverage_depth=float(avg_depth) if avg_depth else 0.0,
                content_count=content_count,
            )
            for topic, content_count, avg_depth in topics_data
        ]

        logger.info(f"Retrieved {len(topic_stats)} topics")

        return topic_stats

    except Exception as e:
        logger.error(f"Error listing topics: {e}")
        raise HTTPException(status_code=500, detail=str(e))
