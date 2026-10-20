from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel

if TYPE_CHECKING:
    from app.models.material import Material


def utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class InventorySnapshot(BaseModel):
    __tablename__ = "inventory_snapshot"
    __table_args__ = (
        Index("inventory_snapshot_code", "code", unique=True),
        Index("inventory_snapshot_status", "status"),
        Index("inventory_snapshot_captured_at", "captured_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(16), default="draft")
    captured_at: Mapped[datetime] = mapped_column(DateTime())
    source: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(), default=utc_now)

    positions: Mapped[list[MaterialSupplyPosition]] = relationship(
        back_populates="snapshot",
        cascade="all, delete-orphan",
        order_by="MaterialSupplyPosition.id",
    )


class MaterialSupplyPosition(BaseModel):
    __tablename__ = "material_supply_position"
    __table_args__ = (
        UniqueConstraint(
            "snapshot_id",
            "material_id",
            "location_code",
            name="uq_supply_position_snapshot_material_location",
        ),
        CheckConstraint("on_hand_quantity >= 0", name="supply_on_hand_non_negative"),
        CheckConstraint("reserved_quantity >= 0", name="supply_reserved_non_negative"),
        CheckConstraint(
            "safety_stock_quantity >= 0", name="supply_safety_stock_non_negative"
        ),
        CheckConstraint(
            "eligible_inbound_quantity >= 0", name="supply_inbound_non_negative"
        ),
        CheckConstraint(
            "excluded_inbound_quantity >= 0",
            name="supply_excluded_inbound_non_negative",
        ),
        Index("supply_position_snapshot_id", "snapshot_id"),
        Index("supply_position_material_id", "material_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    snapshot_id: Mapped[int] = mapped_column(
        ForeignKey("inventory_snapshot.id", ondelete="CASCADE")
    )
    material_id: Mapped[int] = mapped_column(
        ForeignKey("material.id", ondelete="RESTRICT")
    )
    location_code: Mapped[str] = mapped_column(String(48))
    unit: Mapped[str] = mapped_column(String(16))
    on_hand_quantity: Mapped[Decimal] = mapped_column(
        Numeric(16, 6), default=Decimal("0")
    )
    reserved_quantity: Mapped[Decimal] = mapped_column(
        Numeric(16, 6), default=Decimal("0")
    )
    safety_stock_quantity: Mapped[Decimal] = mapped_column(
        Numeric(16, 6), default=Decimal("0")
    )
    eligible_inbound_quantity: Mapped[Decimal] = mapped_column(
        Numeric(16, 6), default=Decimal("0")
    )
    excluded_inbound_quantity: Mapped[Decimal] = mapped_column(
        Numeric(16, 6), default=Decimal("0")
    )

    snapshot: Mapped[InventorySnapshot] = relationship(back_populates="positions")
    material: Mapped[Material] = relationship()
