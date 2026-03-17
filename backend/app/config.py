import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Azure OpenAI
    azure_openai_endpoint: Optional[str] = None
    azure_openai_key: Optional[str] = None
    azure_openai_deployment: str = "gpt-4o"

    # Google AI
    google_ai_key: Optional[str] = None

    # AWS
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "us-east-1"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # LanceDB
    lancedb_uri: str = "./lancedb"

    # App settings
    max_upload_size: int = 10 * 1024 * 1024  # 10MB
    confidence_threshold: float = 0.7

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()