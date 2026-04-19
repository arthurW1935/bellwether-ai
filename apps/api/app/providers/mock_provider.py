from copy import deepcopy
from datetime import UTC, datetime

from app.schemas.brief import Delta
from app.schemas.common import Cohort, KeyExec
from app.schemas.watchlist import Company


class MockProvider:
    def __init__(self) -> None:
        self._catalog = {
            1: {
                "profile": {
                    "id": 1,
                    "name": "Atomicwork",
                    "domain": "atomicwork.com",
                    "headcount": 120,
                    "last_funding": "Series A, $25M, Jul 2025",
                    "key_execs": [
                        {"name": "Vijay Rayapati", "role": "CEO"},
                        {"name": "Anita Sharma", "role": "VP Engineering"},
                    ],
                    "description": "AI-powered IT service management for enterprises.",
                    "tags": ["india", "saas", "it", "enterprise", "series a"],
                },
                "prior_snapshot": {
                    "headcount": 118,
                    "last_funding": "Series A, $25M, Jul 2025",
                    "key_execs": [
                        {"name": "Vijay Rayapati", "role": "CEO"},
                        {"name": "Anita Sharma", "role": "VP Engineering"},
                    ],
                    "jobs_count": 14,
                    "top_job_titles": ["Solutions Engineer", "Product Manager"],
                },
                "current_snapshot": {
                    "headcount": 120,
                    "last_funding": "Series A, $25M, Jul 2025",
                    "key_execs": [
                        {"name": "Vijay Rayapati", "role": "CEO"},
                    ],
                    "jobs_count": 11,
                    "top_job_titles": ["Solutions Engineer"],
                },
            },
            2: {
                "profile": {
                    "id": 2,
                    "name": "M2P Fintech",
                    "domain": "m2pfintech.com",
                    "headcount": 900,
                    "last_funding": "Series D, $56M, Sep 2024",
                    "key_execs": [
                        {"name": "Madhusudanan R", "role": "Co-founder"},
                    ],
                    "description": "Banking and embedded finance infrastructure.",
                    "tags": ["india", "fintech", "embedded finance", "series d"],
                },
                "prior_snapshot": {
                    "headcount": 980,
                    "last_funding": "Series D, $56M, Sep 2024",
                    "key_execs": [
                        {"name": "Madhusudanan R", "role": "Co-founder"},
                    ],
                    "jobs_count": 32,
                    "top_job_titles": ["Backend Engineer", "Sales Manager"],
                },
                "current_snapshot": {
                    "headcount": 900,
                    "last_funding": "Series D, $56M, Sep 2024",
                    "key_execs": [
                        {"name": "Madhusudanan R", "role": "Co-founder"},
                    ],
                    "jobs_count": 21,
                    "top_job_titles": ["Backend Engineer"],
                },
            },
            3: {
                "profile": {
                    "id": 3,
                    "name": "Bellatrix Aerospace",
                    "domain": "bellatrixaerospace.com",
                    "headcount": 220,
                    "last_funding": "Series A, Undisclosed, 2024",
                    "key_execs": [
                        {"name": "Rohan Ganapathy", "role": "Co-founder and CTO"},
                    ],
                    "description": "Space propulsion systems and orbital transfer vehicles.",
                    "tags": ["india", "space", "deeptech", "series a"],
                },
                "prior_snapshot": {
                    "headcount": 180,
                    "last_funding": "Series A, Undisclosed, 2024",
                    "key_execs": [
                        {"name": "Rohan Ganapathy", "role": "Co-founder and CTO"},
                    ],
                    "jobs_count": 9,
                    "top_job_titles": ["Propulsion Engineer", "Manufacturing Engineer"],
                },
                "current_snapshot": {
                    "headcount": 220,
                    "last_funding": "Series A, Undisclosed, 2024",
                    "key_execs": [
                        {"name": "Rohan Ganapathy", "role": "Co-founder and CTO"},
                    ],
                    "jobs_count": 18,
                    "top_job_titles": ["Propulsion Engineer", "Avionics Engineer", "AI Researcher"],
                },
            },
            4: {
                "profile": {
                    "id": 4,
                    "name": "Sarvam AI",
                    "domain": "sarvam.ai",
                    "headcount": 85,
                    "last_funding": "Seed, $41M, Jan 2026",
                    "key_execs": [
                        {"name": "Vivek Raghavan", "role": "Co-founder"},
                    ],
                    "description": "Indian generative AI foundation models and voice infrastructure.",
                    "tags": ["india", "ai", "llm", "seed"],
                },
                "prior_snapshot": {
                    "headcount": 62,
                    "last_funding": "Seed, $41M, Jan 2026",
                    "key_execs": [
                        {"name": "Vivek Raghavan", "role": "Co-founder"},
                    ],
                    "jobs_count": 12,
                    "top_job_titles": ["ML Engineer", "Speech Engineer"],
                },
                "current_snapshot": {
                    "headcount": 85,
                    "last_funding": "Seed, $41M, Jan 2026",
                    "key_execs": [
                        {"name": "Vivek Raghavan", "role": "Co-founder"},
                    ],
                    "jobs_count": 19,
                    "top_job_titles": ["ML Engineer", "Speech Engineer", "Developer Relations"],
                },
            },
            5: {
                "profile": {
                    "id": 5,
                    "name": "Juspay",
                    "domain": "juspay.in",
                    "headcount": 740,
                    "last_funding": "Series D, $60M, Dec 2025",
                    "key_execs": [
                        {"name": "Vimal Kumar", "role": "CEO"},
                    ],
                    "description": "Payments infrastructure and orchestration platform.",
                    "tags": ["india", "payments", "fintech", "series d"],
                },
                "prior_snapshot": {
                    "headcount": 705,
                    "last_funding": "Series C, $50M, 2024",
                    "key_execs": [
                        {"name": "Vimal Kumar", "role": "CEO"},
                    ],
                    "jobs_count": 26,
                    "top_job_titles": ["Site Reliability Engineer", "Product Analyst"],
                },
                "current_snapshot": {
                    "headcount": 740,
                    "last_funding": "Series D, $60M, Dec 2025",
                    "key_execs": [
                        {"name": "Vimal Kumar", "role": "CEO"},
                    ],
                    "jobs_count": 33,
                    "top_job_titles": ["Site Reliability Engineer", "Product Analyst", "Enterprise AE"],
                },
            },
        }
        self._seed_watchlist = [
            {"company_id": 1, "cohort": "invested"},
            {"company_id": 2, "cohort": "invested"},
            {"company_id": 3, "cohort": "watching"},
        ]
        self._staged_deltas = {
            "exec_departure_demo_1": {
                "company_id": 1,
                "cohort": "invested",
                "delta": Delta(
                    kind="exec_departure",
                    description="VP Engineering departed",
                    before="Anita Sharma, VP Engineering",
                    after=None,
                ),
            },
            "competitor_raise_demo_1": {
                "company_id": 5,
                "cohort": "watching",
                "delta": Delta(
                    kind="funding_event",
                    description="Juspay announced a new funding round",
                    before="Series C, $50M, 2024",
                    after="Series D, $60M, Dec 2025",
                ),
            },
            "headcount_surge_demo_1": {
                "company_id": 4,
                "cohort": "watching",
                "delta": Delta(
                    kind="headcount_change",
                    description="Headcount increased from 62 to 85",
                    before=62,
                    after=85,
                ),
            },
        }

    def search_companies(
        self,
        query: str,
        *,
        filters: list[dict] | None = None,
    ) -> list[Company]:
        tokens = {token.lower() for token in query.split() if token.strip()}
        now = datetime.now(UTC).isoformat()
        companies: list[Company] = []
        for item in self._catalog.values():
            profile = item["profile"]
            haystack = " ".join(
                [profile["name"], profile["domain"], profile["description"], " ".join(profile["tags"])]
            ).lower()
            if not tokens or any(token in haystack for token in tokens):
                companies.append(self._company_from_profile(profile, cohort="watching", added_at=now))
        return companies[:10]

    def get_company(self, company_id: int, cohort: Cohort, added_at: str) -> Company | None:
        item = self._catalog.get(company_id)
        if item is None:
            return None
        return self._company_from_profile(item["profile"], cohort=cohort, added_at=added_at)

    def get_prior_snapshot(self, company_id: int) -> dict | None:
        item = self._catalog.get(company_id)
        if item is None:
            return None
        return deepcopy(item["prior_snapshot"])

    def get_current_snapshot(self, company_id: int) -> dict | None:
        item = self._catalog.get(company_id)
        if item is None:
            return None
        return deepcopy(item["current_snapshot"])

    def seed_watchlist(self) -> list[dict[str, int | str]]:
        return deepcopy(self._seed_watchlist)

    def get_staged_delta(self, delta_id: str) -> dict | None:
        staged = self._staged_deltas.get(delta_id)
        if staged is None:
            return None
        return deepcopy(staged)

    def _company_from_profile(self, profile: dict, cohort: Cohort, added_at: str) -> Company:
        return Company(
            id=profile["id"],
            name=profile["name"],
            domain=profile["domain"],
            cohort=cohort,
            headcount=profile["headcount"],
            last_funding=profile["last_funding"],
            key_execs=[KeyExec(**item) for item in profile["key_execs"]],
            added_at=added_at,
        )


mock_provider = MockProvider()
