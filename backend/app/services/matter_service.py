from collections.abc import Callable
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.db.session import SessionLocal
from app.models.matter import MatterAIPrepModel, MatterEventModel, MatterFileModel, MatterModel
from app.schemas.ai import AIPrepResult
from app.schemas.matters import (
    AttorneyApprovalRequest,
    CreateMatterRequest,
    CreateMatterResponse,
    MatterDetailResponse,
    MatterEvent,
    MatterStatus,
    MatterSummary,
    PaymentStatus,
    UploadTarget,
    demo_expiry,
)
from app.services.ai_prep_service import ai_prep_service, issues_from_json, issues_to_json
from app.services.storage_service import StorageService, storage_service


LEGAL_TRANSITIONS: dict[str, set[str]] = {
    "intake": {"ai_review"},
    "ai_review": {"attorney_queue"},
    "attorney_queue": {"attorney_review"},
    "attorney_review": {"delivered"},
    "delivered": {"completed"},
    "completed": set(),
}


class MatterService:
    def __init__(
        self,
        session_factory: Callable[[], Session] | sessionmaker[Session] = SessionLocal,
        storage: StorageService = storage_service,
        seed_demo: bool = False,
    ) -> None:
        self._session_factory = session_factory
        self._storage = storage
        if seed_demo:
            self.seed_demo_data()

    def list_matters(self, organisation_id: str) -> list[MatterSummary]:
        with self._session_factory() as db:
            rows = db.scalars(
                select(MatterModel)
                .where(MatterModel.organisation_id == organisation_id)
                .order_by(MatterModel.submitted_at.desc())
            ).all()
            return [matter_to_summary(row) for row in rows]

    def list_attorney_queue(self, organisation_id: str) -> list[MatterSummary]:
        with self._session_factory() as db:
            rows = db.scalars(
                select(MatterModel)
                .where(
                    MatterModel.organisation_id == organisation_id,
                    MatterModel.status.in_(("attorney_queue", "attorney_review")),
                )
                .order_by(MatterModel.submitted_at.asc())
            ).all()
            return [matter_to_summary(row) for row in rows]

    def create_matter(self, request: CreateMatterRequest, organisation_id: str) -> CreateMatterResponse:
        matter_id = f"matter_{uuid4().hex[:10]}"
        now = datetime.now(timezone.utc)
        upload_target = self._storage.create_upload_target(matter_id, request.file_name)

        with self._session_factory() as db:
            matter = MatterModel(
                id=matter_id,
                organisation_id=organisation_id,
                file_name=request.file_name,
                service_tier=request.service_tier,
                status="intake",
                upload_status="awaiting_upload",
                payment_status="unpaid",
                submitted_at=now,
                next_update_eta_minutes=15,
                deliverable_available=False,
            )
            matter.events.append(
                MatterEventModel(
                    type="matter_created",
                    actor="client",
                    occurred_at=now,
                    note="Matter created from portal intake.",
                )
            )
            matter.files.append(
                MatterFileModel(
                    role="source_contract",
                    file_name=request.file_name,
                    storage_bucket=upload_target.bucket,
                    storage_object=upload_target.object_name,
                    content_type=upload_target.content_type,
                    created_at=now,
                )
            )
            db.add(matter)
            db.commit()

        return CreateMatterResponse(
            matter_id=matter_id,
            status="intake",
            upload=UploadTarget(
                method=upload_target.method,
                url=upload_target.url,
                expires_at=demo_expiry(),
                mode=upload_target.mode,
            ),
        )

    def get_matter(self, matter_id: str, organisation_id: str) -> MatterDetailResponse | None:
        with self._session_factory() as db:
            matter = self._get_matter_model(db, matter_id, organisation_id)
            if matter is None:
                return None
            return MatterDetailResponse(
                matter=matter_to_summary(matter),
                events=[event_to_schema(event) for event in matter.events],
            )

    def require_matter(self, matter_id: str, organisation_id: str) -> MatterSummary:
        detail = self.get_matter(matter_id, organisation_id)
        if detail is None:
            raise HTTPException(status_code=404, detail="Matter not found")
        return detail.matter

    def mark_upload_complete(self, matter_id: str, organisation_id: str) -> MatterSummary:
        with self._session_factory() as db:
            matter = self._get_matter_model(db, matter_id, organisation_id)
            if matter is None:
                raise HTTPException(status_code=404, detail="Matter not found")

            matter.upload_status = "uploaded"
            matter.events.append(
                MatterEventModel(
                    type="upload_completed",
                    actor="client",
                    occurred_at=datetime.now(timezone.utc),
                    note="Source contract upload was marked complete.",
                )
            )
            if matter.status == "intake" and not matter.ai_preps:
                matter.status = "ai_review"
                matter.events.append(
                    MatterEventModel(
                        type="ai_prep_started",
                        actor="system",
                        occurred_at=datetime.now(timezone.utc),
                        note="Internal AI preparation started after upload.",
                    )
                )
                prep = ai_prep_service.generate_for_uploaded_contract(matter.file_name, matter.service_tier)
                matter.ai_preps.append(
                    MatterAIPrepModel(
                        mode=prep.mode,
                        summary=prep.summary,
                        issues_json=issues_to_json(prep.issues),
                        created_at=datetime.now(timezone.utc),
                    )
                )
                matter.status = "attorney_queue"
                matter.next_update_eta_minutes = 45
                matter.events.append(
                    MatterEventModel(
                        type="ai_prep_completed",
                        actor="system",
                        occurred_at=datetime.now(timezone.utc),
                        note="Internal AI preparation completed and matter moved to attorney queue.",
                    )
                )
            db.commit()
            db.refresh(matter)
            return matter_to_summary(matter)

    def mark_checkout_created(
        self,
        matter_id: str,
        organisation_id: str,
        checkout_session_id: str,
    ) -> MatterSummary:
        with self._session_factory() as db:
            matter = self._get_matter_model(db, matter_id, organisation_id)
            if matter is None:
                raise HTTPException(status_code=404, detail="Matter not found")

            matter.checkout_session_id = checkout_session_id
            matter.payment_status = "checkout_pending"
            matter.events.append(
                MatterEventModel(
                    type="checkout_created",
                    actor="system",
                    occurred_at=datetime.now(timezone.utc),
                    note="Stripe hosted checkout was created for this matter.",
                )
            )
            db.commit()
            db.refresh(matter)
            return matter_to_summary(matter)

    def mark_payment_status(
        self,
        matter_id: str,
        payment_status: PaymentStatus,
        checkout_session_id: str | None = None,
    ) -> MatterSummary | None:
        with self._session_factory() as db:
            matter = self._get_matter_by_checkout(db, checkout_session_id) if checkout_session_id else db.get(MatterModel, matter_id)
            if matter is None:
                return None

            matter.payment_status = payment_status
            if checkout_session_id:
                matter.checkout_session_id = checkout_session_id
            matter.events.append(
                MatterEventModel(
                    type=f"payment_{payment_status}",
                    actor="stripe",
                    occurred_at=datetime.now(timezone.utc),
                    note=f"Payment status changed to {payment_status}.",
                )
            )
            db.commit()
            db.refresh(matter)
            return matter_to_summary(matter)

    def approve_deliverable(
        self,
        matter_id: str,
        organisation_id: str,
        request: AttorneyApprovalRequest,
    ) -> MatterSummary:
        with self._session_factory() as db:
            matter = self._get_matter_model(db, matter_id, organisation_id)
            if matter is None:
                raise HTTPException(status_code=404, detail="Matter not found")
            if matter.upload_status != "uploaded":
                raise HTTPException(status_code=409, detail="Source contract upload is required before delivery")
            if matter.payment_status != "paid":
                raise HTTPException(status_code=409, detail="Payment is required before delivery")
            if matter.status not in {"attorney_queue", "attorney_review"}:
                raise HTTPException(status_code=409, detail="Matter must be in attorney review before delivery")

            now = datetime.now(timezone.utc)
            matter.status = "delivered"
            matter.next_update_eta_minutes = None
            matter.deliverable_available = True
            matter.files.append(
                MatterFileModel(
                    role="approved_redline",
                    file_name=request.deliverable_file_name,
                    storage_bucket=self._storage.bucket_name(),
                    storage_object=f"matters/{matter_id}/deliverables/{request.deliverable_file_name}",
                    content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    created_at=now,
                )
            )
            matter.events.append(
                MatterEventModel(
                    type="attorney_approved",
                    actor="attorney",
                    occurred_at=now,
                    note=request.note,
                )
            )
            db.commit()
            db.refresh(matter)
            return matter_to_summary(matter)

    def delivery_download_url(self, matter_id: str, organisation_id: str) -> str:
        with self._session_factory() as db:
            matter = self._get_matter_model(db, matter_id, organisation_id)
            if matter is None:
                raise HTTPException(status_code=404, detail="Matter not found")
            if matter.status != "delivered" or not matter.deliverable_available:
                raise HTTPException(status_code=409, detail="Deliverable is not approved yet")

            deliverable = next((file for file in matter.files if file.role == "approved_redline"), None)
            if deliverable is None:
                raise HTTPException(status_code=404, detail="Approved deliverable file not found")

            return self._storage.create_download_url(deliverable.storage_bucket, deliverable.storage_object)

    def transition_status(
        self,
        matter_id: str,
        organisation_id: str,
        status: MatterStatus,
        attorney_approved: bool = False,
    ) -> MatterSummary:
        if status == "delivered" and not attorney_approved:
            raise HTTPException(status_code=409, detail="Attorney approval is required before delivery")

        with self._session_factory() as db:
            matter = self._get_matter_model(db, matter_id, organisation_id)
            if matter is None:
                raise HTTPException(status_code=404, detail="Matter not found")

            allowed = LEGAL_TRANSITIONS.get(matter.status, set())
            if status != matter.status and status not in allowed:
                raise HTTPException(status_code=409, detail=f"Illegal transition {matter.status} -> {status}")

            matter.status = status
            matter.next_update_eta_minutes = None if status in {"delivered", "completed"} else matter.next_update_eta_minutes
            matter.deliverable_available = status in {"delivered", "completed"}
            matter.events.append(
                MatterEventModel(
                    type="status_changed",
                    actor="attorney" if attorney_approved else "system",
                    occurred_at=datetime.now(timezone.utc),
                    note=f"Matter moved to {status}.",
                )
            )
            db.commit()
            db.refresh(matter)
            return matter_to_summary(matter)

    def seed_demo_data(self) -> None:
        organisation_id = "org_demo"
        now = datetime.now(timezone.utc)
        demo_rows = [
            ("matter_demo_1", "vendor-saas-agreement.docx", "attorney_review", 42),
            ("matter_demo_2", "mutual-nda-series-a.docx", "ai_review", 120),
            ("matter_demo_3", "customer-msa-clean.docx", "delivered", None),
        ]

        with self._session_factory() as db:
            for matter_id, file_name, status, eta in demo_rows:
                existing = db.get(MatterModel, matter_id)
                if existing is not None:
                    continue

                matter = MatterModel(
                    id=matter_id,
                    organisation_id=organisation_id,
                    file_name=file_name,
                    service_tier="standard_redline",
                    status=status,
                    upload_status="uploaded",
                    payment_status="paid" if status == "delivered" else "checkout_pending",
                    submitted_at=now,
                    next_update_eta_minutes=eta,
                    deliverable_available=status == "delivered",
                )
                matter.events.append(
                    MatterEventModel(
                        type="matter_seeded",
                        actor="system",
                        occurred_at=now,
                        note="Demo matter for local portal development.",
                    )
                )
                db.add(matter)
            db.commit()

    def list_events(self, matter_id: str, organisation_id: str):
        detail = self.get_matter(matter_id, organisation_id)
        if detail is None:
            raise HTTPException(status_code=404, detail="Matter not found")
        return detail.events

    def get_latest_ai_prep(self, matter_id: str, organisation_id: str) -> AIPrepResult:
        with self._session_factory() as db:
            matter = self._get_matter_model(db, matter_id, organisation_id)
            if matter is None:
                raise HTTPException(status_code=404, detail="Matter not found")
            prep = db.scalar(
                select(MatterAIPrepModel)
                .where(MatterAIPrepModel.matter_id == matter_id)
                .order_by(MatterAIPrepModel.created_at.desc(), MatterAIPrepModel.id.desc())
            )
            if prep is None:
                raise HTTPException(status_code=404, detail="Internal AI preparation not found")
            return AIPrepResult(
                matter_id=matter_id,
                mode=prep.mode,  # type: ignore[arg-type]
                summary=prep.summary,
                issues=issues_from_json(prep.issues_json),
                created_at=prep.created_at,
            )

    def activity_report(self, organisation_id: str) -> dict:
        with self._session_factory() as db:
            rows = db.scalars(
                select(MatterModel).where(MatterModel.organisation_id == organisation_id)
            ).all()
        by_status: dict[str, int] = {}
        for row in rows:
            by_status[row.status] = by_status.get(row.status, 0) + 1
        return {"byStatus": by_status, "total": len(rows)}

    def _get_matter_model(self, db: Session, matter_id: str, organisation_id: str) -> MatterModel | None:
        return db.scalar(
            select(MatterModel).where(
                MatterModel.id == matter_id,
                MatterModel.organisation_id == organisation_id,
            )
        )

    def _get_matter_by_checkout(self, db: Session, checkout_session_id: str | None) -> MatterModel | None:
        if checkout_session_id is None:
            return None
        return db.scalar(select(MatterModel).where(MatterModel.checkout_session_id == checkout_session_id))


def matter_to_summary(matter: MatterModel) -> MatterSummary:
    return MatterSummary(
        id=matter.id,
        file_name=matter.file_name,
        service_tier=matter.service_tier,  # type: ignore[arg-type]
        status=matter.status,  # type: ignore[arg-type]
        upload_status=matter.upload_status,  # type: ignore[arg-type]
        payment_status=matter.payment_status,  # type: ignore[arg-type]
        submitted_at=matter.submitted_at,
        next_update_eta_minutes=matter.next_update_eta_minutes,
        deliverable_available=matter.deliverable_available,
    )


def event_to_schema(event: MatterEventModel) -> MatterEvent:
    return MatterEvent(
        type=event.type,
        actor=event.actor,
        occurred_at=event.occurred_at,
        note=event.note,
    )


matter_service = MatterService()
