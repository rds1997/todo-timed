# Intelligent SDLC Copilot

**AI-powered platform that converts raw software requirements into structured SDLC artifacts** — summaries, epics, user stories, acceptance criteria, dev tasks, test cases, ambiguity findings, and effort estimation — all editable, exportable, and queryable via a conversational assistant.

```
┌──────────────┐     ┌────────────────┐     ┌──────────────────┐     ┌────────────┐
│ Angular 17   │ ──▶ │ ASP.NET Core 8 │ ──▶ │ Python FastAPI   │ ──▶ │ OpenAI API │
│  + Material  │     │   Web API      │     │   AI service     │     └────────────┘
└──────────────┘     └────────┬───────┘     └──────────────────┘
                              ▼
                       ┌──────────────┐
                       │  PostgreSQL  │
                       └──────────────┘
```

## Stack

| Layer          | Tech                                                            |
|----------------|-----------------------------------------------------------------|
| Frontend       | Angular 17 (standalone), Angular Material, SCSS                 |
| Backend API    | ASP.NET Core 8 (clean arch), EF Core, FluentValidation, Serilog |
| AI service     | Python 3.12, FastAPI, OpenAI SDK, Pydantic v2                   |
| Database       | PostgreSQL 16 (jsonb columns for flexible fields)               |
| Infra          | Docker + docker-compose, Azure-ready                            |

## Features

1. **Requirement ingestion** — paste text or upload `.txt`, `.md`, `.pdf`, `.doc`, `.docx`. PDF text is extracted with PdfPig.
2. **AI requirement analysis** — generates a structured summary, epics, user stories (with AC), dev tasks, ambiguity findings, and effort estimation.
3. **Test case generation** — positive, negative, and edge cases per story.
4. **Ambiguity detection** — flags unclear / incomplete / conflicting / untestable statements with concrete suggestions.
5. **Interactive dashboard** — KPI cards, sortable tables, expandable artifact panels, all editable.
6. **Conversational assistant** — chat with a model that has the full requirement in context; history is persisted.
7. **Effort estimation** — total story points, total hours, and per-layer breakdown (backend, frontend, infra, QA, data).
8. **Export** — Markdown and JSON exports of the full structured artifact set.

---

## Quick start (Docker, recommended)

```bash
cd sdlc-copilot
cp .env.example .env          # then edit OPENAI_API_KEY=... (optional)
docker compose up --build
```

Open the UI at <http://localhost:4200>. Swagger lives at <http://localhost:4200/swagger> (proxied) or <http://localhost:8080/swagger>.

**No OpenAI key?** Leave `OPENAI_API_KEY` blank — the AI service returns deterministic mock data so the whole platform demos end-to-end without external dependencies.

### Demo path
1. On the dashboard, paste the contents of [`db/seed-sample-requirement.txt`](db/seed-sample-requirement.txt) into "Paste text" and click **Ingest**.
2. On the resulting page, click **Analyze with AI**. The summary, stories, tasks, tests, ambiguities, and estimation populate.
3. Open the **Assistant** tab and ask a question (e.g., "What are the biggest risks here?").
4. Click **Export MD** or **Export JSON** for the full structured output.

---

## Local development (without Docker)

### Postgres
```bash
docker run --name sdlc-postgres -d -p 5432:5432 \
  -e POSTGRES_USER=sdlc -e POSTGRES_PASSWORD=sdlc -e POSTGRES_DB=sdlc_copilot \
  postgres:16-alpine
```

### AI service
```bash
cd ai-service
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY=sk-...          # optional; otherwise mock mode
uvicorn app.main:app --reload --port 8001
```

### Backend API
```bash
cd backend
export ConnectionStrings__Default="Host=localhost;Port=5432;Database=sdlc_copilot;Username=sdlc;Password=sdlc"
export AiService__BaseUrl="http://localhost:8001"
dotnet run --project src/SdlcCopilot.Api
```
Migrations run automatically on startup. Swagger: <http://localhost:8080/swagger>.

### Frontend
```bash
cd frontend
npm install
npm start                              # ng serve on http://localhost:4200
```

---

## API documentation

Full interactive docs are available at:
- `.NET API`     — `http://localhost:8080/swagger`
- `AI service`   — `http://localhost:8001/docs`

Core endpoints (`/api/v1`):

