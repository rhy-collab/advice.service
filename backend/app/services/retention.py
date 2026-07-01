from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import os

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, sessionmaker

from app.db.session import SessionLocal
from app.models.intake import PublicIntakeModel
from app.models.matter import MatterFileModel, MatterModel
from app.services.storage_service import StorageService, storage_service


@dataclass(frozen=True)
class RetentionReport:
    public_intakes_deleted: int
    matter_file_refs_deleted: int
    storage_objects_deleted: int


class RetentionService:
    def __init__(
        self,
        session_factory: sessionmaker[Session] = SessionLocal,
        storage: StorageService = storage_service,
    ) -> None:
        self._session_factory = session_factory
        self._storage = storage

    def purge_expired(self, now: datetime | None = None) -> RetentionReport:
        current = now or datetime.now(timezone.utc)
        intake_cutoff = current - timedelta(days=public_intake_retention_days())
        matter_file_cutoff = current - timedelta(days=matter_file_retention_days())

        with self._session_factory() as db:
            public_intakes_deleted = db.execute(
                delete(PublicIntakeModel).where(PublicIntakeModel.created_at < intake_cutoff)
            ).rowcount or 0

            old_matter_ids = db.scalars(
                select(MatterModel.id).where(
                    MatterModel.submitted_at < matter_file_cutoff,
                    MatterModel.status.in_(("delivered", "completed")),
                )
            ).all()
            matter_file_refs_deleted = 0
            storage_objects_deleted = 0
            if old_matter_ids:
                expired_files = db.scalars(
                    select(MatterFileModel).where(MatterFileModel.matter_id.in_(old_matter_ids))
                ).all()
                for file in expired_files:
                    if self._storage.delete_object(file.storage_bucket, file.storage_object):
                        storage_objects_deleted += 1
                matter_file_refs_deleted = db.execute(
                    delete(MatterFileModel).where(MatterFileModel.matter_id.in_(old_matter_ids))
                ).rowcount or 0

            db.commit()

        return RetentionReport(
            public_intakes_deleted=public_intakes_deleted,
            matter_file_refs_deleted=matter_file_refs_deleted,
            storage_objects_deleted=storage_objects_deleted,
        )


def public_intake_retention_days() -> int:
    return int(os.getenv("PUBLIC_INTAKE_RETENTION_DAYS", "365"))


def matter_file_retention_days() -> int:
    return int(os.getenv("MATTER_FILE_RETENTION_DAYS", "2555"))


retention_service = RetentionService()
