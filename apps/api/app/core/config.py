from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Bellwether API"
    app_version: str = "0.1.0"
    environment: str = "development"
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])
    crustdata_api_key: str = ""
    crustdata_auth_scheme: Literal["Bearer", "Token"] = "Bearer"
    crustdata_base_url: str = "https://api.crustdata.com"
    crustdata_timeout_seconds: float = 30.0
    llm_provider: str = "gemini"
    llm_api_key: str = ""
    llm_model: str = "gemini-2.5-flash"
    llm_timeout_seconds: float = 30.0
    database_url: str = "sqlite:///./bellwether.db"
    log_level: str = "INFO"
    use_mock_providers: bool = True
    seed_demo_data: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="BELLWETHER_",
        case_sensitive=False,
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, list):
            return value
        if not value:
            return ["*"]

        origins = [origin.strip() for origin in value.split(",") if origin.strip()]
        return origins or ["*"]

    @field_validator("crustdata_auth_scheme", mode="before")
    @classmethod
    def normalize_crustdata_auth_scheme(cls, value: str) -> str:
        if not value:
            return "Bearer"

        normalized = value.strip().lower()
        if normalized == "token":
            return "Token"
        return "Bearer"

    @property
    def crustdata_configured(self) -> bool:
        return bool(self.crustdata_api_key.strip())

    @property
    def llm_configured(self) -> bool:
        return bool(self.llm_api_key.strip())


@lru_cache
def get_settings() -> Settings:
    return Settings()
