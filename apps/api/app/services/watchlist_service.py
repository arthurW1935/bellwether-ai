from app.schemas.common import Cohort, KeyExec
from app.schemas.watchlist import Company
from app.providers.provider_resolver import get_data_provider
from app.repositories.storage import storage_repository
from app.services.clock import utc_now_iso


class CompanyNotFoundError(Exception):
    """Raised when a company cannot be found in the current catalog."""


class AlreadyInWatchlistError(Exception):
    """Raised when a company is already present in the watchlist."""


class WatchlistService:
    def list_companies(self, cohort: Cohort | None = None) -> list[Company]:
        return storage_repository.list_watchlist(cohort=cohort)

    def add_company(
        self,
        company_id: int,
        cohort: Cohort,
        *,
        added_at: str | None = None,
        seed_prior_snapshot: bool = True,
    ) -> Company:
        if storage_repository.watchlist_entry_exists(company_id):
            existing = storage_repository.get_watchlist_company(company_id)
            if existing is None:
                raise CompanyNotFoundError(
                    f"No company with id {company_id} in the current watchlist"
                )
            if existing.cohort == cohort:
                return existing
            raise AlreadyInWatchlistError(
                f"Company {company_id} is already in cohort '{existing.cohort}'"
            )

        timestamp = added_at or utc_now_iso()
        provider = get_data_provider()
        company = provider.get_company(company_id=company_id, cohort=cohort, added_at=timestamp)
        if company is None:
            raise CompanyNotFoundError(
                f"No company with id {company_id} in the current backend catalog"
            )

        storage_repository.upsert_company(company=company, updated_at=timestamp)
        storage_repository.add_watchlist_entry(company_id=company_id, cohort=cohort, added_at=timestamp)

        if seed_prior_snapshot and storage_repository.count_snapshots(company_id) == 0:
            prior_snapshot = provider.get_prior_snapshot(company_id)
            if prior_snapshot is not None:
                storage_repository.add_snapshot(
                    company_id=company_id,
                    taken_at=timestamp,
                    payload=prior_snapshot,
                )
            else:
                current_snapshot = provider.get_current_snapshot(company_id)
                if current_snapshot is not None:
                    storage_repository.add_snapshot(
                        company_id=company_id,
                        taken_at=timestamp,
                        payload=current_snapshot,
                    )

        stored = storage_repository.get_watchlist_company(company_id)
        if stored is None:
            raise CompanyNotFoundError(f"No company with id {company_id} in the current watchlist")
        return stored

    def remove_company(self, company_id: int) -> None:
        if not storage_repository.delete_watchlist_entry(company_id):
            raise CompanyNotFoundError(
                f"No company with id {company_id} in the current watchlist"
            )

    def get_company(self, company_id: int) -> Company:
        company = storage_repository.get_watchlist_company(company_id)
        if company is None:
            raise CompanyNotFoundError(
                f"No company with id {company_id} in the current watchlist"
            )
        return company

    def ensure_company_in_watchlist(self, company_id: int, cohort: Cohort) -> Company:
        company = storage_repository.get_watchlist_company(company_id)
        if company is not None:
            return company
        return self.add_company(company_id=company_id, cohort=cohort)

    def refresh_company_state(self, company_id: int, payload: dict) -> Company:
        company = self.get_company(company_id)
        updated_company = Company(
            id=company.id,
            name=company.name,
            domain=company.domain,
            cohort=company.cohort,
            headcount=payload.get("headcount"),
            last_funding=payload.get("last_funding"),
            key_execs=list(company.key_execs),
            added_at=company.added_at,
        )
        if "key_execs" in payload:
            updated_company.key_execs = [KeyExec(**item) for item in payload["key_execs"]]
        storage_repository.upsert_company(company=updated_company, updated_at=utc_now_iso())
        return self.get_company(company_id)


watchlist_service = WatchlistService()
