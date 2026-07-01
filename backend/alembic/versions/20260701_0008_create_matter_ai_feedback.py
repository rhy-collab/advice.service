"""create matter ai feedback

Revision ID: 20260701_0008
Revises: 20260701_0007
Create Date: 2026-07-01
"""
from alembic import op
import sqlalchemy as sa

revision = "20260701_0008"
down_revision = "20260701_0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "matter_ai_feedback",
        sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("matter_id", sa.String(length=64), nullable=False),
        sa.Column("playbook_check_id", sa.String(length=64), nullable=True),
        sa.Column("issue_title", sa.String(length=256), nullable=False),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("reason_tag", sa.String(length=128), nullable=False),
        sa.Column("corrected_detail", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["matter_id"], ["matters.id"], ondelete="CASCADE"),
    )
    op.create_index(op.f("ix_matter_ai_feedback_matter_id"), "matter_ai_feedback", ["matter_id"], unique=False)
    op.create_index(
        op.f("ix_matter_ai_feedback_playbook_check_id"),
        "matter_ai_feedback",
        ["playbook_check_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_matter_ai_feedback_playbook_check_id"), table_name="matter_ai_feedback")
    op.drop_index(op.f("ix_matter_ai_feedback_matter_id"), table_name="matter_ai_feedback")
    op.drop_table("matter_ai_feedback")
