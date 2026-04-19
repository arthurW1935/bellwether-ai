from time import perf_counter

from app.providers.mock_provider import mock_provider
from app.providers.provider_resolver import get_data_provider
from app.repositories.storage import storage_repository
from app.schemas.brief import Alert
from app.services.alert_engine import detect_deltas, write_alert
from app.services.brief_service import brief_service
from app.services.clock import utc_now_iso
from app.services.watchlist_service import watchlist_service


class DeltaNotFoundError(Exception):
    """Raised when a staged demo delta id does not exist."""


class RefreshService:
    def refresh(self, force: bool = False) -> dict:
        started_at = perf_counter()
        watchlist = watchlist_service.list_companies()
        alerts_generated = 0
        provider = get_data_provider()

        for company in watchlist:
            previous_snapshot = storage_repository.get_latest_snapshot(company.id)
            current_payload = provider.get_current_snapshot(company.id)
            if previous_snapshot is None or current_payload is None:
                continue

            if previous_snapshot["payload"] == current_payload:
                continue

            snapshot_taken_at = utc_now_iso()
            storage_repository.add_snapshot(
                company_id=company.id,
                taken_at=snapshot_taken_at,
                payload=current_payload,
            )
            previous_payload = previous_snapshot["payload"]
            deltas = detect_deltas(previous_payload, current_payload)
            for delta in deltas:
                existing_alert = storage_repository.find_matching_alert(company.id, delta)
                if existing_alert is not None:
                    continue

                alert = write_alert(
                    alert_id=0,
                    company=watchlist_service.refresh_company_state(company.id, current_payload),
                    delta=delta,
                    detected_at=utc_now_iso(),
                    trace_context={
                        "snapshot_collector": {
                            "api_calls": [
                                {"endpoint": "/screener/company", "ms": 0}
                            ]
                        },
                        "delta_detector": {
                            "snapshot_taken_at": snapshot_taken_at,
                        },
                    },
                )
                alert_id = storage_repository.add_alert(alert)
                alert.id = alert_id
                alerts_generated += 1

        all_alerts = storage_repository.list_alerts()
        summary = brief_service.build_summary(all_alerts)
        counts = brief_service.get_brief(min_severity="P2").counts
        generated_at = utc_now_iso()
        storage_repository.save_brief_run(summary=summary, generated_at=generated_at, counts=counts)
        brief = brief_service.get_brief()
        duration_ms = int((perf_counter() - started_at) * 1000)
        return {
            "brief": brief,
            "duration_ms": duration_ms,
            "companies_processed": len(watchlist),
            "alerts_generated": alerts_generated,
        }

    def trigger(self, delta_id: str) -> Alert:
        staged = mock_provider.get_staged_delta(delta_id)
        if staged is None:
            raise DeltaNotFoundError(f"No staged delta with id '{delta_id}'")

        company = watchlist_service.ensure_company_in_watchlist(
            company_id=int(staged["company_id"]),
            cohort=str(staged["cohort"]),
        )
        existing_alert = storage_repository.find_matching_alert(
            company.id,
            staged["delta"],
        )
        if existing_alert is not None:
            return existing_alert

        alert = write_alert(
            alert_id=0,
            company=company,
            delta=staged["delta"],
            detected_at=utc_now_iso(),
            trace_context={
                "snapshot_collector": {
                    "api_calls": [{"endpoint": "staged_delta", "ms": 0}]
                }
            },
        )
        alert.id = storage_repository.add_alert(alert)
        summary = brief_service.build_summary(storage_repository.list_alerts())
        counts = brief_service.get_brief(min_severity="P2").counts
        storage_repository.save_brief_run(
            summary=summary,
            generated_at=utc_now_iso(),
            counts=counts,
        )
        return alert


refresh_service = RefreshService()
