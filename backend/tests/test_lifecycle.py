import pytest
from fastapi import HTTPException

from app.schemas.matters import CreateMatterRequest
from app.services.matter_service import MatterService


def _new(ms: MatterService, org: str = "org_alpha"):
    return ms.create_matter(
        CreateMatterRequest(fileName="c.docx", serviceTier="standard_redline", contractType="nda"),
        org,
    )


def test_legal_transition_progresses(matter_service: MatterService) -> None:
    created = _new(matter_service)
    assert matter_service.transition_status(created.matter_id, "org_alpha", "ai_review").status == "ai_review"
    assert (
        matter_service.transition_status(created.matter_id, "org_alpha", "attorney_queue").status
        == "attorney_queue"
    )


def test_illegal_transition_rejected(matter_service: MatterService) -> None:
    created = _new(matter_service)
    with pytest.raises(HTTPException) as exc_info:
        matter_service.transition_status(created.matter_id, "org_alpha", "delivered", attorney_approved=True)
    assert exc_info.value.status_code == 409


def test_events_and_activity_report(matter_service: MatterService) -> None:
    created = _new(matter_service)
    matter_service.transition_status(created.matter_id, "org_alpha", "ai_review")
    events = matter_service.list_events(created.matter_id, "org_alpha")
    assert any(ev.type in {"matter_created", "status_changed"} for ev in events)
    report = matter_service.activity_report("org_alpha")
    assert report["total"] >= 1
    assert "byStatus" in report


def test_events_isolated_by_org(matter_service: MatterService) -> None:
    created = _new(matter_service, "org_alpha")
    with pytest.raises(HTTPException) as exc_info:
        matter_service.list_events(created.matter_id, "org_beta")
    assert exc_info.value.status_code == 404
