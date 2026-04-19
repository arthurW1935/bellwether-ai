from app.core.config import Settings, get_settings


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


llm_client = LLMClient()
