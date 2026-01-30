"""fix ticket defaults and timestamps

Revision ID: c1f410548104
Revises: 8809ef56baf3
Create Date: 2026-01-28 17:08:29.326586
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "c1f410548104"
down_revision: Union[str, Sequence[str], None] = "8809ef56baf3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.alter_column(
        "tickets",
        "status",
        existing_type=sa.VARCHAR(length=20),
        server_default=sa.text("'pending'"),
        existing_nullable=False,
    )

    op.alter_column(
        "tickets",
        "updated_at",
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=False,
        existing_server_default=sa.text("now()"),
    )

    op.alter_column(
        "tickets",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=False,
        existing_server_default=sa.text("now()"),
    )

    op.alter_column(
        "tickets",
        "closed_at",
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=True,
    )

    op.alter_column(
        "tickets",
        "is_in_trash",
        existing_type=sa.BOOLEAN(),
        server_default=sa.text("false"),
        existing_nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.alter_column(
        "tickets",
        "is_in_trash",
        existing_type=sa.BOOLEAN(),
        server_default=None,
        existing_nullable=False,
    )

    op.alter_column(
        "tickets",
        "closed_at",
        existing_type=sa.DateTime(timezone=True),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=True,
    )

    op.alter_column(
        "tickets",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=False,
        existing_server_default=sa.text("now()"),
    )

    op.alter_column(
        "tickets",
        "updated_at",
        existing_type=sa.DateTime(timezone=True),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=False,
        existing_server_default=sa.text("now()"),
    )

    op.alter_column(
        "tickets",
        "status",
        existing_type=sa.VARCHAR(length=20),
        server_default=None,
        existing_nullable=False,
    )
