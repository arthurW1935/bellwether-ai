# Bellwether — TRD

**ContextCon, 19 Apr 2026**
Companion to: Bellwether_PRD.md

## System architecture

```
┌──────────────────────────────────────────────────┐
│  Frontend (Next.js + Tailwind + shadcn)          │
│  /discover   /watchlist   /brief                 │
└──────────────────┬───────────────────────────────┘
                   │ REST (JSON)
┌──────────────────▼───────────────────────────────┐
│  Backend (FastAPI, async)                        │
│                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│  │ Discover │  │ Watchlist│  │ Agent        │  │
│  │ Service  │  │ Service  │  │ Orchestrator │  │
│  └─────┬────┘  └─────┬────┘  └──────┬───────┘  │
│        │             │               │          │
│  ┌─────▼─────────────▼───────────────▼───────┐  │
│  │ Crustdata Client  │  LLM Client           │  │
│  └───────────────────┬──────────────────────-┘  │
│                      │                          │
│  ┌───────────────────▼──────────────────────┐   │
│  │ State (SQLite)                           │   │
│  │ companies | snapshots | alerts           │   │
│  └──────────────────────────────────────────┘   │
└──────────────────────────────────────────────────┘
                      │
                      ▼
         Crustdata API · LLM API
```

Backend is the product. Frontend renders what the backend decides. No business logic in React.

## Stack (opinionated, pre-committed)

| Layer | Choice | Why |
|---|---|---|
| Backend | Python 3.11 + FastAPI | Async, strong LLM ecosystem, team strength |
| Storage | SQLite via SQLModel | Zero setup, persists across restarts, survives demo |
| LLM | Gemini 2.5 Flash via LiteLLM | Free tier via Google AI Studio; LiteLLM gives one-line provider swap as insurance |
| Frontend | Next.js 14 + Tailwind + shadcn/ui | Fastest path to a demo-grade UI |
| Frontend host | Vercel (free tier) | Built for Next.js, zero-config, every push auto-deploys |
| Backend host | Render (free tier) + UptimeRobot keep-alive | Free, Docker-based, browser setup; keep-alive pings prevent cold starts |
| HTTP | `httpx` async client | Parallel Crustdata calls, critical for brief-refresh latency |

No Redis, no Celery, no background workers. A single FastAPI process with async handlers is enough.

## Data model

```python
# companies
id: int           # Crustdata company_id (source of truth)
name: str
domain: str
cohort: Literal["invested", "watching"]
added_at: datetime

# snapshots — immutable state at a point in time
id: int
company_id: int
taken_at: datetime
payload: dict    # JSON blob: headcount, execs, funding, jobs, web_traffic

# alerts — interpreted deltas
id: int
company_id: int
detected_at: datetime
delta: dict                  # raw diff
alert_type: Literal["talent_poaching", "competitive", "roadmap", "health", "reopen", "routine"]
severity: Literal["P0", "P1", "P2"]  # partner / associate / noise
explanation: str             # one paragraph
recommended_action: str      # one line
reasoning_trace: list        # ordered log of API calls + LLM hops
```

Snapshots are append-only. Deltas are computed at interpretation time, not stored as first-class. Alerts are persisted.

## Crustdata endpoint map

| Bellwether feature | Crustdata calls | When |
|---|---|---|
| Seed portfolio companies | `POST /company/identify` | Startup, once |
| Discover tab search | `POST /company/search` → `POST /company/enrich` | On user query |
| Snapshot collection | `POST /company/enrich` + `POST /job/search` | Per watchlist company, on refresh |
| Exec departure chain (P1) | `POST /person/search` + `POST /person/enrich` | When delta type is `exec_departure` |
| Context for alerts (P1) | `POST /web/search/live` | Optional, for news-grounded alerts |

The full P0 path hits four Crustdata surfaces. Structural API depth, not garnish.

## Agent orchestration

**No framework.** Raw Python + `asyncio` + LiteLLM. The pipeline is linear with one conditional branch and parallel fan-out — LangGraph, CrewAI, and AutoGen solve problems we do not have (self-directed tool loops, multi-agent negotiation, checkpointing) and would obscure the reasoning trace that is our demo moment.

