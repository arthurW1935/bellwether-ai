from fastapi import APIRouter, HTTPException, status

from app.schemas.brief import CompanyAlertsResponse
from app.schemas.watchlist import ErrorResponse
from app.services.brief_service import brief_service
from app.services.watchlist_service import CompanyNotFoundError


router = APIRouter(prefix="/companies", tags=["companies"])


@router.get(
    "/{company_id}/alerts",
    response_model=CompanyAlertsResponse,
    responses={404: {"model": ErrorResponse}},
)
async def get_company_alerts(company_id: int) -> CompanyAlertsResponse:
    try:
        return brief_service.get_company_alerts(company_id)
    except CompanyNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "company_not_found",
                "message": str(exc),
            },
        ) from exc
