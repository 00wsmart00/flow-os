from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class SalesOrderQuery(BaseModel):
    order_number: str | None = Field(default=None, max_length=64)
    customer_code: str | None = Field(default=None, max_length=32)
    status: str | None = Field(default=None, max_length=24)
    before_id: int | None = Field(default=None, ge=1)
    limit: int = Field(default=50, ge=1, le=200)


class CustomerSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str


class SalesOrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_number: str
    customer_id: int
    customer: CustomerSummaryResponse
    status: str
    order_date: date
    promised_date: date | None
    currency: str
    total_amount: Decimal


class SalesOrderListResponse(BaseModel):
    items: list[SalesOrderResponse]
    next_before_id: int | None = None

