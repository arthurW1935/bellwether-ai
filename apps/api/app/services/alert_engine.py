from app.schemas.brief import Alert, Delta, TraceStep
from app.schemas.common import AlertType, Cohort, Severity
from app.schemas.watchlist import Company
from app.services.llm_analysis_service import llm_analysis_service


def detect_deltas(previous_payload: dict, current_payload: dict) -> list[Delta]:
    deltas: list[Delta] = []

    before_headcount = previous_payload.get("headcount")
    after_headcount = current_payload.get("headcount")
    if (
        isinstance(before_headcount, int)
        and isinstance(after_headcount, int)
        and before_headcount > 0
    ):
        change_ratio = (after_headcount - before_headcount) / before_headcount
        if abs(change_ratio) >= 0.1:
            deltas.append(
                Delta(
                    kind="headcount_change",
                    description=f"Headcount changed from {before_headcount} to {after_headcount}",
                    before=before_headcount,
                    after=after_headcount,
                )
            )

    before_execs = {item["name"]: item["role"] for item in previous_payload.get("key_execs", [])}
    after_execs = {item["name"]: item["role"] for item in current_payload.get("key_execs", [])}
    removed_execs = [name for name in before_execs if name not in after_execs]
    if removed_execs:
        name = removed_execs[0]
        deltas.append(
            Delta(
                kind="exec_departure",
                description=f"{before_execs[name]} departed",
                before=f"{name}, {before_execs[name]}",
                after=None,
            )
        )

    before_funding = previous_payload.get("last_funding")
    after_funding = current_payload.get("last_funding")
    if before_funding and after_funding and before_funding != after_funding:
        deltas.append(
            Delta(
                kind="funding_event",
                description="Funding round changed",
                before=before_funding,
                after=after_funding,
            )
        )

    before_jobs = previous_payload.get("jobs_count")
    after_jobs = current_payload.get("jobs_count")
    if isinstance(before_jobs, int) and isinstance(after_jobs, int) and abs(after_jobs - before_jobs) >= 5:
        deltas.append(
            Delta(
                kind="job_posting_shift",
                description=f"Open roles changed from {before_jobs} to {after_jobs}",
                before=before_jobs,
                after=after_jobs,
            )
        )

    return deltas


def classify_delta(delta: Delta, cohort: Cohort) -> tuple[AlertType, Severity]:
    if delta.kind == "exec_departure":
        return "talent_poaching", "P0" if cohort == "invested" else "P1"
    if delta.kind == "funding_event":
        return ("competitive", "P1") if cohort == "invested" else ("reopen", "P0")
    if delta.kind == "headcount_change":
        if isinstance(delta.before, int) and isinstance(delta.after, int):
            if delta.after < delta.before:
                return "health", "P0" if cohort == "invested" else "P1"
            return ("routine", "P2") if cohort == "invested" else ("reopen", "P0")
    if delta.kind == "job_posting_shift":
        return "roadmap", "P1"
    return "routine", "P2"


def write_alert(
    *,
    alert_id: int,
    company: Company,
    delta: Delta,
    detected_at: str,
    trace_context: dict | None = None,
) -> Alert:
    llm_result = llm_analysis_service.analyze_delta(company=company, delta=delta)
    llm_used = llm_result is not None
    if llm_result is None:
        alert_type, severity = classify_delta(delta, company.cohort)
        explanation = build_explanation(company=company, delta=delta, alert_type=alert_type)
        recommended_action = build_recommended_action(company=company, alert_type=alert_type)
        classifier_summary = f"Classified as {alert_type}, {severity}"
    else:
        alert_type = llm_result["alert_type"]
        severity = llm_result["severity"]
        explanation = llm_result["explanation"]
        recommended_action = llm_result["recommended_action"]
        classifier_summary = f"LLM classified as {alert_type}, {severity}"
    trace = [
        TraceStep(
            stage="snapshot_collector",
            summary="Loaded previous and current company snapshots",
            duration_ms=45,
            detail=(trace_context or {}).get("snapshot_collector"),
        ),
        TraceStep(
            stage="delta_detector",
            summary=f"Detected {delta.kind}",
            duration_ms=8,
            detail=(trace_context or {}).get("delta_detector"),
        ),
        TraceStep(
            stage="classifier",
            summary=classifier_summary,
            duration_ms=12,
            detail=(
                (trace_context or {}).get("classifier")
                or (
                    {"llm_model": llm_analysis_service.llm_model_name()}
                    if llm_used and llm_analysis_service.llm_model_name()
                    else None
                )
            ),
        ),
        TraceStep(
            stage="writer",
            summary="Generated explanation and recommended action",
            duration_ms=9,
            detail=(
                (trace_context or {}).get("writer")
                or (
                    {"llm_model": llm_analysis_service.llm_model_name()}
                    if llm_used and llm_analysis_service.llm_model_name()
                    else None
                )
            ),
        ),
    ]
    return Alert(
        id=alert_id,
        company=company,
        cohort=company.cohort,
        delta=delta,
        alert_type=alert_type,
        severity=severity,
        explanation=explanation,
        recommended_action=recommended_action,
        trace=trace,
        detected_at=detected_at,
    )


def build_explanation(*, company: Company, delta: Delta, alert_type: AlertType) -> str:
    if alert_type == "talent_poaching":
        return (
            f"{company.name} lost a senior leader: {delta.before}. "
            "For an invested company, that is a near-term execution and retention risk."
        )
    if alert_type == "health":
        return (
            f"{company.name} showed a material contraction in operating signals. "
            "This suggests slowing momentum and deserves partner attention."
        )
    if alert_type == "reopen":
        return (
            f"{company.name} is showing fresh momentum aligned with a watching thesis. "
            "The signal is strong enough to reopen the conversation."
        )
    if alert_type == "competitive":
        return (
            f"{company.name} has a new market or funding signal that could shift competitive positioning. "
            "It is worth triaging with current context."
        )
    if alert_type == "roadmap":
        return (
            f"{company.name} changed its hiring posture materially. "
            "That often implies a product or go-to-market shift underway."
        )
    return (
        f"{company.name} generated a product signal, but it does not appear partner-critical yet."
    )


def build_recommended_action(*, company: Company, alert_type: AlertType) -> str:
    actions = {
        "talent_poaching": f"Reach out to {company.name}'s founder this week and understand the backfill plan.",
        "health": f"Ask for a quick operating update from {company.name} and confirm whether the contraction is expected.",
        "reopen": f"Reopen the {company.name} thread and decide whether to schedule a fresh meeting.",
        "competitive": f"Have the team sanity-check how this changes {company.name}'s position in the market.",
        "roadmap": f"Review the new hiring pattern at {company.name} and infer the likely roadmap shift.",
        "routine": f"Keep {company.name} on the regular monitoring cadence.",
    }
    return actions[alert_type]
