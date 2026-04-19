from pydantic import BaseModel, Field

from app.schemas.watchlist import Company


class DiscoverRequest(BaseModel):
    query: str


class ParsedFilters(BaseModel):
    description: str


class DiscoverResponse(BaseModel):
    companies: list[Company] = Field(default_factory=list)
    parsed_filters: ParsedFilters

