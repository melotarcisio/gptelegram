from pydantic import BaseSettings


class Settings(BaseSettings):
    """Models the environment variables used around the application."""

    TELEGRAM_BOT: str
    TELEGRAM_LOG_GROUP: str
    OPEN_API_KEY: str
    
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    DB_PORT: int = 5432
    
    CONTEXT_MESSAGES_MAX_SIZE: int = 5
    FREE_CREDIT: int = 5000

    class Config:
        """Configure the environment variable model to be case sensitive."""

        case_sensitive = True


settings = Settings()
