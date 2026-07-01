from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.models.intake import PublicIntakeModel
from app.models.matter import MatterFileModel, MatterModel
from app.schemas.matters import AttorneyApprovalRequest, CreateMatterRequest
from app.schemas.public import PublicIntakeRequest
from app.services.intake_service import IntakeService
from app.services.matter_service import MatterService
from app.services.retention import RetentionService


def test_retention_purges_old_public_intakes(
    session_factory: sessionmaker[Session],
    monkeypatch,
) -> None:
    monkeypatch.setenv("PUBLIC_INTAKE_RETENTION_DAYS", "30")
    intake_service = IntakeService(session_factory)
    retention = RetentionService(session_factory)
    old = intake_service.create_public_intake(
        PublicIntakeRequest(
            name="Old Lead",
            email="old@example.com",
            company="Old Co",
            contractType="vendor_saas",
            urgency="standard",
            serviceTier="standard_redline",
        )
    )
    fresh = intake_service.create_public_intake(
        PublicIntakeRequest(
            name="Fresh Lead",
            email="fresh@example.com",
            company="Fresh Co",
            contractType="vendor_saas",
            urgency="standard",
            serviceTier="standard_redline",
        )
    )

    with session_factory() as db:
        row = db.get(PublicIntakeModel, old.intake_id)
        assert row is not None
        row.created_at = datetime.now(timezone.utc) - timedelta(days=45)
        db.commit()

    report = retention.purge_expired()

    with session_factory() as db:
        assert db.get(PublicIntakeModel, old.intake_id) is None
        assert db.get(PublicIntakeModel, fresh.intake_id) is not None
    assert report.public_intakes_deleted == 1


def test_retention_purges_only_old_delivered_matter_file_refs(
    matter_service: MatterService,
    session_factory: sessionmaker[Session],
    monkeypatch,
) -> None:
    monkeypatch.setenv("MATTER_FILE_RETENTION_DAYS", "30")
    retention = RetentionService(session_factory)
    old_delivered = _delivered_matter(matter_service, "old-delivered.docx")
    fresh_delivered = _delivered_matter(matter_service, "fresh-delivered.docx")
    active = matter_service.create_matter(
        CreateMatterRequest(fileName="active.docx", serviceTier="standard_redline", contractType="vendor_saas"),
        "org_demo",
    )

    with session_factory() as db:
        old_row = db.get(MatterModel, old_delivered.matter_id)
        assert old_row is not None
        old_row.submitted_at = datetime.now(timezone.utc) - timedelta(days=45)
        db.commit()

    report = retention.purge_expired()

    with session_factory() as db:
        old_files = db.scalars(
            select(MatterFileModel).where(MatterFileModel.matter_id == old_delivered.matter_id)
        ).all()
        fresh_files = db.scalars(
            select(MatterFileModel).where(MatterFileModel.matter_id == fresh_delivered.matter_id)
        ).all()
        active_files = db.scalars(select(MatterFileModel).where(MatterFileModel.matter_id == active.matter_id)).all()

    assert old_files == []
    assert fresh_files
    assert active_files
    assert report.matter_file_refs_deleted >= 1


def _delivered_matter(matter_service: MatterService, file_name: str):
    created = matter_service.create_matter(
        CreateMatterRequest(fileName=file_name, serviceTier="standard_redline", contractType="vendor_saas"),
        "org_demo",
    )
    matter_service.mark_upload_complete(created.matter_id, "org_demo")
    matter_service.mark_payment_status(created.matter_id, "paid")
    matter_service.approve_deliverable(
        created.matter_id,
        "org_demo",
        AttorneyApprovalRequest(deliverableFileName=file_name.replace(".docx", "-redline.docx")),
    )
    return created
