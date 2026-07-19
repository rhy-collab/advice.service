"""add adviser budget to founder context profile

Revision ID: 20260701_0014
Revises: 20260701_0013
Create Date: 2026-07-19
"""
from alembic import op
import sqlalchemy as sa

revision = "20260701_0014"
down_revision = "20260701_0013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("founder_context_profiles", sa.Column("adviser_budget_per_hour", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("founder_context_profiles", "adviser_budget_per_hour")
