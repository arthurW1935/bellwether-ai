## API Contract — Bellwether v1

**Locked:** 12:55, 19 Apr 2026
**Base URL:** `<render-backend-url>`
**Content-Type:** `application/json` on all endpoints
**CORS:** wildcard during build; tighten to Vercel URL before demo

---

## Type definitions

All types are the canonical shapes. Field names are lowercase snake_case everywhere. Frontend and backend must match exactly.

```typescript
// Cohort label for a company
type Cohort = "invested" | "watching"

// Alert classification taxonomy (6 types, locked)
type AlertType =
  | "talent_poaching"   // key person departed, especially to competitor
  | "competitive"       // a competitor raised, hired, shipped
  | "roadmap"           // hiring pattern implies product direction
  | "health"            // headcount contraction, sustained decline
  | "reopen"            // momentum on a Watching co — revisit
  | "routine"           // noted, no action

// Alert severity (routes who sees it)
type Severity =
  | "P0"   // partner-alert, top of brief
  | "P1"   // associate-alert, middle of brief
  | "P2"   // noise, filtered out of brief by default

// Key executive on a company card
interface KeyExec {
  name: string
  role: string          // e.g., "VP Engineering", "Co-founder & CTO"
}

// Minimal company shape
interface Company {
  id: number            // Crustdata company_id, source of truth
  name: string
  domain: string
  cohort: Cohort
  headcount: number | null
  last_funding: string | null      // e.g., "Series B, $45M, Oct 2025"
  key_execs: KeyExec[]             // max 5, ordered by seniority
  added_at: string                  // ISO8601
}

// One step in the agent's reasoning, shown in UI expander
interface TraceStep {
  stage: string         // "snapshot_collector" | "delta_detector" | "classifier" | "writer" | ...
  summary: string       // one-line human-readable description
  duration_ms: number
  // Optional detail payload — shown only if user clicks deeper
  detail?: {
    api_calls?: { endpoint: string; ms: number }[]
    llm_model?: string
    llm_tokens_in?: number
    llm_tokens_out?: number
  }
}

// Raw delta — what changed between snapshots
interface Delta {
  kind: string          // "exec_departure" | "exec_arrival" | "headcount_change" | "funding_event" | "job_posting_shift" | "news_mention"
  description: string   // one-line human-readable ("VP Engineering left")
  before: unknown       // prior value (shape varies by kind)
  after: unknown        // current value
}

// The fully interpreted alert — the product's output
interface Alert {
  id: number
  company: Company      // nested, not just id — frontend renders inline
  cohort: Cohort        // denormalized for convenience (matches company.cohort)
  delta: Delta
  alert_type: AlertType
  severity: Severity
  explanation: string   // 2–3 sentence LLM-generated reasoning
  recommended_action: string  // one sentence
  trace: TraceStep[]    // ordered, earliest first
  detected_at: string   // ISO8601
}

// The daily brief — the hero view
interface Brief {
  summary: string       // LLM-generated exec summary, 3–4 sentences
  generated_at: string  // ISO8601
  alerts: Alert[]       // ordered by severity (P0 first), then by detected_at desc
  counts: {
    p0: number
    p1: number
    p2: number
  }
}

// Standard error shape for all 4xx / 5xx
interface ErrorResponse {
  error: string         // machine-readable code, e.g., "company_not_found"
  message: string       // human-readable explanation
  detail?: unknown      // optional debug info, only in dev
}
```

---

## Endpoints

### `GET /health`
Liveness probe. UptimeRobot pings this every 5 minutes.

**Request:** none
**Response 200:**
```json
{ "ok": true, "version": "0.1.0" }
```

---

### `GET /watchlist`
Returns all companies in the watchlist, optionally filtered by cohort.

**Query params:**
- `cohort` (optional): `"invested"` | `"watching"` — if omitted, returns both

**Response 200:**
```json
{
  "companies": [Company, Company, ...]
}
```

**Notes:**
- Empty list is valid, not an error.
- Companies ordered by `added_at` descending.

---

### `POST /watchlist/add`
Adds a company to the watchlist in the specified cohort.

**Request body:**
```json
{
  "company_id": 663861,
  "cohort": "watching"
}
```

**Response 200:**
```json
{ "company": Company }
```

