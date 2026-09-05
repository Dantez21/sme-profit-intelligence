"""add historical cost to sale items

Revision ID: 2eb4ce06875b
Revises: 392332ec6bde
Create Date: 2026-09-04 20:25:54.028495

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2eb4ce06875b"
down_revision: Union[str, Sequence[str], None] = "392332ec6bde"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add historical product cost to existing sale items."""

    # Add the column temporarily as nullable so existing rows
    # can be populated safely.
    op.add_column(
        "sale_items",
        sa.Column(
            "unit_cost",
            sa.Numeric(
                precision=12,
                scale=2,
            ),
            nullable=True,
        ),
    )

    # Populate historical cost for existing sale items using
    # the product cost currently stored on the product record.
    op.execute(
        """
        UPDATE sale_items
        SET unit_cost = products.cost_price
        FROM products
        WHERE sale_items.product_id = products.id
        """
    )

    # Ensure every existing sale item received a cost.
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM sale_items
                WHERE unit_cost IS NULL
            ) THEN
                RAISE EXCEPTION
                    'Some sale items could not be assigned a unit cost.';
            END IF;
        END
        $$;
        """
    )

    # Make the column mandatory for all future sale items.
    op.alter_column(
        "sale_items",
        "unit_cost",
        nullable=False,
    )


def downgrade() -> None:
    """Remove historical cost from sale items."""

    op.drop_column(
        "sale_items",
        "unit_cost",
    )
