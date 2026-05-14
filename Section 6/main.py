import uvicorn
from backend.config.settings import settings


def main():
    """Launch the Course Strategy Engine API"""
    uvicorn.run(
        "backend.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level="info",
    )


if __name__ == "__main__":
    main()
