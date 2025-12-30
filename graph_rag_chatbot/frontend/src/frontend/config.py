import os
from typing import Callable

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env"),
        env_prefix="FRONTEND_",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    # API Settings
    api_title: str = "Graph RAG Chatbot Frontend"
    api_version: str = "1.0.0"
    port: int = 9001
    debug: bool = False

    # Authorization
    api_key: str = "dev-api-key"  # Override in production   
    
    # Backend URL
    backend_url: str = "http://localhost:9001"  # Override in production

# delayed singleton pattern for settings
# want to try it from https://www.lihil.cc/blog/design-patterns-you-should-unlearn-in-python-part1/
def _settings() -> Callable[[], Settings]:
    settings: Settings = Settings()

    def get_settings() -> Settings:
        return settings

    return get_settings


get_settings: Callable[[], Settings] = _settings()