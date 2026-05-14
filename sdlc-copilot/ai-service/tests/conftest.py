"""Shared fixtures for ai-service tests."""
from __future__ import annotations

import os

import pytest

from app.config import Settings, reset_settings_for_tests


@pytest.fixture(autouse=True)
def _isolate_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Strip OPENAI_* and FORCE_MOCK from os.environ for each test so Settings is deterministic."""
    for key in list(os.environ):
        if key.startswith("OPENAI_") or key in {"FORCE_MOCK", "LOG_LEVEL"}:
            monkeypatch.delenv(key, raising=False)
    reset_settings_for_tests()


@pytest.fixture
def mock_mode_settings() -> Settings:
    return Settings(openai_api_key="", openai_model="gpt-4o-mini")


@pytest.fixture
def live_mode_settings() -> Settings:
    return Settings(
        openai_api_key="sk-test-not-real",
        openai_model="gpt-4o-mini",
        openai_schema_retry_attempts=1,
    )
