from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class PlaybookModel(Base):
    __tablename__ = "playbooks"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    contract_type: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    jurisdiction: Mapped[str] = mapped_column(String(128), nullable=False, default="general")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    checks: Mapped[list["PlaybookCheckModel"]] = relationship(
        back_populates="playbook",
        cascade="all, delete-orphan",
        order_by="PlaybookCheckModel.created_at",
    )


class PlaybookCheckModel(Base):
    __tablename__ = "playbook_checks"
    __table_args__ = (UniqueConstraint("playbook_id", "key", name="uq_playbook_checks_playbook_key"),)

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    playbook_id: Mapped[str] = mapped_column(ForeignKey("playbooks.id", ondelete="CASCADE"), index=True)
    key: Mapped[str] = mapped_column(String(128), nullable=False)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    detection: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(64), nullable=False)
    remediation_intent: Mapped[str] = mapped_column(Text, nullable=False)
    preferred_language: Mapped[str] = mapped_column(Text, nullable=False)
    acceptable_fallback: Mapped[str] = mapped_column(Text, nullable=False)
    unacceptable_fallback: Mapped[str] = mapped_column(Text, nullable=False)
    accuracy_correct: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    accuracy_total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    playbook: Mapped[PlaybookModel] = relationship(back_populates="checks")
