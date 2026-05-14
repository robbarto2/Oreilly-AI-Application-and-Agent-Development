# Phase 1 Testing Guide

## Prerequisites Check ✅

- ✅ Docker installed
- ✅ uv installed
- ✅ Python 3.10.13

## Step 1: Start Docker Desktop

1. Open **Docker Desktop** application
2. Wait for Docker to fully start (whale icon in menu bar should be static)

## Step 2: Set Up PostgreSQL with pgvector

```bash
cd "Lesson 6"

# Start PostgreSQL with pgvector extension
docker run -d --name postgres-pgvector \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_DB=course_strategy \
  -p 5432:5432 \
  pgvector/pgvector:pg16

# Verify container is running
docker ps | grep postgres-pgvector

# Test connection (should see "course_strategy" database)
docker exec postgres-pgvector psql -U postgres -c '\l'
```

## Step 3: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your settings
nano .env  # or use your preferred editor
```

**Required .env configuration:**
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/course_strategy
ANTHROPIC_API_KEY=your_actual_api_key_here
EMBEDDING_MODEL=claude-3-5-sonnet-20241022
CONTENT_UPLOAD_DIR=./uploads
```

**Get your Anthropic API key:**
- Go to: https://console.anthropic.com/settings/keys
- Create a new API key if needed
- Copy it to the .env file

## Step 4: Install Dependencies

```bash
# Install all dependencies with uv
uv sync

# Activate virtual environment
source .venv/bin/activate

# Verify installation
python -c "import fastapi; print('FastAPI installed')"
python -c "import anthropic; print('Anthropic SDK installed')"
```

## Step 5: Initialize Database

```bash
# Start Python shell
python

# Run initialization
>>> from backend.database.connection import init_db
>>> import asyncio
>>> asyncio.run(init_db())

# You should see:
# - pgvector extension enabled
# - Database tables created

# Exit Python
>>> exit()
```

**Alternative: Manual verification**
```bash
# Connect to database
docker exec -it postgres-pgvector psql -U postgres -d course_strategy

# Check if pgvector extension exists
\dx

# List tables (should see: documents, content_items, topics, content_topics, content_metadata)
\dt

# Exit psql
\q
```

## Step 6: Start the API Server

```bash
# Make sure you're in Lesson 6 directory
cd "Lesson 6"

# Start the server
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Access the API:**
- API Docs (Swagger UI): http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

## Step 7: Test Document Upload & Processing

### Option A: Using the Swagger UI (Easiest)

1. Go to http://localhost:8000/docs
2. Expand **POST /api/v1/ingest/upload**
3. Click **"Try it out"**
4. Click **"Choose File"** and select a PPTX, DOCX, or PDF
5. Click **"Execute"**
6. Copy the `document_id` from the response

7. Expand **POST /api/v1/ingest/process/{document_id}**
8. Click **"Try it out"**
9. Paste the `document_id`
10. Click **"Execute"**

11. Check status: **GET /api/v1/ingest/status/{document_id}**
12. Wait until status shows "completed"

### Option B: Using curl (Command Line)

```bash
# Upload a document
curl -X POST http://localhost:8000/api/v1/ingest/upload \
  -F "file=@/path/to/your/document.pptx"

# Response will include document_id
# {
#   "document_id": "123e4567-e89b-12d3-a456-426614174000",
#   "message": "File uploaded successfully..."
# }

# Process the document (replace with your document_id)
DOC_ID="123e4567-e89b-12d3-a456-426614174000"

curl -X POST http://localhost:8000/api/v1/ingest/process/$DOC_ID

# Check processing status
curl http://localhost:8000/api/v1/ingest/status/$DOC_ID

# List all documents
curl http://localhost:8000/api/v1/documents

# Get document content
curl http://localhost:8000/api/v1/documents/$DOC_ID/content
```

## Step 8: Test Semantic Search

```bash
# Search for content
curl -X POST http://localhost:8000/api/v1/search/semantic \
  -H "Content-Type: application/json" \
  -d '{
    "query": "LangGraph multi-agent systems",
    "limit": 10
  }'

# Search with filters
curl -X POST http://localhost:8000/api/v1/search/semantic \
  -H "Content-Type: application/json" \
  -d '{
    "query": "artificial intelligence",
    "limit": 5,
    "source_types": ["pptx", "docx"]
  }'

