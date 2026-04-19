from typing import Any

import httpx

from app.core.config import Settings, get_settings


class CrustdataClient:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    @property
    def is_configured(self) -> bool:
        return self.settings.crustdata_configured

    @property
    def base_url(self) -> str:
        return self.settings.crustdata_base_url.rstrip("/")

    @property
    def headers(self) -> dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.settings.crustdata_api_key.strip():
            headers["Authorization"] = (
                f"{self.settings.crustdata_auth_scheme} "
                f"{self.settings.crustdata_api_key}"
            )
        return headers

    @property
    def timeout(self) -> httpx.Timeout:
        return httpx.Timeout(self.settings.crustdata_timeout_seconds)

    def build_url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    async def search_companies(
        self, filters: list[dict[str, Any]], page: int = 1
    ) -> dict[str, Any]:
        payload = {"filters": filters, "page": page}
        return {
            "configured": self.is_configured,
            "request": {
                "method": "POST",
                "url": self.build_url("/screener/company/search"),
                "headers": self.headers,
                "json": payload,
            },
        }

    async def enrich_companies(
        self,
        *,
        company_ids: list[int] | None = None,
        domains: list[str] | None = None,
        fields: list[str] | None = None,
    ) -> dict[str, Any]:
        params: dict[str, str] = {}
        if company_ids:
            params["company_id"] = ",".join(str(company_id) for company_id in company_ids)
        if domains:
            params["company_domain"] = ",".join(domains)
        if fields:
            params["fields"] = ",".join(fields)

        return {
            "configured": self.is_configured,
            "request": {
                "method": "GET",
                "url": self.build_url("/screener/company"),
                "headers": self.headers,
                "params": params,
            },
        }

    async def search_people(
        self, filters: list[dict[str, Any]], page: int = 1
    ) -> dict[str, Any]:
        payload = {"filters": filters, "page": page}
        return {
            "configured": self.is_configured,
            "request": {
                "method": "POST",
                "url": self.build_url("/screener/person/search"),
                "headers": self.headers,
                "json": payload,
            },
        }

    async def enrich_people(self, linkedin_urls: list[str]) -> dict[str, Any]:
        params = {"linkedin_profile_url": ",".join(linkedin_urls)}
        return {
            "configured": self.is_configured,
            "request": {
                "method": "GET",
                "url": self.build_url("/screener/person/enrich"),
                "headers": self.headers,
                "params": params,
            },
        }


crustdata_client = CrustdataClient()
