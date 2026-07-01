"""create matter files

Revision ID: 20260701_0002
Revises: 20260701_0001
Create Date: 2026-07-01
"""
from alembic import op
import sqlalchemy as sa

revision = "20260701_0002"
down_revision = "20260701_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "matter_files",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("matter_id", sa.String(length=64), nullable=False),
        sa.Column("role", sa.String(length=64), nullable=False),
        sa.Column("file_name", sa.String(length=512), nullable=False),
        sa.Column("storage_bucket", sa.String(length=256), nullable=False),
        sa.Column("storage_object", sa.String(length=1024), nullable=False),
        sa.Column("content_type", sa.String(length=256), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["matter_id"], ["matters.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_matter_files_matter_id"), "matter_files", ["matter_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_matter_files_matter_id"), table_name="matter_files")
    op.drop_table("matter_files")
