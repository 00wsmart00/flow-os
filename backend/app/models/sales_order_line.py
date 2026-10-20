from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
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
    from app.models.bom import BomVersion
    from app.models.product import Product
    from app.models.sales_order import SalesOrder


def utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class SalesOrderLine(BaseModel):
    __tablename__ = "sales_order_line"
    __table_args__ = (
        UniqueConstraint("sales_order_id", "line_number", name="uq_order_line_order_line"),
        CheckConstraint("quantity > 0", name="sales_order_line_quantity_positive"),
        Index("sales_order_line_sales_order_id", "sales_order_id"),
        Index("sales_order_line_product_id", "product_id"),
        Index("sales_order_line_bom_version_id", "bom_version_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    sales_order_id: Mapped[int] = mapped_column(
        ForeignKey("sales_order.id", ondelete="CASCADE")
    )
    line_number: Mapped[int] = mapped_column(Integer())
    product_id: Mapped[int] = mapped_column(
        ForeignKey("product.id", ondelete="RESTRICT")
    )
    bom_version_id: Mapped[int | None] = mapped_column(
        ForeignKey("bom_version.id", ondelete="RESTRICT"), nullable=True
    )
    quantity: Mapped[Decimal] = mapped_column(Numeric(14, 3))
    unit: Mapped[str] = mapped_column(String(16))
    color: Mapped[str | None] = mapped_column(String(48), nullable=True)
    size: Mapped[str | None] = mapped_column(String(32), nullable=True)
    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), default=Decimal("0.00")
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(), default=utc_now, onupdate=utc_now
    )

    sales_order: Mapped[SalesOrder] = relationship(back_populates="lines")
    product: Mapped[Product] = relationship(back_populates="order_lines")
    bom_version: Mapped[BomVersion | None] = relationship(back_populates="order_lines")
