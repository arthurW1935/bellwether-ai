from pydantic import BaseModel, Field

from app.schemas.common import AlertType, Cohort, Severity
from app.schemas.watchlist import Company


class TraceStep(BaseModel):
    stage: str
    summary: str
    duration_ms: int
    detail: dict | None = None


class Delta(BaseModel):
    kind: str
    description: str
    before: dict | str | int | None = None
    after: dict | str | int | None = None


class Alert(BaseModel):
    id: int
    company: Company
    cohort: Cohort
    delta: Delta
    alert_type: AlertType
    severity: Severity
    explanation: str
    recommended_action: str
    trace: list[TraceStep] = Field(default_factory=list)
    detected_at: str


class BriefCounts(BaseModel):
    p0: int
    p1: int
    p2: int


class BriefResponse(BaseModel):
    summary: str
    generated_at: str
    alerts: list[Alert] = Field(default_factory=list)
    counts: BriefCounts


class CompanyAlertsResponse(BaseModel):
    company: Company
    alerts: list[Alert] = Field(default_factory=list)


class RefreshRequest(BaseModel):
    force: bool = False


class RefreshResponse(BaseModel):
    brief: BriefResponse
    duration_ms: int
    companies_processed: int
    alerts_generated: int


class TriggerRequest(BaseModel):
    delta_id: str


class TriggerResponse(BaseModel):
    alert: Alert
