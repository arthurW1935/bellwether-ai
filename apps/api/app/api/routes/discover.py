from fastapi import APIRouter, HTTPException, status

from app.clients.crustdata import CrustdataClientError
from app.schemas.discover import DiscoverRequest, DiscoverResponse
from app.services.discover_service import discover_service


router = APIRouter(prefix="/discover", tags=["discover"])


@router.post("", response_model=DiscoverResponse)
async def discover_companies(payload: DiscoverRequest) -> DiscoverResponse:
    try:
        return discover_service.search(payload.query)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "query_unparseable",
                "message": str(exc),
            },
        ) from exc
    except CrustdataClientError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "upstream_unavailable",
                "message": str(exc),
            },
        ) from exc
