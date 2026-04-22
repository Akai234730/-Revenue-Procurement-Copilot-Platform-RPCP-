from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="Revenue & Procurement Copilot Platform API", alias="APP_NAME")
    app_env: Literal["development", "test", "staging", "production"] = Field(default="development", alias="APP_ENV")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    app_debug: bool = Field(default=True, alias="APP_DEBUG")
    database_url: str = Field(alias="DATABASE_URL")
    jwt_secret: str = Field(alias="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=120, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    cors_origins: list[str] = Field(default_factory=list, alias="CORS_ORIGINS")
    ai_provider: Literal["mock", "openai", "azure_openai", "local", "aliyun_qwen"] = Field(default="mock", alias="AI_PROVIDER")
    ai_model_name: str = Field(default="qwen-plus", alias="AI_MODEL_NAME")
    ai_api_key: str = Field(default="", alias="AI_API_KEY")
    ai_base_url: str = Field(default="", alias="AI_BASE_URL")
    ai_timeout_seconds: int = Field(default=180, alias="AI_TIMEOUT_SECONDS")
    ai_retry_count: int = Field(default=2, alias="AI_RETRY_COUNT")


@lru_cache
def get_settings() -> Settings:
    return Settings()
