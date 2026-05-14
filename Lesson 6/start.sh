#!/bin/bash
# Course Strategy Engine - Startup Script

set -e  # Exit on error

echo "🚀 Starting Course Strategy Engine..."
echo ""

# Change to script directory
cd "$(dirname "$0")"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Check if PostgreSQL container exists
if docker ps -a | grep -q postgres-pgvector; then
    echo "✅ PostgreSQL container exists"

    # Check if it's running
    if ! docker ps | grep -q postgres-pgvector; then
        echo "▶️  Starting PostgreSQL container..."
        docker start postgres-pgvector
        sleep 3
    else
        echo "✅ PostgreSQL already running"
    fi
else
    echo "📦 Creating PostgreSQL container..."
    docker run -d --name postgres-pgvector \
      -e POSTGRES_PASSWORD=password \
      -e POSTGRES_USER=postgres \
      -e POSTGRES_DB=course_strategy \
      -p 5432:5432 \
      pgvector/pgvector:pg16

    echo "⏳ Waiting for PostgreSQL to start..."
    sleep 5

    echo "🔧 Initializing database..."
    uv run python -c "from backend.database.connection import init_db; import asyncio; asyncio.run(init_db())"
fi

echo ""
echo "🌐 Starting API server..."
echo "📍 API Docs will be available at: http://localhost:8000/docs"
echo "📍 Health check at: http://localhost:8000/health"
echo ""
echo "Press CTRL+C to stop the server"
echo ""

# Start the server
uv run python main.py
