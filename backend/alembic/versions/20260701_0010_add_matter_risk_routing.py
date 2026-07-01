"""add matter risk routing

Revision ID: 20260701_0010
Revises: 20260701_0009
Create Date: 2026-07-01
"""
from alembic import op
import sqlalchemy as sa

revision = "20260701_0010"
down_revision = "20260701_0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("matters", sa.Column("risk_score", sa.Integer(), nullable=False, server_default="0"))
    op.add_column(
        "matters",
        sa.Column("risk_route", sa.String(length=64), nullable=False, server_default="standard_review"),
    )


def downgrade() -> None:
    op.drop_column("matters", "risk_route")
    op.drop_column("matters", "risk_score")
