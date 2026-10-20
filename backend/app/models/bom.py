from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel

if TYPE_CHECKING:
    from app.models.material import Material
    from app.models.product import Product
    from app.models.sales_order_line import SalesOrderLine


def utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class BomVersion(BaseModel):
    __tablename__ = "bom_version"
    __table_args__ = (
        UniqueConstraint("product_id", "version", name="uq_bom_version_product_version"),
        CheckConstraint("base_quantity > 0", name="bom_version_base_quantity_positive"),
        Index("bom_version_product_id", "product_id"),
        Index("bom_version_status", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("product.id", ondelete="RESTRICT")
    )
    version: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(16), default="draft")
    base_quantity: Mapped[Decimal] = mapped_column(Numeric(14, 3))
    effective_from: Mapped[date] = mapped_column(Date())
    effective_to: Mapped[date | None] = mapped_column(Date(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(), default=utc_now, onupdate=utc_now
    )

    product: Mapped[Product] = relationship(back_populates="bom_versions")
    items: Mapped[list[BomItem]] = relationship(
        back_populates="bom_version",
        cascade="all, delete-orphan",
        order_by="BomItem.line_number",
    )
    order_lines: Mapped[list[SalesOrderLine]] = relationship(back_populates="bom_version")


class BomItem(BaseModel):
    __tablename__ = "bom_item"
    __table_args__ = (
        UniqueConstraint("bom_version_id", "line_number", name="uq_bom_item_version_line"),
        CheckConstraint("quantity_per > 0", name="bom_item_quantity_per_positive"),
        CheckConstraint("waste_rate >= 0", name="bom_item_waste_rate_non_negative"),
        CheckConstraint(
            "rounding_increment > 0", name="bom_item_rounding_increment_positive"
        ),
        Index("bom_item_bom_version_id", "bom_version_id"),
        Index("bom_item_material_id", "material_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    bom_version_id: Mapped[int] = mapped_column(
        ForeignKey("bom_version.id", ondelete="CASCADE")
    )
    line_number: Mapped[int] = mapped_column(Integer())
    material_id: Mapped[int] = mapped_column(
        ForeignKey("material.id", ondelete="RESTRICT")
    )
    quantity_per: Mapped[Decimal] = mapped_column(Numeric(14, 6))
    unit: Mapped[str] = mapped_column(String(16))
    waste_rate: Mapped[Decimal] = mapped_column(
        Numeric(7, 4), default=Decimal("0.0000")
    )
    rounding_increment: Mapped[Decimal] = mapped_column(
        Numeric(14, 6), default=Decimal("0.001000")
    )

    bom_version: Mapped[BomVersion] = relationship(back_populates="items")
    material: Mapped[Material] = relationship(back_populates="bom_items")
