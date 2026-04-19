# Bellwether

Bellwether is an AI associate for VC partners that helps with three things: discovering companies, monitoring a watchlist, and generating a daily brief of only the signals that matter.

The plan for P0 is intentionally narrow:
- `Discover`: natural-language search that turns a thesis into Crustdata-backed company results.
- `Watchlist`: two cohorts, `Invested` and `Watching`, with current company state and tracked snapshots.
- `Brief`: ranked, cohort-aware alerts with a short explanation, recommended action, and reasoning trace.

The core idea is simple: collect signals, detect deltas, interpret them differently based on cohort, and surface only the highest-signal updates to the partner.

For the full product plan, see [Bellwether_PRD.md](/d:/extras/bellwether/Bellwether_PRD.md).

For the technical design and build plan, see [Bellwether_TRD.md](/d:/extras/bellwether/Bellwether_TRD.md).
