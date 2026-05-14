# Architecture

## Goals
- **Enterprise-grade clean architecture** — the system is split along Domain → Application → Infrastructure → Api boundaries so business logic is testable and decoupled from EF Core, HTTP, and the LLM.
- **Hackathon-friendly speed** — the AI service falls back to deterministic mock data when no OpenAI key is configured, so the full UI can be demoed without external dependencies.

## Sequence: ingest → analyze

```
[ Browser ] --POST /api/v1/requirements--> [ .NET Api ]
[ Browser ] --POST /api/v1/requirements/{id}/analyze--> [ .NET Api ]
                                                          |
                                                          | IRequirementService.AnalyzeAsync
                                                          v
                                                  [ IAiService (HttpClient) ]
                                                          |
                                                          | POST /api/v1/analyze
                                                          v
                                                  [ FastAPI orchestrator ]
                                                          |
                                                          | gpt-4o-mini  *(parallel prompts)*
                                                          v
                                                  [ Azure / OpenAI ]
                                                          |
                                                          | structured JSON
                                                          v
                                                  [ FastAPI orchestrator merges into AnalyzeResponse ]
                                                          |
                                                          v
                                                  [ .NET Application.RequirementService.ApplyAiResponse ]
                                                          |
                                                          v
                                                  [ EF Core save: epics, stories, tasks, tests, ambiguities, analysis ]
```

## Backend layers

- **`SdlcCopilot.Domain`** — pure entities + enums. No EF, no JSON, no HTTP. The aggregate root is `Requirement` (owns epics, stories, tasks, tests, ambiguities, analysis, chat messages).
- **`SdlcCopilot.Application`** — DTOs, validators, service interfaces (`IRequirementService`, `IChatService`), AI wire contracts (`AiContracts`), repository interface (`IRequirementRepository`), `Result<T>` helper. Has no dependency on EF or ASP.NET.
- **`SdlcCopilot.Infrastructure`** — EF Core `AppDbContext` (Npgsql), `RequirementRepository`, `HttpAiService` (typed HttpClient), `DocumentTextExtractor` (PdfPig + UTF-8 fallback), DI registration.
- **`SdlcCopilot.Api`** — Controllers (`RequirementsController`, `ChatController`), Program.cs (Serilog, Swagger, CORS, FluentValidation auto-validation, JWT-ready bearer, exception middleware, `/health`), and EF auto-migration on startup.

## AI service

- `routers/analyze.py` exposes two endpoints: `/api/v1/analyze` and `/api/v1/chat`.
- `services/orchestrator.py` composes the analysis from independent, reusable prompts in `app/prompts/`:
  - `summary` — exec summary, goals, stakeholders, constraints
  - `user_stories` — epics + BDD user stories with acceptance criteria
  - `tasks` — backend/frontend/infra/qa/data tasks
  - `test_cases` — positive/negative/edge tests per story
  - `ambiguity` — ambiguity findings with severity + category
  - `estimation` — total story points + per-layer hour breakdown
  - `chat` — grounded conversational replies
- Calls are issued in three phases (summary+stories+ambiguity in parallel, then tasks+tests, then estimation) to keep latency low and cost bounded.
- All prompts ask for **JSON-mode** responses validated against Pydantic models in `app/schemas.py`. If validation fails the call is retried (configurable via `OPENAI_SCHEMA_RETRY_ATTEMPTS`) with the validation error fed back into the user message so the model can self-correct.
- **Per-artifact resilience**: each artifact is generated independently. If a single prompt still fails after retries — or the OpenAI SDK raises after its own transport-level retries (`OPENAI_MAX_RETRIES`) — only that artifact falls back to mock data. The rest of the analysis stays live.
- Mode is reported by `/health` and on every `AnalyzeResponse`: `openai` when at least one live artifact succeeded, `mock` otherwise.
- The live LLM defaults to `gpt-4o-mini`; override with `OPENAI_MODEL`. Azure OpenAI is supported by setting `OPENAI_BASE_URL` and `OPENAI_MODEL` to your deployment name.

## Database

- One Postgres database `sdlc_copilot` with these tables:
  - `requirements` (root)
  - `analyses` (one-to-one with requirement; stores the summary block + raw JSON)
  - `epics`, `user_stories`, `dev_tasks`, `test_cases`, `ambiguities` (one-to-many)
  - `chat_messages` (one-to-many)
- Free-form arrays (`acceptance_criteria`, test `steps`, raw LLM JSON) are stored in `jsonb` columns for fast querying and structural flexibility.
- Schema is owned by EF Core migrations (`SdlcCopilot.Infrastructure.Persistence.Migrations.InitialCreate`) and applied on startup; no manual SQL needed.

## Frontend

- Standalone Angular 17 app with two routes:
  - `/` — dashboard (KPIs, upload panel, table of requirements)
  - `/requirements/:id` — detail view (KPIs, summary, epics+stories, tasks, tests, ambiguities, chat assistant)
- Material components throughout; SCSS theme based on Indigo/Pink with a custom palette and rounded cards.
- All API calls go through `RequirementService` (`HttpClient`). `environment.prod.ts` uses a relative base URL so nginx can proxy `/api/*` to the .NET service in the Docker setup.

## Security / Operations

- **JWT-ready** — `Program.cs` wires bearer auth when `Jwt:Authority` is configured; otherwise endpoints are unauthenticated for hackathon use. No code changes needed to flip the switch.
- **CORS** — origins are configurable via `Cors:AllowedOrigins` (comma-separated).
- **Health** — `GET /health` on the .NET API and the FastAPI service.
- **Logging** — Serilog on the backend, Python `logging` on the AI service; both emit to stdout for container log capture.
- **Observability** — Swagger on both API surfaces makes endpoints self-documenting.
