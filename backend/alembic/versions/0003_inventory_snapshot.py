"""Add immutable inventory and supply snapshots."""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0003_inventory_snapshot"
down_revision: str | Sequence[str] | None = "0002_order_requirements"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "inventory_snapshot",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("captured_at", sa.DateTime(), nullable=False),
        sa.Column("source", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_inventory_snapshot")),
    )
    op.create_index(
        "inventory_snapshot_captured_at", "inventory_snapshot", ["captured_at"]
    )
    op.create_index("inventory_snapshot_code", "inventory_snapshot", ["code"], unique=True)
    op.create_index("inventory_snapshot_status", "inventory_snapshot", ["status"])

    op.create_table(
        "material_supply_position",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("snapshot_id", sa.Integer(), nullable=False),
        sa.Column("material_id", sa.Integer(), nullable=False),
        sa.Column("location_code", sa.String(length=48), nullable=False),
        sa.Column("unit", sa.String(length=16), nullable=False),
        sa.Column("on_hand_quantity", sa.Numeric(precision=16, scale=6), nullable=False),
        sa.Column("reserved_quantity", sa.Numeric(precision=16, scale=6), nullable=False),
        sa.Column(
            "safety_stock_quantity", sa.Numeric(precision=16, scale=6), nullable=False
        ),
        sa.Column(
            "eligible_inbound_quantity", sa.Numeric(precision=16, scale=6), nullable=False
        ),
        sa.Column(
            "excluded_inbound_quantity", sa.Numeric(precision=16, scale=6), nullable=False
        ),
        sa.CheckConstraint(
            "eligible_inbound_quantity >= 0",
            name=op.f("ck_material_supply_position_supply_inbound_non_negative"),
        ),
        sa.CheckConstraint(
            "excluded_inbound_quantity >= 0",
            name=op.f(
                "ck_material_supply_position_supply_excluded_inbound_non_negative"
            ),
        ),
        sa.CheckConstraint(
            "on_hand_quantity >= 0",
            name=op.f("ck_material_supply_position_supply_on_hand_non_negative"),
        ),
        sa.CheckConstraint(
            "reserved_quantity >= 0",
            name=op.f("ck_material_supply_position_supply_reserved_non_negative"),
        ),
        sa.CheckConstraint(
            "safety_stock_quantity >= 0",
            name=op.f("ck_material_supply_position_supply_safety_stock_non_negative"),
        ),
        sa.ForeignKeyConstraint(
            ["material_id"],
            ["material.id"],
            name=op.f("fk_material_supply_position_material_id_material"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["snapshot_id"],
            ["inventory_snapshot.id"],
            name=op.f("fk_material_supply_position_snapshot_id_inventory_snapshot"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_material_supply_position")),
        sa.UniqueConstraint(
            "snapshot_id",
            "material_id",
            "location_code",
            name="uq_supply_position_snapshot_material_location",
        ),
    )
    op.create_index(
        "supply_position_material_id", "material_supply_position", ["material_id"]
    )
    op.create_index(
        "supply_position_snapshot_id", "material_supply_position", ["snapshot_id"]
    )


def downgrade() -> None:
    op.drop_index("supply_position_snapshot_id", table_name="material_supply_position")
    op.drop_index("supply_position_material_id", table_name="material_supply_position")
    op.drop_table("material_supply_position")
    op.drop_index("inventory_snapshot_status", table_name="inventory_snapshot")
    op.drop_index("inventory_snapshot_code", table_name="inventory_snapshot")
    op.drop_index("inventory_snapshot_captured_at", table_name="inventory_snapshot")
    op.drop_table("inventory_snapshot")
