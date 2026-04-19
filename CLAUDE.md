# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Bellwether is an AI-powered VC portfolio intelligence assistant. It collects raw signals (exec departures, fundraising, hiring pivots), detects deltas from prior state, classifies them through an LLM with cohort-awareness, and surfaces high-signal alerts to VC partners. Built for ContextCon hackathon (April 19, 2026).

## Planned Stack

| Layer | Tool |
|---|---|
| Backend | Python 3.11 + FastAPI (async) |
| Frontend | Next.js 14 + Tailwind + shadcn/ui |
| LLM | Gemini 2.5 Flash via LiteLLM |
| Storage | SQLite + SQLModel |
| Deploy | Vercel (frontend) + Render (backend) |

## Commands

### Backend (once `backend/` exists)
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

### Frontend (once `frontend/` exists)
```bash
cd frontend
npm install
npm run dev       # http://localhost:3000
npm run build
npm run lint
```

### Environment Variables
```
GEMINI_API_KEY=...
CRUSTDATA_API_KEY=...
CORS_ORIGINS=http://localhost:3000
```

## Planned Directory Structure

```
bellwether-ai/
├── backend/
│   ├── main.py               # FastAPI app, all 10 REST endpoints
│   ├── crustdata.py          # Crustdata API client
│   ├── llm.py                # LiteLLM wrapper, semaphore(8) concurrency cap
│   ├── state/
│   │   ├── db.py             # SQLite engine + session
│   │   └── models.py         # SQLModel tables: companies, snapshots, alerts
│   ├── agent/
│   │   ├── detector.py       # Pure-Python delta diffing
│   │   ├── classifier.py     # Classifier LLM agent
│   │   ├── chain.py          # Orchestrator: runs all 7 agents in sequence
│   │   └── writer.py         # Writer + Brief Summarizer LLM agents
│   ├── prompts/              # Markdown prompt templates
│   ├── seed/                 # Pre-staged demo data (portfolios, 30-day-old snapshots)
│   ├── requirements.txt
│   └── Dockerfile
└── frontend/
    ├── app/
    │   ├── discover/page.tsx
    │   ├── watchlist/page.tsx
    │   └── brief/page.tsx
    ├── components/
    │   ├── CompanyCard.tsx
    │   ├── AlertCard.tsx
    │   └── ReasoningTrace.tsx
    └── lib/api.ts             # All fetch calls to backend
```

## Architecture

### Data Flow
1. `/discover`: NL query → Query Parser LLM extracts filters → Crustdata search → enriched results
2. User adds company to watchlist with cohort label (`invested` or `watching`)
3. `/refresh` (manual or daily): for each watchlist company → Snapshot Collector (Crustdata) → Delta Detector (pure Python diff vs prior snapshot) → Classifier LLM (per delta) → Writer LLM (explanation + action) → Brief Summarizer
4. `/brief`: returns alerts sorted P0 → P1 → P2, grouped by cohort, each with `reasoning_trace`

### Seven Stateless Async Agents
1. **Query Parser** — NL → Crustdata filter params
2. **Snapshot Collector** — parallel Crustdata calls (headcount, execs, funding, jobs)
3. **Delta Detector** — pure Python; no LLM; diffs today vs prior snapshot
4. **Destination Chain** — routes deltas to classifier
5. **Classifier** — tool-use call returning `{type, severity, cohort_context}`; cohort-aware prompt
6. **Writer** — tool-use call returning `{headline, explanation, suggested_action}`
7. **Brief Summarizer** — writes exec summary across all alerts

### Key Design Decisions

**No agentic framework** — raw `asyncio` + LiteLLM only. Linear pipeline with parallel fan-out. More transparent for hackathon demo than LangGraph/CrewAI.

**Tool use for structured output** — all LLM calls returning typed data use tool use with strict JSON schema, never parse freeform text for enums. On validation failure: one retry, then default to `routine/P2`. Pipeline never halts on bad LLM output.

**Cohort-aware classification** — the same signal ("headcount +15%") classifies differently for `invested` vs `watching` companies. This logic is baked into the classifier prompt, not post-processed.

**Reasoning trace as first-class output** — every pipeline step (API call, LLM hop, duration) is appended to an ordered `reasoning_trace` list, persisted on each alert, and rendered in the UI as a step-by-step timeline.

**Seed data for guaranteed demo** — `seed/prior_snapshots.py` contains snapshots dated ~30 days ago with pre-staged compelling deltas. The live `/trigger` endpoint posts a staged delta through the real pipeline (not a mock animation).

**Snapshots are immutable** — append-only state blobs. Deltas are computed at interpretation time. Only interpreted alerts are persisted.

**Latency budget** — ~18s worst case for 10-company full refresh: 2s Crustdata + 50ms detector + 6s classify (30 calls @ semaphore(8)) + 8s write + 2s summarize. Single live-trigger delta: ~3s.

**Frontend is dumb** — all business logic in backend. Frontend renders structured API output with `useSWR`.

## API Contract

10 REST endpoints — full specs in [API_Contract.md](API_Contract.md):

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Liveness check |
| GET | `/discover` | NL company search |
| GET | `/watchlist` | All watchlist companies |
| POST | `/watchlist` | Add company to cohort |
| DELETE | `/watchlist/{id}` | Remove company |
| POST | `/refresh` | Full pipeline run |
| GET | `/brief` | Latest brief + alerts |
| GET | `/brief/alerts/{id}` | Single alert with trace |
| POST | `/trigger` | Live demo: inject pre-staged delta |
| GET | `/snapshot/{id}` | Raw snapshot for a company |

## Reference Docs

- [Bellwether_PRD.md](Bellwether_PRD.md) — product scope, P0 vs P1 features, target user
- [Bellwether_TRD.md](Bellwether_TRD.md) — full technical design, build sequence, latency analysis
- [API_Contract.md](API_Contract.md) — locked type definitions and endpoint specs with mock responses