| Method | Path                                            | Purpose                                                         |
|--------|-------------------------------------------------|-----------------------------------------------------------------|
| GET    | `/requirements`                                 | List all requirements (summary view)                            |
| POST   | `/requirements`                                 | Ingest a raw text requirement                                   |
| POST   | `/requirements/upload`                          | Multipart upload of a `.txt/.md/.pdf/.doc/.docx`                |
| GET    | `/requirements/{id}`                            | Full structured view                                            |
| POST   | `/requirements/{id}/analyze`                    | Run AI analysis (epics/stories/tasks/tests/ambiguity/estimation)|
| DELETE | `/requirements/{id}`                            | Delete a requirement and all artifacts                          |
| PUT    | `/requirements/{id}/user-stories/{storyId}`     | Edit a generated story                                          |
| PUT    | `/requirements/{id}/tasks/{taskId}`             | Edit a generated task                                           |
| PUT    | `/requirements/{id}/test-cases/{testCaseId}`    | Edit a generated test case                                      |
| GET    | `/requirements/{id}/chat`                       | Chat history                                                    |
| POST   | `/requirements/{id}/chat`                       | Send a chat message and get an AI reply                         |
| GET    | `/requirements/{id}/export.md`                  | Download Markdown export                                        |
| GET    | `/requirements/{id}/export.json`                | Download JSON export                                            |

The AI service exposes:
| Method | Path           | Purpose                                              |
|--------|----------------|------------------------------------------------------|
| POST   | `/api/v1/analyze` | Full structured analysis                          |
| POST   | `/api/v1/chat`    | Conversational reply grounded in the requirement  |
| GET    | `/health`         | Liveness + current mode (`openai` or `mock`)      |

---

## Project layout

```
sdlc-copilot/
├── backend/                            # .NET 8 Web API (clean architecture)
│   ├── SdlcCopilot.sln
│   ├── src/SdlcCopilot.Domain/         # Pure entities + enums
│   ├── src/SdlcCopilot.Application/    # DTOs, services, validators, AI contracts
│   ├── src/SdlcCopilot.Infrastructure/ # EF Core (Npgsql), repositories, AI HTTP client, PDF extractor
│   └── src/SdlcCopilot.Api/            # Controllers, Program.cs, Swagger, JWT-ready auth, Serilog
├── ai-service/                         # Python FastAPI AI service
│   ├── app/
│   │   ├── main.py                     # FastAPI entrypoint
│   │   ├── routers/analyze.py          # /api/v1/analyze, /api/v1/chat
│   │   ├── services/
│   │   │   ├── openai_client.py        # OpenAI Chat Completions JSON-mode wrapper
│   │   │   ├── orchestrator.py         # Composes prompts into one analysis
│   │   │   └── mock_provider.py        # Deterministic fallback
│   │   └── prompts/                    # Reusable prompt templates per artifact
│   └── requirements.txt
├── frontend/                           # Angular 17 + Material
│   ├── src/app/pages/{dashboard,requirement-detail}
│   ├── src/app/components/{upload,chat-panel}
│   └── src/app/core/{models,services}
├── db/
│   ├── init.sql                        # Optional bootstrap (role/database)
│   └── seed-sample-requirement.txt     # Demo data
├── docs/
│   └── architecture.md                 # Deeper architecture notes
├── docker-compose.yml
└── .env.example
```

---

## Coding standards (enforced in this repo)

- **Modular clean architecture** — Domain → Application → Infrastructure → Api with strict project references.
- **DTO pattern** — entities never leak across the API boundary (`SdlcCopilot.Application.Dtos`).
- **Repository pattern** — `IRequirementRepository` shields the application from EF Core.
- **Result type** — `Result<T>` returns success/error/status uniformly from services to controllers.
- **Validation** — FluentValidation auto-validates request DTOs.
- **Async everywhere** — every I/O path is `async`/`await`, with `CancellationToken` plumbed through.
- **Structured logging** — Serilog (backend) and `logging` (AI service) emit JSON to stdout.
- **Environment-driven config** — no secrets in code; everything is `.env`/env-var driven.
- **Prompt engineering** — separate, reusable prompts per artifact in `ai-service/app/prompts/`.

---

## Azure deployment

The stack is Azure-ready:

| Component   | Recommended Azure service           |
|-------------|-------------------------------------|
| `frontend`  | Azure Static Web Apps or App Service|
| `api`       | Azure App Service (Linux containers) or Azure Container Apps |
| `ai-service`| Azure Container Apps                |
| `postgres`  | Azure Database for PostgreSQL Flexible Server |
| `LLM`       | Azure OpenAI (set `OPENAI_BASE_URL`)|

Each service has its own `Dockerfile` and a `PORT` env-var; the same Docker images deploy to any of the above without modification.

For Azure OpenAI, set:
```
OPENAI_API_KEY=<aoai-key>
OPENAI_BASE_URL=https://<your-resource>.openai.azure.com
OPENAI_MODEL=<your-deployment-name>
```

---

## License

MIT. Built as a hackathon scaffold — feel free to fork and ship.
