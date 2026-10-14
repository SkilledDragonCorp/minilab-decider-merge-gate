"""pr.json schema and gate result types."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

Decision = Literal["allow", "deny", "escalate"]


class DiffStats(BaseModel):
    files_changed: int = 0
    additions: int = 0
    deletions: int = 0


class CiStatus(BaseModel):
    state: str = "unknown"
    conclusion: str | None = None


class OcrRipwire(BaseModel):
    findings: list[str] = Field(default_factory=list)
    risk: str | None = None


class PrSummary(BaseModel):
    title: str
    body: str | None = None
    author: str | None = None
    base_ref: str | None = None
    head_ref: str | None = None
    touched_paths: list[str] = Field(default_factory=list)
    diff_stats: DiffStats = Field(default_factory=DiffStats)
    ci_status: CiStatus | None = None
    ocr_ripwire: OcrRipwire | None = None
    extra: dict[str, Any] = Field(default_factory=dict)


class GateResult(BaseModel):
    decision: Decision
    confidence: float
    reasons: list[str]
    noul: float | None = None
    score: float | None = None
    model: str | None = None

    def exit_code(self) -> int:
        if self.decision == "allow":
            return 0
        if self.decision == "deny":
            return 1
        return 3
