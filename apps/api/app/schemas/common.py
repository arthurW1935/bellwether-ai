from typing import Literal

from pydantic import BaseModel


Cohort = Literal["invested", "watching"]
AlertType = Literal[
    "talent_poaching",
    "competitive",
    "roadmap",
    "health",
    "reopen",
    "routine",
]
Severity = Literal["P0", "P1", "P2"]


class ErrorResponse(BaseModel):
    error: str
    message: str
    detail: dict | list | str | None = None


class KeyExec(BaseModel):
    name: str
    role: str

