from fastapi import APIRouter

from app.core.config import get_settings


router = APIRouter(tags=["health"])


@router.get("/health")
async def healthcheck() -> dict[str, object]:
    settings = get_settings()
    return {"ok": True, "version": settings.app_version}

