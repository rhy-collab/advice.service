from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from app.schemas.ai import AIPrepIssue

RiskRoute = Literal["fast_track", "standard_review", "escalate"]


@dataclass(frozen=True)
class RiskAssessment:
    score: int
    route: RiskRoute


class RiskService:
    def assess(self, issues: list[AIPrepIssue]) -> RiskAssessment:
        score = sum(self._issue_score(issue) for issue in issues)
        if score <= 3:
            route: RiskRoute = "fast_track"
        elif score >= 7:
            route = "escalate"
        else:
            route = "standard_review"
        return RiskAssessment(score=score, route=route)

    def _issue_score(self, issue: AIPrepIssue) -> int:
        severity_weight = {"low": 1, "medium": 2, "high": 3, "critical": 4}[issue.severity]
        confidence_weight = {"strong": 0, "medium": 1, "weak": 2}[issue.confidence]
        return severity_weight + confidence_weight


risk_service = RiskService()