**Response 404** (company not resolvable via Crustdata):
```json
{ "error": "company_not_found", "message": "No company with id 663861 in Crustdata" }
```

**Response 409** (already in watchlist):
```json
{ "error": "already_in_watchlist", "message": "Company 663861 is already in cohort 'invested'" }
```

**Notes:**
- Backend should call `/company/enrich` on add to populate fields.
- Idempotent on (company_id, cohort) pair — same call twice returns the same company.

---

### `POST /watchlist/remove`
Removes a company from the watchlist.

**Request body:**
```json
{ "company_id": 663861 }
```

**Response 200:**
```json
{ "removed": true }
```

**Response 404:**
```json
{ "error": "company_not_found", "message": "..." }
```

---

### `POST /discover`
Natural-language search over Crustdata companies. The Discover tab calls this.

**Request body:**
```json
{
  "query": "Series B fintech in India with 20% YoY headcount growth"
}
```

**Response 200:**
```json
{
  "companies": [Company, Company, ...],
  "parsed_filters": {
    "description": "Series B, fintech, India, headcount growth >= 20%"
  }
}
```

**Notes:**
- Returns max 10 companies.
- Companies returned here are NOT yet in the watchlist. Frontend renders them with an "Add to Watching" button that calls `/watchlist/add`.
- `parsed_filters.description` is a human-readable summary of what the LLM understood — shown above results so user knows the query was interpreted correctly.

**Response 400** (query unparseable):
```json
{ "error": "query_unparseable", "message": "Could not extract filters from query" }
```

---

### `GET /brief`
Returns the current daily brief across both cohorts. This is the hero endpoint.

**Query params:**
- `min_severity` (optional, default `"P1"`): `"P0"` | `"P1"` | `"P2"` — filters alerts below this level. Default hides P2 noise.

**Response 200:**
```json
{
  "summary": "Three partner-level alerts today. Two concerns on Invested — talent-poaching risk at <co> and a competitive raise affecting <co>. One reopen signal on Watching — <co> showed momentum aligned with your thesis.",
  "generated_at": "2026-04-19T13:42:00Z",
  "alerts": [Alert, Alert, ...],
  "counts": { "p0": 3, "p1": 4, "p2": 8 }
}
```

**Notes:**
- `counts` always includes all severities even if filtered from `alerts`.
- Alerts are sorted: P0 first, then P1 (and P2 if requested), each tier ordered by `detected_at` descending.
- The brief is recomputed on `/refresh` call; otherwise returns the last computed brief.

---

### `POST /refresh`
Runs the full orchestration: collect snapshots for every watchlist company, detect deltas, classify, write, summarize. Expensive — the latency budget is ~15s worst case.

**Request body:** none (or `{ "force": true }` to bypass any caching)

**Response 200:**
```json
{
  "brief": Brief,
  "duration_ms": 14200,
  "companies_processed": 10,
  "alerts_generated": 12
}
```

**Notes:**
- Triggered manually in the demo by a "Refresh" button on `/brief`.
- Backend should be idempotent — running twice in a row is safe.
- Do NOT call this during the Loom recording unless explicitly scripted.

---

### `POST /trigger`
Demo-critical. Runs one pre-staged delta through the real agent pipeline end-to-end and returns the resulting alert. Used by the live-trigger button on `/brief`.

**Request body:**
```json
{ "delta_id": "exec_departure_demo_1" }
```

Supported `delta_id` values (pre-seeded in backend code):
- `exec_departure_demo_1` — fires a talent-poaching alert on a hero company
- `competitor_raise_demo_1` — fires a competitive alert
- `headcount_surge_demo_1` — fires a reopen alert on a Watching company

**Response 200:**
```json
{ "alert": Alert }
```

**Response 404:**
```json
{ "error": "delta_not_found", "message": "No staged delta with id '<x>'" }
```

**Notes:**
- The alert IS persisted — after this call, the alert shows up in `GET /brief` too.
- Runs the REAL pipeline (classifier + writer + trace). The only "staged" part is the delta input; the interpretation happens live. This is the honest version of the demo.

---

### `GET /companies/{company_id}/alerts`
All alerts for a single company, for the drill-in view when user clicks a company card.

**Path params:**
- `company_id`: int

**Response 200:**
```json
{
  "company": Company,
  "alerts": [Alert, Alert, ...]
}
```

