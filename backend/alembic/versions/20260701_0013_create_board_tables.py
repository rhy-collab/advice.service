"""create board tables (context profile, threads, boards, positions, verdicts, messages, advisers)

Revision ID: 20260701_0013
Revises: 20260701_0012
Create Date: 2026-07-19
"""
from alembic import op
import sqlalchemy as sa

revision = "20260701_0013"
down_revision = "20260701_0012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "founder_context_profiles",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("organisation_id", sa.String(length=128), nullable=False),
        sa.Column("users_customers", sa.Text(), nullable=True),
        sa.Column("revenue_or_funding_stage", sa.Text(), nullable=True),
        sa.Column("customer_profile", sa.Text(), nullable=True),
        sa.Column("team_size", sa.Text(), nullable=True),
        sa.Column("goals", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index(
        op.f("ix_founder_context_profiles_organisation_id"),
        "founder_context_profiles",
        ["organisation_id"],
        unique=True,
    )

    op.create_table(
        "problem_threads",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("organisation_id", sa.String(length=128), nullable=False),
        sa.Column("title", sa.String(length=256), nullable=False),
        sa.Column("problem_text", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("domain", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index(op.f("ix_problem_threads_organisation_id"), "problem_threads", ["organisation_id"], unique=False)
    op.create_index(op.f("ix_problem_threads_status"), "problem_threads", ["status"], unique=False)

    op.create_table(
        "boards",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("thread_id", sa.String(length=64), nullable=False),
        sa.Column("round", sa.Integer(), nullable=False),
        sa.Column("domain", sa.String(length=64), nullable=True),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["thread_id"], ["problem_threads.id"], ondelete="CASCADE"),
    )
    op.create_index(op.f("ix_boards_thread_id"), "boards", ["thread_id"], unique=False)

    op.create_table(
        "advisor_positions",
        sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("board_id", sa.String(length=64), nullable=False),
        sa.Column("advisor_name", sa.String(length=128), nullable=False),
        sa.Column("persona", sa.Text(), nullable=False),
        sa.Column("position", sa.Text(), nullable=False),
        sa.Column("cross_examination", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["board_id"], ["boards.id"], ondelete="CASCADE"),
    )
    op.create_index(op.f("ix_advisor_positions_board_id"), "advisor_positions", ["board_id"], unique=False)

    op.create_table(
        "verdicts",
        sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("board_id", sa.String(length=64), nullable=False),
        sa.Column("ruling", sa.Text(), nullable=False),
        sa.Column("assumptions_json", sa.Text(), nullable=False),
        sa.Column("dissent", sa.Text(), nullable=True),
        sa.Column("validation_plan", sa.Text(), nullable=True),
        sa.Column("follow_up_questions_json", sa.Text(), nullable=False),
        sa.Column("price_tier", sa.String(length=64), nullable=True),
        sa.Column("estimated_cost", sa.Integer(), nullable=True),
        sa.Column("real_hours_estimate", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["board_id"], ["boards.id"], ondelete="CASCADE"),
    )
    op.create_index(op.f("ix_verdicts_board_id"), "verdicts", ["board_id"], unique=True)

    op.create_table(
        "thread_messages",
        sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("thread_id", sa.String(length=64), nullable=False),
        sa.Column("role", sa.String(length=64), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["thread_id"], ["problem_threads.id"], ondelete="CASCADE"),
    )
    op.create_index(op.f("ix_thread_messages_thread_id"), "thread_messages", ["thread_id"], unique=False)

    op.create_table(
        "advisers",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("name", sa.String(length=256), nullable=False),
        sa.Column("domain", sa.String(length=64), nullable=False),
        sa.Column("metro", sa.String(length=128), nullable=False),
        sa.Column("hourly_rate", sa.Integer(), nullable=False),
        sa.Column("skills_profile", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index(op.f("ix_advisers_domain"), "advisers", ["domain"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_advisers_domain"), table_name="advisers")
    op.drop_table("advisers")
    op.drop_index(op.f("ix_thread_messages_thread_id"), table_name="thread_messages")
    op.drop_table("thread_messages")
    op.drop_index(op.f("ix_verdicts_board_id"), table_name="verdicts")
    op.drop_table("verdicts")
    op.drop_index(op.f("ix_advisor_positions_board_id"), table_name="advisor_positions")
    op.drop_table("advisor_positions")
    op.drop_index(op.f("ix_boards_thread_id"), table_name="boards")
    op.drop_table("boards")
    op.drop_index(op.f("ix_problem_threads_status"), table_name="problem_threads")
    op.drop_index(op.f("ix_problem_threads_organisation_id"), table_name="problem_threads")
    op.drop_table("problem_threads")
    op.drop_index(op.f("ix_founder_context_profiles_organisation_id"), table_name="founder_context_profiles")
    op.drop_table("founder_context_profiles")
