from __future__ import annotations

from dataclasses import dataclass

from app.schemas.ai import AIPrepIssue


@dataclass(frozen=True)
class DraftDeliverable:
    redline_file_name: str
    redline_storage_object: str
    cover_letter_file_name: str
    cover_letter_storage_object: str
    cover_letter_body: str


class DeliverableService:
    def generate_internal_draft(
        self,
        matter_id: str,
        source_file_name: str,
        issues: list[AIPrepIssue],
    ) -> DraftDeliverable:
        base_name = source_file_name.rsplit(".", 1)[0]
        redline_file_name = f"{base_name}-internal-redline.docx"
        cover_letter_file_name = f"{base_name}-cover-letter.txt"
        return DraftDeliverable(
            redline_file_name=redline_file_name,
            redline_storage_object=f"matters/{matter_id}/internal/{redline_file_name}",
            cover_letter_file_name=cover_letter_file_name,
            cover_letter_storage_object=f"matters/{matter_id}/internal/{cover_letter_file_name}",
            cover_letter_body=self._cover_letter(source_file_name, issues),
        )

    def _cover_letter(self, source_file_name: str, issues: list[AIPrepIssue]) -> str:
        lines = [
            f"Internal cover letter for {source_file_name}",
            "",
            "This draft is for attorney review only. It is intentionally over-inclusive.",
            "",
            "Key changes and risk rationale:",
        ]
        for issue in issues:
            fallback = f" Playbook check: {issue.playbook_check_key}." if issue.playbook_check_key else ""
            lines.append(f"- {issue.title} ({issue.severity}, {issue.confidence} confidence): {issue.detail}{fallback}")
        lines.extend(
            [
                "",
                "Suggested fallback position:",
                "Prioritise preserving the client's commercial position while offering narrower wording where risk is acceptable.",
            ]
        )
        return "\n".join(lines)


deliverable_service = DeliverableService()
