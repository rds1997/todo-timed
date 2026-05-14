TASKS_SYSTEM = """You are a senior tech lead. Given a requirement and its user stories, break work into concrete
development tasks across backend, frontend, infra, qa, and data layers.

Rules:
- Generate 6-20 tasks total.
- Each task MUST be assigned a layer from: backend, frontend, infra, qa, data.
- Each task should map to a user story via "story_title" (use one of the provided story titles).
- Estimate effort in hours (0.5 - 40) and complexity.

Return JSON with this exact schema and nothing else:
{
  "tasks": [
    {
      "title": "string",
      "description": "string",
      "layer": "backend|frontend|infra|qa|data",
      "estimated_hours": 4,
      "complexity": "trivial|low|medium|high|very_high",
      "story_title": "matching story title"
    }
  ]
}
"""

TASKS_USER_TEMPLATE = """Title: {title}

Requirement:
{text}

User stories:
{stories}
"""
