"""Reusable prompt templates for SDLC Copilot.

Each prompt returns a single JSON object that conforms to a documented schema.
The orchestrator runs them in parallel and merges results into an AnalyzeResponse.
"""
from .summary import SUMMARY_SYSTEM, SUMMARY_USER_TEMPLATE
from .user_stories import STORIES_SYSTEM, STORIES_USER_TEMPLATE
from .tasks import TASKS_SYSTEM, TASKS_USER_TEMPLATE
from .test_cases import TESTS_SYSTEM, TESTS_USER_TEMPLATE
from .ambiguity import AMBIGUITY_SYSTEM, AMBIGUITY_USER_TEMPLATE
from .estimation import ESTIMATION_SYSTEM, ESTIMATION_USER_TEMPLATE
from .chat import CHAT_SYSTEM, CHAT_USER_TEMPLATE

__all__ = [
    "SUMMARY_SYSTEM", "SUMMARY_USER_TEMPLATE",
    "STORIES_SYSTEM", "STORIES_USER_TEMPLATE",
    "TASKS_SYSTEM", "TASKS_USER_TEMPLATE",
    "TESTS_SYSTEM", "TESTS_USER_TEMPLATE",
    "AMBIGUITY_SYSTEM", "AMBIGUITY_USER_TEMPLATE",
    "ESTIMATION_SYSTEM", "ESTIMATION_USER_TEMPLATE",
    "CHAT_SYSTEM", "CHAT_USER_TEMPLATE",
]
