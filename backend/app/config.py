from decimal import Decimal
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Net Worth Automator"
    app_version: str = "0.1.0"
    environment: str = "development"
    openai_api_key: str
    database_url: str
    storage_root: str = "./storage"
    api_prefix: str = "/api/v1"

    cors_origins: str = "http://localhost:5173"

    extraction_auto_accept_threshold: Decimal = Decimal("0.85")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()