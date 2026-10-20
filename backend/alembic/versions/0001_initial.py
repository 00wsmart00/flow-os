"""Create the initial customer and sales-order tables."""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0001_initial"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "customer",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_customer")),
    )
    op.create_index("customer_code", "customer", ["code"], unique=True)

    op.create_table(
        "sales_order",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("order_number", sa.String(length=64), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("order_date", sa.Date(), nullable=False),
        sa.Column("promised_date", sa.Date(), nullable=True),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("total_amount", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["customer_id"],
            ["customer.id"],
            name=op.f("fk_sales_order_customer_id_customer"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_sales_order")),
    )
    op.create_index("sales_order_customer_id", "sales_order", ["customer_id"])
    op.create_index("sales_order_order_date", "sales_order", ["order_date"])
    op.create_index(
        "sales_order_order_number",
        "sales_order",
        ["order_number"],
        unique=True,
    )
    op.create_index("sales_order_status", "sales_order", ["status"])


def downgrade() -> None:
    op.drop_index("sales_order_status", table_name="sales_order")
    op.drop_index("sales_order_order_number", table_name="sales_order")
    op.drop_index("sales_order_order_date", table_name="sales_order")
    op.drop_index("sales_order_customer_id", table_name="sales_order")
    op.drop_table("sales_order")
    op.drop_index("customer_code", table_name="customer")
    op.drop_table("customer")
