"""
Application configuration settings.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database settings
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "postgres"
    db_password: str = "postgres"
    db_name: str = "derbit_db"
    
    # Redis settings (for Celery)
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    
    # Deribit API settings
    deribit_api_url: str = "https://www.deribit.com/api/v2"
    
    # Celery settings
    celery_broker_url: Optional[str] = None
    celery_result_backend: Optional[str] = None
    
    @property
    def database_url(self) -> str:
        """Construct PostgreSQL database URL."""
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    @property
    def async_database_url(self) -> str:
        """Construct async PostgreSQL database URL."""
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.celery_broker_url is None:
            self.celery_broker_url = f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
        if self.celery_result_backend is None:
            self.celery_result_backend = f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

