from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    database_url: str

    # Anthropic/Claude
    anthropic_api_key: str
    embedding_model: str = "claude-3-5-sonnet-20241022"

    # Content ingestion
    content_upload_dir: str = "./uploads"
    max_file_size_mb: int = 100

    # Embeddings
    embedding_dimension: int = 1024
    chunk_size: int = 1000
    chunk_overlap: int = 200

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000


settings = Settings()
