"""Add database checks for inventory and order values.

Revision ID: 0002_order_inventory_checks
Revises: 429be60fed4b
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0002_order_inventory_checks"
down_revision: Union[str, None] = "429be60fed4b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("products") as batch_op:
        batch_op.create_check_constraint("ck_products_price_nonnegative", "price >= 0")
        batch_op.create_check_constraint("ck_products_quantity_nonnegative", "quantity >= 0")
    with op.batch_alter_table("orders") as batch_op:
        batch_op.create_check_constraint("ck_orders_total_nonnegative", "total >= 0")
        batch_op.create_check_constraint(
            "ck_orders_status_valid", "status IN ('placed', 'cancelled')"
        )
    with op.batch_alter_table("order_items") as batch_op:
        batch_op.create_check_constraint(
            "ck_order_items_quantity_positive", "quantity > 0"
        )
        batch_op.create_check_constraint(
            "ck_order_items_unit_price_nonnegative", "unit_price >= 0"
        )


def downgrade() -> None:
    with op.batch_alter_table("order_items") as batch_op:
        batch_op.drop_constraint("ck_order_items_unit_price_nonnegative", type_="check")
        batch_op.drop_constraint("ck_order_items_quantity_positive", type_="check")
    with op.batch_alter_table("orders") as batch_op:
        batch_op.drop_constraint("ck_orders_status_valid", type_="check")
        batch_op.drop_constraint("ck_orders_total_nonnegative", type_="check")
    with op.batch_alter_table("products") as batch_op:
        batch_op.drop_constraint("ck_products_quantity_nonnegative", type_="check")
        batch_op.drop_constraint("ck_products_price_nonnegative", type_="check")