LiteLLM is the LLM abstraction. Gemini 2.5 Flash is the primary model (Google AI Studio free tier). If rate limits bite, one-line swap to OpenAI or another provider without touching agent code.

### Design rules

1. **Agents are stateless async functions.** Inputs in, structured outputs out. No shared state except explicit arguments.
2. **Every agent appends to a shared trace.** A `list[dict]` is passed through the call chain and captures API calls and LLM hops. This renders directly into the `/brief` reasoning expander.
3. **Structured outputs via LiteLLM tool use.** Every LLM call that returns typed data uses tool use with a strict JSON schema. Never parse freeform text for enum values.
4. **Fan out with `asyncio.gather`, capped by semaphore.** Independent operations run in parallel but limited to 8 concurrent LLM calls to stay inside Gemini free-tier rate limits. Dependent operations are sequential `await`.
5. **Every agent has a fallback.** If output validation fails, one retry, then default to the safest classification (`routine/P2`). No pipeline halts on a single bad response.

### The graph

```
refresh()
  ├─ gather(collect_snapshot(co) for co in watchlist)     # parallel
  │     └─ gather(/company/enrich, /job/search)           # parallel per co
  ├─ for each co: detect_deltas(today, prior)             # pure Python, fast
  ├─ gather(interpret(d, cohort) for d in all_deltas)     # parallel
  │     ├─ if exec_departure: chain_destination(d)        # P1, sequential
  │     ├─ classify(d, cohort, context)                   # LLM call 1
  │     └─ write(d, classification, cohort)               # LLM call 2
  └─ summarize_brief(all_alerts)                          # LLM call 3, final
```

### The seven agents

| # | Agent | Purpose | Input | Tool | Output |
|---|---|---|---|---|---|
| 1 | Query Parser | NL thesis → Crustdata filters | User query | LLM w/ tool schema | `CompanyFilters` |
| 2 | Snapshot Collector | Current state of one company | company_id | `/company/enrich` + `/job/search` | `Snapshot` |
| 3 | Delta Detector | Diff two snapshots | today, prior | Pure Python | `list[Delta]` |
| 4 | Destination Chain (P1) | Resolve where a departed exec went | Delta (exec_departure) | `/person/search` + `/person/enrich` + LLM | Delta + destination |
| 5 | Classifier | Alert type + severity | Delta, cohort, context | LLM w/ tool schema | `{alert_type, severity, rationale}` |
| 6 | Writer | Explanation + recommended action | Delta, classification, cohort | LLM freeform (≤100 words) | `{explanation, action}` |
| 7 | Brief Summarizer | Exec summary across all alerts | `list[Alert]` | LLM freeform (≤3 sentences) | Summary string |

### Model choice

Single model: **Gemini 2.5 Flash** via LiteLLM for all three LLM roles (Classifier, Writer, Brief Summarizer). Fast, cheap, free-tier. Tool use and JSON mode supported.

If the brief summary quality is weak, optionally upgrade that one call to Gemini 2.5 Pro — same provider, same key, one-line change. Do this only if P0 ships with time to spare.

Concurrency is capped at 8 parallel LLM calls via `asyncio.Semaphore(8)` to stay inside free-tier rate limits.

### Latency budget (10 companies, ~30 deltas)

| Stage | Time |
|---|---|
| Snapshot collection (parallel Crustdata calls) | ~2s |
| Delta detection | ~50ms |
| Classification (30 calls, 8-concurrency) | ~6s |
| Writing (30 calls, 8-concurrency) | ~8s |
| Destination chain (sequential per departure) | +1.5s each |
| Brief summary (single call) | ~2s |
| **Total** | **~18s worst case** |

The demo's live-trigger button runs one delta end-to-end in ~3s, which is the user-facing path that matters. Full refresh is pre-computed before the Loom begins.

### Classifier prompt (structure)

