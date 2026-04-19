from app.core.config import get_settings
from app.providers.live_provider import live_provider
from app.providers.mock_provider import mock_provider


def get_data_provider():
    settings = get_settings()
    if settings.use_mock_providers or not settings.crustdata_configured:
        return mock_provider
    return live_provider
