import json
from typing import Any
import os
import re

import litellm
from litellm import completion

from app.core.config import Settings, get_settings


class LLMClientError(Exception):
    """Raised when the LLM provider returns an error or invalid output."""


class LLMClient:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    @property
    def is_configured(self) -> bool:
        return self.settings.llm_configured

    @property
    def model(self) -> str:
        return self.settings.llm_model

    @property
    def provider(self) -> str:
        return self.settings.llm_provider

    @property
    def timeout_seconds(self) -> float:
        return self.settings.llm_timeout_seconds

    def create_structured_output(
        self,
        *,
        instructions: str,
        user_input: str,
        schema_name: str,
        schema: dict[str, Any],
    ) -> dict[str, Any]:
        if not self.is_configured:
            raise LLMClientError("Gemini API key is not configured")
        if self.provider != "litellm":
            raise LLMClientError(f"Unsupported LLM provider '{self.provider}'")

        os.environ["GEMINI_API_KEY"] = self.settings.gemini_api_key
        litellm.drop_params = True
        prompt = (
            f"{instructions}\n\n"
            f"You must return valid JSON that conforms to this schema name: {schema_name}.\n"
            f"JSON schema:\n{json.dumps(schema)}\n\n"
            "Return JSON only. Do not wrap it in markdown fences.\n\n"
            f"User input:\n{user_input}"
        )

        try:
            response = completion(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a precise JSON generator."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0,
                timeout=self.timeout_seconds,
            )
        except Exception as exc:
            raise LLMClientError("LLM request failed") from exc

        try:
            text_output = response.choices[0].message.content
        except Exception as exc:
            raise LLMClientError("LLM returned an invalid completion payload") from exc
        if not text_output.strip():
            raise LLMClientError("LLM returned an empty response")

        text_output = self._strip_json_fences(text_output)
        try:
            return json.loads(text_output)
        except json.JSONDecodeError as exc:
            raise LLMClientError("LLM returned non-JSON structured output") from exc

    def _strip_json_fences(self, text: str) -> str:
        fenced = re.match(r"^\s*```(?:json)?\s*(.*?)\s*```\s*$", text, flags=re.DOTALL)
        if fenced:
            return fenced.group(1)
        return text.strip()


llm_client = LLMClient()
