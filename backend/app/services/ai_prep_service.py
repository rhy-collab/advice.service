from __future__ import annotations

from dataclasses import dataclass
import json
import os
from urllib import request

from app.schemas.ai import AIPrepIssue
from app.schemas.playbook import PlaybookCheck


@dataclass(frozen=True)
class GeneratedAIPrep:
    mode: str
    summary: str
    issues: list[AIPrepIssue]


class AnthropicMessageClient:
    def create_message(self, payload: dict) -> dict:
        api_key = os.environ["ANTHROPIC_API_KEY"]
        base_url = os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com")
        req = request.Request(
            f"{base_url.rstrip('/')}/v1/messages",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "content-type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": os.getenv("ANTHROPIC_VERSION", "2023-06-01"),
            },
            method="POST",
        )
        with request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))


class AIPrepService:
    def __init__(self, anthropic_client: AnthropicMessageClient | None = None) -> None:
        self._anthropic_client = anthropic_client or AnthropicMessageClient()

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
        payload = {
            "model": os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
            "max_tokens": 1200,
            "system": (
                "You are preparing internal attorney work product for Charter Law. "
                "Return only compact JSON with keys summary and issues. "
                "Issues must be over-inclusive, attorney-facing, and not customer advice."
            ),
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(
                                {
                                    "file_name": file_name,
                                    "service_tier": service_tier,
                                    "playbook_checks": [
                                        {
                                            "id": check.id,
                                            "key": check.key,
                                            "title": check.title,
                                            "detection": check.detection,
                                            "severity": check.severity,
                                            "remediation_intent": check.remediation_intent,
                                        }
                                        for check in playbook_checks
                                    ],
                                    "required_issue_fields": [
                                        "title",
                                        "severity",
                                        "detail",
                                        "confidence",
                                        "playbook_check_id",
                                        "playbook_check_key",
                                    ],
                                },
                                separators=(",", ":"),
                            ),
                        }
                    ],
                }
            ],
        }
        response = self._anthropic_client.create_message(payload)
        return self._parse_anthropic_response(response, file_name, service_tier, playbook_checks)

    def _parse_anthropic_response(
        self,
        response: dict,
        file_name: str,
        service_tier: str,
        playbook_checks: list[PlaybookCheck],
    ) -> GeneratedAIPrep:
        text = "".join(part.get("text", "") for part in response.get("content", []) if part.get("type") == "text")
        try:
            raw = json.loads(text)
        except json.JSONDecodeError:
            fallback = self._deterministic_stub(file_name, service_tier, playbook_checks)
            return GeneratedAIPrep(mode="anthropic", summary=fallback.summary, issues=fallback.issues)

        issues = [
            AIPrepIssue(
                title=item["title"],
                severity=item["severity"],
                detail=item["detail"],
                confidence=item["confidence"],
                playbook_check_id=item.get("playbook_check_id"),
                playbook_check_key=item.get("playbook_check_key"),
            )
            for item in raw.get("issues", [])
        ]
        if not issues:
            issues = self._deterministic_stub(file_name, service_tier, playbook_checks).issues
        return GeneratedAIPrep(mode="anthropic", summary=raw.get("summary", ""), issues=issues)


def issues_to_json(issues: list[AIPrepIssue]) -> str:
    return json.dumps([issue.model_dump() for issue in issues], separators=(",", ":"))


def issues_from_json(value: str) -> list[AIPrepIssue]:
    return [AIPrepIssue(**item) for item in json.loads(value)]


ai_prep_service = AIPrepService()
