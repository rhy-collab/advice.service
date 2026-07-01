from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app.main import app
from app.schemas.matters import CreateMatterRequest
from app.schemas.playbook import PlaybookCheckCreate, PlaybookCreate
from app.services.auth import AuthContext, require_auth_context
from app.services.matter_service import MatterService
from app.services.playbook_service import PlaybookService
from app.services.storage_service import UploadTargetData
import app.routers.attorney as attorney_router


class FakeStorageService:
    def bucket_name(self) -> str:
        return "test-bucket"

    def create_upload_target(self, matter_id: str, file_name: str) -> UploadTargetData:
        return UploadTargetData(
            method="PUT",
            url=f"https://storage.example.test/{matter_id}/{file_name}",
            bucket="test-bucket",
            object_name=f"matters/{matter_id}/source/{file_name}",
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            mode="demo",
        )

    def create_download_url(self, bucket: str, object_name: str) -> str:
        return f"https://storage.example.test/download/{object_name}"


@pytest.fixture
def attorney_client(session_factory: sessionmaker[Session]) -> Iterator[tuple[TestClient, MatterService]]:
    service = MatterService(session_factory, storage=FakeStorageService())
    original_service = attorney_router.matter_service
    attorney_router.matter_service = service

    def auth() -> AuthContext:
        return AuthContext(
            user_id="attorney_1",
            email="attorney@example.com",
            name="Reviewing Attorney",
            organisation_id="org_alpha",
            organisation_name="Alpha Co",
            role="attorney",
        )

    app.dependency_overrides[require_auth_context] = auth

    try:
        yield TestClient(app), service
    finally:
        app.dependency_overrides.clear()
        attorney_router.matter_service = original_service


def test_attorney_queue_rejects_non_attorney() -> None:
    def auth() -> AuthContext:
        return AuthContext(
            user_id="customer_1",
            email="customer@example.com",
            name="Customer",
            organisation_id="org_alpha",
            organisation_name="Alpha Co",
            role="member",
        )

    app.dependency_overrides[require_auth_context] = auth
    try:
        response = TestClient(app).get("/v1/attorney/queue")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 403


def test_attorney_queue_lists_review_matters_for_attorney_org(
    attorney_client: tuple[TestClient, MatterService],
) -> None:
    client, service = attorney_client
    queued = _create_queued_matter(service, "org_alpha", "alpha-review.docx")
    _create_queued_matter(service, "org_beta", "beta-review.docx")
    draft = service.create_matter(
        CreateMatterRequest(fileName="draft.docx", serviceTier="standard_redline", contractType="nda"),
        "org_alpha",
    )

    response = client.get("/v1/attorney/queue")

    assert response.status_code == 200
    matter_ids = {matter["id"] for matter in response.json()["matters"]}
    assert queued.matter_id in matter_ids
    assert draft.matter_id not in matter_ids


def test_attorney_approve_route_delivers_review_matter(
    attorney_client: tuple[TestClient, MatterService],
) -> None:
    client, service = attorney_client
    queued = _create_queued_matter(service, "org_alpha", "ready-review.docx")

    response = client.post(
        f"/v1/attorney/matters/{queued.matter_id}/approve",
        json={"deliverableFileName": "ready-review-redline.docx"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["matter"]["status"] == "delivered"
    assert payload["matter"]["deliverableAvailable"] is True


def test_attorney_can_read_internal_ai_prep(
    attorney_client: tuple[TestClient, MatterService],
) -> None:
    client, service = attorney_client
    queued = _create_queued_matter(service, "org_alpha", "prep-ready.docx")

    response = client.get(f"/v1/attorney/matters/{queued.matter_id}/ai-prep")

    assert response.status_code == 200
    payload = response.json()
    assert payload["prep"]["matterId"] == queued.matter_id
    assert payload["prep"]["mode"] == "stub"
    assert payload["prep"]["issues"]
    assert payload["prep"]["issues"][0]["confidence"] in {"weak", "medium", "strong"}


def test_attorney_feedback_updates_linked_playbook_accuracy(
    attorney_client: tuple[TestClient, MatterService],
    session_factory: sessionmaker[Session],
) -> None:
    client, service = attorney_client
    playbooks = PlaybookService(session_factory)
    playbook = playbooks.create_playbook(
        PlaybookCreate(name="NDA baseline", contract_type="nda", jurisdiction="general")
    )
    playbooks.add_check(
        playbook.id,
        PlaybookCheckCreate(
            key="mutuality",
            title="Confirm NDA mutuality",
            detection="Find whether obligations are mutual.",
            severity="medium",
            remediation_intent="Make obligations reciprocal unless one-way protection is justified.",
            preferred_language="Both parties protect confidential information using reciprocal obligations.",
            acceptable_fallback="One-way obligations are acceptable only for a clear business reason.",
            unacceptable_fallback="Founder discloses sensitive information without reciprocal protection.",
        ),
    )
    queued = _create_queued_matter(service, "org_alpha", "feedback-ready.docx")

    response = client.post(
        f"/v1/attorney/matters/{queued.matter_id}/ai-prep/feedback",
        json={"issueIndex": 0, "action": "apply", "reasonTag": "correct_risk"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["matterId"] == queued.matter_id
    assert payload["playbookCheckId"] is not None
    assert payload["accuracyCorrect"] == 1
    assert payload["accuracyTotal"] == 1

    updated = playbooks.list_playbooks(contract_type="nda")[0]
    assert updated.checks[0].accuracy_correct == 1
    assert updated.checks[0].accuracy_total == 1


def test_attorney_edit_feedback_updates_playbook_fallback_language(
    attorney_client: tuple[TestClient, MatterService],
    session_factory: sessionmaker[Session],
) -> None:
    client, service = attorney_client
    playbooks = PlaybookService(session_factory)
    playbook = playbooks.create_playbook(
        PlaybookCreate(name="NDA edit baseline", contract_type="nda", jurisdiction="general")
    )
    playbooks.add_check(
        playbook.id,
        PlaybookCheckCreate(
            key="return_destroy",
            title="Check return and destruction",
            detection="Find return or destruction obligations.",
            severity="medium",
            remediation_intent="Clarify what happens to confidential information at the end.",
            preferred_language="Recipient returns or destroys confidential information on request.",
            acceptable_fallback="Original fallback.",
            unacceptable_fallback="No return or destruction obligation.",
        ),
    )
    queued = _create_queued_matter(service, "org_alpha", "edit-feedback-ready.docx")

    response = client.post(
        f"/v1/attorney/matters/{queued.matter_id}/ai-prep/feedback",
        json={
            "issueIndex": 0,
            "action": "edit",
            "reasonTag": "fallback_too_strict",
            "correctedDetail": "Accept deletion certificates where return is technically impractical.",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["accuracyCorrect"] == 0
    assert payload["accuracyTotal"] == 1

    updated = playbooks.list_playbooks(contract_type="nda")[0]
    assert updated.checks[0].acceptable_fallback == "Accept deletion certificates where return is technically impractical."


def _create_queued_matter(service: MatterService, organisation_id: str, file_name: str):
    created = service.create_matter(
        CreateMatterRequest(fileName=file_name, serviceTier="standard_redline", contractType="nda"),
        organisation_id,
    )
    service.mark_upload_complete(created.matter_id, organisation_id)
    service.mark_payment_status(created.matter_id, "paid")
    return created
