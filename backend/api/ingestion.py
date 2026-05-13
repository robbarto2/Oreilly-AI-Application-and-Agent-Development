from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.database.connection import get_session
from backend.models.database import Document, ContentItem, SourceType
from backend.models.schemas import (
    DocumentResponse,
    UploadResponse,
    ProcessingStatus,
    ContentItemResponse,
)
from backend.parsers.pptx_parser import PPTXParser
from backend.parsers.docx_parser import DOCXParser
from backend.parsers.pdf_parser import PDFParser
from backend.embeddings.chunker import SemanticChunker
from backend.embeddings.generator import EmbeddingGenerator
from backend.config.settings import settings
from typing import List
from pathlib import Path
import logging
import shutil
from uuid import UUID

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize parsers
parsers = [
    PPTXParser(),
    DOCXParser(),
    PDFParser(),
]


@router.post("/ingest/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
):
    """
    Upload a document file for ingestion.

    Supported formats: PPTX, DOCX, PDF
    """
    try:
        # Validate file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ['.pptx', '.docx', '.pdf', '.ppt', '.doc']:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file_ext}. Supported: PPTX, DOCX, PDF"
            )

        # Create upload directory if it doesn't exist
        upload_dir = Path(settings.content_upload_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)

        # Save file
        file_path = upload_dir / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Determine source type
        source_type_map = {
            '.pptx': SourceType.PPTX,
            '.ppt': SourceType.PPTX,
            '.docx': SourceType.DOCX,
            '.doc': SourceType.DOCX,
            '.pdf': SourceType.PDF,
        }
        source_type = source_type_map.get(file_ext)

        # Create document record
        document = Document(
            title=file.filename,
            source_type=source_type,
            file_path=str(file_path),
            metadata={"status": "uploaded", "original_filename": file.filename},
        )

        session.add(document)
        await session.commit()
        await session.refresh(document)

        logger.info(f"Document uploaded: {document.id} - {file.filename}")

        return UploadResponse(
            document_id=document.id,
            message=f"File uploaded successfully. Use /ingest/process/{document.id} to process it.",
        )

    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest/process/{document_id}", response_model=ProcessingStatus)
async def process_document(
    document_id: UUID,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    """
    Process an uploaded document: parse, chunk, generate embeddings, and store.

    This is a long-running operation that runs in the background.
    """
    try:
        # Get document
        result = await session.execute(
            select(Document).where(Document.id == document_id)
        )
        document = result.scalar_one_or_none()

        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        if document.metadata and document.metadata.get("status") == "processing":
            raise HTTPException(status_code=400, detail="Document is already being processed")

        # Update status to processing
        document.metadata = document.metadata or {}
        document.metadata["status"] = "processing"
        await session.commit()

        # Schedule background processing
        background_tasks.add_task(
            _process_document_background,
            document_id,
            document.file_path,
            document.source_type,
        )

        return ProcessingStatus(
            document_id=document_id,
            status="processing",
            message="Document processing started in background",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting document processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def _process_document_background(
    document_id: UUID,
    file_path: str,
    source_type: SourceType,
):
    """Background task to process document"""
    from backend.database.connection import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        try:
            logger.info(f"Processing document {document_id}")

            # Select appropriate parser
            parser = None
            for p in parsers:
                if p.supports(file_path):
                    parser = p
                    break

            if not parser:
                raise ValueError(f"No parser found for {file_path}")

            # Parse document
            parsed_content = await parser.parse(file_path)
            logger.info(f"Document parsed: {document_id}")

            # Chunk content
            chunker = SemanticChunker()
            chunks = await chunker.chunk_content(parsed_content)
            logger.info(f"Created {len(chunks)} chunks for document {document_id}")

            # Generate embeddings
            embedding_gen = EmbeddingGenerator()
            chunk_texts = [chunk[0] for chunk in chunks]
            embeddings = await embedding_gen.generate_embeddings_batch(chunk_texts)

            # Store content items with embeddings
            content_items_created = 0
            for (chunk_text, node, context), embedding in zip(chunks, embeddings):
                content_item = ContentItem(
                    document_id=document_id,
                    item_type=node.item_type,
                    title=node.title,
                    content=chunk_text,
                    sequence_order=node.sequence_order,
                    metadata=node.metadata,
                    embedding=embedding,
                )
                session.add(content_item)
                content_items_created += 1

            # Update document status
            result = await session.execute(
                select(Document).where(Document.id == document_id)
            )
            document = result.scalar_one()
            document.metadata["status"] = "completed"
            document.metadata["content_items_created"] = content_items_created

            await session.commit()

            logger.info(f"Document processing completed: {document_id}")

        except Exception as e:
            logger.error(f"Error in background processing for {document_id}: {e}")

            # Update document status to failed
            result = await session.execute(
                select(Document).where(Document.id == document_id)
            )
            document = result.scalar_one_or_none()
            if document:
                document.metadata = document.metadata or {}
                document.metadata["status"] = "failed"
                document.metadata["error"] = str(e)
                await session.commit()


@router.get("/ingest/status/{document_id}", response_model=ProcessingStatus)
async def get_processing_status(
    document_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    """Get processing status for a document"""
    try:
        result = await session.execute(
            select(Document).where(Document.id == document_id)
        )
        document = result.scalar_one_or_none()

        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        metadata = document.metadata or {}
        status = metadata.get("status", "unknown")

        return ProcessingStatus(
            document_id=document_id,
            status=status,
            message=metadata.get("error") if status == "failed" else None,
            content_items_created=metadata.get("content_items_created"),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting processing status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents", response_model=List[DocumentResponse])
async def list_documents(
    session: AsyncSession = Depends(get_session),
):
    """List all ingested documents"""
    try:
        result = await session.execute(select(Document).order_by(Document.created_at.desc()))
        documents = result.scalars().all()

        return [DocumentResponse.model_validate(doc) for doc in documents]

    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    """Get document details"""
    try:
        result = await session.execute(
            select(Document).where(Document.id == document_id)
        )
        document = result.scalar_one_or_none()

        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        return DocumentResponse.model_validate(document)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/{document_id}/content", response_model=List[ContentItemResponse])
async def get_document_content(
    document_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    """Get all content items for a document"""
    try:
        result = await session.execute(
            select(ContentItem)
            .where(ContentItem.document_id == document_id)
            .order_by(ContentItem.sequence_order)
        )
        content_items = result.scalars().all()

        return [ContentItemResponse.model_validate(item) for item in content_items]

    except Exception as e:
        logger.error(f"Error getting document content: {e}")
        raise HTTPException(status_code=500, detail=str(e))
