from functools import lru_cache

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="SLLM_", extra="ignore")

    environment: str = "development"
    token_secret: SecretStr = Field(default=SecretStr("development-only-change-me"), min_length=24)
    token_ttl_seconds: int = Field(default=900, ge=60, le=86400)
    llm_provider: str = "mock"
    rate_limit_requests: int = Field(default=5, ge=1, le=1000)
    rate_limit_window_seconds: int = Field(default=60, ge=1, le=3600)
    max_prompt_chars: int = Field(default=2000, ge=100, le=10000)

    @field_validator("token_secret")
    @classmethod
    def reject_default_secret_in_production(cls, value: SecretStr, info):
        environment = info.data.get("environment", "development")
        if environment == "production" and value.get_secret_value() == "development-only-change-me":
            raise ValueError("SLLM_TOKEN_SECRET must be changed in production")
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
