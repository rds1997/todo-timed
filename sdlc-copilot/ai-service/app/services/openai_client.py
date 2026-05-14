"""Thin async wrapper around the OpenAI Chat Completions API enforcing JSON output."""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

from openai import AsyncOpenAI

from ..config import Settings

logger = logging.getLogger(__name__)


class OpenAIClient:
    def __init__(self, settings: Settings):
        self._settings = settings
        self._client: Optional[AsyncOpenAI] = None

    @property
    def enabled(self) -> bool:
        return bool(self._settings.openai_api_key) and not self._settings.force_mock

    def _get_client(self) -> AsyncOpenAI:
        if self._client is None:
            kwargs: Dict[str, Any] = {"api_key": self._settings.openai_api_key}
            if self._settings.openai_base_url:
                kwargs["base_url"] = self._settings.openai_base_url
            self._client = AsyncOpenAI(**kwargs)
        return self._client

    async def generate_json(self, system: str, user: str) -> Dict[str, Any]:
        """Run a JSON-mode chat completion and return the parsed object."""
        client = self._get_client()
        response = await client.chat.completions.create(
            model=self._settings.openai_model,
            temperature=self._settings.openai_temperature,
            max_tokens=self._settings.openai_max_output_tokens,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        content = response.choices[0].message.content or "{}"
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            logger.warning("OpenAI returned invalid JSON, attempting recovery: %s", content[:200])
            start = content.find("{")
            end = content.rfind("}")
            if 0 <= start < end:
                return json.loads(content[start : end + 1])
            raise

    async def chat(self, system: str, history: List[Dict[str, str]], user: str) -> str:
        client = self._get_client()
        messages = [{"role": "system", "content": system}]
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
