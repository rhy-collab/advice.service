from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.models.intake import PublicIntakeModel
from app.models.matter import MatterFileModel, MatterModel
from app.schemas.matters import AttorneyApprovalRequest, CreateMatterRequest
from app.schemas.public import PublicIntakeRequest
from app.services.auth import AuthContext, require_auth_context
from app.services.intake_service import IntakeService
from app.services.matter_service import MatterService
from app.services.retention import RetentionService
import app.routers.attorney as attorney_router


class DeletingStorage:
    def __init__(self) -> None:
        self.deleted: list[tuple[str, str]] = []

    def delete_object(self, bucket: str, object_name: str) -> bool:
        self.deleted.append((bucket, object_name))
        return True


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
    storage = DeletingStorage()
    retention = RetentionService(session_factory, storage=storage)  # type: ignore[arg-type]
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
    assert report.storage_objects_deleted == report.matter_file_refs_deleted
    assert storage.deleted
    assert all("old-delivered" in object_name for _, object_name in storage.deleted)


def test_attorney_retention_purge_endpoint_requires_attorney_and_runs(
    session_factory: sessionmaker[Session],
    monkeypatch,
) -> None:
    monkeypatch.setenv("PUBLIC_INTAKE_RETENTION_DAYS", "0")
    original_service = attorney_router.retention_service
    attorney_router.retention_service = RetentionService(session_factory, storage=DeletingStorage())  # type: ignore[arg-type]

    def attorney_auth() -> AuthContext:
        return AuthContext(
            user_id="attorney",
            email="attorney@example.com",
            name="Attorney",
            organisation_id="org_demo",
            organisation_name="Demo",
            role="attorney",
        )

    app.dependency_overrides[require_auth_context] = attorney_auth
    try:
        response = TestClient(app).post("/v1/attorney/retention/purge")
    finally:
        app.dependency_overrides.clear()
        attorney_router.retention_service = original_service

    assert response.status_code == 200
    assert set(response.json()) == {
        "public_intakes_deleted",
        "matter_file_refs_deleted",
        "storage_objects_deleted",
    }


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
