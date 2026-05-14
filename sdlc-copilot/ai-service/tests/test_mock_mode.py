"""Mock-mode parity tests.

These tests cover the path the demo runs on when no OpenAI key is configured.
They prove the orchestrator returns a fully populated AnalyzeResponse without
ever calling the network, and that ``mode`` is reported correctly.
"""
from __future__ import annotations

from app.config import Settings
from app.schemas import AnalyzeRequest, ChatRequest
from app.services.orchestrator import Orchestrator


async def test_mock_mode_returns_full_artifact_set(mock_mode_settings: Settings) -> None:
    orchestrator = Orchestrator(mock_mode_settings)
    req = AnalyzeRequest(title="Loyalty Portal", text="Customers earn points and redeem rewards.")

    response = await orchestrator.analyze(req)

    assert response.mode == "mock"
    assert len(response.epics) >= 2
    assert len(response.user_stories) >= 5
    assert len(response.tasks) >= 10
    assert len(response.test_cases) >= 8
    assert len(response.ambiguities) >= 3
    assert response.estimation.total_story_points > 0
    assert response.estimation.total_estimated_hours > 0
    # Every story has BDD-style acceptance criteria.
    assert all(s.acceptance_criteria for s in response.user_stories)
    # Every test case has steps.
    assert all(tc.steps for tc in response.test_cases)
    # Per-layer hour rollup is populated.
    assert sum(response.estimation.breakdown.values()) > 0


async def test_mock_chat_returns_grounded_reply(mock_mode_settings: Settings) -> None:
    orchestrator = Orchestrator(mock_mode_settings)
    req = ChatRequest(
        title="Loyalty Portal",
        text="Customers earn points and redeem rewards across Bronze/Silver/Gold tiers.",
        message="What are the biggest risks?",
    )

    response = await orchestrator.chat(req)

    assert response.mode == "mock"
    assert "Loyalty Portal" in response.reply
    assert "Mock reply" in response.reply


async def test_force_mock_overrides_key() -> None:
    """When FORCE_MOCK=true, mock provider runs even if a key is present."""
    settings = Settings(openai_api_key="sk-test", force_mock=True)
    orchestrator = Orchestrator(settings)

    response = await orchestrator.analyze(
        AnalyzeRequest(title="x", text="trivial requirement text.")
    )

    assert response.mode == "mock"
