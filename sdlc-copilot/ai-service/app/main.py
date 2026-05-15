"""FastAPI entrypoint for the SDLC Copilot AI service."""
from __future__ import annotations

import logging
import os
import time
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .deps import get_openai_client, get_orchestrator
from .routers import analyze as analyze_router
from .services.openai_client import OpenAIClient

# Stamped at process start.  Surfaced in /health so operators can confirm the
# running image is the freshly-built one (rules out a stale docker layer cache).
_PROCESS_START_TS = int(time.time())
_BUILD_ID = os.getenv("BUILD_ID") or f"runtime-{_PROCESS_START_TS}"


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Validate configuration and warm up singletons at startup."""
    settings = get_settings()
    # Trigger singleton construction (logs config summary via _log_startup in config.py).
    get_orchestrator()
    logging.getLogger(__name__).info(
        "ai-service ready: build_id=%s pid=%d", _BUILD_ID, os.getpid()
    )
    yield
    # Nothing to clean up — httpx connection pool is managed by the GC.


app = FastAPI(
    title="SDLC Copilot AI Service",
    description=(
        "Converts software requirements into structured SDLC artifacts "
        "via prompt-engineered LLM calls."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze_router.router)

# Configure logging before calling get_settings() so _log_startup() messages
# are not silently dropped (no handler exists before basicConfig is called).
logging.basicConfig(
    level="INFO",
    format="%(levelname)s:%(name)s:%(message)s",
)
settings = get_settings()
# Apply the operator-configured log level (may differ from the INFO default above).
logging.getLogger().setLevel(settings.log_level.upper())

logger = logging.getLogger(__name__)


@app.get("/health", tags=["meta"])
async def health() -> dict[str, object]:
    """Liveness + current mode + which model is configured.

    ``mode`` is ``"openai"`` when ``OPENAI_API_KEY`` is set and ``FORCE_MOCK`` is
    false, otherwise ``"mock"``.  ``model`` is reported so operators can confirm
    the deployed configuration without poking the LLM.  ``build_id`` and
    ``started_at_ts`` let you confirm the freshly-built image is actually running
    (rules out stale docker layers).

    NOTE: this endpoint does NOT call OpenAI.  Use ``/health/openai`` for a live
    round-trip probe.
    """
    client = get_openai_client()
    mode = "openai" if client.enabled else "mock"
    return {
        "status": "ok",
        "service": settings.service_name,
        "mode": mode,
        "model": client.model if client.enabled else "mock",
        "force_mock": settings.force_mock,
        "api_key_set": bool(settings.openai_api_key),
        "chat_history_window": settings.chat_history_window,
        "build_id": _BUILD_ID,
        "started_at_ts": _PROCESS_START_TS,
    }


@app.get("/health/openai", tags=["meta"])
async def health_openai(
    client: OpenAIClient = Depends(get_openai_client),
) -> dict[str, object]:
    """Live OpenAI round-trip probe.

    Makes a real one-token chat completion against the configured model so the
    operator can confirm the key / model / base_url actually works end-to-end.
    Uses the *same* :class:`OpenAIClient` instance the application uses — not a
    freshly-constructed one — so the test is representative.

    Known error types (quota, bad key, network) are surfaced as human-readable
    strings in the response body; they are not swallowed.
    """
    if not settings.openai_api_key:
        return {"ok": False, "reason": "OPENAI_API_KEY not set", "model": settings.openai_model}
    if settings.force_mock:
        return {"ok": False, "reason": "FORCE_MOCK is true — set to false to enable live mode", "model": settings.openai_model}

    started = time.monotonic()
    try:
        reply = await client.chat(
            "You are a connectivity probe. Reply with the single word: pong.",
            [],
            "ping",
        )
        elapsed_ms = int((time.monotonic() - started) * 1000)
        return {
            "ok": True,
            "model": settings.openai_model,
            "base_url": settings.openai_base_url or "https://api.openai.com/v1",
            "latency_ms": elapsed_ms,
            "sample_reply": reply[:200],
        }
    except Exception as exc:
        elapsed_ms = int((time.monotonic() - started) * 1000)
        friendly = OpenAIClient.friendly_error(exc)
        logger.warning("/health/openai probe failed: %s", friendly)
        logger.debug("/health/openai full exception", exc_info=exc)
        return {
            "ok": False,
            "model": settings.openai_model,
            "base_url": settings.openai_base_url or "https://api.openai.com/v1",
            "latency_ms": elapsed_ms,
            "error": friendly,
            "error_detail": f"{type(exc).__name__}: {exc}",
        }


@app.get("/", tags=["meta"])
async def root() -> dict[str, str]:
    return {"service": settings.service_name, "docs": "/docs"}
