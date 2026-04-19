from typing import Any
import re

from app.clients.llm import LLMClientError, llm_client


QUERY_PARSER_SCHEMA = {
    "type": "object",
    "properties": {
        "description": {"type": "string"},
        "filters": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "filter_type": {"type": "string"},
                    "type": {"type": "string"},
                    "value": {
                        "anyOf": [
                            {"type": "array", "items": {"type": "string"}},
                            {
                                "type": "object",
                                "properties": {
                                    "min": {"type": "number"},
                                    "max": {"type": "number"},
                                },
                                "required": ["min", "max"],
                                "additionalProperties": False,
                            },
                        ]
                    },
                    "sub_filter": {"type": "string"},
                },
                "required": ["filter_type", "type", "value"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["description", "filters"],
    "additionalProperties": False,
}

QUERY_PARSER_INSTRUCTIONS = """You convert a VC thesis into Crustdata company search filters.
Return JSON only.
Use only these filter types when relevant:
- REGION with type in or not in and value as a list of regions
- INDUSTRY with type in or not in and value as a list of industries
- COMPANY_HEADCOUNT with type in and value as a list of headcount buckets
- COMPANY_HEADCOUNT_GROWTH with type between and value with min/max percentages
- ANNUAL_REVENUE with type between and value with min/max and optional sub_filter currency
- ACCOUNT_ACTIVITIES with type in and value list
- JOB_OPPORTUNITIES with type in and value list
- KEYWORD with type in and value as a single-item list
Prefer precise filters. If the query is broad or ambiguous, include a KEYWORD filter with the full thesis text."""


class QueryParserService:
    def parse(self, query: str) -> dict[str, Any]:
        normalized_query = query.strip()
        if not normalized_query:
            raise ValueError("Could not extract filters from query")

        if llm_client.is_configured:
            try:
                parsed = llm_client.create_structured_output(
                    instructions=QUERY_PARSER_INSTRUCTIONS,
                    user_input=normalized_query,
                    schema_name="crustdata_company_search_filters",
                    schema=QUERY_PARSER_SCHEMA,
                )
                if parsed.get("filters"):
                    return parsed
            except LLMClientError:
                pass

        return self._heuristic_parse(normalized_query)

    def _heuristic_parse(self, query: str) -> dict[str, Any]:
        lowered = query.lower()
        filters: list[dict[str, Any]] = []

        if "india" in lowered:
            filters.append(
                {"filter_type": "REGION", "type": "in", "value": ["India"]}
            )
        if "united states" in lowered or "usa" in lowered or "us " in lowered:
            filters.append(
                {"filter_type": "REGION", "type": "in", "value": ["United States"]}
            )

        industry_map = {
            "fintech": "Financial Services",
            "saas": "Software",
            "software": "Software",
            "ai": "Artificial Intelligence",
            "space": "Aviation and Aerospace",
            "health": "Hospital & Health Care",
        }
        industries = [
            mapped for keyword, mapped in industry_map.items() if keyword in lowered
        ]
        if industries:
            filters.append(
                {"filter_type": "INDUSTRY", "type": "in", "value": sorted(set(industries))}
            )

        growth_match = re.search(r"(\d+)\s*%.*headcount growth", lowered)
        if growth_match:
            growth = int(growth_match.group(1))
            filters.append(
                {
                    "filter_type": "COMPANY_HEADCOUNT_GROWTH",
                    "type": "between",
                    "value": {"min": growth, "max": 1000},
                }
            )

        headcount_match = re.search(r"(\d+)\+?\s*(employees|employee)", lowered)
        if headcount_match:
            employees = int(headcount_match.group(1))
            bucket = self._headcount_bucket(employees)
            if bucket is not None:
                filters.append(
                    {"filter_type": "COMPANY_HEADCOUNT", "type": "in", "value": [bucket]}
                )

        if "hiring" in lowered:
            filters.append(
                {"filter_type": "JOB_OPPORTUNITIES", "type": "in", "value": ["Hiring"]}
            )
        if "funding" in lowered or "raised" in lowered:
            filters.append(
                {
                    "filter_type": "ACCOUNT_ACTIVITIES",
                    "type": "in",
                    "value": ["Funding events in past 12 months"],
                }
            )

        if not filters:
            filters.append(
                {"filter_type": "KEYWORD", "type": "in", "value": [query]}
            )

        return {"description": query, "filters": filters}

    def _headcount_bucket(self, employees: int) -> str | None:
        if employees <= 10:
            return "1-10"
        if employees <= 50:
            return "11-50"
        if employees <= 200:
            return "51-200"
        if employees <= 500:
            return "201-500"
        if employees <= 1000:
            return "501-1,000"
        if employees <= 5000:
            return "1,001-5,000"
        if employees <= 10000:
            return "5,001-10,000"
        return "10,001+"


query_parser_service = QueryParserService()
