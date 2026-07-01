"""create matter draft deliverables

Revision ID: 20260701_0009
Revises: 20260701_0008
Create Date: 2026-07-01
"""
from alembic import op
import sqlalchemy as sa

revision = "20260701_0009"
down_revision = "20260701_0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "matter_draft_deliverables",
        sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("matter_id", sa.String(length=64), nullable=False),
        sa.Column("redline_file_name", sa.String(length=512), nullable=False),
        sa.Column("redline_storage_bucket", sa.String(length=256), nullable=False),
        sa.Column("redline_storage_object", sa.String(length=1024), nullable=False),
        sa.Column("cover_letter_file_name", sa.String(length=512), nullable=False),
        sa.Column("cover_letter_storage_bucket", sa.String(length=256), nullable=False),
        sa.Column("cover_letter_storage_object", sa.String(length=1024), nullable=False),
        sa.Column("cover_letter_body", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=64), nullable=False, server_default="internal_only"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["matter_id"], ["matters.id"], ondelete="CASCADE"),
    )
    op.create_index(
        op.f("ix_matter_draft_deliverables_matter_id"),
        "matter_draft_deliverables",
        ["matter_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_matter_draft_deliverables_matter_id"), table_name="matter_draft_deliverables")
    op.drop_table("matter_draft_deliverables")
