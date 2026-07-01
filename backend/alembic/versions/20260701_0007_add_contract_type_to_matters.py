"""add contract type to matters

Revision ID: 20260701_0007
Revises: 20260701_0006
Create Date: 2026-07-01
"""
from alembic import op
import sqlalchemy as sa

revision = "20260701_0007"
down_revision = "20260701_0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "matters",
        sa.Column("contract_type", sa.String(length=128), nullable=False, server_default="unknown"),
    )


def downgrade() -> None:
    op.drop_column("matters", "contract_type")
