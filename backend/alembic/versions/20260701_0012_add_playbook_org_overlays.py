"""add playbook org overlays

Revision ID: 20260701_0012
Revises: 20260701_0011
Create Date: 2026-07-01
"""
from alembic import op
import sqlalchemy as sa

revision = "20260701_0012"
down_revision = "20260701_0011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("playbooks", sa.Column("organisation_id", sa.String(length=128), nullable=True))
    op.create_index(op.f("ix_playbooks_organisation_id"), "playbooks", ["organisation_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_playbooks_organisation_id"), table_name="playbooks")
    op.drop_column("playbooks", "organisation_id")
