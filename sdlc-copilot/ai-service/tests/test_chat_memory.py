"""Tests covering conversation memory in the chat path.

These cover both the mock-mode demo path (no key) and the live OpenAI path
(via a stub OpenAI client) to verify that:

- ``Orchestrator.chat`` ships prior turns through to the LLM in chronological order.
- The window is capped to ``Settings.chat_history_window`` so prompts stay bounded.
- The mock provider reflects prior turns back into the demo reply so the demo
  visibly exercises the contract even without a key.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import pytest

from app.config import Settings
from app.schemas import ChatMessage, ChatRequest
from app.services.openai_client import OpenAIClient
from app.services.orchestrator import Orchestrator


# ---- mock-mode tests -------------------------------------------------------

async def test_mock_chat_includes_prior_turns_in_reply(mock_mode_settings: Settings) -> None:
    """Mock mode: when history is supplied, the reply must reflect it."""
    history = [
        ChatMessage(role="user", content="What is the primary user persona?"),
        ChatMessage(role="assistant", content="The primary persona is an end user submitting data."),
    ]
    req = ChatRequest(
        title="Loyalty Portal",
        text="Customers earn points and redeem rewards across Bronze/Silver/Gold tiers.",
        history=history,
        message="And what about retention metrics?",
    )

    response = await Orchestrator(mock_mode_settings).chat(req)

    assert response.mode == "mock"
    # Acknowledges that this is a follow-up, not a first turn.
    assert "Picking up where we left off" in response.reply
    # Echoes the most recent prior user question so the demo demonstrates memory.
    assert "primary user persona" in response.reply
    # Still grounded in the current question.
    assert "retention metrics" in response.reply


async def test_mock_chat_first_turn_has_no_history_recap(mock_mode_settings: Settings) -> None:
    """Mock mode: the first turn must NOT pretend to remember earlier messages."""
    req = ChatRequest(
        title="Loyalty Portal",
        text="Customers earn points and redeem rewards across Bronze/Silver/Gold tiers.",
        message="What are the biggest risks?",
    )

    response = await Orchestrator(mock_mode_settings).chat(req)

    assert response.mode == "mock"
    assert "Picking up where we left off" not in response.reply
    assert "Loyalty Portal" in response.reply
    assert "biggest risks" in response.reply


# ---- live-mode tests via a stub OpenAI client -----------------------------

class _RecordingOpenAIClient(OpenAIClient):
    """Captures what the orchestrator hands to the OpenAI chat call."""

    def __init__(self, settings: Settings, canned_reply: str = "live reply"):
        super().__init__(settings)
        self._canned_reply = canned_reply
        self.last_system: Optional[str] = None
        self.last_history: Optional[List[Dict[str, str]]] = None
        self.last_user: Optional[str] = None

    @property
    def enabled(self) -> bool:  # type: ignore[override]
        return True

    async def chat(  # type: ignore[override]
        self,
        system: str,
        history: List[Dict[str, str]],
        user: str,
    ) -> str:
        self.last_system = system
        self.last_history = list(history)
        self.last_user = user
        return self._canned_reply


async def test_orchestrator_passes_history_to_openai_in_order(
    live_mode_settings: Settings,
) -> None:
    """Live mode: prior turns are forwarded as OpenAI messages, oldest-first."""
    stub = _RecordingOpenAIClient(live_mode_settings)
    history = [
        ChatMessage(role="user", content="Who are the primary users?"),
        ChatMessage(role="assistant", content="End users earning loyalty points."),
        ChatMessage(role="user", content="What tiers exist?"),
        ChatMessage(role="assistant", content="Bronze, Silver, Gold."),
    ]
    req = ChatRequest(
        title="Loyalty Portal",
        text="Customers earn points and redeem rewards across Bronze/Silver/Gold tiers.",
        history=history,
        message="How do users move between tiers?",
    )

    response = await Orchestrator(live_mode_settings, stub).chat(req)

    assert response.mode == "openai"
    assert response.reply == "live reply"
    assert stub.last_history is not None
    # All four prior turns are forwarded, in chronological order.
    assert len(stub.last_history) == 4
    assert [m["role"] for m in stub.last_history] == ["user", "assistant", "user", "assistant"]
    assert stub.last_history[0]["content"] == "Who are the primary users?"
    assert stub.last_history[-1]["content"] == "Bronze, Silver, Gold."
    # The current question is sent as the final user message, NOT inside history.
    assert "How do users move between tiers?" in (stub.last_user or "")
    assert all("How do users move between tiers?" not in m["content"] for m in stub.last_history)


async def test_orchestrator_caps_history_to_window() -> None:
    """Live mode: only the last ``chat_history_window`` turns are forwarded."""
    settings = Settings(
        openai_api_key="sk-test-not-real",
        openai_model="gpt-4o-mini",
        chat_history_window=4,
    )
    stub = _RecordingOpenAIClient(settings)

    history = []
    for i in range(10):
        history.append(ChatMessage(role="user", content=f"user msg {i}"))
        history.append(ChatMessage(role="assistant", content=f"assistant msg {i}"))

    req = ChatRequest(
        title="Loyalty Portal",
        text="Customers earn points.",
        history=history,
        message="latest question",
    )

    await Orchestrator(settings, stub).chat(req)

    assert stub.last_history is not None
    assert len(stub.last_history) == 4
    # The window keeps the most recent turns, dropping the oldest.
    assert stub.last_history[0]["content"] == "user msg 8"
    assert stub.last_history[-1]["content"] == "assistant msg 9"


async def test_orchestrator_surfaces_openai_error_in_live_mode(
    live_mode_settings: Settings,
) -> None:
    """When a key is configured and OpenAI fails, the actual error MUST be surfaced.

    Regression guard: an earlier implementation silently fell back to ``mock_chat``
    here, which made a real OpenAI failure indistinguishable from no-key mode and
    led operators to think nothing was wrong with their key/config.
    """

    class _FailingClient(OpenAIClient):
        @property
        def enabled(self) -> bool:  # type: ignore[override]
            return True

        async def chat(  # type: ignore[override]
            self,
            system: str,
            history: List[Dict[str, str]],
            user: str,
        ) -> str:
            raise RuntimeError("simulated OpenAI outage")

    failing = _FailingClient(live_mode_settings)
    history = [
        ChatMessage(role="user", content="Earlier question about scope."),
        ChatMessage(role="assistant", content="Scope is loosely defined."),
    ]
    req = ChatRequest(
        title="Loyalty Portal",
        text="Customers earn points.",
        history=history,
        message="Follow-up?",
    )

    response = await Orchestrator(live_mode_settings, failing).chat(req)

    # CRITICAL: mode is "error", NOT "mock" — silent fallback regression guard.
    assert response.mode == "error"
    assert response.error is not None
    assert "RuntimeError" in response.error
    assert "simulated OpenAI outage" in response.error
    # The reply text must clearly indicate the live path failed (not the mock signature).
    assert "live OpenAI chat failed" in response.reply
    assert "Mock reply" not in response.reply
