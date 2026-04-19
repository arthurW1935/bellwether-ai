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
- live-provider path for Crustdata-backed discover and company enrichment
- Watchlist add/remove/list using persistence
- LiteLLM-backed Gemini structured-output path for query parsing and alert generation
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

- real person enrichment and exec destination chain
- production-grade retries, observability, and test suite
- runtime validation of the live Crustdata field mappings against a real account
- richer live snapshot extraction beyond the current minimal headcount/funding/jobs mapping

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

### Entry 5

- `Date`: April 19, 2026
- `Chat scope`: Start integrating live Crustdata and a real LLM while preserving mock fallback
- `What changed`:
  - added real Crustdata HTTP request execution in the shared client
  - added a live provider for:
    - Crustdata-backed discover search
    - live company enrichment on watchlist add
    - live current snapshot fetch on refresh
  - added provider resolution so the app can switch between mock and live mode based on config
  - added a direct LLM integration path for structured JSON outputs
  - added LLM-backed query parsing for discover filter generation, with heuristic fallback
  - added LLM-backed alert classification and writing, with rule-based fallback
  - added `503 upstream_unavailable` handling on discover, watchlist add, and refresh
- `Files touched`:
  - `apps/api/app/core/config.py`
  - `apps/api/.env.example`
  - `apps/api/app/clients/crustdata.py`
  - `apps/api/app/clients/llm.py`
  - `apps/api/app/providers/live_provider.py`
  - `apps/api/app/providers/provider_resolver.py`
  - `apps/api/app/services/query_parser.py`
  - `apps/api/app/services/llm_analysis_service.py`
  - `apps/api/app/services/discover_service.py`
  - `apps/api/app/services/watchlist_service.py`
  - `apps/api/app/services/bootstrap_service.py`
  - `apps/api/app/services/refresh_service.py`
  - `apps/api/app/services/alert_engine.py`
  - `apps/api/app/providers/mock_provider.py`
  - `apps/api/app/api/routes/discover.py`
  - `apps/api/app/api/routes/watchlist.py`
  - `apps/api/app/api/routes/brief.py`
- `What is now testable`:
  - mock mode still works as before
  - live discover can be exercised when Crustdata and LLM keys are configured and mock mode is disabled
  - watchlist add can use live company enrichment in that same mode
  - refresh can fetch live current company state and use a real LLM for alert text and classification
- `Open gaps / next move`:
  - validate the live Crustdata field mappings against a real account
  - improve live snapshot richness and key executive extraction
  - add automated integration tests around mock vs live mode selection

### Entry 6

- `Date`: April 19, 2026
- `Chat scope`: Switch the real LLM integration from OpenAI-specific code to LiteLLM with Gemini
- `What changed`:
  - removed the OpenAI-specific LLM config assumptions
  - switched backend LLM config to use:
    - LiteLLM as the client library
    - a Gemini API key from `BELLWETHER_GEMINI_API_KEY`
    - default model `gemini/gemini-1.5-flash`
  - replaced the direct OpenAI Responses client with LiteLLM chat-completion based JSON generation
  - updated the backend trace to reflect that the intended real LLM stack is LiteLLM + Gemini, not OpenAI
- `Files touched`:
  - `apps/api/pyproject.toml`
  - `apps/api/app/core/config.py`
  - `apps/api/.env.example`
  - `apps/api/app/clients/llm.py`
  - `Backend_Trace.md`
- `What is now testable`:
  - mock mode still works unchanged
  - real LLM mode now expects a Gemini key and LiteLLM-backed Gemini model configuration
- `Open gaps / next move`:
  - validate the inferred LiteLLM model string against a real Gemini key
  - if needed, adjust the configured model alias to the exact LiteLLM-supported Gemini naming used in your account setup

### Entry 7

- `Date`: April 19, 2026
- `Chat scope`: Harden the live Crustdata path before real API-key testing
- `What changed`:
  - added automatic `Bearer`/`Token` auth fallback in the Crustdata client to handle the current docs inconsistency more safely
  - expanded live company enrichment fields using documented Crustdata company dictionary fields
  - added live decision-maker extraction from `founder_names_and_profile_urls` into Bellwether `key_execs`
  - added richer live snapshot normalization including growth metrics
  - added an inferred prior-snapshot path from live headcount growth fields so first-run live refresh has a better chance of producing a meaningful delta
- `Files touched`:
  - `apps/api/app/clients/crustdata.py`
  - `apps/api/app/providers/live_provider.py`
  - `Backend_Trace.md`
