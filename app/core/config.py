"""Application configuration management"""
from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-3.5-turbo"
    openai_embedding_model: str = "text-embedding-3-small"
    
    # Database
    database_url: str = "sqlite:///./data/nyvo.db"
    
    # Vector Database
    chroma_persist_dir: str = "./data/chroma_db"
    
    # Application
    app_name: str = "NYVO Insurance Advisor"
    app_env: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    
    # Content Library
    nyvo_content_path: str = "./nyvo-content"
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = '["*"]'
    
    @property
    def cors_origins_list(self) -> List[str]:
        return json.loads(self.cors_origins)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
