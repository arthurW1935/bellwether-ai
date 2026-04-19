from typing import Any

import httpx

from app.core.config import Settings, get_settings


class CrustdataClientError(Exception):
    """Raised when Crustdata returns an error or an invalid response."""


class CrustdataClient:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    @property
    def is_configured(self) -> bool:
        return self.settings.crustdata_configured

    @property
    def base_url(self) -> str:
        return self.settings.crustdata_base_url.rstrip("/")

    def headers(self, auth_scheme: str | None = None) -> dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.settings.crustdata_api_key.strip():
            scheme = auth_scheme or self.settings.crustdata_auth_scheme
            headers["Authorization"] = (
                f"{scheme} "
                f"{self.settings.crustdata_api_key}"
            )
        return headers

    @property
    def timeout(self) -> httpx.Timeout:
        return httpx.Timeout(self.settings.crustdata_timeout_seconds)

    def build_url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    def _request(
        self,
        *,
        method: str,
        path: str,
        json_body: dict[str, Any] | None = None,
        params: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        if not self.is_configured:
            raise CrustdataClientError("Crustdata API key is not configured")

        try:
            response = self._request_with_auth_fallback(
                method=method,
                path=path,
                json_body=json_body,
                params=params,
            )
        except httpx.HTTPStatusError as exc:
            raise CrustdataClientError(
                f"Crustdata request failed with status {exc.response.status_code}"
            ) from exc
        except httpx.HTTPError as exc:
            raise CrustdataClientError("Crustdata request failed") from exc

        try:
            payload = response.json()
        except ValueError as exc:
            raise CrustdataClientError("Crustdata returned invalid JSON") from exc

        if isinstance(payload, dict):
            return payload
        return {"data": payload}

    def _request_with_auth_fallback(
        self,
        *,
        method: str,
        path: str,
        json_body: dict[str, Any] | None,
        params: dict[str, str] | None,
    ) -> httpx.Response:
        schemes = [self.settings.crustdata_auth_scheme]
        alternate = "Token" if self.settings.crustdata_auth_scheme == "Bearer" else "Bearer"
        if alternate not in schemes:
            schemes.append(alternate)

        last_response: httpx.Response | None = None
        with httpx.Client(timeout=self.timeout) as client:
            for scheme in schemes:
                response = client.request(
                    method=method,
                    url=self.build_url(path),
                    headers=self.headers(scheme),
                    json=json_body,
                    params=params,
                )
                last_response = response
                if response.status_code != 401:
                    response.raise_for_status()
                    return response

        if last_response is None:
            raise CrustdataClientError("Crustdata request failed before a response was returned")
        last_response.raise_for_status()
        return last_response

    def search_companies(
        self, filters: list[dict[str, Any]], page: int = 1
    ) -> dict[str, Any]:
        payload = {"filters": filters, "page": page}
        return self._request(
            method="POST",
            path="/screener/company/search",
            json_body=payload,
        )

    def enrich_companies(
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

        return self._request(
            method="GET",
            path="/screener/company",
            params=params,
        )

    def search_people(
        self, filters: list[dict[str, Any]], page: int = 1
    ) -> dict[str, Any]:
        payload = {"filters": filters, "page": page}
        return self._request(
            method="POST",
            path="/screener/person/search",
            json_body=payload,
        )

    def enrich_people(self, linkedin_urls: list[str]) -> dict[str, Any]:
        params = {"linkedin_profile_url": ",".join(linkedin_urls)}
        return self._request(
            method="GET",
            path="/screener/person/enrich",
            params=params,
        )


crustdata_client = CrustdataClient()
