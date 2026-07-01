from collections.abc import Callable
from datetime import datetime
from uuid import uuid4

from sqlalchemy.orm import Session, sessionmaker

from app.db.session import SessionLocal
from app.models.intake import PublicIntakeModel
from app.schemas.public import PublicIntakeRequest, PublicIntakeResponse


class IntakeService:
    def __init__(
        self,
        session_factory: Callable[[], Session] | sessionmaker[Session] = SessionLocal,
    ) -> None:
        self._session_factory = session_factory

    def create_public_intake(self, request: PublicIntakeRequest) -> PublicIntakeResponse:
        intake_id = f"intake_{uuid4().hex[:10]}"

        with self._session_factory() as db:
            intake = PublicIntakeModel(
                id=intake_id,
                name=request.name.strip(),
                email=request.email.strip().lower(),
                company=request.company.strip(),
                contract_type=request.contract_type,
                urgency=request.urgency,
                service_tier=request.service_tier,
                notes=request.notes.strip(),
                status="new",
            )
            db.add(intake)
            db.commit()
            db.refresh(intake)

            return PublicIntakeResponse(
                intake_id=intake.id,
                status=intake.status,
                created_at=intake.created_at if isinstance(intake.created_at, datetime) else datetime.utcnow(),
                message="Thanks. Charter Law will review the intake and follow up before any legal work begins.",
            )


intake_service = IntakeService()
