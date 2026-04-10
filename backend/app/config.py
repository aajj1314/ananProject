"""Application configuration."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized runtime configuration."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = Field(default="elderly-insole-platform", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    debug: bool = Field(default=True, alias="DEBUG")
    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")
    database_url: str = Field(
        default="sqlite+aiosqlite:///./elderly_insole_dev.db",
        alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://localhost:6379/1", alias="REDIS_URL")
    jwt_secret: str = Field(default="dev-secret-key", alias="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_expire_minutes: int = Field(default=1440, alias="JWT_EXPIRE_MINUTES")
    influxdb_url: str = Field(default="http://localhost:8086", alias="INFLUXDB_URL")
    influxdb_token: str = Field(default="dev-token", alias="INFLUXDB_TOKEN")
    influxdb_org: str = Field(default="elderly-care", alias="INFLUXDB_ORG")
    influxdb_bucket: str = Field(default="device_location", alias="INFLUXDB_BUCKET")
    rate_limit_requests: int = Field(default=60, alias="RATE_LIMIT_REQUESTS")
    rate_limit_window_seconds: int = Field(default=60, alias="RATE_LIMIT_WINDOW_SECONDS")
    cache_ttl_seconds: int = Field(default=120, alias="CACHE_TTL_SECONDS")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the singleton settings object."""

    return Settings()
