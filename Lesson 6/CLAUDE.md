# Course Strategy Engine - Project Guide

## Project Overview

This is an AI-powered curriculum strategy copilot that helps technical educators identify and prioritize future course opportunities. The system analyzes existing educational content and monitors AI ecosystem trends to recommend strategic course investments.

**Current Status:** Phase 1 Complete (Content Ingestion & Semantic Search)

## Architecture

### Technology Stack
- **Backend:** FastAPI with async/await
- **Database:** PostgreSQL 14+ with pgvector extension
- **LLM Provider:** Anthropic Claude (Opus 4.7 / Sonnet 4.6)
- **Document Parsing:** python-pptx, python-docx, PyMuPDF
- **Python Version:** 3.10+
- **Package Manager:** uv (fast, modern Python package management)

### Project Structure

```
Lesson 6/
├── backend/
│   ├── api/              # FastAPI endpoints
│   │   ├── main.py       # App initialization, CORS, startup
│   │   ├── ingestion.py  # Document upload & processing
│   │   └── search.py     # Semantic search endpoints
│   ├── config/
│   │   └── settings.py   # Pydantic settings (env vars)
│   ├── database/
│   │   └── connection.py # SQLAlchemy async engine, pgvector init
│   ├── embeddings/
│   │   ├── chunker.py    # Hierarchy-aware semantic chunking
│   │   └── generator.py  # Embedding generation (needs implementation)
│   ├── models/
│   │   ├── database.py   # SQLAlchemy models
│   │   └── schemas.py    # Pydantic request/response models
│   └── parsers/
│       ├── base.py       # Abstract DocumentParser interface
│       ├── pptx_parser.py  # PowerPoint parsing
│       ├── docx_parser.py  # Word document parsing
│       └── pdf_parser.py   # PDF parsing
├── uploads/              # Document upload directory
├── .env.example          # Environment variable template
├── main.py               # Application entry point
└── pyproject.toml        # Dependencies and project metadata
```

## Key Design Principles

### 1. Hierarchical Content Preservation
**CRITICAL:** Do NOT flatten documents into raw text blobs. Preserve semantic structure:

```
Document → Sections → Slides/Paragraphs → Notes → Concepts
```

This hierarchy is stored in the database via `parent_id` self-reference in `content_items` table.

### 2. Coverage Depth Model
Track not just topic existence, but **how deeply** each topic is covered (1-10 scale):
- 1-3: Mentioned briefly
- 4-6: Moderate coverage
- 7-9: Deep dive
- 10: Comprehensive mastery

### 3. Semantic Chunking
Content is chunked while respecting hierarchy boundaries. The chunker never splits mid-section or mid-concept. Context from parent nodes is prepended to each chunk.

## Database Schema

### Core Tables

**documents:**
- Stores document metadata (title, source_type, file_path, authors)
- `source_type` enum: pptx, docx, pdf, markdown, github

**content_items:**
- Hierarchical content chunks with self-reference via `parent_id`
- `item_type` enum: section, slide, paragraph, code_block, table, list
- `embedding` vector(1024) for pgvector similarity search
- `sequence_order` preserves original document order

**topics:**
- Extracted topics/concepts (name, category, description)

**content_topics:**
- Many-to-many: links content_items to topics
- `relevance_score` (0-1): how strongly topic appears
- `coverage_depth` (1-10): depth of coverage

**content_metadata:**
- Additional metadata: frameworks, difficulty, audience, duration

### Indexes
- GIN index on JSONB metadata fields
- HNSW index on embedding vectors (pgvector)
- B-tree indexes on foreign keys

## API Endpoints

### Ingestion
- `POST /api/v1/ingest/upload` - Upload document file
- `POST /api/v1/ingest/process/{document_id}` - Process uploaded document (background task)
- `GET /api/v1/ingest/status/{document_id}` - Check processing status
- `GET /api/v1/documents` - List all documents
- `GET /api/v1/documents/{document_id}` - Get document details
- `GET /api/v1/documents/{document_id}/content` - Get content hierarchy

### Search
- `POST /api/v1/search/semantic` - Semantic search via query embedding
- `POST /api/v1/search/topics` - Search by topic coverage
- `GET /api/v1/topics` - List all extracted topics with statistics

## Development Guidelines

### Running the Application

