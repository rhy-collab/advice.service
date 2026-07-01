"""add upload and payment state

Revision ID: 20260701_0003
Revises: 20260701_0002
Create Date: 2026-07-01
"""
from alembic import op
import sqlalchemy as sa

revision = "20260701_0003"
down_revision = "20260701_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "matters",
        sa.Column("upload_status", sa.String(length=64), nullable=False, server_default="awaiting_upload"),
    )
    op.add_column(
        "matters",
        sa.Column("payment_status", sa.String(length=64), nullable=False, server_default="unpaid"),
    )
    op.add_column("matters", sa.Column("checkout_session_id", sa.String(length=256), nullable=True))


def downgrade() -> None:
    op.drop_column("matters", "checkout_session_id")
    op.drop_column("matters", "payment_status")
    op.drop_column("matters", "upload_status")
