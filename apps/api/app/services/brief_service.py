from collections import Counter

from app.schemas.brief import Alert, BriefCounts, BriefResponse, CompanyAlertsResponse
from app.schemas.common import Severity
from app.repositories.storage import storage_repository
from app.services.watchlist_service import CompanyNotFoundError, watchlist_service


SEVERITY_ORDER = {"P0": 0, "P1": 1, "P2": 2}


class BriefService:
    def get_brief(self, min_severity: Severity = "P1") -> BriefResponse:
        all_alerts = self._sorted_alerts(storage_repository.list_alerts())
        counts = self._counts_for(all_alerts)
        filtered_alerts = [
            alert
            for alert in all_alerts
            if SEVERITY_ORDER[alert.severity] <= SEVERITY_ORDER[min_severity]
        ]

        latest_brief = storage_repository.get_latest_brief_run()
        if latest_brief is None:
            summary = "No brief has been generated yet."
            generated_at = "2026-04-19T00:00:00Z"
        else:
            summary = latest_brief["summary"]
            generated_at = latest_brief["generated_at"]

        return BriefResponse(
            summary=summary,
            generated_at=generated_at,
            alerts=filtered_alerts,
            counts=counts,
        )

    def get_company_alerts(self, company_id: int) -> CompanyAlertsResponse:
        company = watchlist_service.get_company(company_id)
        alerts = storage_repository.list_alerts(company_id=company_id)
        return CompanyAlertsResponse(company=company, alerts=alerts)

    def build_summary(self, alerts: list[Alert]) -> str:
        if not alerts:
            return "No material alerts today."

        counts = Counter(alert.severity for alert in alerts)
        companies = ", ".join(alert.company.name for alert in alerts[:3])
        p0 = counts.get("P0", 0)
        p1 = counts.get("P1", 0)
        if p0:
            return (
                f"{p0} partner-level alerts and {p1} associate-level alerts were generated today. "
                f"Top companies to review: {companies}."
            )
        return f"{p1} associate-level alerts were generated today. Top companies to review: {companies}."

    def _counts_for(self, alerts: list[Alert]) -> BriefCounts:
        counts = Counter(alert.severity for alert in alerts)
        return BriefCounts(
            p0=counts.get("P0", 0),
            p1=counts.get("P1", 0),
            p2=counts.get("P2", 0),
        )

    def _sorted_alerts(self, alerts: list[Alert]) -> list[Alert]:
        alerts = sorted(alerts, key=lambda alert: alert.detected_at, reverse=True)
        alerts.sort(key=lambda alert: SEVERITY_ORDER[alert.severity])
        return alerts


brief_service = BriefService()
