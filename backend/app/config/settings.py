"""
Nexora Platform — Application Settings

Centralized configuration management using Pydantic Settings.
All configuration values are loaded from environment variables with
type validation and sensible defaults for development.

Usage:
    from app.config.settings import get_settings
    settings = get_settings()
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Environment variables are automatically mapped to these fields.
    A .env file in the backend root is loaded if present.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # -------------------- Application --------------------
    app_name: str = Field(default="nexora-platform", description="Application name")
    app_env: Literal["development", "staging", "production", "testing"] = Field(
        default="development",
        description="Application environment",
    )
    app_debug: bool = Field(default=False, description="Enable debug mode")
    app_version: str = Field(default="0.1.0", description="Application version")
    app_host: str = Field(default="0.0.0.0", description="Server bind host")
    app_port: int = Field(default=8000, ge=1, le=65535, description="Server bind port")
    app_log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level",
    )
    app_log_format: Literal["console", "json"] = Field(
        default="json",
        description="Log output format — 'console' for dev, 'json' for production",
    )
    app_workers: int = Field(default=1, ge=1, description="Number of worker processes")

    # -------------------- Database --------------------
    database_host: str = Field(default="localhost", description="PostgreSQL host")
    database_port: int = Field(default=5432, ge=1, le=65535, description="PostgreSQL port")
    database_name: str = Field(default="nexora", description="PostgreSQL database name")
    database_user: str = Field(default="nexora_user", description="PostgreSQL user")
    database_password: str = Field(default="", description="PostgreSQL password")
    database_pool_size: int = Field(default=20, ge=1, description="Connection pool size")
    database_max_overflow: int = Field(default=10, ge=0, description="Max overflow connections")
    database_pool_timeout: int = Field(default=30, ge=1, description="Pool timeout in seconds")
    database_pool_recycle: int = Field(default=1800, ge=60, description="Connection recycle time in seconds")
    database_echo: bool = Field(default=False, description="Echo SQL queries")

    # -------------------- Redis --------------------
    redis_host: str = Field(default="localhost", description="Redis host")
    redis_port: int = Field(default=6379, ge=1, le=65535, description="Redis port")
    redis_db: int = Field(default=0, ge=0, le=15, description="Redis database number")
    redis_password: str = Field(default="", description="Redis password")
    redis_max_connections: int = Field(default=50, ge=1, description="Redis max connections")

    # -------------------- Security --------------------
    secret_key: str = Field(
        default="CHANGE_ME_GENERATE_A_SECURE_RANDOM_KEY",
        min_length=32,
        description="Secret key for signing tokens",
    )
    allowed_origins: str = Field(
        default="http://localhost:3000",
        description="Comma-separated list of allowed CORS origins",
    )
    allowed_hosts: str = Field(default="*", description="Comma-separated list of allowed hosts")

    # -------------------- CORS --------------------
    cors_allow_credentials: bool = Field(default=True, description="Allow credentials in CORS")
    cors_allow_methods: str = Field(
        default="GET,POST,PUT,PATCH,DELETE,OPTIONS",
        description="Comma-separated allowed HTTP methods",
    )
    cors_allow_headers: str = Field(default="*", description="Comma-separated allowed headers")

    # -------------------- Computed Properties --------------------
    @computed_field  # type: ignore[prop-decorator]
    @property
    def database_url(self) -> str:
        """Construct async PostgreSQL connection URL."""
        return (
            f"postgresql+asyncpg://{self.database_user}:{self.database_password}"
            f"@{self.database_host}:{self.database_port}/{self.database_name}"
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def database_url_sync(self) -> str:
        """Construct sync PostgreSQL connection URL (for Alembic)."""
        return (
            f"postgresql://{self.database_user}:{self.database_password}"
            f"@{self.database_host}:{self.database_port}/{self.database_name}"
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def redis_url(self) -> str:
        """Construct Redis connection URL."""
        password_part = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{password_part}{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse comma-separated origins into a list."""
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    @property
    def cors_methods_list(self) -> list[str]:
        """Parse comma-separated methods into a list."""
        return [method.strip() for method in self.cors_allow_methods.split(",") if method.strip()]

    @property
    def cors_headers_list(self) -> list[str]:
        """Parse comma-separated headers into a list."""
        if self.cors_allow_headers == "*":
            return ["*"]
        return [header.strip() for header in self.cors_allow_headers.split(",") if header.strip()]

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.app_env == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.app_env == "development"

    @property
    def is_testing(self) -> bool:
        """Check if running in testing."""
        return self.app_env == "testing"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Get cached application settings.

    Uses lru_cache to ensure settings are only loaded once
    from environment variables and .env file.

    Returns:
        Settings: Application settings instance.
    """
    return Settings()
