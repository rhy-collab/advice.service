from __future__ import annotations

from dataclasses import dataclass
import json
import os

from app.schemas.ai import AIPrepIssue
from app.schemas.playbook import PlaybookCheck


@dataclass(frozen=True)
class GeneratedAIPrep:
    mode: str
    summary: str
    issues: list[AIPrepIssue]


class AIPrepService:
    def generate_for_uploaded_contract(
        self,
        file_name: str,
        service_tier: str,
        playbook_checks: list[PlaybookCheck] | None = None,
    ) -> GeneratedAIPrep:
        if os.getenv("ANTHROPIC_API_KEY"):
            return self._anthropic_placeholder(file_name, service_tier, playbook_checks or [])
        return self._deterministic_stub(file_name, service_tier, playbook_checks or [])

    def _deterministic_stub(
        self,
        file_name: str,
        service_tier: str,
        playbook_checks: list[PlaybookCheck] | None = None,
    ) -> GeneratedAIPrep:
        checks = playbook_checks or []
        if checks:
            return GeneratedAIPrep(
                mode="stub",
                summary=(
                    f"Internal preparation summary for {file_name}: uploaded for {service_tier}. "
                    f"Attorney review should apply {len(checks)} structured playbook check(s). "
                    "This is internal preparation only."
                ),
                issues=[
                    AIPrepIssue(
                        title=check.title,
                        severity=check.severity,
                        detail=f"{check.detection} Remediation intent: {check.remediation_intent}",
                        confidence="medium",
                        playbook_check_id=check.id,
                        playbook_check_key=check.key,
                    )
                    for check in checks
                ],
            )

        return GeneratedAIPrep(
            mode="stub",
            summary=(
                f"Internal preparation summary for {file_name}: uploaded for {service_tier}. "
                "Attorney review should focus on commercial risk, liability allocation, payment mechanics, "
                "termination rights, and any missing operational detail. This is internal preparation only."
            ),
            issues=[
                AIPrepIssue(
                    title="Check limitation of liability",
                    severity="high",
                    detail="Confirm whether the liability cap matches the commercial value and excludes appropriate carve-outs.",
                    confidence="medium",
                ),
                AIPrepIssue(
                    title="Check termination mechanics",
                    severity="medium",
                    detail="Confirm notice periods, cure rights, and post-termination obligations are workable.",
                    confidence="medium",
                ),
                AIPrepIssue(
                    title="Check confidentiality and data handling",
                    severity="medium",
                    detail="Confirm confidentiality, security, and return/deletion obligations match the transaction.",
                    confidence="weak",
                ),
            ],
        )

    def _anthropic_placeholder(
        self,
        file_name: str,
        service_tier: str,
        playbook_checks: list[PlaybookCheck],
    ) -> GeneratedAIPrep:
        # The integration boundary is intentionally isolated here. Until the
        # Anthropic client and document retrieval path are wired, production
        # keeps deterministic behavior rather than making an unreviewed call.
        generated = self._deterministic_stub(file_name, service_tier, playbook_checks)
        return GeneratedAIPrep(mode="anthropic", summary=generated.summary, issues=generated.issues)


def issues_to_json(issues: list[AIPrepIssue]) -> str:
    return json.dumps([issue.model_dump() for issue in issues], separators=(",", ":"))


def issues_from_json(value: str) -> list[AIPrepIssue]:
    return [AIPrepIssue(**item) for item in json.loads(value)]


ai_prep_service = AIPrepService()
