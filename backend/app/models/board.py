from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

# The fixed seven-domain menu (charter-consultancy-roadmap.md §1 step 5).
DOMAINS = (
    "pricing",
    "fundraising",
    "gtm",
    "pitch",
    "legal",
    "ecosystem",
    "engineering",
)

PRICE_TIERS = ("simple", "standard", "negotiation", "drafting")


class FounderContextProfileModel(Base):
    """Persistent business-context profile — one per organisation (roadmap §3 item 1)."""

    __tablename__ = "founder_context_profiles"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organisation_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    users_customers: Mapped[str | None] = mapped_column(Text, nullable=True)
    revenue_or_funding_stage: Mapped[str | None] = mapped_column(Text, nullable=True)
    customer_profile: Mapped[str | None] = mapped_column(Text, nullable=True)
    team_size: Mapped[str | None] = mapped_column(Text, nullable=True)
    goals: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class ProblemThreadModel(Base):
    """A founder problem thread — the generalized 'matter' (roadmap §1 step 8)."""

    __tablename__ = "problem_threads"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organisation_id: Mapped[str] = mapped_column(String(128), index=True)
    title: Mapped[str] = mapped_column(String(256))
    problem_text: Mapped[str] = mapped_column(Text)
    # context_pending -> triage -> panel -> agent_ready
    status: Mapped[str] = mapped_column(String(64), index=True, default="context_pending")
    domain: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    boards: Mapped[list["BoardModel"]] = relationship(
        back_populates="thread", cascade="all, delete-orphan", order_by="BoardModel.round"
    )
    messages: Mapped[list["ThreadMessageModel"]] = relationship(
        back_populates="thread", cascade="all, delete-orphan", order_by="ThreadMessageModel.id"
    )


class BoardModel(Base):
    """One board per round (roadmap §3 item 2). round: 1=context, 2=triage, 3=domain panel."""

    __tablename__ = "boards"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    thread_id: Mapped[str] = mapped_column(ForeignKey("problem_threads.id", ondelete="CASCADE"), index=True)
    round: Mapped[int] = mapped_column(Integer)
    domain: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(64), default="complete")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    thread: Mapped[ProblemThreadModel] = relationship(back_populates="boards")
    positions: Mapped[list["AdvisorPositionModel"]] = relationship(
        back_populates="board", cascade="all, delete-orphan", order_by="AdvisorPositionModel.id"
    )
    verdict: Mapped["VerdictModel | None"] = relationship(
        back_populates="board", cascade="all, delete-orphan", uselist=False
    )


class AdvisorPositionModel(Base):
    __tablename__ = "advisor_positions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    board_id: Mapped[str] = mapped_column(ForeignKey("boards.id", ondelete="CASCADE"), index=True)
    advisor_name: Mapped[str] = mapped_column(String(128))
    persona: Mapped[str] = mapped_column(Text)
    position: Mapped[str] = mapped_column(Text)
    cross_examination: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    board: Mapped[BoardModel] = relationship(back_populates="positions")


class VerdictModel(Base):
    __tablename__ = "verdicts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    board_id: Mapped[str] = mapped_column(
        ForeignKey("boards.id", ondelete="CASCADE"), index=True, unique=True
    )
    ruling: Mapped[str] = mapped_column(Text)
    assumptions_json: Mapped[str] = mapped_column(Text, default="[]")
    dissent: Mapped[str | None] = mapped_column(Text, nullable=True)
    validation_plan: Mapped[str | None] = mapped_column(Text, nullable=True)
    follow_up_questions_json: Mapped[str] = mapped_column(Text, default="[]")
    # Internal only until the founder asks to be matched (roadmap invariant 7).
    price_tier: Mapped[str | None] = mapped_column(String(64), nullable=True)
    estimated_cost: Mapped[int | None] = mapped_column(Integer, nullable=True)
    real_hours_estimate: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    board: Mapped[BoardModel] = relationship(back_populates="verdict")


class ThreadMessageModel(Base):
    """Stage 4 chat: founder <-> perfect agent (free tab) and adviser-tab events."""

    __tablename__ = "thread_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    thread_id: Mapped[str] = mapped_column(ForeignKey("problem_threads.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(String(64))  # founder | agent | system
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    thread: Mapped[ProblemThreadModel] = relationship(back_populates="messages")


class AdviserModel(Base):
    """A real individual on the platform (roadmap §3 item 6). Self-set rate + skills profile."""

    __tablename__ = "advisers"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(256))
    domain: Mapped[str] = mapped_column(String(64), index=True)
    metro: Mapped[str] = mapped_column(String(128), default="San Francisco")
    hourly_rate: Mapped[int] = mapped_column(Integer)
    skills_profile: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
