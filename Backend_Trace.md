# Backend Trace

**Project:** Bellwether
**Last updated:** April 19, 2026
**Purpose:** This is the canonical backend handoff file. It tracks:

- the backend plan
- architectural decisions
- what was implemented in each chat
- current status
- next steps

If another LLM or engineer picks up this repo, they should read this file first.

## Working Agreement

After every meaningful backend implementation change, append a new entry to the `Implementation Log` section instead of rewriting history. Keep older entries intact so future contributors can reconstruct why the backend looks the way it does.

Each new entry should include:

- `Date`
- `Chat scope`
- `What changed`
- `Files touched`
- `What is now testable`
- `Open gaps / next move`

## Monorepo Layout

This repo is planned as a standard app-first monorepo:

```text
apps/
  web/    # frontend
  api/    # backend
```

Current backend location:

- `apps/api`

## Backend Goal

Bellwether backend is responsible for:

- thesis-based company discovery
- watchlist management across `invested` and `watching`
- snapshot collection
- delta detection
- alert generation
- brief generation
- traceability for why each alert was produced

The frontend should render backend decisions, not own business logic.

## Verified Product Shape

The repo PRD/TRD define three P0 user-facing surfaces:

1. `Discover`
   Natural-language thesis to company results
2. `Watchlist`
   Cohort-aware company monitoring
3. `Brief`
   Ranked alerts with reasoning trace

## Verified Crustdata Context

Based on the Crustdata public docs reviewed on April 19, 2026, the backend plan is grounded in these surfaces:

| Area | Verified surface | Intended Bellwether use |
|---|---|---|
| Company search | `POST /screener/company/search` | Discover |
| Company enrich | `GET /screener/company` | Company cards, snapshots |
| Company screening | `POST /screener/screen/` | Fallback / bulk lookup |
| Person search | `POST /screener/person/search` | P1 exec tracking |
| Person enrich | `GET /screener/person/enrich` | P1 exec tracking |
| Web APIs | Search/fetch web content | Optional P1 context |

Important constraints captured earlier:

- Crustdata docs say some Company and Person live workflows are enterprise-only or plan-specific.
- Auth examples in docs are inconsistent between `Bearer` and `Token`.
- Company enrichment supports `fields`, so payload shaping should happen centrally in the adapter.

## Current Architecture

The backend currently uses this shape:

```text
apps/api/
  app/
    api/routes/
    clients/
    core/
    providers/
    repositories/
    schemas/
    services/
```

High-level responsibilities:

- `api/routes`: HTTP routes
- `core`: config, DB bootstrap, error handling
- `clients`: future live integrations like Crustdata and LLM
- `providers`: current mock provider path for deterministic testing
- `repositories`: SQLite persistence
- `schemas`: request/response and domain models
- `services`: business logic and orchestration

## Current Implementation Status

### Implemented

- FastAPI service scaffold
- shared config via env vars
- CORS setup
- flat JSON error responses
- SQLite initialization
- persisted companies, watchlist entries, snapshots, alerts, and brief runs
- deterministic mock provider for company search and state changes
- seeded demo watchlist on startup
- Discover API using mock provider
- Watchlist add/remove/list using persistence
- Refresh flow that:
  - reads watchlist companies
  - loads prior snapshot
  - creates a new snapshot
  - detects deltas
  - writes alerts
  - stores a brief run
- Brief retrieval with severity filtering
- Company alert history
- Staged trigger endpoint for demo flows

### Not Yet Implemented

- live Crustdata HTTP calls
- NL query to real Crustdata filter generation
- live company enrichment mapping
- LLM-backed classifier/writer
- real person enrichment and exec destination chain
- production-grade retries, observability, and test suite

## Current API Surface

Implemented routes:

- `GET /health`
- `POST /discover`
- `GET /watchlist`
- `POST /watchlist/add`
- `POST /watchlist/remove`
- `GET /brief`
- `POST /refresh`
- `POST /trigger`
- `GET /companies/{company_id}/alerts`

## Current Testing Mode

The backend is currently designed to be testable immediately in deterministic mock mode.

That means:

- a frontend can be built against the current API contract now
- seeded companies appear on startup
- `discover` returns stable mock results
- `refresh` generates consistent deltas and alerts
- `trigger` produces demo-safe staged alerts

This is intentional so the product can behave end to end before live upstream integrations are complete.

## Implementation Log

### Entry 1

- `Date`: April 19, 2026
- `Chat scope`: Convert repo thinking into a backend-specific monorepo plan grounded in Crustdata docs
- `What changed`:
  - established monorepo-standard app names: `apps/web` and `apps/api`
  - created the initial backend planning document
  - documented verified Crustdata surfaces, backend architecture, data model direction, and phased delivery plan
- `Files touched`:
  - `README.md`
  - `Backend_Trace.md`
  - `apps/api/.gitkeep`
  - `apps/web/.gitkeep`
- `What is now testable`:
  - repo structure and planning only
- `Open gaps / next move`:
  - scaffold `apps/api` into a real FastAPI backend

### Entry 2

