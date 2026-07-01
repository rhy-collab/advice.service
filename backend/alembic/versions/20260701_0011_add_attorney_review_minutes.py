"""add attorney review minutes

Revision ID: 20260701_0011
Revises: 20260701_0010
Create Date: 2026-07-01
"""
from alembic import op
import sqlalchemy as sa

revision = "20260701_0011"
down_revision = "20260701_0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("matters", sa.Column("attorney_review_minutes", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("matters", "attorney_review_minutes")
