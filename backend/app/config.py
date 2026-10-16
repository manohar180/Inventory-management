"""
Application configuration module for StockPilot.
Reads environment variables with validation via Pydantic Settings.
"""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """
    Central settings class loading environment variables for StockPilot.
    """
    APP_NAME: str = Field(default="StockPilot", description="Service application name")
    APP_ENV: str = Field(default="development", description="Environment stage: development, test, production")
    APP_PORT: int = Field(default=8000, description="Port the application listens on")
    DEBUG: bool = Field(default=True, description="Debug mode flag")

    # Database URL: default connects to local PostgreSQL via psycopg v3 driver
    DATABASE_URL: str = Field(
        default="postgresql+psycopg://stockpilot_user:stockpilot_pass@localhost:5432/stockpilot_db",
        description="SQLAlchemy database connection string"
    )

    METRICS_ENABLED: bool = Field(default=True, description="Enable Prometheus metrics scraping")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False
    )


settings = Settings()
