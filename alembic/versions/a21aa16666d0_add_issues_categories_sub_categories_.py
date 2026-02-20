"""add issues, categories, sub-categories and update tickets table (phase 1)

Revision ID: a21aa16666d0
Revises: 86aeffc11f05
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision: str = "a21aa16666d0"
down_revision: Union[str, Sequence[str], None] = "86aeffc11f05"
branch_labels = None
depends_on = None


# ==========================================================
# UPGRADE
# ==========================================================

def upgrade() -> None:
    """Phase 1: Add new structure without data removal"""

    # ------------------------------------------------------
    # GLOBAL MASTER TABLES
    # ------------------------------------------------------

    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("name", name="uq_categories_name"),
    )
    op.create_index("ix_categories_slug", "categories", ["slug"], unique=True)

    op.create_table(
        "issues",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("name", name="uq_issues_name"),
    )
    op.create_index("ix_issues_slug", "issues", ["slug"], unique=True)

    op.create_table(
        "sub_categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("name", name="uq_subcategories_name"),
    )
    op.create_index("ix_sub_categories_slug", "sub_categories", ["slug"], unique=True)

    # ------------------------------------------------------
    # GLOBAL MAPPING TABLES
    # ------------------------------------------------------

    op.create_table(
        "category_subcategory_map",
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("sub_category_id", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["category_id"], ["categories.id"],
            name="fk_category_subcategory_category",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["sub_category_id"], ["sub_categories.id"],
            name="fk_category_subcategory_subcategory",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("category_id", "sub_category_id"),
    )

    op.create_table(
        "issue_category_map",
        sa.Column("issue_id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["issue_id"], ["issues.id"],
            name="fk_issue_category_issue",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["category_id"], ["categories.id"],
            name="fk_issue_category_category",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("issue_id", "category_id"),
    )

    # ------------------------------------------------------
    # OUTLET TABLES
    # ------------------------------------------------------

    op.create_table(
        "outlet_categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("outlet_id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("is_custom", sa.Boolean(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_trash", sa.Boolean(),
                  server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["category_id"], ["categories.id"],
            name="fk_outlet_category_global",
        ),
        sa.UniqueConstraint("outlet_id", "slug",
                            name="uq_outlet_category_slug"),
    )

    op.create_table(
        "outlet_issues",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("outlet_id", sa.Integer(), nullable=False),
        sa.Column("issue_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("is_custom", sa.Boolean(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_trash", sa.Boolean(),
                  server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["issue_id"], ["issues.id"],
            name="fk_outlet_issue_global",
        ),
        sa.UniqueConstraint("outlet_id", "slug",
                            name="uq_outlet_issue_slug"),
    )

    op.create_table(
        "outlet_sub_categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("outlet_id", sa.Integer(), nullable=False),
        sa.Column("sub_category_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("is_custom", sa.Boolean(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_trash", sa.Boolean(),
                  server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["sub_category_id"], ["sub_categories.id"],
            name="fk_outlet_subcategory_global",
        ),
        sa.UniqueConstraint("outlet_id", "slug",
                            name="uq_outlet_subcategory_slug"),
    )

    # ------------------------------------------------------
    # OUTLET MAPPING TABLES
    # ------------------------------------------------------

    op.create_table(
        "outlet_category_subcategory_map",
        sa.Column("outlet_category_id", sa.Integer(), nullable=False),
        sa.Column("outlet_sub_category_id", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["outlet_category_id"],
            ["outlet_categories.id"],
            name="fk_outlet_category_subcategory_outlet_category",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["outlet_sub_category_id"],
            ["outlet_sub_categories.id"],
            name="fk_outlet_category_subcategory_outlet_subcategory",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "outlet_category_id",
            "outlet_sub_category_id",
            name="pk_outlet_category_subcategory",
        ),
        sa.UniqueConstraint(
            "outlet_category_id",
            "outlet_sub_category_id",
            name="uq_outlet_category_subcategory",
        ),
    )

    op.create_table(
        "outlet_issue_category_map",
        sa.Column("outlet_issue_id", sa.Integer(), nullable=False),
        sa.Column("outlet_category_id", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["outlet_issue_id"],
            ["outlet_issues.id"],
            name="fk_outlet_issue_category_outlet_issue",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["outlet_category_id"],
            ["outlet_categories.id"],
            name="fk_outlet_issue_category_outlet_category",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "outlet_issue_id",
            "outlet_category_id",
            name="pk_outlet_issue_category",
        ),
        sa.UniqueConstraint(
            "outlet_issue_id",
            "outlet_category_id",
            name="uq_outlet_issue_category",
        ),
    )

    
    # ------------------------------------------------------
    # TICKETS (NON-DESTRUCTIVE ADDITIONS)
    # ------------------------------------------------------

    op.add_column("tickets", sa.Column("outlet_issue_id", sa.Integer(), nullable=False))
    op.add_column("tickets", sa.Column("outlet_category_id", sa.Integer(), nullable=False))
    op.add_column("tickets", sa.Column("outlet_sub_category_id", sa.Integer(), nullable=False))

    op.add_column("tickets", sa.Column("issue_name_snapshot", sa.String(), nullable=False))
    op.add_column("tickets", sa.Column("category_name_snapshot", sa.String(), nullable=False))
    op.add_column("tickets", sa.Column("sub_category_name_snapshot", sa.String(), nullable=False))

    op.create_foreign_key(
        "fk_ticket_outlet_issue",
        "tickets",
        "outlet_issues",
        ["outlet_issue_id"],
        ["id"],
    )

    op.create_foreign_key(
        "fk_ticket_outlet_category",
        "tickets",
        "outlet_categories",
        ["outlet_category_id"],
        ["id"],
    )

    op.create_foreign_key(
        "fk_ticket_outlet_subcategory",
        "tickets",
        "outlet_sub_categories",
        ["outlet_sub_category_id"],
        ["id"],
    )


# ==========================================================
# DOWNGRADE
# ==========================================================

def downgrade() -> None:
    """Reverse Phase 1 safely"""

    # ------------------------------------------------------
    # DROP TICKET FOREIGN KEYS
    # ------------------------------------------------------

    op.drop_constraint(
        "fk_ticket_outlet_subcategory",
        "tickets",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_ticket_outlet_category",
        "tickets",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_ticket_outlet_issue",
        "tickets",
        type_="foreignkey",
    )

    # ------------------------------------------------------
    # DROP TICKET COLUMNS
    # ------------------------------------------------------

    op.drop_column("tickets", "sub_category_name_snapshot")
    op.drop_column("tickets", "category_name_snapshot")
    op.drop_column("tickets", "issue_name_snapshot")

    op.drop_column("tickets", "outlet_sub_category_id")
    op.drop_column("tickets", "outlet_category_id")
    op.drop_column("tickets", "outlet_issue_id")

    # ------------------------------------------------------
    # DROP OUTLET MAPPING TABLES (DEPEND ON OUTLET TABLES)
    # ------------------------------------------------------

    op.drop_table("outlet_issue_category_map")
    op.drop_table("outlet_category_subcategory_map")

    # ------------------------------------------------------
    # DROP OUTLET TABLES
    # ------------------------------------------------------

    op.drop_table("outlet_sub_categories")
    op.drop_table("outlet_issues")
    op.drop_table("outlet_categories")

    # ------------------------------------------------------
    # DROP GLOBAL MAPPING TABLES
    # ------------------------------------------------------

    op.drop_table("issue_category_map")
    op.drop_table("category_subcategory_map")

    # ------------------------------------------------------
    # DROP GLOBAL MASTER TABLES
    # ------------------------------------------------------

    op.drop_table("sub_categories")
    op.drop_table("issues")
    op.drop_table("categories")
