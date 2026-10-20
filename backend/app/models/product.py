from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel

if TYPE_CHECKING:
    from app.models.bom import BomVersion
    from app.models.sales_order_line import SalesOrderLine


def utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class Product(BaseModel):
    __tablename__ = "product"
    __table_args__ = (Index("product_code", "code", unique=True),)

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(48))
    name: Mapped[str] = mapped_column(String(120))
    base_unit: Mapped[str] = mapped_column(String(16), default="piece")
    created_at: Mapped[datetime] = mapped_column(DateTime(), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(), default=utc_now, onupdate=utc_now
    )

    order_lines: Mapped[list[SalesOrderLine]] = relationship(back_populates="product")
    bom_versions: Mapped[list[BomVersion]] = relationship(back_populates="product")
