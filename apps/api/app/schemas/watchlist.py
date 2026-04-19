from pydantic import BaseModel, Field

from app.schemas.common import Cohort, ErrorResponse, KeyExec


class Company(BaseModel):
    id: int
    name: str
    domain: str
    cohort: Cohort
    headcount: int | None = None
    last_funding: str | None = None
    key_execs: list[KeyExec] = Field(default_factory=list)
    added_at: str


class WatchlistResponse(BaseModel):
    companies: list[Company]


class WatchlistAddRequest(BaseModel):
    company_id: int
    cohort: Cohort


class WatchlistCompanyResponse(BaseModel):
    company: Company


class RemoveWatchlistRequest(BaseModel):
    company_id: int


class RemoveWatchlistResponse(BaseModel):
    removed: bool


__all__ = [
    "Company",
    "ErrorResponse",
    "RemoveWatchlistRequest",
    "RemoveWatchlistResponse",
    "WatchlistAddRequest",
    "WatchlistCompanyResponse",
    "WatchlistResponse",
]

