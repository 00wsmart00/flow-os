from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel

if TYPE_CHECKING:
    from app.models.sales_order import SalesOrder


def utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class Customer(BaseModel):
    __tablename__ = "customer"
    __table_args__ = (Index("customer_code", "code", unique=True),)

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(32))
    name: Mapped[str] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(DateTime(), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(),
        default=utc_now,
        onupdate=utc_now,
    )

    sales_orders: Mapped[list[SalesOrder]] = relationship(back_populates="customer")
