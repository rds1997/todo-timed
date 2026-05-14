from functools import lru_cache

from .config import Settings, get_settings
from .services.openai_client import OpenAIClient
from .services.orchestrator import Orchestrator


@lru_cache(maxsize=1)
def _build_orchestrator() -> Orchestrator:
    settings = get_settings()
    return Orchestrator(settings, OpenAIClient(settings))


def get_orchestrator() -> Orchestrator:
    return _build_orchestrator()


def get_app_settings() -> Settings:
    return get_settings()
