"""Configuration loaded from environment variables."""
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # OpenAI / LLM
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_base_url: str | None = None  # set for Azure OpenAI or local proxies
    openai_temperature: float = 0.2
    openai_max_output_tokens: int = 4000

    # Service
    service_name: str = "sdlc-copilot-ai"
    log_level: str = "INFO"

    # Fallback mode: when true (or no API key) returns deterministic mock data.
    force_mock: bool = False


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
