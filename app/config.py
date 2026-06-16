"""Application settings, loaded from environment variables / .env."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Security
    secret_key: str = "dev-secret-change-me"  # override in production!
    access_token_expire_minutes: int = 60 * 24  # 24h
    jwt_algorithm: str = "HS256"

    # Database
    database_url: str = "sqlite:///./linkforge.db"

    # Rate limiting (requests per window, per client IP)
    rate_limit_requests: int = 60
    rate_limit_window_seconds: int = 60

    # Redirect cache
    cache_ttl_seconds: int = 300
    cache_max_size: int = 1024

    # Base URL used when returning short links
    base_url: str = "http://localhost:8000"


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()
