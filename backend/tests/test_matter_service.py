import pytest
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.models.matter import MatterAIPrepModel, MatterFileModel
from app.services.matter_service import MatterService


def test_delivery_requires_attorney_approval(matter_service: MatterService) -> None:
    with pytest.raises(HTTPException) as exc_info:
        matter_service.transition_status("matter_demo_1", "org_demo", "delivered")

    assert exc_info.value.status_code == 409


def test_delivery_allowed_after_attorney_approval(matter_service: MatterService) -> None:
    matter = matter_service.transition_status(
        "matter_demo_1",
        "org_demo",
        "delivered",
        attorney_approved=True,
    )

    assert matter.status == "delivered"
    assert matter.deliverable_available is True


def test_created_matter_persists_in_database(matter_service: MatterService) -> None:
    from app.schemas.matters import CreateMatterRequest

    created = matter_service.create_matter(
        CreateMatterRequest(
            fileName="persistent-contract.docx",
            serviceTier="standard_redline",
            contractType="vendor_saas",
            notes="Focus on limitation of liability.",
        ),
        "org_demo",
    )

    matters = matter_service.list_matters("org_demo")

    assert created.matter_id in {matter.id for matter in matters}
    assert any(matter.file_name == "persistent-contract.docx" for matter in matters)
    assert created.upload.mode == "demo"
    assert created.upload.url.endswith("/persistent-contract.docx")
    created_summary = next(matter for matter in matters if matter.id == created.matter_id)
    assert created_summary.upload_status == "awaiting_upload"
    assert created_summary.payment_status == "unpaid"


def test_created_matter_records_source_file(
    matter_service: MatterService,
    session_factory: sessionmaker[Session],
) -> None:
    from app.schemas.matters import CreateMatterRequest

    created = matter_service.create_matter(
        CreateMatterRequest(
            fileName="stored-contract.docx",
            serviceTier="standard_redline",
            contractType="vendor_saas",
        ),
        "org_demo",
    )

    detail = matter_service.get_matter(created.matter_id, "org_demo")

    assert detail is not None
    assert any(event.type == "matter_created" for event in detail.events)

    with session_factory() as db:
        source_file = db.scalar(
            select(MatterFileModel).where(
                MatterFileModel.matter_id == created.matter_id,
                MatterFileModel.role == "source_contract",
            )
        )

    assert source_file is not None
    assert source_file.file_name == "stored-contract.docx"
    assert source_file.storage_bucket == "test-bucket"
    assert source_file.storage_object == f"matters/{created.matter_id}/source/stored-contract.docx"
    assert source_file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def test_upload_complete_updates_matter_and_timeline(matter_service: MatterService) -> None:
    from app.schemas.matters import CreateMatterRequest

    created = matter_service.create_matter(
        CreateMatterRequest(
            fileName="uploaded-contract.docx",
            serviceTier="standard_redline",
            contractType="vendor_saas",
        ),
        "org_demo",
    )

    matter = matter_service.mark_upload_complete(created.matter_id, "org_demo")
    detail = matter_service.get_matter(created.matter_id, "org_demo")

    assert matter.upload_status == "uploaded"
    assert matter.status == "attorney_queue"
    assert detail is not None
    assert any(event.type == "upload_completed" for event in detail.events)
    assert any(event.type == "ai_prep_completed" for event in detail.events)


def test_checkout_and_payment_updates_matter_state(matter_service: MatterService) -> None:
    from app.schemas.matters import CreateMatterRequest

    created = matter_service.create_matter(
        CreateMatterRequest(
            fileName="paid-contract.docx",
            serviceTier="standard_redline",
            contractType="vendor_saas",
        ),
        "org_demo",
    )

    checkout_pending = matter_service.mark_checkout_created(created.matter_id, "org_demo", "cs_test_123")
    paid = matter_service.mark_payment_status(created.matter_id, "paid", checkout_session_id="cs_test_123")
    detail = matter_service.get_matter(created.matter_id, "org_demo")

    assert checkout_pending.payment_status == "checkout_pending"
    assert paid is not None
    assert paid.payment_status == "paid"
    assert detail is not None
    assert any(event.type == "checkout_created" for event in detail.events)
    assert any(event.type == "payment_paid" for event in detail.events)


def test_attorney_approval_requires_upload_and_payment(matter_service: MatterService) -> None:
    from app.schemas.matters import AttorneyApprovalRequest, CreateMatterRequest

    created = matter_service.create_matter(
        CreateMatterRequest(
            fileName="not-ready-contract.docx",
            serviceTier="standard_redline",
            contractType="vendor_saas",
        ),
        "org_demo",
    )

    with pytest.raises(HTTPException) as exc_info:
        matter_service.approve_deliverable(
            created.matter_id,
            "org_demo",
            AttorneyApprovalRequest(deliverableFileName="not-ready-redline.docx"),
        )

    assert exc_info.value.status_code == 409


