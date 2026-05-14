"""Orchestrator tests for the live OpenAI path using a stubbed client.

These tests exercise the resilience model end-to-end:
- All artifacts succeed → mode="openai" with all live data.
- One artifact's first JSON is invalid (Pydantic) → retried with corrective hint → succeeds.
- One artifact fails every attempt → only that artifact falls back to mock.
- Every artifact fails → orchestrator still returns a valid AnalyzeResponse (mode="mock").
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import pytest

from app.config import Settings
from app.schemas import AnalyzeRequest, AnalyzeResponse
from app.services.openai_client import OpenAIClient
from app.services.orchestrator import Orchestrator


# ---- canned LLM responses (the JSON shapes our prompts expect) -------------

def _good_summary() -> Dict[str, Any]:
    return {
        "summary": "Live executive summary",
        "goals": "- live goal a\n- live goal b",
        "stakeholders": "- live stakeholder",
        "key_constraints": "- live constraint",
    }


def _good_stories() -> Dict[str, Any]:
    return {
        "epics": [{"title": "Live Epic", "description": "Live epic description"}],
        "user_stories": [
            {
                "title": "Live Story",
                "as_a": "live user",
                "i_want": "to do live things",
                "so_that": "I get live value",
                "acceptance_criteria": ["Given live state, when I act, then live outcome."],
                "story_points": 3,
                "complexity": "medium",
                "estimated_hours": 8,
                "epic_title": "Live Epic",
            }
        ],
    }


def _good_ambiguities() -> Dict[str, Any]:
    return {
        "ambiguities": [
            {
                "excerpt": "live excerpt",
                "issue": "live issue",
                "suggestion": "live suggestion",
                "severity": "medium",
                "category": "unclear",
            }
        ]
    }


def _good_tasks() -> Dict[str, Any]:
    return {
        "tasks": [
            {
                "title": "Live task",
                "description": "Live task description",
                "layer": "backend",
                "estimated_hours": 5,
                "complexity": "medium",
                "story_title": "Live Story",
            }
        ]
    }


def _good_tests() -> Dict[str, Any]:
    return {
        "test_cases": [
            {
                "title": "Live test",
                "kind": "positive",
                "preconditions": "",
                "steps": ["do thing"],
                "expected_result": "thing happens",
                "story_title": "Live Story",
            }
        ]
    }


def _good_estimation() -> Dict[str, Any]:
    return {
        "total_story_points": 13,
        "total_estimated_hours": 42,
        "breakdown": {"backend": 30, "frontend": 8, "qa": 4},
    }


# ---- stub OpenAI client ----------------------------------------------------

class StubOpenAIClient(OpenAIClient):
    """Bypasses the real OpenAI SDK. Routes generate_json by matching the system prompt."""

    def __init__(self, settings: Settings, responses: Dict[str, List[Any]]):
        super().__init__(settings)
        self._responses = responses
        self.calls: List[str] = []

    @property
    def enabled(self) -> bool:  # type: ignore[override]
        return True

    @property
    def model(self) -> str:  # type: ignore[override]
        return self._settings.openai_model

    async def generate_json(
        self,
        system: str,
        user: str,
        *,
        extra_messages: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        key = _classify(system)
        self.calls.append(key)
        queue = self._responses.get(key) or []
        if not queue:
            raise RuntimeError(f"no canned response for {key}")
        next_value = queue.pop(0)
        if isinstance(next_value, Exception):
            raise next_value
        return next_value


def _classify(system: str) -> str:
    """Map a prompt system message to its artifact key by exact phrase."""
    s = system.lower()
    if "business analyst" in s:
        return "summary"
    if "agile coach" in s:
        return "user_stories"
    if "requirements reviewer" in s:
        return "ambiguities"
    if "engineering manager" in s:
        return "estimation"
    if "tech lead" in s:
        return "tasks"
    if "qa engineer" in s:
        return "test_cases"
    return "unknown"


@pytest.fixture
def req() -> AnalyzeRequest:
    return AnalyzeRequest(
        title="Loyalty Portal",
        text="Customers earn points and redeem rewards across Bronze/Silver/Gold tiers.",
    )


# ---- happy path ------------------------------------------------------------

async def test_all_artifacts_live(live_mode_settings: Settings, req: AnalyzeRequest) -> None:
    stub = StubOpenAIClient(
        live_mode_settings,
        {
            "summary": [_good_summary()],
            "user_stories": [_good_stories()],
            "ambiguities": [_good_ambiguities()],
            "tasks": [_good_tasks()],
            "test_cases": [_good_tests()],
            "estimation": [_good_estimation()],
        },
    )
    orchestrator = Orchestrator(live_mode_settings, stub)

    response = await orchestrator.analyze(req)

    assert response.mode == "openai"
    assert response.summary.summary == "Live executive summary"
    assert len(response.epics) == 1 and response.epics[0].title == "Live Epic"
    assert len(response.user_stories) == 1 and response.user_stories[0].title == "Live Story"
    assert len(response.tasks) == 1 and response.tasks[0].title == "Live task"
    assert len(response.test_cases) == 1 and response.test_cases[0].title == "Live test"
    assert len(response.ambiguities) == 1
    assert response.estimation.total_story_points == 13
    assert response.estimation.total_estimated_hours == 42


# ---- per-artifact retry on invalid schema ---------------------------------

async def test_invalid_summary_is_retried_with_correction(
    live_mode_settings: Settings, req: AnalyzeRequest
) -> None:
    bad_summary = {"summary": "missing other fields"}  # fails Pydantic validation
    stub = StubOpenAIClient(
        live_mode_settings,
        {
            "summary": [bad_summary, _good_summary()],
            "user_stories": [_good_stories()],
            "ambiguities": [_good_ambiguities()],
            "tasks": [_good_tasks()],
            "test_cases": [_good_tests()],
            "estimation": [_good_estimation()],
        },
    )
    orchestrator = Orchestrator(live_mode_settings, stub)

    response = await orchestrator.analyze(req)

    assert response.mode == "openai"
    assert response.summary.summary == "Live executive summary"
    # summary was called twice (initial + retry), the rest once each.
    assert stub.calls.count("summary") == 2


# ---- per-artifact fallback when all retries fail --------------------------

async def test_persistent_failure_falls_back_to_mock_artifact(
    live_mode_settings: Settings, req: AnalyzeRequest
) -> None:
    bad = {"summary": "still wrong"}  # never passes validation
    stub = StubOpenAIClient(
        live_mode_settings,
        {
            "summary": [bad, bad],  # consume both attempts
            "user_stories": [_good_stories()],
            "ambiguities": [_good_ambiguities()],
            "tasks": [_good_tasks()],
            "test_cases": [_good_tests()],
            "estimation": [_good_estimation()],
        },
    )
    orchestrator = Orchestrator(live_mode_settings, stub)

    response = await orchestrator.analyze(req)

    # Summary fell back to mock; everything else is live, so overall mode stays openai.
    assert response.mode == "openai"
    assert "ingestion path" in response.summary.summary.lower()  # signature of mock_summary
    assert response.user_stories[0].title == "Live Story"


async def test_transport_error_falls_back_to_mock_artifact(
    live_mode_settings: Settings, req: AnalyzeRequest
) -> None:
    stub = StubOpenAIClient(
        live_mode_settings,
        {
            "summary": [RuntimeError("simulated OpenAI 500")],
            "user_stories": [_good_stories()],
            "ambiguities": [_good_ambiguities()],
            "tasks": [_good_tasks()],
            "test_cases": [_good_tests()],
            "estimation": [_good_estimation()],
        },
    )
    orchestrator = Orchestrator(live_mode_settings, stub)

    response = await orchestrator.analyze(req)

    assert response.mode == "openai"
    assert "ingestion path" in response.summary.summary.lower()
    # Transport errors break out without consuming the retry attempts beyond the first call.
    assert stub.calls.count("summary") == 1


# ---- complete failure → entire pipeline reports mock ----------------------

async def test_all_artifacts_fail_returns_mock_mode(
    live_mode_settings: Settings, req: AnalyzeRequest
) -> None:
    err = RuntimeError("simulated outage")
    stub = StubOpenAIClient(
        live_mode_settings,
        {
            "summary": [err],
            "user_stories": [err],
            "ambiguities": [err],
            "tasks": [err],
            "test_cases": [err],
            "estimation": [err],
        },
    )
    orchestrator = Orchestrator(live_mode_settings, stub)

    response = await orchestrator.analyze(req)

    assert response.mode == "mock"
    # We still get a usable response — orchestrator never raises.
    assert response.summary is not None
    assert isinstance(response, AnalyzeResponse)
