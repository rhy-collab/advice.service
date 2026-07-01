from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class MatterModel(Base):
    __tablename__ = "matters"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organisation_id: Mapped[str] = mapped_column(String(128), index=True)
    file_name: Mapped[str] = mapped_column(String(512))
    service_tier: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(64), index=True)
    upload_status: Mapped[str] = mapped_column(String(64), default="awaiting_upload")
    payment_status: Mapped[str] = mapped_column(String(64), default="unpaid")
    checkout_session_id: Mapped[str | None] = mapped_column(String(256), nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    next_update_eta_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    deliverable_available: Mapped[bool] = mapped_column(Boolean, default=False)

    events: Mapped[list["MatterEventModel"]] = relationship(
        back_populates="matter",
        cascade="all, delete-orphan",
        order_by="MatterEventModel.occurred_at",
    )
    files: Mapped[list["MatterFileModel"]] = relationship(
        back_populates="matter",
        cascade="all, delete-orphan",
        order_by="MatterFileModel.created_at",
    )
    ai_preps: Mapped[list["MatterAIPrepModel"]] = relationship(
        back_populates="matter",
        cascade="all, delete-orphan",
        order_by="MatterAIPrepModel.created_at",
    )


class MatterEventModel(Base):
    __tablename__ = "matter_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    matter_id: Mapped[str] = mapped_column(ForeignKey("matters.id", ondelete="CASCADE"), index=True)
    type: Mapped[str] = mapped_column(String(128))
    actor: Mapped[str] = mapped_column(String(128))
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    note: Mapped[str] = mapped_column(Text)

    matter: Mapped[MatterModel] = relationship(back_populates="events")


class MatterFileModel(Base):
    __tablename__ = "matter_files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    matter_id: Mapped[str] = mapped_column(ForeignKey("matters.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(String(64))
    file_name: Mapped[str] = mapped_column(String(512))
    storage_bucket: Mapped[str] = mapped_column(String(256))
    storage_object: Mapped[str] = mapped_column(String(1024))
    content_type: Mapped[str] = mapped_column(String(256))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    matter: Mapped[MatterModel] = relationship(back_populates="files")


class MatterAIPrepModel(Base):
    __tablename__ = "matter_ai_preps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    matter_id: Mapped[str] = mapped_column(ForeignKey("matters.id", ondelete="CASCADE"), index=True)
    mode: Mapped[str] = mapped_column(String(64))
    summary: Mapped[str] = mapped_column(Text)
    issues_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    matter: Mapped[MatterModel] = relationship(back_populates="ai_preps")
