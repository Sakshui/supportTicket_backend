"""update agent and ticket schema - type and structure

Revision ID: b9baab9a9200
Revises: c1f410548104
Create Date: 2026-01-29 16:51:32.836168
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "b9baab9a9200"
down_revision: Union[str, Sequence[str], None] = "c1f410548104"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1 Add new columns
    op.add_column(
        "agents",
        sa.Column(
            "status",
            sa.String(),
            nullable=False,
            server_default="active",
        ),
    )

    op.add_column(
        "agents",
        sa.Column(
            "hired_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    # 2 DROP default on skills (CRITICAL)
    op.alter_column(
        "agents",
        "skills",
        server_default=None,
    )

    # 3 Convert skills: TEXT[] -> JSONB
    op.alter_column(
        "agents",
        "skills",
        type_=sa.dialects.postgresql.JSONB,
        postgresql_using="to_jsonb(skills)",
        nullable=False,
    )

    # 4 Set new JSONB default
    op.alter_column(
        "agents",
        "skills",
        server_default=sa.text("'[]'::jsonb"),
    )

    # 5 Convert enums -> strings
    op.alter_column(
        "agents",
        "category",
        type_=sa.String(),
        postgresql_using="category::text",
        nullable=False,
    )

    op.alter_column(
        "agents",
        "sub_category",
        type_=sa.String(),
        postgresql_using="sub_category::text",
        nullable=False,
    )

    # 6 Drop enum types
    op.execute("DROP TYPE IF EXISTS agent_category_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS agent_sub_category_enum CASCADE")



def downgrade() -> None:
    raise NotImplementedError(
        "Downgrade not supported for enum -> string and ARRAY -> JSONB migration"
    )
