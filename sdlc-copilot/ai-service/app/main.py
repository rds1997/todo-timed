"""FastAPI entrypoint for the SDLC Copilot AI service."""
from __future__ import annotations

import logging
import os
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .routers import analyze as analyze_router
from .services.openai_client import OpenAIClient

settings = get_settings()
logging.basicConfig(level=settings.log_level.upper())
logger = logging.getLogger(__name__)

# Stamped at process start. Used in /health so operators can verify the running
# image is the freshly-built one (rules out a stale docker layer cache).
_PROCESS_START_TS = int(time.time())
_BUILD_ID = os.getenv("BUILD_ID") or f"runtime-{_PROCESS_START_TS}"

app = FastAPI(
    title="SDLC Copilot AI Service",
    description="Converts software requirements into structured SDLC artifacts via prompt-engineered LLM calls.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze_router.router)


def _current_mode() -> str:
    return "openai" if (settings.openai_api_key and not settings.force_mock) else "mock"


@app.get("/health", tags=["meta"])
async def health() -> dict[str, object]:
    """Liveness + current mode + which model is configured.

    ``mode`` is ``"openai"`` when ``OPENAI_API_KEY`` is set and ``FORCE_MOCK`` is false,
    otherwise ``"mock"``. ``model`` is reported so operators can confirm the deployed
    configuration without poking the LLM. ``build_id`` and ``started_at_ts`` let you
    confirm a freshly-built image is actually running (rules out stale docker layers).

    NOTE: this endpoint does NOT actually call OpenAI. Use ``/health/openai`` for a
    real live round-trip probe.
    """
    mode = _current_mode()
    return {
        "status": "ok",
        "service": settings.service_name,
        "mode": mode,
        "model": settings.openai_model if mode == "openai" else "mock",
        "force_mock": settings.force_mock,
        "api_key_set": bool(settings.openai_api_key),
        "chat_history_window": settings.chat_history_window,
        "build_id": _BUILD_ID,
        "started_at_ts": _PROCESS_START_TS,
    }


@app.get("/health/openai", tags=["meta"])
async def health_openai() -> dict[str, object]:
    """Live OpenAI round-trip probe.

    Makes a real one-token chat completion against the configured model so the
    operator can confirm the key/model/base_url actually works end-to-end. The
    real error message (incl. ``RateLimitError``, ``AuthenticationError``, etc.)
    is surfaced in the response body, not swallowed.
    """
    if not settings.openai_api_key:
        return {"ok": False, "reason": "OPENAI_API_KEY not set", "model": settings.openai_model}
    if settings.force_mock:
        return {"ok": False, "reason": "FORCE_MOCK is true", "model": settings.openai_model}

    client = OpenAIClient(settings)
    started = time.monotonic()
    try:
        # Use the same code path that /api/v1/chat takes, with a trivial prompt.
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
        err_type = type(exc).__name__
        logger.exception("/health/openai live probe FAILED (model=%s)", settings.openai_model)
        return {
            "ok": False,
            "model": settings.openai_model,
            "base_url": settings.openai_base_url or "https://api.openai.com/v1",
            "latency_ms": elapsed_ms,
            "error_type": err_type,
            "error": str(exc) or repr(exc),
        }


@app.get("/", tags=["meta"])
async def root() -> dict[str, str]:
    return {"service": settings.service_name, "docs": "/docs"}
