"""Orchestrates the SDLC analyze pipeline by composing the individual prompts.

Resilience model:

- The orchestrator runs each artifact (summary, epics+stories, ambiguities, tasks,
  test cases, estimation) as an independent unit.
- Each unit calls :class:`OpenAIClient.generate_json` and validates the raw JSON
  against the appropriate Pydantic schema. If validation fails the call is retried
  up to ``openai_schema_retry_attempts`` times with the validation error fed back
  into the user message.
- If a single artifact still fails after retries (or raises a transport / API error
  the OpenAI SDK didn't recover), the orchestrator falls back to the mock data for
  *that artifact only* — the rest of the analysis stays live.
- ``AnalyzeResponse.mode`` is reported as ``"openai"`` if at least one live artifact
  succeeded, ``"mock"`` otherwise.
"""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Awaitable, Callable, Dict, List, Tuple, TypeVar

from pydantic import ValidationError

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

T = TypeVar("T")


class Orchestrator:
    """Runs the full SDLC analysis. Falls back to mock data per-artifact when live calls fail."""

    def __init__(self, settings: Settings, openai_client: OpenAIClient | None = None):
        self._settings = settings
        self._openai = openai_client or OpenAIClient(settings)

    # ---- public API --------------------------------------------------------

    async def analyze(self, req: AnalyzeRequest) -> AnalyzeResponse:
        if not self._openai.enabled:
            logger.info("OpenAI disabled (no API key or force_mock=true); returning mock analysis.")
            return mock_provider.mock_analyze(req.title, req.text)

        logger.info(
            "Starting live analyze with model=%s for title=%r (text_len=%d)",
            self._openai.model, req.title, len(req.text),
        )

        succeeded: List[str] = []
        failed: List[str] = []

        # Phase 1: summary + epics/stories + ambiguity in parallel.
        summary_result, stories_result, ambiguity_result = await asyncio.gather(
            self._summary(req, succeeded, failed),
            self._stories(req, succeeded, failed),
            self._ambiguities(req, succeeded, failed),
        )
        summary = summary_result
        epics, stories = stories_result
        ambiguities = ambiguity_result

        # Phase 2: tasks + tests in parallel (need stories from phase 1 for grounding).
        stories_summary_json = json.dumps([
            {"title": s.title, "as_a": s.as_a, "i_want": s.i_want, "so_that": s.so_that}
            for s in stories
        ])
        tasks, test_cases = await asyncio.gather(
            self._tasks(req, stories_summary_json, succeeded, failed),
            self._test_cases(req, stories_summary_json, succeeded, failed),
        )

        # Phase 3: estimation (always have a deterministic rollup, optionally override with LLM).
        estimation = await self._estimation(stories, tasks, succeeded, failed)

        mode = "openai" if succeeded else "mock"
        logger.info(
            "analyze complete: mode=%s succeeded=%s failed=%s",
            mode, succeeded, failed,
        )
        return AnalyzeResponse(
            summary=summary,
            epics=epics,
            user_stories=stories,
            tasks=tasks,
            test_cases=test_cases,
            ambiguities=ambiguities,
            estimation=estimation,
            mode=mode,
        )

    async def chat(self, req: ChatRequest) -> ChatResponse:
        # Cap the number of prior turns the model sees so prompt size stays bounded
        # even when a requirement has dozens of chat messages persisted in Postgres.
        window = max(0, self._settings.chat_history_window)
        bounded_history = req.history[-window:] if window else []

        logger.info(
            "chat invoked: title=%r message_len=%d history_provided=%d window=%d enabled=%s model=%s force_mock=%s",
            req.title, len(req.message), len(req.history), window,
            self._openai.enabled, self._openai.model, self._settings.force_mock,
        )

        if not self._openai.enabled:
            logger.info(
                "chat: OpenAI disabled (api_key_set=%s force_mock=%s); using mock provider.",
                bool(self._settings.openai_api_key), self._settings.force_mock,
            )
            return mock_provider.mock_chat(req, history=bounded_history)
        try:
            user_msg = CHAT_USER_TEMPLATE.format(
                title=req.title, text=req.text[:6000], message=req.message
            )
            history_payload: List[Dict[str, str]] = [
                {"role": m.role, "content": m.content} for m in bounded_history
            ]
            logger.info(
                "chat: invoking OpenAI model=%s with %d prior turn(s) (window=%d, total_provided=%d)",
                self._openai.model, len(history_payload), window, len(req.history),
            )
            reply = await self._openai.chat(CHAT_SYSTEM, history_payload, user_msg)
            logger.info(
                "chat: OpenAI returned %d-char reply (model=%s)",
                len(reply), self._openai.model,
            )
            return ChatResponse(reply=reply, mode="openai")
        except Exception as exc:
            # IMPORTANT: when a key is configured the operator expects the live
            # path to be taken. Previously we silently fell back to mock_chat,
            # which made a live OpenAI failure look identical to no-key mode.
            # Instead, surface the actual error so the caller can fix the root
            # cause (bad key, model not available, network, quota, etc.).
            err_type = type(exc).__name__
            err_msg = str(exc) or repr(exc)
            logger.exception(
                "chat: OpenAI call FAILED (model=%s error_type=%s); surfacing error to caller.",
                self._openai.model, err_type,
            )
            return ChatResponse(
                reply=(
                    f"[live OpenAI chat failed: {err_type}: {err_msg}] "
                    "The AI service has a key configured (FORCE_MOCK=false) but the "
                    "round-trip to OpenAI did not succeed. Check the ai-service logs "
                    "and try `GET /health/openai` for a live probe."
                ),
                mode="error",
                error=f"{err_type}: {err_msg}",
            )

    # ---- per-artifact runners ---------------------------------------------

    async def _summary(
        self, req: AnalyzeRequest, succeeded: List[str], failed: List[str]
    ) -> Summary:
        async def call(extra: List[Dict[str, str]] | None) -> Dict[str, Any]:
            return await self._openai.generate_json(
                SUMMARY_SYSTEM,
                SUMMARY_USER_TEMPLATE.format(title=req.title, text=req.text),
                extra_messages=extra,
            )

        return await self._run_artifact(
            name="summary",
            call=call,
            parse=lambda raw: Summary(**raw),
            fallback=lambda: mock_provider.mock_summary(req.title, req.text),
            succeeded=succeeded,
            failed=failed,
        )

    async def _stories(
        self, req: AnalyzeRequest, succeeded: List[str], failed: List[str]
    ) -> Tuple[List[Epic], List[UserStory]]:
        async def call(extra: List[Dict[str, str]] | None) -> Dict[str, Any]:
            return await self._openai.generate_json(
                STORIES_SYSTEM,
                STORIES_USER_TEMPLATE.format(title=req.title, text=req.text),
                extra_messages=extra,
            )

        def parse(raw: Dict[str, Any]) -> Tuple[List[Epic], List[UserStory]]:
            epics = [Epic(**e) for e in raw.get("epics", [])]
            stories = [UserStory(**s) for s in raw.get("user_stories", [])]
            if not stories:
                raise ValueError("stories prompt returned no user_stories")
            return epics, stories

        return await self._run_artifact(
            name="user_stories",
            call=call,
            parse=parse,
            fallback=lambda: mock_provider.mock_epics_and_stories(req.title, req.text),
            succeeded=succeeded,
            failed=failed,
        )

    async def _ambiguities(
        self, req: AnalyzeRequest, succeeded: List[str], failed: List[str]
    ) -> List[Ambiguity]:
        async def call(extra: List[Dict[str, str]] | None) -> Dict[str, Any]:
            return await self._openai.generate_json(
                AMBIGUITY_SYSTEM,
                AMBIGUITY_USER_TEMPLATE.format(title=req.title, text=req.text),
                extra_messages=extra,
            )

        def parse(raw: Dict[str, Any]) -> List[Ambiguity]:
            return [Ambiguity(**a) for a in raw.get("ambiguities", [])]

        return await self._run_artifact(
            name="ambiguities",
            call=call,
            parse=parse,
            fallback=lambda: mock_provider.mock_ambiguities(req.title, req.text),
            succeeded=succeeded,
            failed=failed,
        )

    async def _tasks(
        self,
        req: AnalyzeRequest,
        stories_summary_json: str,
        succeeded: List[str],
        failed: List[str],
    ) -> List[DevTask]:
        async def call(extra: List[Dict[str, str]] | None) -> Dict[str, Any]:
            return await self._openai.generate_json(
                TASKS_SYSTEM,
                TASKS_USER_TEMPLATE.format(
                    title=req.title, text=req.text, stories=stories_summary_json
                ),
                extra_messages=extra,
            )

        def parse(raw: Dict[str, Any]) -> List[DevTask]:
            return [DevTask(**t) for t in raw.get("tasks", [])]

        return await self._run_artifact(
            name="tasks",
            call=call,
            parse=parse,
            fallback=mock_provider.mock_tasks,
            succeeded=succeeded,
            failed=failed,
        )

    async def _test_cases(
        self,
        req: AnalyzeRequest,
        stories_summary_json: str,
        succeeded: List[str],
        failed: List[str],
    ) -> List[TestCase]:
        async def call(extra: List[Dict[str, str]] | None) -> Dict[str, Any]:
            return await self._openai.generate_json(
                TESTS_SYSTEM,
                TESTS_USER_TEMPLATE.format(
                    title=req.title, text=req.text, stories=stories_summary_json
                ),
                extra_messages=extra,
            )

        def parse(raw: Dict[str, Any]) -> List[TestCase]:
            return [TestCase(**t) for t in raw.get("test_cases", [])]

        return await self._run_artifact(
            name="test_cases",
            call=call,
            parse=parse,
            fallback=mock_provider.mock_test_cases,
            succeeded=succeeded,
            failed=failed,
        )

    async def _estimation(
        self,
        stories: List[UserStory],
        tasks: List[DevTask],
        succeeded: List[str],
        failed: List[str],
    ) -> Estimation:
        # Deterministic baseline from the artifacts we already have.
        deterministic = mock_provider.mock_estimation(stories, tasks)

        async def call(extra: List[Dict[str, str]] | None) -> Dict[str, Any]:
            return await self._openai.generate_json(
                ESTIMATION_SYSTEM,
                ESTIMATION_USER_TEMPLATE.format(
                    stories=json.dumps([s.model_dump() for s in stories]),
                    tasks=json.dumps([t.model_dump() for t in tasks]),
                ),
                extra_messages=extra,
            )

        def parse(raw: Dict[str, Any]) -> Estimation:
            est = Estimation(**raw)
            # Only trust the model when it produced a non-zero total.
            if est.total_estimated_hours <= 0 and est.total_story_points <= 0:
                raise ValueError("estimation prompt returned a zero rollup")
            return est

        return await self._run_artifact(
            name="estimation",
            call=call,
            parse=parse,
            fallback=lambda: deterministic,
            succeeded=succeeded,
            failed=failed,
        )

    # ---- core retry / fallback loop ---------------------------------------

    async def _run_artifact(
        self,
        *,
        name: str,
        call: Callable[[List[Dict[str, str]] | None], Awaitable[Dict[str, Any]]],
        parse: Callable[[Dict[str, Any]], T],
        fallback: Callable[[], T],
        succeeded: List[str],
        failed: List[str],
    ) -> T:
        """Run one artifact prompt with bounded schema-validation retries and per-artifact fallback."""
        attempts = max(1, 1 + self._settings.openai_schema_retry_attempts)
        last_error_message: str | None = None

        for attempt in range(1, attempts + 1):
            extra: List[Dict[str, str]] | None = None
            if last_error_message is not None:
                # Feed the previous validation error back so the model can self-correct.
                extra = [{
                    "role": "user",
                    "content": (
                        "Your previous response failed validation with the following error. "
                        "Return a corrected JSON object that conforms to the documented schema, "
                        "and return ONLY the JSON object.\n\n"
                        f"Error: {last_error_message}"
                    ),
                }]
            try:
                raw = await call(extra)
                value = parse(raw)
                if attempt > 1:
                    logger.info("artifact %s recovered on attempt %d", name, attempt)
                else:
                    logger.debug("artifact %s succeeded on first attempt", name)
                succeeded.append(name)
                return value
            except (ValidationError, ValueError, json.JSONDecodeError) as ex:
                last_error_message = str(ex)[:600]
                logger.warning(
                    "artifact %s validation failed on attempt %d/%d: %s",
                    name, attempt, attempts, last_error_message,
                )
            except Exception as ex:
                # Transport / API error from the OpenAI SDK after its own retries are exhausted.
                logger.exception(
                    "artifact %s OpenAI call failed on attempt %d/%d: %s",
                    name, attempt, attempts, ex,
                )
                break

        logger.warning("artifact %s falling back to mock data", name)
        failed.append(name)
        return fallback()
