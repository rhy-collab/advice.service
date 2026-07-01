"""create public intakes

Revision ID: 20260701_0004
Revises: 20260701_0003
Create Date: 2026-07-01
"""
from alembic import op
import sqlalchemy as sa

revision = "20260701_0004"
down_revision = "20260701_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "public_intakes",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("name", sa.String(length=256), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("company", sa.String(length=256), nullable=False),
        sa.Column("contract_type", sa.String(length=128), nullable=False),
        sa.Column("urgency", sa.String(length=64), nullable=False),
        sa.Column("service_tier", sa.String(length=64), nullable=False),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("status", sa.String(length=64), nullable=False, server_default="new"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_public_intakes_email", "public_intakes", ["email"])


def downgrade() -> None:
    op.drop_index("ix_public_intakes_email", table_name="public_intakes")
    op.drop_table("public_intakes")
