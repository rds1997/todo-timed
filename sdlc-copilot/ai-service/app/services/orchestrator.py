"""Orchestrates the SDLC analyze pipeline by composing the individual prompts."""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Dict, List

from ..config import Settings
from ..prompts import (
    AMBIGUITY_SYSTEM, AMBIGUITY_USER_TEMPLATE,
    CHAT_SYSTEM, CHAT_USER_TEMPLATE,
    ESTIMATION_SYSTEM, ESTIMATION_USER_TEMPLATE,
    STORIES_SYSTEM, STORIES_USER_TEMPLATE,
    SUMMARY_SYSTEM, SUMMARY_USER_TEMPLATE,
    TASKS_SYSTEM, TASKS_USER_TEMPLATE,
    TESTS_SYSTEM, TESTS_USER_TEMPLATE,
)
from ..schemas import (
    Ambiguity, AnalyzeRequest, AnalyzeResponse, ChatRequest, ChatResponse,
    DevTask, Epic, Estimation, Summary, TestCase, UserStory,
)
from . import mock_provider
from .openai_client import OpenAIClient

logger = logging.getLogger(__name__)


class Orchestrator:
    """Runs the full SDLC analysis. Falls back to mock data when OpenAI is not configured."""

    def __init__(self, settings: Settings, openai_client: OpenAIClient | None = None):
        self._settings = settings
        self._openai = openai_client or OpenAIClient(settings)

    async def analyze(self, req: AnalyzeRequest) -> AnalyzeResponse:
        if not self._openai.enabled:
            logger.info("OpenAI disabled (no API key or force_mock=true); returning mock analysis.")
            return mock_provider.mock_analyze(req.title, req.text)

        try:
            # Phase 1: summary + stories + ambiguity in parallel.
            summary_task = self._openai.generate_json(
                SUMMARY_SYSTEM, SUMMARY_USER_TEMPLATE.format(title=req.title, text=req.text)
            )
            stories_task = self._openai.generate_json(
                STORIES_SYSTEM, STORIES_USER_TEMPLATE.format(title=req.title, text=req.text)
            )
            ambiguity_task = self._openai.generate_json(
                AMBIGUITY_SYSTEM, AMBIGUITY_USER_TEMPLATE.format(title=req.title, text=req.text)
            )
            summary_raw, stories_raw, ambiguity_raw = await asyncio.gather(
                summary_task, stories_task, ambiguity_task
            )

            summary = Summary(**summary_raw)
            epics = [Epic(**e) for e in stories_raw.get("epics", [])]
            stories = [UserStory(**s) for s in stories_raw.get("user_stories", [])]
            ambiguities = [Ambiguity(**a) for a in ambiguity_raw.get("ambiguities", [])]

            stories_summary_json = json.dumps([
                {"title": s.title, "as_a": s.as_a, "i_want": s.i_want, "so_that": s.so_that}
                for s in stories
            ])

            # Phase 2: tasks + tests in parallel (need stories from phase 1).
            tasks_task = self._openai.generate_json(
                TASKS_SYSTEM, TASKS_USER_TEMPLATE.format(title=req.title, text=req.text, stories=stories_summary_json)
            )
            tests_task = self._openai.generate_json(
                TESTS_SYSTEM, TESTS_USER_TEMPLATE.format(title=req.title, text=req.text, stories=stories_summary_json)
            )
            tasks_raw, tests_raw = await asyncio.gather(tasks_task, tests_task)
            tasks = [DevTask(**t) for t in tasks_raw.get("tasks", [])]
            test_cases = [TestCase(**t) for t in tests_raw.get("test_cases", [])]

            # Phase 3: estimation (or compute deterministically if model output is empty).
            estimation = self._compute_estimation(stories, tasks)
            try:
                est_raw = await self._openai.generate_json(
                    ESTIMATION_SYSTEM,
                    ESTIMATION_USER_TEMPLATE.format(
                        stories=json.dumps([s.model_dump() for s in stories]),
                        tasks=json.dumps([t.model_dump() for t in tasks]),
                    ),
                )
                # Only override if the model produced a sensible response.
                if est_raw.get("total_estimated_hours"):
                    estimation = Estimation(**est_raw)
            except Exception as ex:
                logger.warning("Estimation prompt failed, using deterministic rollup: %s", ex)

            return AnalyzeResponse(
                summary=summary,
                epics=epics,
                user_stories=stories,
                tasks=tasks,
                test_cases=test_cases,
                ambiguities=ambiguities,
                estimation=estimation,
                mode="openai",
            )
        except Exception:
            logger.exception("OpenAI analysis failed, falling back to mock provider.")
            response = mock_provider.mock_analyze(req.title, req.text)
            return response

    async def chat(self, req: ChatRequest) -> ChatResponse:
        if not self._openai.enabled:
            return mock_provider.mock_chat(req)
        try:
            user_msg = CHAT_USER_TEMPLATE.format(
                title=req.title, text=req.text[:6000], message=req.message
            )
            history_payload: List[Dict[str, str]] = [
                {"role": m.role, "content": m.content} for m in req.history[-10:]
            ]
            reply = await self._openai.chat(CHAT_SYSTEM, history_payload, user_msg)
            return ChatResponse(reply=reply, mode="openai")
        except Exception:
            logger.exception("OpenAI chat failed, falling back to mock provider.")
            return mock_provider.mock_chat(req)

    @staticmethod
    def _compute_estimation(stories: List[UserStory], tasks: List[DevTask]) -> Estimation:
        breakdown: Dict[str, float] = {}
        for t in tasks:
            breakdown[t.layer] = round(breakdown.get(t.layer, 0.0) + (t.estimated_hours or 0), 2)
        total_hours = round(sum(breakdown.values()), 2)
        if total_hours == 0:
            total_hours = round(sum((s.estimated_hours or 0) for s in stories), 2)
        return Estimation(
            total_story_points=sum(s.story_points or 0 for s in stories),
            total_estimated_hours=total_hours,
            breakdown=breakdown,
        )
