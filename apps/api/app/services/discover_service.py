from app.schemas.discover import DiscoverResponse, ParsedFilters
from app.providers.provider_resolver import get_data_provider
from app.services.query_parser import query_parser_service


class DiscoverService:
    def search(self, query: str) -> DiscoverResponse:
        parsed = query_parser_service.parse(query)
        provider = get_data_provider()

        return DiscoverResponse(
            companies=provider.search_companies(
                query,
                filters=parsed.get("filters"),
            ),
            parsed_filters=ParsedFilters(description=parsed["description"]),
        )


discover_service = DiscoverService()
