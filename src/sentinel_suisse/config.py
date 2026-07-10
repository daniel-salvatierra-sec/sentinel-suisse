"""Application settings from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    secret_key: str = ""
    database_url: str = "postgresql://sentinel:sentinel@localhost:5432/sentinel_suisse"
    admin_username: str = ""
    admin_password_hash: str = ""
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    rate_limit: str = "30/minute"


@lru_cache
def get_settings() -> Settings:
    return Settings()
