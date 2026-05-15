"""Thin async wrapper around the OpenAI Chat Completions API enforcing JSON output.

Reads all knobs from :class:`Settings`:
    - ``openai_api_key`` (required to enable live mode)
    - ``openai_model`` (default ``gpt-4o-mini``)
    - ``openai_base_url`` (Azure OpenAI / proxies — None means standard api.openai.com)
    - ``openai_organization`` (optional)
    - ``openai_temperature``
    - ``openai_max_output_tokens``
    - ``openai_timeout_seconds``
    - ``openai_max_retries`` (transport-level retries on 5xx / 429)

The client itself is intentionally dumb.  Per-artifact schema validation and
per-artifact retry/fallback live in :mod:`orchestrator`.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

from openai import AsyncOpenAI, APIConnectionError, APIStatusError, AuthenticationError, RateLimitError

from ..config import Settings

logger = logging.getLogger(__name__)

# Maps OpenAI SDK exception class names to operator/user-friendly one-liners.
# Used by :meth:`OpenAIClient.friendly_error` to produce readable error messages
# without leaking raw SDK internals to end users.
_FRIENDLY: Dict[str, str] = {
    "AuthenticationError": (
        "the API key is invalid or revoked — update OPENAI_API_KEY"
    ),
    "PermissionDeniedError": (
        "the API key does not have access to this model"
    ),
    "RateLimitError": (
        "the OpenAI quota is exhausted — check billing at platform.openai.com"
    ),
    "APIConnectionError": (
        "the service cannot reach api.openai.com — check network/DNS"
    ),
    "APITimeoutError": (
        "the request to OpenAI timed out — consider raising OPENAI_TIMEOUT_SECONDS"
    ),
    "NotFoundError": (
        "the requested model was not found — check OPENAI_MODEL"
    ),
}

# Default base URL used when none is configured — made explicit so the SDK never
# falls back to reading OPENAI_BASE_URL from the environment (an empty string there
# causes httpx.UnsupportedProtocol on every request).
_DEFAULT_BASE_URL = "https://api.openai.com/v1"


class OpenAIClient:
    def __init__(self, settings: Settings):
        self._settings = settings
        self._client: Optional[AsyncOpenAI] = None

    @property
    def enabled(self) -> bool:
        """True only when a key is configured AND the operator hasn't forced mock mode."""
        return bool(self._settings.openai_api_key) and not self._settings.force_mock

    @property
    def model(self) -> str:
        return self._settings.openai_model

    @staticmethod
    def friendly_error(exc: Exception) -> str:
        """Return a short, human-readable description of a known OpenAI error.

        Falls back to ``"<ExceptionType>: <message>"`` for unknown error types so
        callers always get a non-empty string that's safe to show in a UI.
        """
        name = type(exc).__name__
        if name in _FRIENDLY:
            return _FRIENDLY[name]
        # Include the raw message for unexpected errors so operators can diagnose.
        return f"{name}: {exc}"

    def _get_client(self) -> AsyncOpenAI:
        if self._client is None:
            kwargs: Dict[str, Any] = {
                "api_key": self._settings.openai_api_key,
                "timeout": self._settings.openai_timeout_seconds,
                "max_retries": self._settings.openai_max_retries,
                # Always pass base_url explicitly so the SDK never falls back to
                # reading OPENAI_BASE_URL from the environment.  An empty string
                # there causes httpx.UnsupportedProtocol at request time.
                "base_url": self._settings.openai_base_url or _DEFAULT_BASE_URL,
            }
            if self._settings.openai_organization:
                kwargs["organization"] = self._settings.openai_organization
            self._client = AsyncOpenAI(**kwargs)
            logger.debug(
                "AsyncOpenAI client created: model=%s base_url=%s retries=%d timeout=%.0fs",
                self._settings.openai_model,
                self._settings.openai_base_url or _DEFAULT_BASE_URL,
                self._settings.openai_max_retries,
                self._settings.openai_timeout_seconds,
            )
        return self._client

    async def generate_json(
        self,
        system: str,
        user: str,
        *,
        extra_messages: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """Run a JSON-mode chat completion and return the parsed object.

        Forces ``response_format={"type": "json_object"}`` so the model is
        constrained to return parseable JSON.  If the model still returns
        something that can't be parsed, we attempt to recover a JSON object
        substring before raising.
        """
        client = self._get_client()
        messages: List[Dict[str, str]] = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]
        if extra_messages:
            messages.extend(extra_messages)
        response = await client.chat.completions.create(
            model=self._settings.openai_model,
            temperature=self._settings.openai_temperature,
            max_tokens=self._settings.openai_max_output_tokens,
            response_format={"type": "json_object"},
            messages=messages,
        )
        content = response.choices[0].message.content or "{}"
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            logger.warning(
                "OpenAI returned invalid JSON — attempting substring recovery: %s",
                content[:200],
            )
            start = content.find("{")
            end = content.rfind("}")
            if 0 <= start < end:
                return json.loads(content[start : end + 1])
            raise

    async def chat(self, system: str, history: List[Dict[str, str]], user: str) -> str:
        """Free-form chat completion (no JSON mode).  Returns plain text reply."""
        client = self._get_client()
        messages: List[Dict[str, str]] = [{"role": "system", "content": system}]
        for h in history:
            role = h.get("role", "user")
            if role not in {"user", "assistant", "system"}:
                role = "user"
            messages.append({"role": role, "content": h.get("content", "")})
        messages.append({"role": "user", "content": user})
        response = await client.chat.completions.create(
            model=self._settings.openai_model,
            temperature=self._settings.openai_temperature,
            max_tokens=self._settings.openai_max_output_tokens,
            messages=messages,
        )
        return (response.choices[0].message.content or "").strip()