def test_attorney_approval_records_deliverable_and_enables_download(
    matter_service: MatterService,
    session_factory: sessionmaker[Session],
) -> None:
    from app.schemas.matters import AttorneyApprovalRequest, CreateMatterRequest

    created = matter_service.create_matter(
        CreateMatterRequest(
            fileName="ready-contract.docx",
            serviceTier="standard_redline",
            contractType="vendor_saas",
        ),
        "org_demo",
    )
    matter_service.mark_upload_complete(created.matter_id, "org_demo")
    matter_service.mark_payment_status(created.matter_id, "paid")
    notifications_before = len(matter_service._notifications.sent_notifications)

    delivered = matter_service.approve_deliverable(
        created.matter_id,
        "org_demo",
        AttorneyApprovalRequest(deliverableFileName="ready-contract-redline.docx"),
    )
    detail = matter_service.get_matter(created.matter_id, "org_demo")
    download_url = matter_service.delivery_download_url(created.matter_id, "org_demo")

    assert delivered.status == "delivered"
    assert delivered.deliverable_available is True
    assert delivered.next_update_eta_minutes is None
    assert download_url.endswith(f"/matters/{created.matter_id}/deliverables/ready-contract-redline.docx")
    assert detail is not None
    assert any(event.type == "attorney_approved" for event in detail.events)
    notification = matter_service._notifications.sent_notifications[-1]
    assert len(matter_service._notifications.sent_notifications) == notifications_before + 1
    assert notification.status == "delivered"
    assert notification.channel == "log"
    assert "ready-contract" not in notification.subject
    assert "ready-contract" not in notification.body

    with session_factory() as db:
        deliverable = db.scalar(
            select(MatterFileModel).where(
                MatterFileModel.matter_id == created.matter_id,
                MatterFileModel.role == "approved_redline",
            )
        )

    assert deliverable is not None
    assert deliverable.file_name == "ready-contract-redline.docx"
    assert deliverable.storage_bucket == "test-bucket"
    assert deliverable.storage_object == f"matters/{created.matter_id}/deliverables/ready-contract-redline.docx"


def test_upload_completion_creates_internal_ai_prep(
    matter_service: MatterService,
    session_factory: sessionmaker[Session],
) -> None:
    from app.schemas.matters import CreateMatterRequest

    created = matter_service.create_matter(
        CreateMatterRequest(
            fileName="prep-contract.docx",
            serviceTier="standard_redline",
            contractType="vendor_saas",
        ),
        "org_demo",
    )

    matter = matter_service.mark_upload_complete(created.matter_id, "org_demo")
    prep = matter_service.get_latest_ai_prep(created.matter_id, "org_demo")
    customer_detail = matter_service.get_matter(created.matter_id, "org_demo")

    assert matter.status == "attorney_queue"
    assert prep.mode == "stub"
    assert "Internal preparation summary" in prep.summary
    assert prep.issues
    assert customer_detail is not None
    assert "prep" not in customer_detail.model_dump(by_alias=True)

    with session_factory() as db:
        prep_rows = db.scalars(
            select(MatterAIPrepModel).where(MatterAIPrepModel.matter_id == created.matter_id)
        ).all()

    assert len(prep_rows) == 1


def test_ai_prep_is_org_scoped(matter_service: MatterService) -> None:
    from app.schemas.matters import CreateMatterRequest

    created = matter_service.create_matter(
        CreateMatterRequest(fileName="scoped-prep.docx", serviceTier="standard_redline", contractType="vendor_saas"),
        "org_demo",
    )
    matter_service.mark_upload_complete(created.matter_id, "org_demo")

    with pytest.raises(HTTPException) as exc_info:
        matter_service.get_latest_ai_prep(created.matter_id, "org_other")

    assert exc_info.value.status_code == 404


def test_download_rejected_before_attorney_approval(matter_service: MatterService) -> None:
    from app.schemas.matters import CreateMatterRequest

    created = matter_service.create_matter(
        CreateMatterRequest(
            fileName="undelivered-contract.docx",
            serviceTier="standard_redline",
            contractType="vendor_saas",
        ),
        "org_demo",
    )

    with pytest.raises(HTTPException) as exc_info:
        matter_service.delivery_download_url(created.matter_id, "org_demo")

    assert exc_info.value.status_code == 409


def test_matter_is_isolated_by_organisation(matter_service: MatterService) -> None:
    from app.schemas.matters import CreateMatterRequest

    created = matter_service.create_matter(
        CreateMatterRequest(
            fileName="alpha-secret.docx",
            serviceTier="standard_redline",
            contractType="vendor_saas",
        ),
        "org_alpha",
    )

    # A different organisation must not see it.
    assert matter_service.get_matter(created.matter_id, "org_beta") is None
    assert all(m.id != created.matter_id for m in matter_service.list_matters("org_beta"))

    # The owning organisation can.
    assert matter_service.get_matter(created.matter_id, "org_alpha") is not None
