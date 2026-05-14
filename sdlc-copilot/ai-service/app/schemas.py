"""Pydantic models used at the public ai-service boundary.

These shapes match the C# `AiContracts.cs` records on the .NET side.
"""
from __future__ import annotations

from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field


# --- /analyze ---

class AnalyzeRequest(BaseModel):
    title: str = Field(..., description="Short title for the requirement.")
    text: str = Field(..., description="Raw requirement text to analyze.")


class Summary(BaseModel):
    summary: str
    goals: str
    stakeholders: str
    key_constraints: str


class Epic(BaseModel):
    title: str
    description: str


class UserStory(BaseModel):
    title: str
    as_a: str
    i_want: str
    so_that: str
    acceptance_criteria: List[str] = Field(default_factory=list)
    story_points: int = 0
    complexity: Literal["trivial", "low", "medium", "high", "very_high"] = "medium"
    estimated_hours: float = 0
    epic_title: Optional[str] = None


class DevTask(BaseModel):
    title: str
    description: str
    layer: Literal["backend", "frontend", "infra", "qa", "data"] = "backend"
    estimated_hours: float = 0
    complexity: Literal["trivial", "low", "medium", "high", "very_high"] = "medium"
    story_title: Optional[str] = None


class TestCase(BaseModel):
    title: str
    kind: Literal["positive", "negative", "edge"] = "positive"
    preconditions: str = ""
    steps: List[str] = Field(default_factory=list)
    expected_result: str
    story_title: Optional[str] = None


class Ambiguity(BaseModel):
    excerpt: str
    issue: str
    suggestion: str
    severity: Literal["low", "medium", "high", "critical"] = "medium"
    category: Literal["unclear", "incomplete", "conflicting", "untestable"] = "unclear"


class Estimation(BaseModel):
    total_story_points: int = 0
    total_estimated_hours: float = 0
    breakdown: Dict[str, float] = Field(default_factory=dict)


class AnalyzeResponse(BaseModel):
    summary: Summary
    epics: List[Epic] = Field(default_factory=list)
    user_stories: List[UserStory] = Field(default_factory=list)
    tasks: List[DevTask] = Field(default_factory=list)
    test_cases: List[TestCase] = Field(default_factory=list)
    ambiguities: List[Ambiguity] = Field(default_factory=list)
    estimation: Estimation
    mode: Literal["openai", "mock"] = "mock"


# --- /chat ---

class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class ChatRequest(BaseModel):
    title: str
    text: str
    history: List[ChatMessage] = Field(default_factory=list)
    message: str


class ChatResponse(BaseModel):
    reply: str
    mode: Literal["openai", "mock"] = "mock"
