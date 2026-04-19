from app.schemas.common import KeyExec
from app.schemas.watchlist import Company


def sample_company_catalog() -> dict[int, Company]:
    companies = [
        Company(
            id=1,
            name="Atomicwork",
            domain="atomicwork.com",
            cohort="watching",
            headcount=120,
            last_funding="Series A, $25M, Jul 2025",
            key_execs=[KeyExec(name="Vijay Rayapati", role="CEO")],
            added_at="2026-04-01T00:00:00Z",
        ),
        Company(
            id=2,
            name="M2P Fintech",
            domain="m2pfintech.com",
            cohort="watching",
            headcount=900,
            last_funding="Series D, $56M, Sep 2024",
            key_execs=[KeyExec(name="Madhusudanan R", role="Co-founder")],
            added_at="2026-04-02T00:00:00Z",
        ),
        Company(
            id=3,
            name="Bellatrix Aerospace",
            domain="bellatrixaerospace.com",
            cohort="watching",
            headcount=220,
            last_funding="Series A, Undisclosed, 2024",
            key_execs=[KeyExec(name="Rohan Ganapathy", role="Co-founder and CTO")],
            added_at="2026-04-03T00:00:00Z",
        ),
    ]
    return {company.id: company for company in companies}

