"""Configuration loaded from environment variables."""
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # OpenAI / LLM
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_base_url: str | None = None  # set for Azure OpenAI or local proxies
    openai_organization: str | None = None  # optional OpenAI org id
    openai_temperature: float = 0.2
    openai_max_output_tokens: int = 4000
    openai_timeout_seconds: float = 60.0
    openai_max_retries: int = 2  # AsyncOpenAI client-level retries on transport errors / 429s
    openai_schema_retry_attempts: int = 1  # extra attempts when LLM JSON fails Pydantic validation

    # Service
    service_name: str = "sdlc-copilot-ai"
    log_level: str = "INFO"

    # Chat conversation memory: maximum number of prior messages (user + assistant)
    # included in the prompt for /api/v1/chat. Keeps prompt size bounded as the
    # conversation grows. The .NET backend persists full history; this is just the
    # window the LLM sees per request.
    chat_history_window: int = 20

    # Fallback mode: when true (or no API key) returns deterministic mock data.
    force_mock: bool = False


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reset_settings_for_tests() -> None:
    """Test helper: drop the cached settings singleton so env-var changes take effect."""
    global _settings
    _settings = None
