from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional


class Settings(BaseSettings):
    # App Identity
    APP_NAME: str = "TheMahdiAI"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_VERSION: str = "1.0.0"
    APP_LOG_LEVEL: str = "INFO"

    # Server
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    APP_SECRET_KEY: str = "supersecretkey-change-me-in-production"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://themahdiai:development_password@localhost:5432/themahdiai"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Qdrant
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_GRPC_PORT: int = 6334
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_COLLECTION_NAME: str = "themahdiai_knowledge"
    
    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str = "YOUR_BOT_TOKEN_HERE"
    TELEGRAM_WEBHOOK_URL: Optional[str] = None
    TELEGRAM_WEBHOOK_SECRET: str = "secret-token-for-webhook"
    
    # LLM Providers
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_URL: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o"
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache()
def get_settings() -> Settings:
    return Settings()
