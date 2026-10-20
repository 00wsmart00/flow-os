from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel
from app.models.customer import Customer


def utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class SalesOrder(BaseModel):
    __tablename__ = "sales_order"
    __table_args__ = (
        Index("sales_order_order_number", "order_number", unique=True),
        Index("sales_order_customer_id", "customer_id"),
        Index("sales_order_status", "status"),
        Index("sales_order_order_date", "order_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    order_number: Mapped[str] = mapped_column(String(64))
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customer.id", ondelete="RESTRICT")
    )
    status: Mapped[str] = mapped_column(String(24), default="draft")
    order_date: Mapped[date] = mapped_column(Date(), default=date.today)
    promised_date: Mapped[date | None] = mapped_column(Date(), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="CNY")
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0.00"),
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(),
        default=utc_now,
        onupdate=utc_now,
    )

    customer: Mapped[Customer] = relationship(back_populates="sales_orders")
