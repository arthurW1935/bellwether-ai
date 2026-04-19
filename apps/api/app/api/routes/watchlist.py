from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.common import Cohort
from app.schemas.watchlist import (
    ErrorResponse,
    RemoveWatchlistRequest,
    RemoveWatchlistResponse,
    WatchlistAddRequest,
    WatchlistCompanyResponse,
    WatchlistResponse,
)
from app.services.watchlist_service import (
    AlreadyInWatchlistError,
    CompanyNotFoundError,
    watchlist_service,
)


router = APIRouter(prefix="/watchlist", tags=["watchlist"])


@router.get("", response_model=WatchlistResponse)
async def get_watchlist(
    cohort: Cohort | None = Query(default=None),
) -> WatchlistResponse:
    return WatchlistResponse(companies=watchlist_service.list_companies(cohort=cohort))


@router.post(
    "/add",
    response_model=WatchlistCompanyResponse,
    responses={
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
async def add_to_watchlist(payload: WatchlistAddRequest) -> WatchlistCompanyResponse:
    try:
        company = watchlist_service.add_company(
            company_id=payload.company_id,
            cohort=payload.cohort,
        )
    except CompanyNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "company_not_found",
                "message": str(exc),
            },
        ) from exc
    except AlreadyInWatchlistError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "already_in_watchlist",
                "message": str(exc),
            },
        ) from exc

    return WatchlistCompanyResponse(company=company)


@router.post(
    "/remove",
    response_model=RemoveWatchlistResponse,
    responses={404: {"model": ErrorResponse}},
)
async def remove_from_watchlist(
    payload: RemoveWatchlistRequest,
) -> RemoveWatchlistResponse:
    try:
        watchlist_service.remove_company(company_id=payload.company_id)
    except CompanyNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "company_not_found",
                "message": str(exc),
            },
        ) from exc

    return RemoveWatchlistResponse(removed=True)
