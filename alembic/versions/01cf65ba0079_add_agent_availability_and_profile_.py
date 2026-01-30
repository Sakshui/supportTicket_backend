"""add agent availability and profile fields

Revision ID: 01cf65ba0079
Revises: b9baab9a9200
Create Date: 2026-01-29 17:41:38.935461
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "01cf65ba0079"
down_revision: Union[str, Sequence[str], None] = "b9baab9a9200"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Availability
    op.add_column(
        "agents",
        sa.Column(
            "working_hours",
            postgresql.JSONB,
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )

    op.add_column(
        "agents",
        sa.Column(
            "working_days",
            postgresql.JSONB,
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )

    op.add_column(
        "agents",
        sa.Column(
            "timezone",
            sa.String(length=50),
            nullable=False,
            server_default="UTC",
        ),
    )

    # Expertise / profile
    op.add_column(
        "agents",
        sa.Column(
            "languages",
            postgresql.JSONB,
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )

    op.add_column(
        "agents",
        sa.Column(
            "bio",
            sa.Text(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    # Reverse order of creation
    op.drop_column("agents", "bio")
    op.drop_column("agents", "languages")
    op.drop_column("agents", "timezone")
    op.drop_column("agents", "working_days")
    op.drop_column("agents", "working_hours")
