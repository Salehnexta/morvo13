"""
Configuration settings module for the application.
"""

import os

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Determine the environment, default to 'development'
APP_ENV = os.getenv("APP_ENV", "development")

# Determine the env file path based on the environment
env_file = f".env.{APP_ENV}"
env_path = os.path.join(os.path.dirname(__file__), env_file)


class Settings(BaseSettings):
    """Application configuration settings loaded from environment variables."""

    # App settings
    PROJECT_NAME: str = "Morvo AI Marketing Platform"
    API_V1_STR: str = "/v1"
    DEBUG: bool = False
    ENVIRONMENT: str = APP_ENV

    # CORS settings
    BACKEND_CORS_ORIGINS: list[str] = ["*"]
    CORS_ALLOW_METHODS: list[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True

    # Logging
    LOG_LEVEL: str = "INFO"
    JSON_LOGS: bool = False

    # Authentication
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"
    REDIS_URL: str = "redis://localhost:6379/0"

    # AI Providers
    OPENAI_API_KEY: str
    GPT_4O_MODEL: str = "gpt-4o"
    PERPLEXITY_API_KEY: str
    SERANKING_API_KEY: str

    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment is valid."""
        allowed = {"development", "staging", "production", "testing"}
        if v not in allowed:
            raise ValueError(f"ENVIRONMENT must be one of {allowed}, got '{v}'")
        return v

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if not v:
            raise ValueError("DATABASE_URL is required")
        return v

    model_config = SettingsConfigDict(
        env_file=env_path, env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )


# Global settings instance
settings = Settings()  # type: ignore
