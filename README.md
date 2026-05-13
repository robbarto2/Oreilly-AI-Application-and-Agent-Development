# Course Strategy Engine

AI-powered curriculum strategy copilot for technical educators. Phase 1: Content Ingestion & Semantic Search.

## Overview

The Course Strategy Engine helps experienced technical educators identify and prioritize future course opportunities by analyzing existing educational content and monitoring AI ecosystem trends.

**Phase 1 Features:**
- Document ingestion (PowerPoint, Word, PDF)
- Hierarchical content parsing (preserves structure, not flattened)
- Semantic embeddings with pgvector
- Topic extraction and coverage depth analysis
- Semantic search API
- RESTful API with FastAPI

## Architecture

```
FastAPI Backend
├── Document Parsers (PPTX, DOCX, PDF)
├── Semantic Chunker (hierarchy-aware)
├── Embedding Generator (Claude/OpenAI)
├── PostgreSQL + pgvector (vector search)
└── REST API (upload, process, search)
```

## Prerequisites

- **Python 3.10+**
- **PostgreSQL 14+ with pgvector extension**
- **Anthropic API key** (for embeddings and future agent workflows)
- **Docker** (recommended for PostgreSQL)

## Quick Start

### 1. Set up PostgreSQL with pgvector

Using Docker:

```bash
docker run -d --name postgres-pgvector \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=course_strategy \
  -p 5432:5432 \
  pgvector/pgvector:pg16
```

### 2. Install dependencies

Using `uv` (recommended):

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync
```

Or using pip:

```bash
pip install -e .
```

### 3. Configure environment

Copy the example environment file and edit with your credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/course_strategy
ANTHROPIC_API_KEY=your_api_key_here
EMBEDDING_MODEL=claude-3-5-sonnet-20241022
CONTENT_UPLOAD_DIR=./uploads
```

### 4. Start the API server

```bash
python main.py
```

The API will be available at `http://localhost:8000`

- **API Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Usage

### Upload a document

```bash
curl -X POST http://localhost:8000/api/v1/ingest/upload \
  -F "file=@your_course.pptx"
```

Response:
```json
{
  "document_id": "123e4567-e89b-12d3-a456-426614174000",
  "message": "File uploaded successfully. Use /ingest/process/{document_id} to process it."
}
```

### Process the document

```bash
curl -X POST http://localhost:8000/api/v1/ingest/process/{document_id}
```

This starts background processing: parsing → chunking → embedding → storage.

### Check processing status

```bash
curl http://localhost:8000/api/v1/ingest/status/{document_id}
```

### Semantic search

```bash
curl -X POST http://localhost:8000/api/v1/search/semantic \
  -H "Content-Type: application/json" \
  -d '{
    "query": "LangGraph multi-agent systems",
    "limit": 10
  }'
```

### List all documents

```bash
curl http://localhost:8000/api/v1/documents
```

### Get document content

```bash
curl http://localhost:8000/api/v1/documents/{document_id}/content
```

### List extracted topics

```bash
curl http://localhost:8000/api/v1/topics
```

## Project Structure

```
.
├── backend/
│   ├── api/
│   │   ├── main.py         # FastAPI application
│   │   ├── ingestion.py    # Document upload & processing endpoints
│   │   └── search.py       # Semantic search endpoints
│   ├── config/
│   │   └── settings.py     # Configuration management
│   ├── database/
│   │   └── connection.py   # Database connection & pgvector setup
│   ├── embeddings/
│   │   ├── chunker.py      # Semantic chunking (hierarchy-aware)
│   │   └── generator.py    # Embedding generation
│   ├── models/
│   │   ├── database.py     # SQLAlchemy models
│   │   └── schemas.py      # Pydantic API schemas
│   └── parsers/
│       ├── base.py         # Base parser interface
│       ├── pptx_parser.py  # PowerPoint parser
│       ├── docx_parser.py  # Word document parser
│       └── pdf_parser.py   # PDF parser
├── uploads/                # Document upload directory
├── main.py                 # Application entry point
├── pyproject.toml          # Project dependencies
└── README.md               # This file
```

## Database Schema

### Core Tables

1. **documents** - Document metadata
   - `id`, `title`, `source_type`, `file_path`, `authors`, `created_at`, `metadata`

2. **content_items** - Hierarchical content chunks
   - `id`, `document_id`, `parent_id` (self-reference), `item_type`, `title`, `content`
   - `sequence_order`, `metadata`, `embedding` (vector), `created_at`

3. **topics** - Extracted topics/concepts
   - `id`, `name`, `category`, `description`

4. **content_topics** - Many-to-many relationship
   - `content_item_id`, `topic_id`, `relevance_score`, `coverage_depth`

5. **content_metadata** - Specialized metadata
   - `content_item_id`, `frameworks`, `difficulty`, `audience`, `duration_minutes`

## Key Design Principles

### 1. Hierarchical Content Preservation

The system does NOT flatten documents into raw text blobs. Instead, it preserves semantic structure:

```
Document → Sections → Slides → Notes → Concepts
```

This hierarchy is critical for reasoning about content.

### 2. Coverage Depth Model

The system tracks not just topic existence, but **how deeply** each topic is covered (1-10 scale).

### 3. Semantic Chunking

Content is chunked while respecting hierarchy boundaries. We don't split mid-section or mid-concept.

## Development

### Running tests

```bash
pytest
```

### Code formatting

```bash
black backend/
ruff check backend/
```

## Important Notes

### Embedding Generation

**Current State:** The embedding generator uses mock embeddings for development.

**Production:** You'll need to implement actual embedding generation using:
- OpenAI's `text-embedding-3-large` model (3072 dimensions)
- Or another embedding service

See `backend/embeddings/generator.py` for implementation notes.

### Next Steps (Phase 2+)

- **Phase 2:** External trend monitoring (GitHub, YouTube, Reddit agents)
- **Phase 3:** Recommendation engine with scoring logic
- **Phase 4:** Multi-agent orchestration with LangGraph
- **Phase 5:** Long-term memory system
- **Phase 6:** Autonomous research workflows

## Troubleshooting

### Database connection errors

Ensure PostgreSQL is running and pgvector extension is installed:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### Import errors

Make sure you've installed dependencies and activated the virtual environment:

```bash
uv sync
source .venv/bin/activate  # On Unix
```

### File upload errors

Ensure the `uploads/` directory exists and has write permissions:

```bash
mkdir -p uploads
chmod 755 uploads
```

## License

MIT

## Contributing

This is an educational project. Contributions welcome!

## Support

For questions or issues, please open a GitHub issue.