- `What is now testable`:
  - live Crustdata auth can tolerate either documented auth scheme without a manual code change
  - live company cards should have a better chance of showing key people and richer state
  - first-run live refresh can sometimes infer a usable baseline from documented headcount growth metrics
- `Open gaps / next move`:
  - validate the real response shape for `founder_names_and_profile_urls`
  - confirm the live inferred baseline is good enough with real company records and adjust if it is too noisy

### Entry 8

- `Date`: April 19, 2026
- `Chat scope`: Tighten the remaining P0 backend contract behavior before real-key testing
- `What changed`:
  - made `POST /watchlist/add` idempotent for the same `(company_id, cohort)` pair by returning the existing company instead of treating it as an error
  - added duplicate-alert protection in refresh and staged-trigger flows using exact delta matching
  - made refresh safer to rerun by skipping identical latest snapshots instead of persisting redundant state
  - upgraded brief summary generation to use the real LLM path with fallback to the heuristic summary
  - enriched alert traces with more meaningful detail payloads so the reasoning trace is closer to the API contract intent
- `Files touched`:
  - `apps/api/app/repositories/storage.py`
  - `apps/api/app/services/llm_analysis_service.py`
  - `apps/api/app/services/alert_engine.py`
  - `apps/api/app/services/brief_service.py`
  - `apps/api/app/services/refresh_service.py`
  - `apps/api/app/services/watchlist_service.py`
  - `Backend_Trace.md`
- `What is now testable`:
  - repeated watchlist adds for the same company and cohort are safe
  - refresh can be rerun without multiplying identical alerts
  - brief summaries can exercise the live LLM path as soon as keys are configured
  - trace payloads now carry more useful orchestration context in the stored alerts
- `Open gaps / next move`:
  - run the live API-key smoke test and validate the remaining real response-shape assumptions
  - if live LLM JSON output is unstable, tighten prompts or add a retry pass for structured output repair

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

## Live Test Checklist

Use this checklist when real API keys are available.

### Required env before testing

- `BELLWETHER_USE_MOCK_PROVIDERS=false`
- `BELLWETHER_CRUSTDATA_API_KEY=<real key>`
- `BELLWETHER_GEMINI_API_KEY=<real key>`
- optional: `BELLWETHER_CRUSTDATA_AUTH_SCHEME=Bearer`
- optional: `BELLWETHER_LLM_MODEL=gemini/gemini-1.5-flash`

### Smoke test order

1. `GET /health`
   Expected:
   - `200`
   - response contains `{ "ok": true, "version": "0.1.0" }`

2. `POST /discover`
   Example body:
   ```json
   { "query": "Series A fintech in India with 20% headcount growth" }
   ```
   Expected:
   - `200`
   - `parsed_filters.description` is populated
   - `companies` is an array
   Watch for:
   - `503 upstream_unavailable` means Crustdata auth, permissions, or upstream shape problems
   - empty `companies` can still be valid if the thesis is too narrow

3. `POST /watchlist/add`
   Example body:
   ```json
   { "company_id": 123456, "cohort": "watching" }
   ```
   Expected:
   - `200`
   - returns `{ "company": ... }`
   - repeating the same request should return `200` with the same company because this flow is now idempotent for the same cohort
   Watch for:
   - `404 company_not_found`
   - `503 upstream_unavailable`

4. `GET /watchlist`
   Expected:
   - `200`
   - recently added company is present

5. `POST /refresh`
   Example body:
   ```json
   { "force": false }
   ```
   Expected:
   - `200`
   - response includes `brief`, `duration_ms`, `companies_processed`, `alerts_generated`
   - rerunning should be safe and should not multiply identical alerts
   Watch for:
   - `alerts_generated` may be `0` if live data produces no detectable deltas
   - `503 upstream_unavailable` means live Crustdata refresh failed

6. `GET /brief`
   Expected:
   - `200`
   - `summary` is populated
   - `counts` object is populated
   - `alerts` are ordered by severity then recency

7. `GET /companies/{company_id}/alerts`
   Expected:
   - `200`
   - returns the company plus alert history for that company

8. `POST /trigger`
   Example body:
   ```json
   { "delta_id": "exec_departure_demo_1" }
   ```
   Expected:
   - `200`
   - returns `{ "alert": ... }`
   - useful as a fallback sanity check even when live refresh produces no interesting deltas

### Known validation points during testing

- confirm the exact live response shape of `founder_names_and_profile_urls`
- confirm the exact LiteLLM model alias accepted in your environment
- check whether the inferred live prior snapshot creates useful deltas or noisy ones
- verify that Crustdata field permissions allow the fields requested by the live provider

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
