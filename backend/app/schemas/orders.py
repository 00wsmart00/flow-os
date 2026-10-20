from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class SalesOrderQuery(BaseModel):
    order_number: str | None = Field(default=None, max_length=64)
    customer_code: str | None = Field(default=None, max_length=32)
    limit: int = Field(default=50, ge=1, le=200)


class SalesOrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_number: str
    customer_id: int
    status: str
    order_date: date
    promised_date: date | None
    currency: str
    total_amount: Decimal

