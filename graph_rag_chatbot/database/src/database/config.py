import os
from typing import Callable

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    """
    If you create a model that inherits from BaseSettings,
    the model initialiser will attempt to determine the values 
    of any fields not passed as keyword arguments by reading 
    from the environment. (Default values will still be used 
    if the matching environment variable is not set.)
    """
    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env"),
        env_prefix="DATABASE_",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # API Settings
    api_title: str = "Graph RAG Database API"
    api_version: str = "1.0.0"
    debug: bool = False
    port: int = 9010

    # Authorization
    api_key: str = "my-secret"  # Override in production


# delayed singleton pattern for settings
# want to try it from https://www.lihil.cc/blog/design-patterns-you-should-unlearn-in-python-part1/
def _settings() -> Callable[[], Settings]:
    settings: Settings = Settings()

    def get_settings() -> Settings:
        return settings

    return get_settings


get_settings: Callable[[], Settings] = _settings()