- `Date`: April 19, 2026
- `Chat scope`: Create the backend scaffold
- `What changed`:
  - created the FastAPI app skeleton
  - added route modules for `health`, `discover`, `watchlist`, `brief`, and `companies`
  - added typed schemas for watchlist, discover, brief, alerts, and common enums
  - added initial in-memory sample-data services
  - added JSON error normalization
  - added `pyproject.toml`
- `Files touched`:
  - `apps/api/pyproject.toml`
  - `apps/api/app/main.py`
  - `apps/api/app/api/routes/*`
  - `apps/api/app/core/config.py`
  - `apps/api/app/core/errors.py`
  - `apps/api/app/schemas/*`
  - `apps/api/app/services/sample_data.py`
  - `apps/api/app/services/discover_service.py`
  - `apps/api/app/services/watchlist_service.py`
- `What is now testable`:
  - API shapes and route wiring at the file level
- `Open gaps / next move`:
  - wire env config fully and define client boundaries

### Entry 3

- `Date`: April 19, 2026
- `Chat scope`: Wire environment config and client boundaries
- `What changed`:
  - created `apps/api/.env.example`
  - expanded settings to include Crustdata, LLM, DB, provider mode, and logging variables
  - added typed Crustdata and LLM client skeletons
  - added shared Crustdata field allowlists
  - connected discover/watchlist services to the client boundary
  - fixed packaging to include all `app*` packages
- `Files touched`:
  - `apps/api/.env.example`
  - `apps/api/app/core/config.py`
  - `apps/api/app/clients/crustdata.py`
  - `apps/api/app/clients/llm.py`
  - `apps/api/app/services/crustdata_fields.py`
  - `apps/api/app/services/discover_service.py`
  - `apps/api/app/services/watchlist_service.py`
  - `apps/api/pyproject.toml`
- `What is now testable`:
  - env-driven configuration and client setup boundaries
- `Open gaps / next move`:
  - move from scaffold to a genuinely testable backend slice

### Entry 4

- `Date`: April 19, 2026
- `Chat scope`: Implement a testable end-to-end backend slice in mock mode
- `What changed`:
  - added SQLite persistence and schema initialization
  - added repository layer for companies, watchlist entries, snapshots, alerts, and brief runs
  - added deterministic mock provider with:
    - search results
    - seeded companies
    - prior/current snapshots
    - staged demo deltas
  - added startup bootstrap service to initialize DB and seed the watchlist
  - replaced in-memory watchlist behavior with persistent storage
  - implemented delta detection and alert generation logic
  - implemented brief assembly and company alert history
  - implemented `POST /refresh` and `POST /trigger`
  - corrected route paths so `refresh` and `trigger` are root-level endpoints, matching the API contract
- `Files touched`:
  - `apps/api/app/core/db.py`
  - `apps/api/app/repositories/storage.py`
  - `apps/api/app/providers/mock_provider.py`
  - `apps/api/app/services/bootstrap_service.py`
  - `apps/api/app/services/clock.py`
  - `apps/api/app/services/alert_engine.py`
  - `apps/api/app/services/brief_service.py`
  - `apps/api/app/services/refresh_service.py`
  - `apps/api/app/services/discover_service.py`
  - `apps/api/app/services/watchlist_service.py`
  - `apps/api/app/api/routes/brief.py`
  - `apps/api/app/api/routes/companies.py`
  - `apps/api/app/main.py`
  - `apps/api/app/schemas/brief.py`
  - `apps/api/.env.example`
- `What is now testable`:
  - seeded watchlist behavior
  - discover responses
  - adding/removing companies
  - refresh-driven snapshot and alert creation
  - brief retrieval
  - per-company alert history
  - staged trigger flows
- `Open gaps / next move`:
  - swap mock provider paths for real Crustdata-backed flows while preserving the same API contract

## How To Continue From Here

If another LLM continues this work, the safest next sequence is:

1. Replace mock `discover` with real Crustdata company search plus enrich.
2. Replace mock company fetch in watchlist add with real Crustdata enrichment.
3. Keep SQLite and the current API contract unchanged while swapping providers.
4. Add a provider abstraction so mock and live mode can coexist cleanly.
5. After live data works, replace rule-based alert writing/classification with LLM-backed classification and generation.

## Current Risks

1. The backend is functionally testable, but still mock-data-backed.
2. Crustdata auth/header behavior is not fully validated yet.
3. Runtime verification was not completed in this environment because the local Python launcher returned an access-denied error.
4. No automated tests have been written yet.

## Important Files To Read Next

- [README.md](README.md)
- [Bellwether_PRD.md](Bellwether_PRD.md)
- [Bellwether_TRD.md](Bellwether_TRD.md)
- [main.py](apps/api/app/main.py)
- [config.py](apps/api/app/core/config.py)
- [storage.py](apps/api/app/repositories/storage.py)
- [mock_provider.py](apps/api/app/providers/mock_provider.py)
- [watchlist_service.py](apps/api/app/services/watchlist_service.py)
- [refresh_service.py](apps/api/app/services/refresh_service.py)
- [brief_service.py](apps/api/app/services/brief_service.py)
