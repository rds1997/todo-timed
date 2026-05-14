"""FastAPI entrypoint for the SDLC Copilot AI service."""
from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .routers import analyze as analyze_router

settings = get_settings()
logging.basicConfig(level=settings.log_level.upper())

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
async def health() -> dict[str, str]:
    """Liveness + current mode + which model is configured.

    ``mode`` is ``"openai"`` when ``OPENAI_API_KEY`` is set and ``FORCE_MOCK`` is false,
    otherwise ``"mock"``. ``model`` is reported so operators can confirm the deployed
    configuration without poking the LLM.
    """
    mode = _current_mode()
    return {
        "status": "ok",
        "service": settings.service_name,
        "mode": mode,
        "model": settings.openai_model if mode == "openai" else "mock",
    }


@app.get("/", tags=["meta"])
async def root() -> dict[str, str]:
    return {"service": settings.service_name, "docs": "/docs"}
