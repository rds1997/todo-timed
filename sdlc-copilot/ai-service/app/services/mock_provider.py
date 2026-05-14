"""Deterministic mock data so the platform demos end-to-end without an OpenAI key.

The mock is intentionally rich enough to populate every dashboard widget while still
reflecting the input requirement (title + first sentence) so demos feel real.
"""
from __future__ import annotations

import re
from typing import List

from ..schemas import (
    AnalyzeResponse, Ambiguity, ChatRequest, ChatResponse, DevTask, Epic,
    Estimation, Summary, TestCase, UserStory,
)


def _first_sentence(text: str) -> str:
    text = text.strip().replace("\n", " ")
    if not text:
        return "the system"
    parts = re.split(r"(?<=[.!?])\s+", text)
    return parts[0].strip()[:160] if parts else text[:160]


def mock_analyze(title: str, text: str) -> AnalyzeResponse:
    focus = _first_sentence(text) or title
    epics = [
        Epic(title="Core Functionality", description=f"Deliver the primary capability: {focus}"),
        Epic(title="User Experience", description="Provide a clean, responsive interface end users can adopt quickly."),
        Epic(title="Operations & Security", description="Make the system observable, secure, and deployable."),
    ]

    stories: List[UserStory] = [
        UserStory(
            title="Capture primary input",
            as_a="end user",
            i_want="to submit my data through the UI",
            so_that="the system can process my request",
            acceptance_criteria=[
                "Given valid input, when I submit, then I see a success confirmation.",
                "Given empty required fields, when I submit, then I see field-level errors.",
            ],
            story_points=3, complexity="medium", estimated_hours=8, epic_title="Core Functionality",
        ),
        UserStory(
            title="Process input asynchronously",
            as_a="end user",
            i_want="to see progress while my request is being processed",
            so_that="I understand the system is working",
            acceptance_criteria=[
                "A status indicator appears within 1s of submission.",
                "On completion, results are rendered without a full page reload.",
            ],
            story_points=5, complexity="medium", estimated_hours=12, epic_title="Core Functionality",
        ),
        UserStory(
            title="Browse historical results",
            as_a="returning user",
            i_want="to see my previous submissions",
            so_that="I can revisit and compare them",
            acceptance_criteria=[
                "List is sorted by most recent first.",
                "I can open any historical item to see the full result.",
            ],
            story_points=3, complexity="low", estimated_hours=6, epic_title="User Experience",
        ),
        UserStory(
            title="Export results",
            as_a="end user",
            i_want="to export the generated output",
            so_that="I can share it outside the platform",
            acceptance_criteria=[
                "Export to JSON works for any result.",
                "Export to Markdown works for any result.",
            ],
            story_points=2, complexity="low", estimated_hours=4, epic_title="User Experience",
        ),
        UserStory(
            title="Authenticate users",
            as_a="platform owner",
            i_want="users to authenticate before using the system",
            so_that="data is private per user",
            acceptance_criteria=[
                "Unauthenticated requests to protected endpoints return 401.",
                "JWT tokens are validated against the configured authority.",
            ],
            story_points=5, complexity="medium", estimated_hours=10, epic_title="Operations & Security",
        ),
        UserStory(
            title="Operate the platform",
            as_a="ops engineer",
            i_want="health and metrics endpoints",
            so_that="I can monitor the system in production",
            acceptance_criteria=[
                "GET /health returns 200 when dependencies are healthy.",
                "Structured logs are emitted for every request.",
            ],
            story_points=2, complexity="low", estimated_hours=4, epic_title="Operations & Security",
        ),
    ]

    tasks: List[DevTask] = [
        DevTask(title="Design REST contract for submission", description="Document POST/GET endpoints with example payloads.", layer="backend", estimated_hours=4, complexity="low", story_title="Capture primary input"),
        DevTask(title="Implement submission endpoint", description="Validate, persist, and dispatch async processing.", layer="backend", estimated_hours=6, complexity="medium", story_title="Capture primary input"),
        DevTask(title="Build submission form UI", description="Material-styled form with inline validation.", layer="frontend", estimated_hours=6, complexity="medium", story_title="Capture primary input"),
        DevTask(title="Async processing pipeline", description="Background worker / queue integration.", layer="backend", estimated_hours=8, complexity="high", story_title="Process input asynchronously"),
        DevTask(title="Progress indicator + polling", description="Frontend polls or subscribes for status.", layer="frontend", estimated_hours=4, complexity="medium", story_title="Process input asynchronously"),
        DevTask(title="History list endpoint", description="Paginated list of past submissions.", layer="backend", estimated_hours=3, complexity="low", story_title="Browse historical results"),
        DevTask(title="History dashboard view", description="Sortable list with detail drawer.", layer="frontend", estimated_hours=5, complexity="medium", story_title="Browse historical results"),
        DevTask(title="JSON + Markdown export", description="Export endpoints + frontend buttons.", layer="backend", estimated_hours=3, complexity="low", story_title="Export results"),
        DevTask(title="JWT auth middleware", description="Validate tokens, enforce scopes on protected routes.", layer="backend", estimated_hours=6, complexity="medium", story_title="Authenticate users"),
        DevTask(title="Login screen", description="OIDC redirect + token storage.", layer="frontend", estimated_hours=4, complexity="medium", story_title="Authenticate users"),
        DevTask(title="Containerize services", description="Dockerfiles + docker-compose for local dev.", layer="infra", estimated_hours=4, complexity="medium", story_title="Operate the platform"),
        DevTask(title="Structured logging & /health", description="Add Serilog + health checks.", layer="backend", estimated_hours=2, complexity="low", story_title="Operate the platform"),
        DevTask(title="Smoke + integration tests", description="Cover golden path of every story.", layer="qa", estimated_hours=8, complexity="medium", story_title="Capture primary input"),
        DevTask(title="Seed sample data", description="Provide one demo-ready requirement.", layer="data", estimated_hours=2, complexity="low", story_title="Browse historical results"),
    ]

    test_cases: List[TestCase] = [
        TestCase(title="Submit valid payload", kind="positive", preconditions="User is authenticated.", steps=["Fill all required fields", "Press Submit"], expected_result="Submission succeeds and appears in history.", story_title="Capture primary input"),
        TestCase(title="Submit empty payload", kind="negative", preconditions="User is authenticated.", steps=["Leave all fields empty", "Press Submit"], expected_result="Field-level errors are shown and request is not sent.", story_title="Capture primary input"),
        TestCase(title="Submit oversized payload", kind="edge", preconditions="User is authenticated.", steps=["Paste payload near the maximum allowed size", "Press Submit"], expected_result="System either accepts or rejects with a clear error; no 5xx.", story_title="Capture primary input"),
        TestCase(title="Progress appears within 1s", kind="positive", preconditions="A submission is dispatched.", steps=["Submit a valid request", "Observe UI"], expected_result="Progress indicator is visible within 1 second.", story_title="Process input asynchronously"),
        TestCase(title="History sorted recent-first", kind="positive", preconditions="At least two prior submissions exist.", steps=["Open history page"], expected_result="Items are ordered by creation date descending.", story_title="Browse historical results"),
        TestCase(title="Export JSON contains all fields", kind="positive", preconditions="A processed result exists.", steps=["Open the result", "Click Export JSON"], expected_result="Downloaded JSON includes summary, stories, tasks, tests.", story_title="Export results"),
        TestCase(title="Unauthenticated request returns 401", kind="negative", preconditions="No token is sent.", steps=["Call a protected endpoint without Authorization header"], expected_result="Server returns 401 Unauthorized.", story_title="Authenticate users"),
        TestCase(title="Expired token returns 401", kind="edge", preconditions="A JWT past its expiry is available.", steps=["Call a protected endpoint with the expired token"], expected_result="Server returns 401 with a clear error.", story_title="Authenticate users"),
        TestCase(title="Health endpoint healthy", kind="positive", preconditions="DB is reachable.", steps=["GET /health"], expected_result="Returns 200 with status=ok.", story_title="Operate the platform"),
    ]

    ambiguities: List[Ambiguity] = [
        Ambiguity(excerpt=focus, issue="The user persona is not explicitly defined.", suggestion="Identify the primary persona(s) and their goals.", severity="medium", category="incomplete"),
        Ambiguity(excerpt="responsive modern UI", issue="No target devices or breakpoints specified.", suggestion="List supported viewports (e.g. >= 1024px desktop, 768-1023 tablet, < 768 mobile).", severity="low", category="unclear"),
        Ambiguity(excerpt="export support", issue="Export formats and scope are unclear.", suggestion="Specify which artifacts can be exported, and into which formats (JSON, MD, PDF...).", severity="medium", category="incomplete"),
        Ambiguity(excerpt="effort estimation", issue="Estimation units are not defined.", suggestion="Decide whether estimates are in story points, ideal hours, or both, and which scale.", severity="low", category="unclear"),
        Ambiguity(excerpt="conversational assistant", issue="Scope and memory of the assistant are not specified.", suggestion="Define whether the assistant has access to project history and tool calls.", severity="high", category="incomplete"),
    ]

    total_points = sum(s.story_points for s in stories)
    breakdown = {"backend": 0.0, "frontend": 0.0, "infra": 0.0, "qa": 0.0, "data": 0.0}
    for t in tasks:
        breakdown[t.layer] = round(breakdown.get(t.layer, 0.0) + t.estimated_hours, 2)
    total_hours = round(sum(breakdown.values()), 2)

    return AnalyzeResponse(
        summary=Summary(
            summary=f"This requirement focuses on: {focus} The system needs an ingestion path, async processing, history, exports, and basic auth/observability.",
            goals="- Convert the described intent into a working flow\n- Provide a usable dashboard\n- Be deployable and observable",
            stakeholders="- End users submitting input\n- Returning users reviewing history\n- Platform owners / admins\n- Ops engineers",
            key_constraints="- Modern web stack (Angular + .NET + Python + Postgres)\n- Hackathon timeframe\n- Dockerized for portability\n- JWT-ready auth",
        ),
        epics=epics,
        user_stories=stories,
        tasks=tasks,
        test_cases=test_cases,
        ambiguities=ambiguities,
        estimation=Estimation(
            total_story_points=total_points,
            total_estimated_hours=total_hours,
            breakdown=breakdown,
        ),
        mode="mock",
    )


def mock_chat(req: ChatRequest) -> ChatResponse:
    snippet = _first_sentence(req.text) or req.title
    reply = (
        f"Looking at \"{req.title}\", which describes: {snippet} — "
        f"here's a quick answer to your question (\"{req.message.strip()[:120]}\"): "
        "Based on the captured requirement, the most likely concern is that scope, "
        "user persona, and acceptance criteria are not fully nailed down. I'd recommend "
        "tightening those before deciding on architecture details. "
        "(Mock reply — set OPENAI_API_KEY for live responses.)"
    )
    return ChatResponse(reply=reply, mode="mock")
