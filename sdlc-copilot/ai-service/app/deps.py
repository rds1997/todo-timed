"""FastAPI dependency providers.

All heavy objects (Settings, OpenAIClient, Orchestrator) are singletons built once
at first request via :func:`lru_cache` and reused for the lifetime of the process.
This ensures the httpx connection pool inside AsyncOpenAI is shared, not recreated
per request.
"""
from functools import lru_cache

from .config import Settings, get_settings
from .services.openai_client import OpenAIClient
from .services.orchestrator import Orchestrator


@lru_cache(maxsize=1)
def _build_orchestrator() -> Orchestrator:
    settings = get_settings()
    return Orchestrator(settings, OpenAIClient(settings))


def get_orchestrator() -> Orchestrator:
    """FastAPI dependency: returns the process-wide Orchestrator singleton."""
    return _build_orchestrator()


def get_openai_client() -> OpenAIClient:
    """FastAPI dependency: returns the shared OpenAIClient (same instance used by the Orchestrator).

    Used by the ``/health/openai`` endpoint so it exercises the exact same client
    the application uses, not a freshly-constructed one.
    """
    return _build_orchestrator().openai_client


def get_app_settings() -> Settings:
    """FastAPI dependency: returns the process-wide Settings singleton."""
    return get_settings()
