# SDLC Copilot — Demo Recording Script
### Target length: 3–5 minutes | Format: Screen recording with narration

---

## Before you hit Record

**Setup checklist:**
- [ ] Run `docker compose up` — all 4 containers healthy (postgres, ai-service, api, frontend)
- [ ] Open browser: `http://localhost:4200`
- [ ] Set browser zoom to 90% (more screen real estate)
- [ ] Close all other tabs / notifications
- [ ] Hide taskbar / dock (full-screen or presentation mode)
- [ ] Set screen resolution: 1920×1080 if possible
- [ ] Microphone test: record 10 seconds, play back — check levels

**Demo data already seeded in the DB:**
1. E-Commerce Order Management System ← start here
2. Hospital Patient Portal
3. Real-Time Collaboration Platform

---

## Scene 1 — Dashboard (0:00–0:30)

**Screen:** `http://localhost:4200` — the requirements dashboard

**Narration:**
> "This is SDLC Copilot — an AI-powered tool that transforms raw software requirements into a complete, structured SDLC artifact package.
>
> On the dashboard, you can see three real-world requirements already ingested — an e-commerce platform, a hospital patient portal, and a real-time collaboration tool. Each card shows the current status and a count of generated artifacts."

**Mouse action:** Slowly pan across the 3 requirement cards.

---

## Scene 2 — Paste a new requirement (0:30–1:10)

**Screen:** Click the "+ New Requirement" or text input area

**Narration:**
> "Let me show you how easy it is to add a new requirement. I'll paste in a raw description — exactly the kind of paragraph a product manager or stakeholder might send in an email."

**Action:** Paste this text into the title and body:
- Title: `Mobile Banking App`
- Body:
```
We need a mobile banking app for retail customers.
Users should be able to check account balances, transfer funds between accounts,
pay utility bills, view transaction history for the last 12 months,
set spending alerts, and block/unblock their debit card.
The app must support biometric login (Face ID / fingerprint),
work offline for balance viewing, and comply with PCI-DSS and RBI guidelines.
```

**Narration:**
> "I hit Submit — the requirement is ingested immediately. Now I'll click 'Analyze with AI'."

**Action:** Click Analyze. Show the indeterminate progress bar.

> "In about 20 seconds, the AI reads this requirement and generates the full SDLC package."

---

## Scene 3 — Summary Tab (1:10–1:40)

**Screen:** Summary tab of the Mobile Banking App requirement (or switch to E-Commerce which is pre-populated)

**Narration:**
> "The Summary tab gives us an AI-generated project overview: the goals, stakeholders, and key constraints. This is the kind of document a BA would spend half a day writing — done in seconds."

**Mouse action:** Scroll slowly through the summary content. Point at "stakeholders" and "key constraints" sections.

---

## Scene 4 — Epics & User Stories (1:40–2:20)

**Screen:** Click "Epics & Stories" tab

**Narration:**
> "The Epics and User Stories tab organises the work into feature groups. Each epic expands to show its user stories."

**Action:** Click to expand one story accordion (e.g., "Shopping Cart" or "Account Management").

> "Every story follows the industry-standard format: 'As a [role], I want [feature], so that [benefit]' — with acceptance criteria pre-written. These are immediately ready to paste into Jira."

**Mouse action:** Read one story's acceptance criteria aloud.

---

## Scene 5 — Dev Tasks (2:20–2:40)

**Screen:** Click "Tasks" tab

**Narration:**
> "The Tasks tab breaks each story into concrete development tasks. Each task is tagged with a layer — Backend, Frontend, QA, or Infra — along with an hour estimate and complexity level. This is your sprint backlog, pre-populated."

**Mouse action:** Hover over a row to highlight. Point to the Layer and Hours columns.

---

## Scene 6 — Ambiguities (2:40–3:00)

**Screen:** Click "Ambiguities" tab

**Narration:**
> "The Ambiguities tab is where SDLC Copilot really earns its keep. The AI reads the requirement like a senior engineer and flags the things that would cause arguments in sprint planning."

**Action:** Click to expand or highlight a High severity ambiguity.

> "Each flag includes the specific excerpt that's ambiguous, the issue it causes, and a concrete suggestion to resolve it. This prevents costly rework down the line."

---

## Scene 7 — Estimation Tab (3:00–3:30)

**Screen:** Click "Estimation" tab

**Narration:**
> "The Estimation tab gives you instant project planning data — total story points, total hours, and a breakdown by engineering discipline."

**Mouse action:** Point at the hero cards, then trace each progress bar.

> "In this example, backend is the heaviest investment at 38 hours. Frontend, QA, and Infra are shown proportionally. Below that, every individual user story has its own story point and hour estimate."

> "All of this used to take a half-day estimation poker session. Now it takes 20 seconds."

---

## Scene 8 — AI Chat (3:30–4:00)

**Screen:** Click "Assistant" tab

**Action:** Type this message: `What are the top 3 technical risks in this requirement?`

**Narration (while waiting for response):**
> "The built-in AI assistant has full context of this requirement — it knows the stories, tasks, and ambiguities. You can ask it anything."

**After response appears:**
> "Notice it gives specific, contextual answers — not generic advice. The conversation is persisted per requirement in the database, so you can return to this thread days later."

---

## Scene 9 — Export CSV (4:00–4:20)

**Screen:** Click the "Export CSV" button in the header

**Narration:**
> "Finally — the Jira export. One click downloads a CSV in Jira's import format: epics, stories, sub-tasks with all the fields Jira expects."

**Action:** Show the download or open the CSV file briefly.

> "A team can go from pasting raw requirements to having a populated Jira backlog in under two minutes."

---

## Scene 10 — Close (4:20–4:40)

**Screen:** Navigate back to dashboard, show all 3 requirements

**Narration:**
> "SDLC Copilot is a fully working, Docker-deployed product. One command to run — `docker compose up`. All artifacts persisted in Postgres. Works with GPT-4o-mini or fully offline in mock mode for demos and CI pipelines.
>
> Turn raw requirements into a production-ready SDLC package — in under 30 seconds. Thank you."

---

## Recording Tips

| Tip | Detail |
|---|---|
| **Pace** | Speak slower than feels natural — nerves speed you up |
| **Cursor** | Move the mouse slowly and intentionally — no rapid zigzagging |
| **Pauses** | Pause 1 second before clicking a new tab — gives watchers time to read |
| **Re-do sections** | Record in sections, not one long take — easier to re-do a bad section |
| **Tool** | OBS Studio (free) or Windows Game Bar (Win+G) for recording |
| **Editing** | DaVinci Resolve (free) or CapCut — cut dead air and stumbles |
| **Background music** | Optional: low-energy lo-fi track at 10% volume underneath narration |

---

## Suggested Title Cards (add in video editor)

- `0:00` — **"SDLC Copilot"** (logo + tagline)
- `0:30` — **"Step 1: Paste your requirement"**
- `1:10` — **"Instant AI Analysis"**
- `1:40` — **"Epics & User Stories"**
- `2:20` — **"Dev Tasks"**
- `2:40` — **"Ambiguity Detection"**
- `3:00` — **"Effort Estimation"**
- `3:30` — **"AI Chat Assistant"**
- `4:00` — **"Jira CSV Export"**
- `4:20` — **"Built on: Angular · .NET · FastAPI · Postgres · GPT-4o"**
