from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse
from backend.api import ingestion, search
from backend.database.connection import init_db
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Course Strategy Engine API",
    description="AI-powered curriculum strategy copilot for educational content analysis",
    version="0.1.0",
    docs_url=None,
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ingestion.router, prefix="/api/v1", tags=["ingestion"])
app.include_router(search.router, prefix="/api/v1", tags=["search"])


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    logger.info("Initializing database...")
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui() -> HTMLResponse:
    html = get_swagger_ui_html(openapi_url="/openapi.json", title="Course Strategy Engine API")
    dark_css = """
    <style>
      body { background: #1a1a2e !important; }
      .swagger-ui { filter: invert(88%) hue-rotate(180deg); }
      .swagger-ui .microlight, .swagger-ui img, .swagger-ui svg { filter: invert(100%) hue-rotate(180deg); }
    </style>
    """
    return HTMLResponse(html.body.decode().replace("</head>", f"{dark_css}</head>"))


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Course Strategy Engine API",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
