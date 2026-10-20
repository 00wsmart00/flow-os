"""Add products, order lines, materials, and versioned BOMs."""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0002_order_requirements"
down_revision: str | Sequence[str] | None = "0001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "material",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=48), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("unit", sa.String(length=16), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_material")),
    )
    op.create_index("material_code", "material", ["code"], unique=True)

    op.create_table(
        "product",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=48), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("base_unit", sa.String(length=16), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_product")),
    )
    op.create_index("product_code", "product", ["code"], unique=True)

    op.create_table(
        "bom_version",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("version", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("base_quantity", sa.Numeric(precision=14, scale=3), nullable=False),
        sa.Column("effective_from", sa.Date(), nullable=False),
        sa.Column("effective_to", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "base_quantity > 0",
            name=op.f("ck_bom_version_bom_version_base_quantity_positive"),
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["product.id"],
            name=op.f("fk_bom_version_product_id_product"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_bom_version")),
        sa.UniqueConstraint(
            "product_id", "version", name="uq_bom_version_product_version"
        ),
    )
    op.create_index("bom_version_product_id", "bom_version", ["product_id"])
    op.create_index("bom_version_status", "bom_version", ["status"])

    op.create_table(
        "bom_item",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("bom_version_id", sa.Integer(), nullable=False),
        sa.Column("line_number", sa.Integer(), nullable=False),
        sa.Column("material_id", sa.Integer(), nullable=False),
        sa.Column("quantity_per", sa.Numeric(precision=14, scale=6), nullable=False),
        sa.Column("unit", sa.String(length=16), nullable=False),
        sa.Column("waste_rate", sa.Numeric(precision=7, scale=4), nullable=False),
        sa.Column(
            "rounding_increment", sa.Numeric(precision=14, scale=6), nullable=False
        ),
        sa.CheckConstraint(
            "quantity_per > 0",
            name=op.f("ck_bom_item_bom_item_quantity_per_positive"),
        ),
        sa.CheckConstraint(
            "rounding_increment > 0",
            name=op.f("ck_bom_item_bom_item_rounding_increment_positive"),
        ),
        sa.CheckConstraint(
            "waste_rate >= 0",
            name=op.f("ck_bom_item_bom_item_waste_rate_non_negative"),
        ),
        sa.ForeignKeyConstraint(
            ["bom_version_id"],
            ["bom_version.id"],
            name=op.f("fk_bom_item_bom_version_id_bom_version"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["material_id"],
            ["material.id"],
            name=op.f("fk_bom_item_material_id_material"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_bom_item")),
        sa.UniqueConstraint(
            "bom_version_id", "line_number", name="uq_bom_item_version_line"
        ),
    )
    op.create_index("bom_item_bom_version_id", "bom_item", ["bom_version_id"])
    op.create_index("bom_item_material_id", "bom_item", ["material_id"])

    op.create_table(
        "sales_order_line",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sales_order_id", sa.Integer(), nullable=False),
        sa.Column("line_number", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("bom_version_id", sa.Integer(), nullable=True),
        sa.Column("quantity", sa.Numeric(precision=14, scale=3), nullable=False),
        sa.Column("unit", sa.String(length=16), nullable=False),
        sa.Column("color", sa.String(length=48), nullable=True),
        sa.Column("size", sa.String(length=32), nullable=True),
        sa.Column("unit_price", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "quantity > 0",
            name=op.f("ck_sales_order_line_sales_order_line_quantity_positive"),
        ),
        sa.ForeignKeyConstraint(
            ["bom_version_id"],
            ["bom_version.id"],
            name=op.f("fk_sales_order_line_bom_version_id_bom_version"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["product.id"],
            name=op.f("fk_sales_order_line_product_id_product"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["sales_order_id"],
            ["sales_order.id"],
            name=op.f("fk_sales_order_line_sales_order_id_sales_order"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_sales_order_line")),
        sa.UniqueConstraint(
            "sales_order_id", "line_number", name="uq_order_line_order_line"
        ),
    )
    op.create_index(
        "sales_order_line_bom_version_id", "sales_order_line", ["bom_version_id"]
    )
    op.create_index(
        "sales_order_line_product_id", "sales_order_line", ["product_id"]
    )
    op.create_index(
        "sales_order_line_sales_order_id", "sales_order_line", ["sales_order_id"]
    )


def downgrade() -> None:
    op.drop_index("sales_order_line_sales_order_id", table_name="sales_order_line")
    op.drop_index("sales_order_line_product_id", table_name="sales_order_line")
    op.drop_index("sales_order_line_bom_version_id", table_name="sales_order_line")
    op.drop_table("sales_order_line")
    op.drop_index("bom_item_material_id", table_name="bom_item")
    op.drop_index("bom_item_bom_version_id", table_name="bom_item")
    op.drop_table("bom_item")
    op.drop_index("bom_version_status", table_name="bom_version")
    op.drop_index("bom_version_product_id", table_name="bom_version")
    op.drop_table("bom_version")
    op.drop_index("product_code", table_name="product")
    op.drop_table("product")
    op.drop_index("material_code", table_name="material")
    op.drop_table("material")