```
You are an analyst for a VC partner. A signal was detected on a company
in their {cohort} cohort.

Cohort meanings:
- invested: partner has put money in; alerts are about risk and value
- watching: partner passed or is tracking; alerts are about reasons to
  reopen the conversation

Signal: {delta}
Company context: {company_state}
If destination resolved: {destination_context}

Classify into exactly one alert_type from:
  talent_poaching, competitive, roadmap, health, reopen, routine

Assign severity:
  P0 — partner should see this today
  P1 — associate can triage this week
  P2 — noise, do not surface

Return as tool call: {alert_type, severity, rationale}
```

Cohort-awareness is the key. The same signal ("headcount +15% in 30 days") is `reopen/P0` for a Watching company and `routine/P2` for an Invested company already known to be scaling. The cohort label sits in the prompt; the model does the rest.

### Trace format

Every entry on the trace list:

```python
{
  "stage": "classifier",
  "timestamp": "2026-04-19T13:22:04Z",
  "inputs": {...},
  "tool_calls": [{"name": "...", "args": {...}}],
  "llm_output": {...},
  "duration_ms": 420
}
```

Rendered in the `/brief` expander as a vertical timeline. The visible proof of agentic orchestration.

## Frontend architecture

Three routes, one shared API client.

- `/discover` — single-input chat box, streams results as they enrich. Each result card has an **Add to Watching** button.
- `/watchlist` — tab toggle Invested | Watching. Grid of company cards showing key fields from the latest snapshot. Click a card to see its alert history.
- `/brief` — the hero. Exec summary at top (LLM-written), then alerts grouped by severity, color-coded by cohort. Each alert has a **Show reasoning** expander that renders the `reasoning_trace` as a step list: API calls on the left, LLM outputs on the right.

Keep it boring. No animations, no complex state. `useSWR` for data fetching, server components where possible.

## Demo-critical engineering

Two things must work on camera. Everything else is polish.

**1. Guaranteed-interesting deltas.** For the 6–10 seed companies, hand-craft a "30 days ago" snapshot with 3–5 compelling deltas pre-seeded. Store in `seed/prior_snapshots.py`. This is the difference between a demo that works and one that doesn't — real Crustdata historical diffs are unpredictable.

**2. The live-trigger button.** In `/brief`, a "Simulate new signal" button posts a pre-staged delta through the real pipeline. The user sees the agent process it on camera — detector → classifier → writer — and a new alert card appears. It is the real pipeline running a staged input, not a fake animation. Never stage the output.

## Deployment

Deploy on hour one, not hour five. Every commit after setup ships to the environment the judges will see. Leaving deploy for the end means debugging CORS while recording the Loom.

### Chosen stack (fully free)

| Piece | Host | Why |
|---|---|---|
| Frontend (Next.js) | **Vercel**, free tier | Built by the Next.js team; GitHub connect; HTTPS; every push ships |
| Backend (FastAPI) | **Render**, free tier | Docker-based, browser setup, auto-deploys from GitHub |
| Keep-alive | **UptimeRobot**, free | Pings `/health` every 5 minutes so Render never spins down during the event |
| Storage | SQLite, ephemeral | Seeded from code at startup; persists for the container's lifetime |

### Setup sequence (first 30 minutes)

1. Create GitHub repo. Push a minimal FastAPI + Next.js hello-world so both services have something to build.
2. Vercel: connect repo, point at `frontend/`. Auto-builds on push.
3. Render: connect repo, point at `backend/` with a Dockerfile. Auto-builds on push.
4. Set env vars in both dashboards: `GEMINI_API_KEY`, `CRUSTDATA_API_KEY`, `CORS_ORIGINS` (the Vercel URL).
5. UptimeRobot: create an HTTP monitor pinging `<render-url>/health` every 5 minutes. Done.
6. Verify: frontend can hit `GET /health` on the backend over HTTPS.

After this gate, every commit validates the full pipeline in the deployed environment.

### Minimum backend Dockerfile

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### CORS (the one thing that always bites)

FastAPI blocks cross-origin requests by default. Add this on minute one:

