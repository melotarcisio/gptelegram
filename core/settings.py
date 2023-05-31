"""
Configuration for running environment variables.

Shared between API and mariner, on ray and backend instances
Sometimes cause the application to fail when missing an ENV VAR
"""

from pydantic import BaseSettings


# Make settings be the aggregation of several settings
# Possibly using multi-inheritance
class Settings(BaseSettings):
    """Models the environment variables used around the application."""

    TELEGRAM_BOT: str
    TELEGRAM_LOG_GROUP: str
    OPEN_API_KEY: str
    
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    DB_PORT: int = 5432
    
    CONTEXT_MESSAGES_MAX_SIZE: int = 10
    FREE_CREDIT: int = 5000

    class Config:
        """Configure the environment variable model to be case sensitive."""

        case_sensitive = True


settings = Settings()