```bash
# Set up database
docker run -d --name postgres-pgvector \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=course_strategy \
  -p 5432:5432 \
  pgvector/pgvector:pg16

# Install dependencies
uv sync

# Configure environment
cp .env.example .env
# Edit .env with your ANTHROPIC_API_KEY

# Start server
python main.py
```

Access at: http://localhost:8000/docs

### Adding New Document Parsers

1. Inherit from `backend/parsers/base.py::DocumentParser`
2. Implement `parse()` and `supports()` methods
3. Return `ParsedContent` with hierarchical structure
4. Register parser in `backend/api/ingestion.py::parsers` list

Example:
```python
class MarkdownParser(DocumentParser):
    def supports(self, file_path: str) -> bool:
        return file_path.lower().endswith('.md')
    
    async def parse(self, file_path: str) -> ParsedContent:
        # Parse and return hierarchical structure
        pass
```

### Embedding Generation (TODO)

**Current State:** `backend/embeddings/generator.py` uses mock embeddings for development.

**Production Implementation Needed:**

```python
# Option 1: OpenAI embeddings
from openai import AsyncOpenAI

client = AsyncOpenAI()
response = await client.embeddings.create(
    model="text-embedding-3-large",
    input=text,
    dimensions=1024  # or 3072 for full dimension
)
embedding = response.data[0].embedding
```

**Action Required:** Replace `_mock_embedding()` with actual embedding service before production use.

## Testing with Real Content

### Test Workflow

1. **Upload a PowerPoint deck:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/ingest/upload \
     -F "file=@your_course.pptx"
   ```

2. **Process the document:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/ingest/process/{document_id}
   ```

3. **Search for content:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/search/semantic \
     -H "Content-Type: application/json" \
     -d '{"query": "LangGraph multi-agent systems", "limit": 10}'
   ```

4. **Verify in database:**
   ```sql
   -- Check content hierarchy
   SELECT id, title, item_type, parent_id, sequence_order 
   FROM content_items 
   WHERE document_id = '...' 
   ORDER BY sequence_order;
   
   -- Test vector search
   SELECT title, content, 1 - (embedding <=> '[...]') AS similarity
   FROM content_items
   ORDER BY embedding <=> '[...]'
   LIMIT 10;
   ```

## Known Issues & TODOs

### Phase 1 (Current)
- [ ] **CRITICAL:** Implement real embedding generation (replace mock embeddings)
- [ ] Add Alembic migrations for database schema management
- [ ] Implement topic extraction logic (currently not extracted)
- [ ] Add content_metadata population during ingestion
- [ ] Add GitHub repository parser
- [ ] Add Markdown parser
- [ ] Improve PDF section detection (currently basic)
- [ ] Add unit tests for parsers
- [ ] Add integration tests for full ingestion pipeline

### Future Phases
- [ ] Phase 2: External trend monitoring (GitHub, YouTube, Reddit agents)
- [ ] Phase 3: Recommendation engine with scoring logic
- [ ] Phase 4: Multi-agent orchestration with LangGraph
- [ ] Phase 5: Long-term memory system
- [ ] Phase 6: Autonomous research workflows

## Important Notes

### Git Workflow
- **Main branch:** `main` - stable, production-ready code
- **Feature branches:** `feature/phase-N-description` - development work
- Always rebase feature branches on main before merging
- Use conventional commits: `feat:`, `fix:`, `docs:`, etc.

### Code Style
- Use `black` for formatting
- Use `ruff` for linting
- Type hints required for all functions
- Async/await for all I/O operations
- Document complex logic with comments

### Security Considerations
- Never commit `.env` files (in .gitignore)
- API keys should be in environment variables only
- Validate file uploads (size, type)
- Sanitize user inputs before database queries
- Use parameterized queries (SQLAlchemy handles this)

## PRD Reference

Full Product Requirements Document available at:
`course_strategy_engine_prd_markdown.md`

Key sections:
- Section 8-17: Content ingestion strategy (implemented)
- Section 18: External trend monitoring (Phase 2)
- Section 19: Agent architecture (Phase 4)
- Section 20-21: Recommendation logic (Phase 3)

## Contact & Support

- **GitHub Repository:** https://github.com/robbarto2/Oreilly-AI-Application-and-Agent-Development
- **Current Branch:** `main`
- **Working Directory:** `Lesson 6/`

For questions or issues, refer to the README.md or create a GitHub issue.
