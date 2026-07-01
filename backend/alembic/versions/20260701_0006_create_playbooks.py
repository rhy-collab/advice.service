"""create playbooks

Revision ID: 20260701_0006
Revises: 20260701_0005
Create Date: 2026-07-01
"""
from alembic import op
import sqlalchemy as sa

revision = "20260701_0006"
down_revision = "20260701_0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "playbooks",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("name", sa.String(length=256), nullable=False),
        sa.Column("contract_type", sa.String(length=128), nullable=False),
        sa.Column("jurisdiction", sa.String(length=128), nullable=False, server_default="general"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index(op.f("ix_playbooks_contract_type"), "playbooks", ["contract_type"], unique=False)

    op.create_table(
        "playbook_checks",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("playbook_id", sa.String(length=64), nullable=False),
        sa.Column("key", sa.String(length=128), nullable=False),
        sa.Column("title", sa.String(length=256), nullable=False),
        sa.Column("detection", sa.Text(), nullable=False),
        sa.Column("severity", sa.String(length=64), nullable=False),
        sa.Column("remediation_intent", sa.Text(), nullable=False),
        sa.Column("preferred_language", sa.Text(), nullable=False),
        sa.Column("acceptable_fallback", sa.Text(), nullable=False),
        sa.Column("unacceptable_fallback", sa.Text(), nullable=False),
        sa.Column("accuracy_correct", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("accuracy_total", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["playbook_id"], ["playbooks.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("playbook_id", "key", name="uq_playbook_checks_playbook_key"),
    )
    op.create_index(op.f("ix_playbook_checks_playbook_id"), "playbook_checks", ["playbook_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_playbook_checks_playbook_id"), table_name="playbook_checks")
    op.drop_table("playbook_checks")
    op.drop_index(op.f("ix_playbooks_contract_type"), table_name="playbooks")
    op.drop_table("playbooks")
