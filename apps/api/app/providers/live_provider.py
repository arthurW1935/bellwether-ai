from math import isfinite
from typing import Any
from urllib.parse import urlparse

from app.clients.crustdata import CrustdataClient, CrustdataClientError, crustdata_client
from app.schemas.common import Cohort, KeyExec
from app.schemas.watchlist import Company


LIVE_COMPANY_ENRICH_FIELDS = [
    "company_id",
    "company_name",
    "company_website",
    "company_website_domain",
    "company_description",
    "hq_country",
    "year_founded",
    "industries",
    "last_funding_round_type",
    "total_investment_usd",
    "headcount",
    "headcount.headcount",
    "headcount_yoy_pct",
    "headcount_qoq_pct",
    "headcount_mom_pct",
    "founder_names_and_profile_urls",
    "job_openings",
    "news_articles",
]


class LiveProvider:
    def __init__(self, client: CrustdataClient | None = None) -> None:
        self._client = client or crustdata_client

    def search_companies(
        self,
        query: str,
        *,
        filters: list[dict[str, Any]] | None = None,
    ) -> list[Company]:
        if filters is None:
            raise ValueError("Live search requires Crustdata filters")

        search_payload = self._client.search_companies(filters=filters, page=1)
        raw_companies = self._extract_companies(search_payload)
        enriched_by_id: dict[int, dict[str, Any]] = {}

        company_ids = [
            int(company_id)
            for company_id in [
                self._extract_company_id(item)
                for item in raw_companies[:10]
            ]
            if company_id is not None
        ]
        if company_ids:
            try:
                enrich_payload = self._client.enrich_companies(
                    company_ids=company_ids,
                    fields=LIVE_COMPANY_ENRICH_FIELDS,
                )
                for item in self._extract_companies(enrich_payload):
                    item_id = self._extract_company_id(item)
                    if item_id is not None:
                        enriched_by_id[int(item_id)] = item
            except CrustdataClientError:
                enriched_by_id = {}

        companies: list[Company] = []
        for item in raw_companies[:10]:
            company_id = self._extract_company_id(item)
            enriched = (
                enriched_by_id.get(int(company_id))
                if company_id is not None
                else None
            )
            company = self._normalize_company(
                enriched or item,
                cohort="watching",
                added_at="1970-01-01T00:00:00Z",
            )
            if company is not None:
                companies.append(company)
        return companies

    def get_company(self, company_id: int, cohort: Cohort, added_at: str) -> Company | None:
        payload = self._client.enrich_companies(
            company_ids=[company_id],
            fields=LIVE_COMPANY_ENRICH_FIELDS,
        )
        companies = self._extract_companies(payload)
        if not companies:
            return None
        return self._normalize_company(companies[0], cohort=cohort, added_at=added_at)

    def get_prior_snapshot(self, company_id: int) -> dict[str, Any] | None:
        current_snapshot = self.get_current_snapshot(company_id)
        if current_snapshot is None:
            return None

        inferred_headcount = self._infer_prior_headcount(current_snapshot)
        if inferred_headcount is None:
            return None

        return {
            **current_snapshot,
            "headcount": inferred_headcount,
        }

    def get_current_snapshot(self, company_id: int) -> dict[str, Any] | None:
        payload = self._client.enrich_companies(
            company_ids=[company_id],
            fields=LIVE_COMPANY_ENRICH_FIELDS,
        )
        companies = self._extract_companies(payload)
        if not companies:
            return None
        return self._normalize_snapshot(companies[0])

    def seed_watchlist(self) -> list[dict[str, int | str]]:
        return []

    def get_staged_delta(self, delta_id: str) -> dict[str, Any] | None:
        return None

    def _extract_companies(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
        if isinstance(payload.get("companies"), list):
            return [item for item in payload["companies"] if isinstance(item, dict)]
        if isinstance(payload.get("data"), list):
            return [item for item in payload["data"] if isinstance(item, dict)]
        if isinstance(payload.get("results"), list):
            return [item for item in payload["results"] if isinstance(item, dict)]
        if isinstance(payload.get("company"), dict):
            return [payload["company"]]
        if isinstance(payload, dict) and any(key in payload for key in ("company_id", "company_name", "name")):
            return [payload]
        return []

    def _normalize_company(
        self,
        item: dict[str, Any],
        *,
        cohort: Cohort,
        added_at: str,
    ) -> Company | None:
        company_id = self._extract_company_id(item)
        name = item.get("company_name") or item.get("name")
        domain = self._extract_domain(item)
        if company_id is None or not name or not domain:
            return None

        return Company(
            id=int(company_id),
            name=str(name),
            domain=domain,
            cohort=cohort,
            headcount=self._extract_headcount(item),
            last_funding=self._format_funding(item),
            key_execs=self._extract_key_execs(item),
            added_at=added_at,
        )

    def _normalize_snapshot(self, item: dict[str, Any]) -> dict[str, Any]:
        job_openings = item.get("job_openings")
        if isinstance(job_openings, list):
            job_titles = [
                opening.get("title")
                for opening in job_openings
                if isinstance(opening, dict) and isinstance(opening.get("title"), str)
            ]
            jobs_count = len(job_openings)
        else:
            job_titles = []
            jobs_count = item.get("job_openings_count")

        return {
            "headcount": self._extract_headcount(item),
            "last_funding": self._format_funding(item),
            "key_execs": [exec.model_dump() for exec in self._extract_key_execs(item)],
            "jobs_count": jobs_count,
            "top_job_titles": job_titles[:5],
            "news_articles": item.get("news_articles", []),
            "headcount_yoy_pct": self._extract_numeric(item, "headcount_yoy_pct"),
            "headcount_qoq_pct": self._extract_numeric(item, "headcount_qoq_pct"),
            "headcount_mom_pct": self._extract_numeric(item, "headcount_mom_pct"),
        }

    def _extract_company_id(self, item: dict[str, Any]) -> int | None:
        for key in ("company_id", "id"):
            value = item.get(key)
            if value is None:
                continue
            try:
                return int(value)
            except (TypeError, ValueError):
                continue
        return None

    def _extract_domain(self, item: dict[str, Any]) -> str | None:
        for key in ("company_website_domain", "domain"):
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip().lower()

        for key in ("company_website", "website"):
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                parsed = urlparse(value if "://" in value else f"https://{value}")
                if parsed.netloc:
                    return parsed.netloc.lower().removeprefix("www.")
        return None

    def _extract_headcount(self, item: dict[str, Any]) -> int | None:
        if isinstance(item.get("employee_count"), int):
            return int(item["employee_count"])
        if isinstance(item.get("headcount"), int):
            return int(item["headcount"])
        headcount_obj = item.get("headcount")
        if isinstance(headcount_obj, dict) and isinstance(headcount_obj.get("headcount"), int):
            return int(headcount_obj["headcount"])
        return None

    def _format_funding(self, item: dict[str, Any]) -> str | None:
        round_type = item.get("last_funding_round_type")
        total_usd = item.get("total_investment_usd")
        if round_type and total_usd:
            return f"{round_type}, ${total_usd}"
        if round_type:
            return str(round_type)
        if total_usd:
            return f"Total funding ${total_usd}"
        return None

    def _extract_key_execs(self, item: dict[str, Any]) -> list[KeyExec]:
        raw_people = item.get("founder_names_and_profile_urls")
        if raw_people is None:
            return []

        execs: list[KeyExec] = []
        if isinstance(raw_people, list):
            for person in raw_people:
                exec_model = self._normalize_exec(person)
                if exec_model is not None:
                    execs.append(exec_model)
        elif isinstance(raw_people, str):
            for chunk in raw_people.split(","):
                name = chunk.strip()
                if name:
                    execs.append(KeyExec(name=name, role="Founder / Decision Maker"))

        return execs[:5]

    def _normalize_exec(self, person: Any) -> KeyExec | None:
        if isinstance(person, str):
            name = person.strip()
            if not name:
                return None
            return KeyExec(name=name, role="Founder / Decision Maker")

        if not isinstance(person, dict):
            return None

        name = (
            person.get("name")
            or person.get("full_name")
            or person.get("founder_name")
            or person.get("person_name")
        )
        if not isinstance(name, str) or not name.strip():
            return None

        role = (
            person.get("title")
            or person.get("role")
            or person.get("designation")
            or "Founder / Decision Maker"
        )
        return KeyExec(name=name.strip(), role=str(role).strip())

    def _extract_numeric(self, item: dict[str, Any], key: str) -> float | None:
        value = item.get(key)
        if isinstance(value, (int, float)):
            return float(value)
        return None

    def _infer_prior_headcount(self, snapshot: dict[str, Any]) -> int | None:
        current_headcount = snapshot.get("headcount")
        growth_pct = snapshot.get("headcount_yoy_pct")
        if not isinstance(current_headcount, int):
            return None
        if not isinstance(growth_pct, (int, float)):
            return None
        if not isfinite(growth_pct):
            return None

        growth_ratio = growth_pct / 100
        denominator = 1 + growth_ratio
        if denominator <= 0:
            return None

        inferred = round(current_headcount / denominator)
        if inferred <= 0 or inferred == current_headcount:
            return None
        return inferred


live_provider = LiveProvider()