# List all extracted topics
curl http://localhost:8000/api/v1/topics
```

## Step 9: Verify in Database

```bash
# Connect to database
docker exec -it postgres-pgvector psql -U postgres -d course_strategy

# Check documents
SELECT id, title, source_type, created_at FROM documents;

# Check content items (with hierarchy)
SELECT id, title, item_type, parent_id, sequence_order 
FROM content_items 
WHERE document_id = 'your-document-id-here'
ORDER BY sequence_order
LIMIT 20;

# Check embeddings exist
SELECT COUNT(*) as items_with_embeddings 
FROM content_items 
WHERE embedding IS NOT NULL;

# Test vector search (example - replace with actual embedding)
SELECT title, content, 
       1 - (embedding <=> '[0.1, 0.2, ...]'::vector) AS similarity
FROM content_items
WHERE embedding IS NOT NULL
ORDER BY embedding <=> '[0.1, 0.2, ...]'::vector
LIMIT 5;

# Exit
\q
```

## Expected Results

### ✅ Successful Test Checklist:

- [ ] PostgreSQL container running
- [ ] Database initialized with tables
- [ ] API server starts without errors
- [ ] Document uploads successfully
- [ ] Processing completes (status = "completed")
- [ ] Content items created in database
- [ ] Hierarchy preserved (parent_id relationships)
- [ ] Embeddings generated (even if mock)
- [ ] Semantic search returns results
- [ ] Topics list populated

## Troubleshooting

### Database Connection Errors

```bash
# Check if PostgreSQL is running
docker ps | grep postgres-pgvector

# Check logs
docker logs postgres-pgvector

# Restart container
docker restart postgres-pgvector
```

### Import Errors

```bash
# Reinstall dependencies
uv sync --reinstall

# Or with pip
pip install -e .
```

### File Upload Errors

```bash
# Verify uploads directory exists
ls -la uploads/

# Create if missing
mkdir -p uploads
chmod 755 uploads
```

### Mock Embeddings Warning

If you see: `"Using mock embedding - implement actual embedding generation"`

This is expected! Phase 1 uses mock embeddings for development. To implement real embeddings, see `backend/embeddings/generator.py` and uncomment the OpenAI implementation.

## Sample Test Documents

If you need test documents:

**Create a simple test PPTX:**
1. Open PowerPoint
2. Create 3-5 slides about AI/ML topics
3. Add speaker notes to slides
4. Save as `test_course.pptx`
5. Upload to test the system

**Or use existing course materials:**
- Upload one of your actual course PowerPoint decks
- This will give you real-world testing results

## Next Steps After Testing

Once Phase 1 works:

1. **Implement real embeddings** - Replace mock embeddings in `backend/embeddings/generator.py`
2. **Add topic extraction** - Implement actual topic extraction logic
3. **Test with multiple documents** - Upload several course materials
4. **Validate search quality** - Test if semantic search finds relevant content
5. **Move to Phase 2** - Start building trend monitoring agents

## Monitoring & Logs

```bash
# Watch API logs in real-time
tail -f /tmp/course_strategy_api.log  # if logging to file

# Or watch server output directly
# Server logs appear in terminal where you ran `python main.py`
```

## Stopping Everything

```bash
# Stop API server
# Press CTRL+C in terminal running main.py

# Stop PostgreSQL container
docker stop postgres-pgvector

# Remove container (if you want to start fresh)
docker rm postgres-pgvector
```

## Quick Reset (Start Over)

```bash
# Stop and remove everything
docker stop postgres-pgvector
docker rm postgres-pgvector

# Start fresh
docker run -d --name postgres-pgvector \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_DB=course_strategy \
  -p 5432:5432 \
  pgvector/pgvector:pg16

# Reinitialize database
python -c "from backend.database.connection import init_db; import asyncio; asyncio.run(init_db())"

# Restart server
python main.py
```

---

**Questions or Issues?**

Refer to:
- `README.md` - General documentation
- `CLAUDE.md` - Architecture and development guide
- `course_strategy_engine_prd_markdown.md` - Full product requirements

Or check server logs for error messages.
