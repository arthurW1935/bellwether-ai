from datetime import timedelta

from app.core.config import get_settings
from app.core.db import initialize_database
from app.providers.provider_resolver import get_data_provider
from app.repositories.storage import storage_repository
from app.services.clock import utc_now
from app.services.watchlist_service import watchlist_service


class BootstrapService:
    def initialize(self) -> None:
        initialize_database()
        settings = get_settings()
        if not settings.seed_demo_data:
            return
        if not settings.use_mock_providers:
            return

        if storage_repository.count_watchlist_entries() > 0:
            return

        provider = get_data_provider()
        now = utc_now()
        for index, seed in enumerate(provider.seed_watchlist()):
            added_at = (now - timedelta(days=7 - index)).isoformat()
            watchlist_service.add_company(
                company_id=int(seed["company_id"]),
                cohort=str(seed["cohort"]),
                added_at=added_at,
                seed_prior_snapshot=True,
            )


bootstrap_service = BootstrapService()
