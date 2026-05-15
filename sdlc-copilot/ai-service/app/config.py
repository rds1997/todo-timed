"""Configuration loaded from environment variables.

Pydantic-settings validators ensure that:
- ``openai_api_key`` has any surrounding whitespace stripped (copy-paste safety).
- ``openai_base_url`` and ``openai_organization`` are normalised to ``None`` when the
  environment supplies an empty string (docker-compose ``${VAR:-}`` default pattern).

If the SDK receives an empty string for either field it silently uses it as a URL
or org-id, producing cryptic httpx errors at request time.  Normalising here means
the rest of the code can rely on the invariant: *non-None == non-empty*.
"""
from __future__ import annotations

import logging

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


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
    # included in the prompt for /api/v1/chat.  Keeps prompt size bounded as the
    # conversation grows.  The .NET backend persists full history; this is just the
    # window the LLM sees per request.
    chat_history_window: int = 20

    # Fallback mode: when true (or no API key) returns deterministic mock data.
    force_mock: bool = False

    # ------------------------------------------------------------------ #
    #  Validators — normalise before any code reads the fields            #
    # ------------------------------------------------------------------ #

    @field_validator("openai_api_key", mode="before")
    @classmethod
    def _strip_api_key(cls, v: object) -> object:
        """Strip accidental whitespace around the key (copy-paste from dashboards)."""
        return v.strip() if isinstance(v, str) else v

    @field_validator("openai_base_url", "openai_organization", mode="before")
    @classmethod
    def _empty_string_to_none(cls, v: object) -> object:
        """Treat empty / whitespace-only strings as unset (None).

        docker-compose ``${VAR:-}`` always injects an empty string when the host
        environment lacks the variable.  The OpenAI SDK reads ``OPENAI_BASE_URL``
        from the environment when ``base_url`` is not passed explicitly; an empty
        string there causes ``httpx.UnsupportedProtocol`` at request time.
        """
        if isinstance(v, str):
            stripped = v.strip()
            return stripped if stripped else None
        return v


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
        _log_startup(_settings)
    return _settings


def _log_startup(s: Settings) -> None:
    """Emit a single structured line at startup so operators can verify configuration."""
    mode = "mock (FORCE_MOCK=true)" if s.force_mock else (
        "mock (no API key)" if not s.openai_api_key else "openai"
    )
    key_hint = f"...{s.openai_api_key[-6:]}" if s.openai_api_key else "(not set)"
    logger.info(
        "ai-service starting: mode=%s model=%s key=%s base_url=%s timeout=%.0fs",
        mode,
        s.openai_model,
        key_hint,
        s.openai_base_url or "https://api.openai.com/v1",
        s.openai_timeout_seconds,
    )


def reset_settings_for_tests() -> None:
    """Test helper: drop the cached settings singleton so env-var changes take effect."""
    global _settings
    _settings = None
