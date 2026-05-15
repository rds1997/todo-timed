# SDLC Copilot — Presentation Deck
### PowerPoint / Google Slides Content Outline
### HackerEarth Hackathon Submission

> **How to use:** Each section below = one slide.
> Copy the title, bullets, and speaker notes into your slide tool.
> Suggested theme: dark navy background (#0F172A), accent colour #6366F1 (indigo).

---

## SLIDE 1 — Title

**Title:** SDLC Copilot

**Subtitle:** Turn raw requirements into production-ready SDLC artifacts in seconds — powered by GPT-4o

**Bottom strip (smaller text):**
HackerEarth Hackathon · May 2026 · Team: [Your Name]

**Visual:** Show app screenshot or the logo (a gear + sparkle icon)

> **Speaker notes:**
> Good [morning/afternoon] everyone. Today I'm presenting SDLC Copilot — a tool that takes the tedious manual work out of writing software requirements documentation. You paste in a paragraph of raw requirements text, click one button, and the AI hands you back a complete SDLC artifact set: epics, user stories, dev tasks, test cases, ambiguity flags, and effort estimates. Let me show you how it works.

---

## SLIDE 2 — The Problem

**Title:** Writing SDLC docs is painful — and broken

**3 pain-point columns (use icons):**

| 🐢 Slow | 🎲 Inconsistent | 🕳️ Incomplete |
|---|---|---|
| Senior engineers spend 2–3 days writing user stories for a single feature | Format, depth, and coverage vary by person and mood | Ambiguities and missing acceptance criteria slip through to dev — causing rework |

**Bottom callout box (bold):**
> "40% of software rework is caused by poorly defined requirements."
> — IBM Systems Sciences Institute

**Visual:** A chaotic Word document or a messy whiteboard sketch

> **Speaker notes:**
> Before AI tooling, a BA or senior engineer would sit down with a Word doc and manually write every user story, every acceptance criterion, every test case. For a mid-size feature, that's 2–3 days of work. The output is only as good as the person writing it — knowledge gaps and personal style mean no two people produce the same quality. And critical ambiguities often aren't caught until a developer hits them mid-sprint. SDLC Copilot solves all three of these problems.

---

## SLIDE 3 — Our Solution

**Title:** One input. A complete SDLC package.

**Centre diagram (left-to-right flow):**

```
[Raw Requirements Text]
        ↓
  [ SDLC Copilot AI ]
        ↓
┌─────────────────────────────────────────────────────┐
│  ✅ Project Summary    ✅ Epics & User Stories        │
│  ✅ Dev Tasks          ✅ Test Cases                  │
│  ✅ Ambiguity Report   ✅ Effort Estimation           │
│  ✅ AI Chat Assistant  ✅ Export (MD / JSON / CSV)    │
└─────────────────────────────────────────────────────┘
```

**Bottom tagline:**
From vague paragraph → structured, reviewable, exportable SDLC package in < 30 seconds.

> **Speaker notes:**
> You paste your raw requirement — could be one paragraph or five pages — and SDLC Copilot generates eight types of structured artifacts simultaneously. Every user story follows the "As a / I want / So that" format with acceptance criteria. Every task is tagged with a layer, complexity, and hour estimate. The system even flags ambiguities the team needs to resolve before development starts. And everything is exportable — including a Jira-compatible CSV so teams can import directly into their backlog.

---

## SLIDE 4 — Live Demo (or Screenshots)

**Title:** See it in action

**Option A — Live demo (if presenting live):**
> Switch to the app. Walk through the demo script on the next page.

**Option B — Screenshot grid (if video/static):**
Use 4 screenshots arranged in a 2×2 grid:
1. **Dashboard** — 3 requirements listed (E-Commerce, Hospital Portal, Collaboration Platform)
2. **Analysis running** — the indeterminate progress bar while AI processes
3. **Epics & Stories tab** — expanded accordion showing a user story with acceptance criteria
4. **Estimation tab** — hero cards + layer progress bars + story table

**Caption under each screenshot:** 1–2 word label (Dashboard, Analyzing, User Stories, Estimation)

> **Speaker notes:**
> [Live] I'll navigate to the app now. You'll see three real-world requirement sets already ingested — an e-commerce platform, a hospital patient portal, and a collaboration tool. I'll click into the E-Commerce one to show the full artifact set.
> [Video] This is the app running locally in Docker. You can see the dashboard listing all ingested requirements. When we click into one, we see the full analysis across seven tabs.

---

## SLIDE 5 — Feature Deep-Dive: AI Analysis

**Title:** What the AI generates — in detail

**Two-column layout:**

**LEFT — Artifacts generated:**
- **Summary** — plain-English project summary, goals, stakeholders, key constraints
- **Epics** — high-level feature groupings with descriptions
- **User Stories** — "As a [role], I want [feature], so that [benefit]" + acceptance criteria
- **Dev Tasks** — per-story implementation tasks tagged: Backend / Frontend / QA / Infra
- **Test Cases** — unit, integration, and end-to-end test definitions with steps + expected results
- **Ambiguity Flags** — Low / Medium / High severity issues with suggested resolutions
- **Estimation** — story points, hours per layer, totals

**RIGHT — Example (callout box):**
```
User Story: Persistent Shopping Cart
As a returning shopper,
I want my cart to persist across sessions,
So that I don't lose items when I close the browser.

Acceptance Criteria:
• Cart contents survive browser close + reopen
• Sync across devices when logged in
• Show "saved for later" indicator
Story Points: 5  |  Hours: 8h  |  Complexity: Medium
```

> **Speaker notes:**
> Let me walk through each artifact type. The summary section is like a BA's executive overview — it captures goals, stakeholders, and constraints. User stories follow the industry-standard Connextra format with acceptance criteria baked in. Dev tasks are already layer-tagged so you can filter by Backend, Frontend, QA — useful for capacity planning. The ambiguity report is genuinely valuable: the AI reads the requirement like a senior engineer and flags the things that would cause arguments in sprint planning. And the estimation feeds directly into project planning — you get story points and hours broken down by discipline.

---

## SLIDE 6 — Feature Deep-Dive: Estimation Tab

**Title:** Built-in project estimation — no spreadsheet needed

**Layout — use the actual Estimation tab screenshot:**
- Left: Hero cards (Total Story Points + Total Hours)
- Centre: Layer progress bars (Backend 38h / Frontend 24h / QA 20h / Infra 8h)
- Bottom: Story-by-story SP table

**Callout boxes (3 small cards on right side):**
- 🎯 **Instant** — No manual estimation poker required
- 📊 **Layer-aware** — Plan capacity per engineering discipline
- 📤 **Exportable** — Download Jira CSV, import backlog in 30 seconds

> **Speaker notes:**
> This is the feature I'm most excited to demo. Traditional estimation requires hours of planning poker sessions. Here, the moment the AI analysis completes, you have story points and hour estimates broken down by discipline. The progress bars make it immediately obvious where the bulk of the work sits — in this e-commerce example, backend is the heaviest layer. You can export this as a Jira-compatible CSV and import directly into your sprint board.

---

## SLIDE 7 — Feature Deep-Dive: AI Chat Assistant

**Title:** Ask anything about your requirement

**Screenshot:** Chat panel with 2–3 example exchanges

**Example conversation to show:**
```
👤 What are the biggest technical risks in this requirement?

🤖 Based on the analysis, the top 3 risks are:
   1. PCI-DSS compliance for payment processing — requires
      dedicated security review and likely a certified gateway
   2. Real-time inventory sync under 50k concurrent users —
      needs event-driven architecture (Kafka/Redis)
   3. Multi-currency rounding inconsistencies — define a
      canonical currency early to avoid financial discrepancies

👤 How many sprints would this take with a team of 6?

🤖 At 2-week sprints with 6 developers (mix of FE/BE/QA),
   roughly 6–8 sprints (~12–16 weeks). Backend stories are
   the critical path — recommend starting the payment
   integration in Sprint 1.
```

**Caption:** Full conversation history persisted per requirement in Postgres

> **Speaker notes:**
> Once the artifacts are generated, teams often have follow-up questions. The built-in AI chat assistant has full context of the requirement — it knows the stories, tasks, and ambiguities. You can ask it about technical risks, sprint planning, architecture choices, or anything else. Conversation history is persisted per requirement in the database, so you can come back days later and pick up where you left off.

---

## SLIDE 8 — Architecture

**Title:** Clean, containerised, production-ready architecture

**Architecture diagram (draw this in the slide tool):**

```
         Browser (Angular 17)
               │ HTTP
         ┌─────▼──────┐
         │  .NET 8    │  (ASP.NET Core REST API)
         │  API :8080 │──────── Postgres 16
         └─────┬──────┘         (requirements,
               │ HTTP           stories, chat history)
         ┌─────▼──────┐
         │  FastAPI   │  (Python AI service)
         │   :8001    │──────── GPT-4o-mini
         └────────────┘         (or mock mode)

      All services: Docker Compose  │  One command: docker compose up
```

**Legend boxes:**
- 🔵 Angular 17 standalone components + Angular Material
- 🟣 .NET 8 ASP.NET Core + Entity Framework Core + Npgsql
- 🟡 FastAPI + Pydantic v2 + httpx async + OpenAI SDK v1.5
- 🟢 Postgres 16 — full relational model, EF migrations

> **Speaker notes:**
> The architecture is deliberately simple and production-ready. A single `docker compose up` starts all four services. The Angular frontend talks to the .NET REST API, which stores everything in Postgres and delegates AI calls to a dedicated FastAPI microservice. Separating the AI service means you can swap LLM providers, scale it independently, or even run it offline with mock mode. The .NET API is the source of truth — it persists all generated artifacts relationally, so exports, chat history, and updates are durable.

---

## SLIDE 9 — Tech Stack

**Title:** Technology choices

**4-quadrant grid:**

| **Frontend** | **Backend API** |
|---|---|
| Angular 17 (standalone) | .NET 8 / ASP.NET Core |
| Angular Material (UI) | Entity Framework Core |
| TypeScript strict mode | Npgsql (Postgres driver) |
| Reactive Forms | Result<T> monad pattern |

| **AI Service** | **Infrastructure** |
|---|---|
| Python 3.12 + FastAPI | Postgres 16-alpine |
| Pydantic v2 settings | Docker + Compose |
| OpenAI SDK v1.5 (async) | Nginx (static serving) |
| GPT-4o-mini (JSON mode) | Health checks + restart policies |

**Bottom callout:**
🔒 **Mock mode** — runs fully offline with deterministic responses for CI/CD and demos

> **Speaker notes:**
> Every technology choice was made for production viability, not just hackathon speed. Angular 17's standalone component model gives us a lean bundle. .NET 8 gives us sub-millisecond API response times. The FastAPI Python service was chosen specifically because the OpenAI Python SDK is async-native and integrates cleanly with FastAPI's dependency injection. And Pydantic v2 validates every LLM response against a strict schema before it reaches the database — no surprise nulls in production.

---

## SLIDE 10 — What Makes SDLC Copilot Different

**Title:** Not just another AI wrapper

**3-column comparison:**

| Feature | Generic ChatGPT | SDLC Copilot |
|---|---|---|
| Structured output | ❌ Plain text | ✅ Validated JSON → DB |
| Persistent history | ❌ Session only | ✅ Per-requirement in Postgres |
| Edit & update artifacts | ❌ Regenerate everything | ✅ In-place CRUD per story/task |
| Export to Jira | ❌ Manual copy-paste | ✅ One-click CSV download |
| Ambiguity detection | ❌ You have to ask | ✅ Automatic with severity |
| Effort estimation | ❌ Manual | ✅ Auto + layer breakdown |
| Runs offline / CI | ❌ Always calls API | ✅ Mock mode built-in |

> **Speaker notes:**
> The key differentiator is that SDLC Copilot is a product, not a prompt. Every LLM response is validated against a Pydantic schema — if GPT returns malformed JSON, the service retries automatically. Artifacts are stored relationally, so you can update a single user story without re-running the whole analysis. The Jira CSV export means teams can go from raw requirement to populated backlog in under two minutes. And mock mode means CI/CD pipelines and demos never depend on external API availability.

---

## SLIDE 11 — Results & Impact

**Title:** What we achieved

**3 large number cards (centre of slide):**

```
  < 30 sec          8 artifact types       1 command
  to full SDLC      per requirement        docker compose up
  package           generated              to run everything
```

**Below — bullet list:**
- ✅ End-to-end working product — not a prototype or mockup
- ✅ All SDLC artifacts validated, persisted, and editable
- ✅ Jira-compatible CSV export for immediate team adoption
- ✅ Conversation history persisted — pick up any requirement days later
- ✅ Full Docker Compose deployment — reproducible on any machine
- ✅ Mock mode for offline/CI operation — production reliability built in

> **Speaker notes:**
> We built a fully working product. In under 30 seconds, a user goes from pasting raw requirement text to having a complete SDLC artifact package with epics, user stories, dev tasks, test cases, ambiguity flags, and effort estimates — all persisted in a relational database, all editable, and all exportable. The Jira CSV integration means teams can adopt this in their real workflow today, not after some future integration sprint.

---

## SLIDE 12 — Demo Script (Reference Slide — Hide Before Presenting)

**Title:** Demo walkthrough — step by step

**Steps:**

1. **Open** `http://localhost:4200` — show the dashboard with 3 requirements
2. **Point out** the list cards: E-Commerce (6 stories, 14 tasks), Hospital Portal, Collaboration Platform
3. **Click** "E-Commerce Order Management System"
4. **Show** the KPI strip: Story Points, Total Hours, Backend/Frontend split, Ambiguities
5. **Click** "Summary" tab — read the AI-generated summary aloud briefly
6. **Click** "Epics & Stories" — expand one accordion to show a full user story + acceptance criteria
7. **Click** "Tasks" — scroll through the table, point out Layer and Complexity columns
8. **Click** "Test Cases" — expand one, show steps and expected result
9. **Click** "Ambiguities" — highlight a High severity item and its suggestion
10. **Click** "Estimation" — hero cards, then hover over layer bars
11. **Click** "Export CSV" — show the downloaded file or open it in Excel
12. **Click** "Assistant" tab — type: *"What are the top 3 technical risks in this requirement?"*
13. **Show** the AI reply, then type: *"Which story has the highest implementation risk?"*
14. **Return to dashboard** — click "Hospital Patient Portal" to show breadth

**Timing:** ~4–5 minutes for full walkthrough

---

## SLIDE 13 — Roadmap

**Title:** What's next for SDLC Copilot

**Timeline (3 phases):**

**Phase 1 — Q3 2026 (Near-term)**
- [ ] GPT-4o upgrade for domain-specific depth (healthcare, fintech, e-commerce)
- [ ] File upload: PDF/DOCX requirements ingestion (already scaffolded)
- [ ] GitHub Issues export in addition to Jira CSV
- [ ] User authentication + multi-tenant workspaces

**Phase 2 — Q4 2026 (Growth)**
- [ ] Bi-directional Jira sync (import existing stories, push updates back)
- [ ] Requirement versioning — diff view between analysis runs
- [ ] Team comments and annotation on individual artifacts
- [ ] Slack bot integration for requirement submission

**Phase 3 — 2027 (Scale)**
- [ ] Custom prompt templates per organisation / domain
- [ ] Cost tracking dashboard (tokens used, per-requirement cost)
- [ ] On-premise LLM support (Ollama / Azure OpenAI)
- [ ] Automated acceptance-criteria test generation (Cucumber/Gherkin)

> **Speaker notes:**
> The foundation is solid — a production-grade full-stack system with clean separation of concerns. Near-term, the most valuable additions are GitHub export and authentication for multi-user teams. The Jira bi-directional sync in Phase 2 would make SDLC Copilot a genuine part of the enterprise SDLC workflow rather than a standalone tool. Long-term, domain-specific fine-tuning and on-premise LLM support would make this viable for regulated industries like healthcare and finance where data can't leave the corporate boundary.

---

## SLIDE 14 — Closing / Thank You

**Title:** SDLC Copilot

**Centre — 3 key takeaways:**
1. **Raw text → full SDLC package in < 30 seconds** — epics, stories, tasks, tests, estimates
2. **Production-grade architecture** — Docker, Postgres, validated LLM output, mock mode
3. **Team-ready today** — Jira CSV export, persistent chat, editable artifacts

**Links:**
- 🔗 GitHub: `github.com/rds1997/todo-timed`
- 🚀 Run locally: `git clone ... && docker compose up`

**Bottom:** Thank you — Questions?

> **Speaker notes:**
> To summarise: SDLC Copilot is a production-ready AI tool that eliminates the manual bottleneck in software requirement documentation. It's not a demo — it runs on Docker right now, it persists data in Postgres, and it exports to Jira. If your team writes SDLC documents, this tool can save them days per sprint. Happy to take questions.

---

## APPENDIX — Slide Design Tips

### Colour palette
| Use | Hex |
|---|---|
| Background | `#0F172A` (dark navy) |
| Primary accent | `#6366F1` (indigo) |
| Secondary accent | `#10B981` (emerald) |
| Warning/highlight | `#F59E0B` (amber) |
| Text primary | `#F8FAFC` (near-white) |
| Text muted | `#94A3B8` (slate-400) |

### Font suggestions
- **Headings:** Inter Bold or Poppins SemiBold
- **Body:** Inter Regular
- **Code snippets:** JetBrains Mono or Fira Code

### Icon set
Use [Heroicons](https://heroicons.com/) or [Phosphor Icons](https://phosphoricons.com/) — SVG, free, consistent style.

### Slide count
Full deck = **13 slides** (hide slide 12 during presentation, show only during demo walkthrough).

### Total presentation time
- Slides 1–3: 2 min (problem + solution)
- Live demo (slide 4): 5 min
- Slides 5–11: 5 min (features + architecture + results)
- Slides 13–14: 2 min (roadmap + close)
- Q&A: 5 min
- **Total: ~19 min** (fits a 20-min hackathon slot)
