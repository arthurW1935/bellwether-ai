from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.brief import (
    BriefResponse,
    RefreshRequest,
    RefreshResponse,
    TriggerRequest,
    TriggerResponse,
)
from app.schemas.common import ErrorResponse, Severity
from app.services.refresh_service import DeltaNotFoundError, refresh_service
from app.services.brief_service import brief_service


router = APIRouter(tags=["brief"])


@router.get("/brief", response_model=BriefResponse)
async def get_brief(
    min_severity: Severity = Query(default="P1"),
) -> BriefResponse:
    return brief_service.get_brief(min_severity=min_severity)


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_brief(payload: RefreshRequest | None = None) -> RefreshResponse:
    result = refresh_service.refresh(force=payload.force if payload else False)
    return RefreshResponse(**result)


@router.post(
    "/trigger",
    response_model=TriggerResponse,
    responses={404: {"model": ErrorResponse}},
)
async def trigger_delta(payload: TriggerRequest) -> TriggerResponse:
    try:
        alert = refresh_service.trigger(payload.delta_id)
    except DeltaNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "delta_not_found",
                "message": str(exc),
            },
        ) from exc

    return TriggerResponse(alert=alert)
