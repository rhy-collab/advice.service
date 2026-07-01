"""create matter tables

Revision ID: 20260701_0001
Revises:
Create Date: 2026-07-01
"""
from alembic import op
import sqlalchemy as sa

revision = "20260701_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "matters",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("organisation_id", sa.String(length=128), nullable=False),
        sa.Column("file_name", sa.String(length=512), nullable=False),
        sa.Column("service_tier", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("next_update_eta_minutes", sa.Integer(), nullable=True),
        sa.Column("deliverable_available", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_matters_organisation_id"), "matters", ["organisation_id"], unique=False)
    op.create_index(op.f("ix_matters_status"), "matters", ["status"], unique=False)

    op.create_table(
        "matter_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("matter_id", sa.String(length=64), nullable=False),
        sa.Column("type", sa.String(length=128), nullable=False),
        sa.Column("actor", sa.String(length=128), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("note", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["matter_id"], ["matters.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_matter_events_matter_id"), "matter_events", ["matter_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_matter_events_matter_id"), table_name="matter_events")
    op.drop_table("matter_events")
    op.drop_index(op.f("ix_matters_status"), table_name="matters")
    op.drop_index(op.f("ix_matters_organisation_id"), table_name="matters")
    op.drop_table("matters")
