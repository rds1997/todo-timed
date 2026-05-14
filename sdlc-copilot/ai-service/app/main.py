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


@app.get("/health", tags=["meta"])
async def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": settings.service_name,
        "mode": "openai" if (settings.openai_api_key and not settings.force_mock) else "mock",
    }


@app.get("/", tags=["meta"])
async def root() -> dict[str, str]:
    return {"service": settings.service_name, "docs": "/docs"}
