# Bellwether — PRD

**ContextCon, 19 Apr 2026**

## One-liner

**Bellwether is the AI associate that runs a VC partner's sourcing, watchlist, and portfolio — and only speaks up when something actually matters.**

VCs can't track every company they invested in or considered. We built an AI that watches them all and only pings the VC when something actually matters.

Harmonic finds companies. Standard Metrics reports on portfolio. We unify both under an interpretation layer — the part every incumbent is missing.

## The problem

A VC partner juggles three cohorts: companies to invest in, companies being tracked, and companies already in the portfolio. Today this is three tools and zero interpretation. Every signal — a CTO departure, a competitor raise, a hiring pivot — lands as raw data that a human has to read, rank, and act on. It doesn't scale past a handful of companies per cohort.

| Category | Examples | What they do | What they miss |
|---|---|---|---|
| Sourcing signals | Harmonic, Specter, Synaptic | Surface signals on prospects | No portfolio layer, no interpretation |
| Portfolio monitoring | Standard Metrics, Chronograph | Collect founder-submitted KPIs | No external signals, backward-looking |
| Generic AI | ChatGPT, Claude | Reason over anything | No persistent state, no data pipe, no loop |

No one owns the interpretation layer. That is the product.

## The product

One surface, three views.

**1. Discover.** Chat input. The partner describes a thesis ("Series B fintech in India, 20% YoY headcount growth"). The agent translates to Crustdata filters, enriches the results, and displays them. Each result has an **Add to Watchlist** button.

**2. Watchlist.** Two cohorts: **Invested** (portfolio) and **Watching** (passed or tracking). The same interpretation agent runs on both, cohort-aware. Momentum on a Watching company means "reopen conversation." Exec departure on an Invested company means "talent poaching risk." Same signal, different meaning, routed by cohort.

**3. Brief.** The daily digest. Ranked alerts across both cohorts, each with an expandable reasoning trace.

Every alert passes through a six-type taxonomy — talent poaching, competitive intel, roadmap pivot, health warning, reopen/opportunity, routine — with a severity (partner-alert / associate-alert / noise) and a recommended action.

## Scope

| In | Out |
|---|---|
| Discover tab: NL query → Crustdata search → enriched results | Founder-submitted KPI collection |
| Watchlist with Invested/Watching cohorts | LP reporting, cap table, financial modeling |
| Daily brief with classified, cohort-aware alerts | Full deal-sourcing parity with Harmonic |
| Reasoning trace per alert | CRM replacement, founder-facing surfaces |
| Departed-exec destination chain (P1) | Multi-partner routing, integrations (P1+) |

Enforce this fence. Every feature request on the right side is a distraction.

## Target customer

**Primary:** Seed/Series A partner, 5–40 portfolio companies, no data analyst, handles sourcing and portfolio triage personally.

**Wedge:** Indian early-stage funds. Lower tooling penetration, no local equivalent. Two judges (Siddharth at Grayscale, Ankur at Accel India) are exactly this buyer.

**Why they pay:** One prevented surprise per year covers the product many times over. One reopened-deal-from-the-watchlist that becomes an investment pays for it for life.

## Why we win

**vs. Harmonic:** They are sourcing-only. We bridge sourcing and portfolio under a shared interpretation engine. The Watching-cohort reopen-alert is something they cannot ship without rebuilding the core.

**vs. Standard Metrics:** They need founder-submitted data. We need none. They report backward. We interpret forward.

**vs. generic LLMs:** Persistent state, structured pipe, tuned taxonomy. A partner cannot paste their portfolio into Claude every morning and get this.

**Structural moat (real-company version):** Partner reactions to alerts — dismissed, acted, flagged as noise — retrain the classifier. The more it is used, the less noise it surfaces. A compounding data asset.

## P0 build plan

P0 must ship. Everything else is P1.

1. **Seed data.** 6–10 real companies from Grayscale/Accel India portfolios, pre-loaded into the Invested cohort. Validate Crustdata coverage *before* writing code.
2. **Discover tab.** Chat input → LLM constructs filters for `POST /company/search` → results enriched via `POST /company/enrich` → list UI with **Add to Watchlist (Watching)** button.
3. **Watchlist.** Two-tab UI: Invested | Watching. Each company card shows current headcount, key execs, last funding, recent jobs.
4. **Signal collection.** For every watchlist company, pull state via `/company/enrich` and `/job/search`. Store as a dated snapshot.
5. **Delta detection.** Diff today's snapshot against a prior one. For the demo, pre-seed a plausible "30 days ago" snapshot so real deltas appear.
6. **Interpretation agent.** Each delta → LLM classifier, **cohort-aware** (the Invested vs Watching label changes both the prompt and the alert severity). Output: type, severity, one-paragraph explanation, recommended action.
7. **Brief.** One-page UI. Executive summary at top. Alerts grouped by severity, labeled by cohort. Every alert has an expandable **reasoning trace** exposing which Crustdata calls ran and how the classification landed. The trace is not decoration — it is the only visible proof of agentic orchestration.

## P1 stretch (in priority order)

1. **Departed-exec destination chain.** Detect departure → `/person/search` for new role → enrich new employer → re-classify with destination context. The single most demo-worthy feature after P0.
2. **Natural-language query over the watchlist.** "Which Watching companies showed the strongest momentum this month?"
3. **Roadmap inference from jobs.** GPU engineers = AI pivot. Enterprise AEs = upmarket push.
4. **Slack or email digest output.**