**Notes:**
- Alerts ordered by `detected_at` descending, all severities included.
- Useful for the "alert history" view on company cards, if time permits.

---

## Error handling — universal rules

Every endpoint that can fail returns the `ErrorResponse` shape above with an appropriate HTTP status:

- `400` — bad request (malformed body, unparseable query)
- `404` — resource not found
- `409` — conflict (duplicate add)
- `429` — rate limited (Crustdata or Gemini pushed back)
- `500` — internal error (agent pipeline failure, DB error)
- `503` — upstream unavailable (Crustdata or Gemini down)

**Frontend rule:** on any non-200, show a toast with `error.message`. On 500, show a generic "Something went wrong — try again" and log `error.detail` to console.

---

## Pagination and limits

Not implementing pagination. Every list endpoint returns everything. Rationale: the watchlist is small (≤20 companies), and alerts per day are small (≤30). If this ever grew, we'd add `?limit=&offset=` — but not today.

---

## Field-name drift prevention

The two most common ways this contract breaks during the hackathon:

1. **camelCase vs snake_case.** Backend returns `alert_type`, frontend expects `alertType`. Solution: **backend returns snake_case, frontend consumes snake_case.** Do NOT transform field names at the API boundary. If the frontend wants camelCase internally, it can transform after receiving, but the wire format is snake_case everywhere.

2. **String vs enum.** Backend returns `"talent_poaching"`, frontend expects `"TALENT_POACHING"`. Solution: **lowercase_snake_case strings everywhere.** Define the TypeScript union types from the strings in the contract; don't invent new casing.

If either of you needs to change a field name after 12:55, you message the other person and update this doc. No silent renames.

---

## Minimum shared mocks (for Person B to build against)

Person A, ship these exact mock responses by 13:25 so Person B can build the UI without waiting:

**`GET /watchlist` mock:**
```json
{
  "companies": [
    {
      "id": 1, "name": "Atomicwork", "domain": "atomicwork.com",
      "cohort": "invested", "headcount": 120, "last_funding": "Series A, $25M, Jul 2025",
      "key_execs": [{"name": "Vijay Rayapati", "role": "CEO"}],
      "added_at": "2026-04-01T00:00:00Z"
    }
  ]
}
```

**`GET /brief` mock:**
```json
{
  "summary": "Two partner-level alerts today. Atomicwork's VP Engineering departed to a direct competitor. Freshworks announced a Series D raise affecting Atomicwork's competitive position.",
  "generated_at": "2026-04-19T13:00:00Z",
  "alerts": [
    {
      "id": 1,
      "company": { "id": 1, "name": "Atomicwork", "domain": "atomicwork.com", "cohort": "invested", "headcount": 120, "last_funding": "Series A, $25M, Jul 2025", "key_execs": [], "added_at": "2026-04-01T00:00:00Z" },
      "cohort": "invested",
      "delta": { "kind": "exec_departure", "description": "VP Engineering departed", "before": "Rajesh Kumar, VP Engineering", "after": null },
      "alert_type": "talent_poaching",
      "severity": "P0",
      "explanation": "Rajesh Kumar departed after 2.5 years as VP Engineering. He joined Freshworks, a direct competitor in the IT service management space. This is a talent-poaching signal, not routine churn.",
      "recommended_action": "Reach out to the founder this week to understand the circumstances and retention plan for remaining engineering leadership.",
      "trace": [
        { "stage": "snapshot_collector", "summary": "Pulled current state via /company/enrich", "duration_ms": 420 },
        { "stage": "delta_detector", "summary": "Detected exec_departure on Rajesh Kumar", "duration_ms": 12 },
        { "stage": "destination_chain", "summary": "Resolved new employer: Freshworks", "duration_ms": 890 },
        { "stage": "classifier", "summary": "Classified as talent_poaching, P0", "duration_ms": 612 },
        { "stage": "writer", "summary": "Generated explanation and recommended action", "duration_ms": 1240 }
      ],
      "detected_at": "2026-04-19T12:58:00Z"
    }
  ],
  "counts": { "p0": 1, "p1": 0, "p2": 0 }
}
```

Person B builds the UI against these exact shapes. Person A swaps the mock for real logic later without Person B needing to change anything.
