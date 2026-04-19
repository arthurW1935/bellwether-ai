from app.schemas.discover import DiscoverResponse, ParsedFilters
from app.providers.mock_provider import mock_provider


class DiscoverService:
    def search(self, query: str) -> DiscoverResponse:
        normalized_query = query.strip()
        if not normalized_query:
            raise ValueError("Could not extract filters from query")

        return DiscoverResponse(
            companies=mock_provider.search_companies(normalized_query),
            parsed_filters=ParsedFilters(description=normalized_query),
        )


discover_service = DiscoverService()
