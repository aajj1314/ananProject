"""Application configuration."""

import warnings
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
    notification_channels: list[str] = Field(default=["in_app"], alias="NOTIFICATION_CHANNELS")
    sms_provider: str | None = Field(default=None, alias="SMS_PROVIDER")
    sms_api_key: str | None = Field(default=None, alias="SMS_API_KEY")
    sms_api_secret: str | None = Field(default=None, alias="SMS_API_SECRET")
    sms_from_number: str | None = Field(default=None, alias="SMS_FROM_NUMBER")
    wechat_app_id: str | None = Field(default=None, alias="WECHAT_APP_ID")
    wechat_app_secret: str | None = Field(default=None, alias="WECHAT_APP_SECRET")
    wechat_template_id: str | None = Field(default=None, alias="WECHAT_TEMPLATE_ID")
    cors_origins: list[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
        alias="CORS_ORIGINS",
    )
    admin_phone: str | None = Field(default=None, alias="ADMIN_PHONE")
    admin_password: str | None = Field(default=None, alias="ADMIN_PASSWORD")

    def model_post_init(self, __context) -> None:
        """Validate security-critical settings after initialization."""
        if self.app_env == "production":
            if self.jwt_secret in ("dev-secret-key", "change-me", "REPLACE_WITH_A_SECURE_RANDOM_KEY"):
                warnings.warn(
                    "SECURITY WARNING: JWT_SECRET is using a default/placeholder value in production! "
                    "Generate a secure key with: python -c \"import secrets; print(secrets.token_hex(32))\"",
                    stacklevel=2,
                )
            if self.debug:
                warnings.warn(
                    "SECURITY WARNING: DEBUG mode is enabled in production environment!",
                    stacklevel=2,
                )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the singleton settings object."""

    return Settings()
