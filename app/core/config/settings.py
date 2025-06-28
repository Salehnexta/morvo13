"""
Configuration settings module for the application.
"""

import os
import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import (
    AnyHttpUrl,
    EmailStr,
    PostgresDsn,
    field_validator,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

# Determine the environment, default to 'development'
APP_ENV = os.getenv("APP_ENV", "development")

# Use standard .env file in project root
env_path = os.path.join(os.path.dirname(__file__), "../../../.env")


class Settings(BaseSettings):
    """Application configuration settings loaded from environment variables."""

    # App settings
    PROJECT_NAME: str = "Morvo AI Marketing Platform"
    PROJECT_DESCRIPTION: str = "AI-powered marketing consultant with Saudi cultural intelligence"
    VERSION: str = "0.1.0"
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
    LOG_TO_FILE: bool = False  # Enable file logging in production
    LOG_FILE_PATH: str = "logs/app.log"  # Rotating file path

    # OpenTelemetry
    ENABLE_TRACING: bool = False  # Toggle tracing on/off
    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://localhost:4318/v1/traces"  # OTLP endpoint

    # Authentication
    JWT_SECRET: str = os.getenv("JWT_SECRET", secrets.token_urlsafe(32))
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"
    REDIS_URL: str = "redis://localhost:6379/0"

    # AI Providers
    OPENAI_API_KEY: str
    GPT_4O_MODEL: str = "gpt-4o"
    PERPLEXITY_API_KEY: str
    SERANKING_API_KEY: str

    # Security settings
    ENABLE_TRUSTED_HOST_MIDDLEWARE: bool = not DEBUG
    ALLOWED_HOSTS: List[str] = ["api.morvo.ai", "*.morvo.ai", "localhost", "127.0.0.1"]
    ENABLE_HTTPS_REDIRECT: bool = ENVIRONMENT == "production"

    # Rate limiting
    ENABLE_RATE_LIMITING: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # Cache settings
    ENABLE_CACHE: bool = True
    CACHE_EXPIRE_SECONDS: int = 60 * 5  # 5 minutes

    # Monitoring settings
    ENABLE_ERROR_TRACKING: bool = ENVIRONMENT != "development"
    ENABLE_METRICS: bool = True

    # Celery settings
    CELERY_BROKER_URL: Optional[str] = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
    CELERY_RESULT_BACKEND: Optional[str] = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")

    # Email settings
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = 587
    SMTP_HOST: Optional[str] = os.getenv("SMTP_HOST")
    SMTP_USER: Optional[str] = os.getenv("SMTP_USER")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    EMAILS_FROM_EMAIL: Optional[EmailStr] = os.getenv("EMAILS_FROM_EMAIL")
    EMAILS_FROM_NAME: Optional[str] = os.getenv("EMAILS_FROM_NAME", PROJECT_NAME)

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

    @model_validator(mode="after")
    def validate_database_url(self) -> "Settings":
        """Validate and potentially modify the database URL."""
        if self.DATABASE_URL and "sqlite" in self.DATABASE_URL:
            # Ensure SQLite URLs are properly formatted for async
            if "aiosqlite" not in self.DATABASE_URL:
                self.DATABASE_URL = self.DATABASE_URL.replace("sqlite:", "sqlite+aiosqlite:")
        return self

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )


# Global settings instance
settings = Settings()  # type: ignore
