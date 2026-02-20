"""update tickets and agents schema

Revision ID: 86aeffc11f05
Revises: 5f4ddfda3ebb
Create Date: 2026-02-17 12:46:05.390438

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '86aeffc11f05'
down_revision: Union[str, Sequence[str], None] = '5f4ddfda3ebb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # ==========================================================
    # AGENTS TABLE
    # ==========================================================

    op.add_column("agents", sa.Column("agent_first_name", sa.String(), nullable=False))
    op.add_column("agents", sa.Column("agent_last_name", sa.String(), nullable=False))
    op.add_column("agents", sa.Column("agent_email", sa.String(), nullable=False))
    op.add_column("agents", sa.Column("country_code", sa.String(), nullable=False))
    op.add_column("agents", sa.Column("phone", sa.String(), nullable=False))
    op.add_column("agents", sa.Column("location", sa.String(), nullable=False))

    op.add_column("agents", sa.Column("status", sa.String(), nullable=False))
    op.add_column("agents", sa.Column("hired_at", sa.DateTime(timezone=True), nullable=False))

    op.add_column(
        "agents",
        sa.Column(
            "skills",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )

    op.add_column(
        "agents",
        sa.Column(
            "languages",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )

    op.add_column("agents", sa.Column("bio", sa.Text(), nullable=True))
    op.add_column("agents", sa.Column("timezone", sa.String(length=50), nullable=False))

    op.add_column(
        "agents",
        sa.Column(
            "working_hours",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )

    op.add_column(
        "agents",
        sa.Column(
            "working_days",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )

    op.add_column("agents", sa.Column("category", sa.String(), nullable=False))
    op.add_column("agents", sa.Column("sub_category", sa.String(), nullable=False))

    op.add_column(
        "agents",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.add_column(
        "agents",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    # ==========================================================
    # TICKETS TABLE
    # ==========================================================

    # Drop old JSON structure
    op.drop_column("tickets", "content")
    op.drop_column("tickets", "additional_details")
    op.drop_column("tickets", "assigned_agent")
    op.drop_column("tickets", "is_in_trash")

    # Add new structure
    op.add_column("tickets", sa.Column("subject", sa.String(), nullable=False))
    op.add_column("tickets", sa.Column("description", sa.String(), nullable=True))
    op.add_column("tickets", sa.Column("attachment", sa.String(), nullable=True))
    op.add_column("tickets", sa.Column("raised_by_id", sa.Integer(), nullable=False))
    op.add_column("tickets", sa.Column("tags", postgresql.JSONB(), nullable=True))
    op.add_column("tickets", sa.Column("priority", sa.String(), nullable=False))
    op.add_column("tickets", sa.Column("department", sa.String(), nullable=False))

    # Assignment
    op.add_column("tickets", sa.Column("assigned_agent_id", sa.Integer(), nullable=True))

    op.create_index(
        "ix_tickets_assigned_agent_id",
        "tickets",
        ["assigned_agent_id"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_tickets_assigned_agent_id",
        "tickets",
        "agents",
        ["assigned_agent_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # Previous assignments history
    op.add_column(
        "tickets",
        sa.Column(
            "previous_assigned_agent_id",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )

    op.add_column(
        "tickets",
        sa.Column(
            "is_trash",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )

    # Convert raised_by JSONB -> String
    op.alter_column(
        "tickets",
        "raised_by",
        existing_type=postgresql.JSONB(),
        type_=sa.String(),
        postgresql_using="raised_by::text",
        existing_nullable=False,
    )

    # Convert timestamps to timezone-aware
    op.alter_column(
        "tickets",
        "created_at",
        type_=sa.DateTime(timezone=True),
        existing_type=postgresql.TIMESTAMP(),
    )

    op.alter_column(
        "tickets",
        "updated_at",
        type_=sa.DateTime(timezone=True),
        existing_type=postgresql.TIMESTAMP(),
    )

    op.alter_column(
        "tickets",
        "closed_at",
        type_=sa.DateTime(timezone=True),
        existing_type=postgresql.TIMESTAMP(),
    )


# ==============================================================
# DOWNGRADE
# ==============================================================

def downgrade() -> None:

    # Revert timestamps
    op.alter_column(
        "tickets",
        "closed_at",
        existing_type=sa.DateTime(timezone=True),
        type_=postgresql.TIMESTAMP(),
    )

    op.alter_column(
        "tickets",
        "updated_at",
        existing_type=sa.DateTime(timezone=True),
        type_=postgresql.TIMESTAMP(),
    )

    op.alter_column(
        "tickets",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        type_=postgresql.TIMESTAMP(),
    )

    # Revert raised_by back to JSONB
    op.alter_column(
        "tickets",
        "raised_by",
        existing_type=sa.String(),
        type_=postgresql.JSONB(),
        postgresql_using="raised_by::jsonb",
        existing_nullable=False,
    )

    # Drop new columns
    op.drop_constraint("fk_tickets_assigned_agent_id", "tickets", type_="foreignkey")
    op.drop_index("ix_tickets_assigned_agent_id", table_name="tickets")

    op.drop_column("tickets", "is_trash")
    op.drop_column("tickets", "previous_assigned_agent_id")
    op.drop_column("tickets", "assigned_agent_id")
    op.drop_column("tickets", "department")
    op.drop_column("tickets", "priority")
    op.drop_column("tickets", "tags")
    op.drop_column("tickets", "raised_by_id")
    op.drop_column("tickets", "attachment")
    op.drop_column("tickets", "description")
    op.drop_column("tickets", "subject")

    # Restore original columns
    op.add_column("tickets", sa.Column("assigned_agent", sa.Integer(), nullable=True))
    op.add_column("tickets", sa.Column("additional_details", postgresql.JSONB(), nullable=True))
    op.add_column("tickets", sa.Column("content", postgresql.JSONB(), nullable=False))
    op.add_column("tickets", sa.Column("is_in_trash", sa.Boolean(), nullable=False))

    # Drop agent new columns
    op.drop_column("agents", "updated_at")
    op.drop_column("agents", "created_at")
    op.drop_column("agents", "sub_category")
    op.drop_column("agents", "category")
    op.drop_column("agents", "working_days")
    op.drop_column("agents", "working_hours")
    op.drop_column("agents", "timezone")
    op.drop_column("agents", "bio")
    op.drop_column("agents", "languages")
    op.drop_column("agents", "skills")
    op.drop_column("agents", "hired_at")
    op.drop_column("agents", "status")
    op.drop_column("agents", "location")
    op.drop_column("agents", "phone")
    op.drop_column("agents", "country_code")
    op.drop_column("agents", "agent_email")
    op.drop_column("agents", "agent_last_name")
    op.drop_column("agents", "agent_first_name")