"""fix agents defaults enums timestamps

Revision ID: 8809ef56baf3
Revises: 5c3100b117ea
Create Date: 2026-01-28 16:47:36.782375
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "8809ef56baf3"
down_revision: Union[str, Sequence[str], None] = "5c3100b117ea"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # 1 Fix skills default (Postgres-safe)
    op.alter_column(
        "agents",
        "skills",
        existing_type=postgresql.ARRAY(sa.VARCHAR()),
        server_default=sa.text("'{}'"),
        existing_nullable=False,
    )

    # 2 Rename ENUM types safely (PostgreSQL-level operation)
    op.execute("ALTER TYPE category_enum RENAME TO agent_category_enum")
    op.execute("ALTER TYPE sub_category_enum RENAME TO agent_sub_category_enum")

    # 3 Make timestamps timezone-aware
    op.alter_column(
        "agents",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=False,
        existing_server_default=sa.text("now()"),
    )

    op.alter_column(
        "agents",
        "updated_at",
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=False,
        existing_server_default=sa.text("now()"),
    )


def downgrade() -> None:
    """Downgrade schema."""

    # 1 Revert timestamps to naive
    op.alter_column(
        "agents",
        "updated_at",
        existing_type=sa.DateTime(timezone=True),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=False,
        existing_server_default=sa.text("now()"),
    )

    op.alter_column(
        "agents",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=False,
        existing_server_default=sa.text("now()"),
    )

    # 2 Rename ENUM types back
    op.execute("ALTER TYPE agent_category_enum RENAME TO category_enum")
    op.execute("ALTER TYPE agent_sub_category_enum RENAME TO sub_category_enum")

    # 3 Remove server default from skills
    op.alter_column(
        "agents",
        "skills",
        existing_type=postgresql.ARRAY(sa.VARCHAR()),
        server_default=None,
        existing_nullable=False,
    )