```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("CORS_ORIGINS", "*")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Wildcards are fine during the hackathon. Tighten only if there is time at the end.

### State caveat

SQLite on Render is ephemeral — the disk resets on redeploy. Fine for the demo: the Invested cohort seeds from code at startup, and user additions last the container's lifetime. Do not redeploy during the Loom recording window.

## Directory structure

```
bellwether/
├── backend/
│   ├── main.py                 # FastAPI entrypoint
│   ├── crustdata.py            # Async client, all endpoints
│   ├── llm.py                  # LiteLLM wrapper (Gemini Flash primary)
│   ├── state/
│   │   ├── db.py               # SQLite + SQLModel
│   │   └── models.py           # Company, Snapshot, Alert
│   ├── agent/
│   │   ├── detector.py         # Pure-function diff
│   │   ├── classifier.py       # LLM classification
│   │   ├── chain.py            # Exec destination (P1)
│   │   └── writer.py           # Explanation + action
│   ├── prompts/
│   │   ├── classifier.md
│   │   └── writer.md
│   └── seed/
│       ├── portfolios.py       # Judge-fund companies
│       └── prior_snapshots.py  # Hand-crafted "yesterday"
├── frontend/
│   ├── app/
│   │   ├── discover/page.tsx
│   │   ├── watchlist/page.tsx
│   │   └── brief/page.tsx
│   ├── components/
│   │   ├── CompanyCard.tsx
│   │   ├── AlertCard.tsx
│   │   └── ReasoningTrace.tsx
│   └── lib/api.ts
└── README.md
```

## Build sequence (5-hour window, team of 3–4)

Adjust splits once team size is confirmed. This assumes 3 people.

| Time | Backend + Agent | Frontend | Demo + Data |
|---|---|---|---|
| 11:00–11:30 | Repo + Dockerfile + Render wired | Next.js scaffold + Vercel wired | Crustdata coverage validation + judge-fund research |
| 11:30–12:30 | Crustdata client + state layer + seed load | `/watchlist` skeleton rendering seed data | Hand-craft prior snapshots |
| 12:30–13:30 | Detector + classifier (cohort-aware) | `/brief` layout + AlertCard | Classifier prompt iteration w/ backend |
| 13:30–14:30 | Writer + full pipeline end-to-end | `/discover` chat input + results | Live-trigger wiring |
| 14:30–15:15 | P1: exec destination chain | `ReasoningTrace` component | Loom script, seed-data finalization |
| 15:15–16:00 | Integration, bug triage | Polish pass on `/brief` | Record Loom, submit |

Hard stop on P1 at 14:30 if P0 is not fully integrated.

## Technical risks

1. **Crustdata coverage on judge-fund portfolio.** *Mitigation:* validate in the first 30 min; keep a fallback list of well-covered Indian startups ready.
2. **LLM latency stacking.** 30 deltas × 2 LLM calls each = 60 calls. *Mitigation:* `asyncio.gather`; Haiku or Sonnet for classification, Sonnet for the brief summary only.
3. **Unstructured LLM output breaking the pipeline.** *Mitigation:* tool-use / JSON mode with a strict schema; one retry on validation failure, then fall back to `routine/P2`.
4. **Snapshot drift between companies.** *Mitigation:* snapshot per company is independent; never cross-reference.
5. **Live-trigger fails on camera.** *Mitigation:* record a local backup Loom before the live demo starts; worst case, ship the backup.
6. **Deploy pipeline breaks at hour 4.** *Mitigation:* Vercel + Render wired on minute one; every commit validates. If prod breaks, localhost is always the fallback for the Loom.
7. **CORS blocks frontend → backend calls.** *Mitigation:* wildcard origins from the first commit; tighten only if time allows.
8. **Container restarts mid-demo and drops in-memory state.** *Mitigation:* do not redeploy during the Loom recording window; seed data is deterministic from code.
9. **UptimeRobot ping fails, Render spins down.** *Mitigation:* verify the first ping lands; keep the Render dashboard open during demo prep for instant wake if needed.
