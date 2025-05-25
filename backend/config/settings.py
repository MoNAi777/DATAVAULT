from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Application
    app_name: str = "DataVault"
    app_version: str = "1.0.0"
    debug: bool = True
    secret_key: str = "dev-secret-key"
    
    # Database
    database_url: str = "postgresql://datavault:datavault@localhost:5432/datavault"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # OpenAI
    openai_api_key: str = ""
    
    # Telegram
    telegram_bot_token: str = ""
    
    # MinIO
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket_name: str = "datavault"
    minio_use_ssl: bool = False
    
    # ChromaDB
    chroma_host: str = "localhost"
    chroma_port: int = 8000
    chroma_collection_name: str = "datavault_messages"
    
    # Authentication
    jwt_secret_key: str = "jwt-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    class Config:
        env_file = ".env"


settings = Settings() 