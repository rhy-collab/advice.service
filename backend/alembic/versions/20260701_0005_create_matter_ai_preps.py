"""create matter ai preps

Revision ID: 20260701_0005
Revises: 20260701_0004
Create Date: 2026-07-01
"""
from alembic import op
import sqlalchemy as sa

revision = "20260701_0005"
down_revision = "20260701_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "matter_ai_preps",
        sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("matter_id", sa.String(length=64), nullable=False),
        sa.Column("mode", sa.String(length=64), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("issues_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["matter_id"], ["matters.id"], ondelete="CASCADE"),
    )
    op.create_index(op.f("ix_matter_ai_preps_matter_id"), "matter_ai_preps", ["matter_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_matter_ai_preps_matter_id"), table_name="matter_ai_preps")
    op.drop_table("matter_ai_preps")
