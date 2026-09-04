"""link products to categories

Revision ID: 7a4ee12ddbed
Revises: a56146edc212
Create Date: 2026-09-04

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7a4ee12ddbed"
down_revision: Union[str, Sequence[str], None] = "a56146edc212"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Link existing products to the categories table."""

    # 1. Add the new foreign-key column.
    op.add_column(
        "products",
        sa.Column(
            "category_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    # 2. Create categories from existing product category names.
    op.execute(
        """
        INSERT INTO categories (name)
        SELECT DISTINCT category
        FROM products
        WHERE category IS NOT NULL
        """
    )

    # 3. Link existing products to their corresponding categories.
    op.execute(
        """
        UPDATE products
        SET category_id = categories.id
        FROM categories
        WHERE products.category = categories.name
        """
    )

    # 4. Ensure every existing product was successfully linked.
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM products
                WHERE category_id IS NULL
            ) THEN
                RAISE EXCEPTION
                    'Some products could not be linked to a category.';
            END IF;
        END
        $$;
        """
    )

    # 5. Add the foreign-key constraint.
    op.create_foreign_key(
        "fk_products_category_id_categories",
        "products",
        "categories",
        ["category_id"],
        ["id"],
    )

    # 6. Make category_id mandatory.
    op.alter_column(
        "products",
        "category_id",
        nullable=False,
    )

    # 7. Add an index for efficient category filtering.
    op.create_index(
        "ix_products_category_id",
        "products",
        ["category_id"],
        unique=False,
    )

    # 8. Remove the old text-based category column.
    op.drop_column("products", "category")


def downgrade() -> None:
    """Restore the previous product category representation."""

    # Re-create the old category text column.
    op.add_column(
        "products",
        sa.Column(
            "category",
            sa.String(length=100),
            nullable=True,
        ),
    )

    # Restore category names from the categories table.
    op.execute(
        """
        UPDATE products
        SET category = categories.name
        FROM categories
        WHERE products.category_id = categories.id
        """
    )

    # Make the restored column mandatory.
    op.alter_column(
        "products",
        "category",
        nullable=False,
    )

    # Remove the index and foreign key.
    op.drop_index(
        "ix_products_category_id",
        table_name="products",
    )

    op.drop_constraint(
        "fk_products_category_id_categories",
        "products",
        type_="foreignkey",
    )

    # Remove the foreign-key column.
    op.drop_column("products", "category_id")
