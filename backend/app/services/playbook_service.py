from __future__ import annotations

from collections.abc import Callable
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, sessionmaker

from app.db.session import SessionLocal
from app.models.playbook import PlaybookCheckModel, PlaybookModel
from app.schemas.playbook import Playbook, PlaybookCheck, PlaybookCheckCreate, PlaybookCheckUpdate, PlaybookCreate


class PlaybookService:
    def __init__(self, session_factory: Callable[[], Session] | sessionmaker[Session] = SessionLocal) -> None:
        self._session_factory = session_factory

    def create_playbook(self, request: PlaybookCreate) -> Playbook:
        with self._session_factory() as db:
            row = PlaybookModel(
                id=f"playbook_{uuid4().hex[:10]}",
                name=request.name,
                contract_type=request.contract_type,
                jurisdiction=request.jurisdiction,
                organisation_id=request.organisation_id,
            )
            db.add(row)
            db.commit()
            db.refresh(row)
            return playbook_to_schema(row)

    def get_playbook(self, playbook_id: str) -> Playbook:
        with self._session_factory() as db:
            row = db.get(PlaybookModel, playbook_id)
            if row is None:
                raise HTTPException(status_code=404, detail="Playbook not found")
            return playbook_to_schema(row)

    def list_playbooks(self, contract_type: str | None = None, organisation_id: str | None = None) -> list[Playbook]:
        with self._session_factory() as db:
            query = select(PlaybookModel).order_by(PlaybookModel.created_at.desc())
            if contract_type:
                query = query.where(PlaybookModel.contract_type == contract_type)
            if organisation_id:
                query = query.where(or_(PlaybookModel.organisation_id.is_(None), PlaybookModel.organisation_id == organisation_id))
            rows = db.scalars(query).all()
            return [playbook_to_schema(row) for row in rows]

    def resolve_for_contract(self, contract_type: str, organisation_id: str | None = None) -> Playbook | None:
        playbooks = self.list_playbooks(contract_type=contract_type, organisation_id=organisation_id)
        return next((playbook for playbook in playbooks if playbook.organisation_id == organisation_id), None) or (
            playbooks[0] if playbooks else None
        )

    def add_check(self, playbook_id: str, request: PlaybookCheckCreate) -> Playbook:
        with self._session_factory() as db:
            row = db.get(PlaybookModel, playbook_id)
            if row is None:
                raise HTTPException(status_code=404, detail="Playbook not found")
            row.checks.append(
                PlaybookCheckModel(
                    id=f"check_{uuid4().hex[:10]}",
                    key=request.key,
                    title=request.title,
                    detection=request.detection,
                    severity=request.severity,
                    remediation_intent=request.remediation_intent,
                    preferred_language=request.preferred_language,
                    acceptable_fallback=request.acceptable_fallback,
                    unacceptable_fallback=request.unacceptable_fallback,
                )
            )
            db.commit()
            db.refresh(row)
            return playbook_to_schema(row)

    def update_check(self, check_id: str, request: PlaybookCheckUpdate) -> PlaybookCheck:
        with self._session_factory() as db:
            check = db.get(PlaybookCheckModel, check_id)
            if check is None:
                raise HTTPException(status_code=404, detail="Playbook check not found")
            for field, value in request.model_dump(exclude_unset=True).items():
                if value is not None:
                    setattr(check, field, value)
            db.commit()
            db.refresh(check)
            return PlaybookCheck(
                id=check.id,
                key=check.key,
                title=check.title,
                detection=check.detection,
                severity=check.severity,  # type: ignore[arg-type]
                remediation_intent=check.remediation_intent,
                preferred_language=check.preferred_language,
                acceptable_fallback=check.acceptable_fallback,
                unacceptable_fallback=check.unacceptable_fallback,
                accuracy_correct=check.accuracy_correct,
                accuracy_total=check.accuracy_total,
                created_at=check.created_at,
            )

    def record_check_feedback(
        self,
        check_id: str,
        was_correct: bool,
        corrected_detail: str | None = None,
    ) -> tuple[int, int] | None:
        with self._session_factory() as db:
            check = db.get(PlaybookCheckModel, check_id)
            if check is None:
                return None
            check.accuracy_total += 1
            if was_correct:
                check.accuracy_correct += 1
            if corrected_detail:
                check.acceptable_fallback = corrected_detail
            db.commit()
            return check.accuracy_correct, check.accuracy_total

    def seed_nda_playbook(self) -> Playbook:
        existing = self.list_playbooks(contract_type="nda")
        if existing:
            return existing[0]
        playbook = self.create_playbook(
            PlaybookCreate(name="Startup NDA baseline", contract_type="nda", jurisdiction="general")
        )
        return self.add_check(
            playbook.id,
            PlaybookCheckCreate(
                key="mutuality",
                title="Confirm NDA mutuality",
                detection="Find whether confidentiality obligations apply to one or both parties.",
                severity="medium",
                remediation_intent="Make obligations mutual unless the business case clearly supports one-way protection.",
                preferred_language="Both parties protect confidential information using reciprocal obligations.",
                acceptable_fallback="One-way obligations are acceptable only when the founder is solely receiving confidential information.",
                unacceptable_fallback="Founder discloses sensitive information without reciprocal protection.",
            ),
        )


def playbook_to_schema(row: PlaybookModel) -> Playbook:
    return Playbook(
        id=row.id,
        name=row.name,
        contract_type=row.contract_type,
        jurisdiction=row.jurisdiction,
        organisation_id=row.organisation_id,
        created_at=row.created_at,
        checks=[
            PlaybookCheck(
                id=check.id,
                key=check.key,
                title=check.title,
                detection=check.detection,
                severity=check.severity,  # type: ignore[arg-type]
                remediation_intent=check.remediation_intent,
                preferred_language=check.preferred_language,
                acceptable_fallback=check.acceptable_fallback,
                unacceptable_fallback=check.unacceptable_fallback,
                accuracy_correct=check.accuracy_correct,
                accuracy_total=check.accuracy_total,
                created_at=check.created_at,
            )
            for check in row.checks
        ],
    )


playbook_service = PlaybookService()
