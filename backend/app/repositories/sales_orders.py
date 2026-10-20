from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models import BomItem, BomVersion, Customer, SalesOrder, SalesOrderLine
from app.schemas.orders import SalesOrderQuery


@dataclass(frozen=True)
class SalesOrderPage:
    items: list[SalesOrder]
    next_before_id: int | None


class SalesOrderRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def search(self, query: SalesOrderQuery) -> SalesOrderPage:
        statement = select(SalesOrder).options(joinedload(SalesOrder.customer)).join(Customer)
        if query.order_number:
            statement = statement.where(SalesOrder.order_number == query.order_number)
        if query.customer_code:
            statement = statement.where(Customer.code == query.customer_code)
        if query.status:
            statement = statement.where(SalesOrder.status == query.status)
        if query.before_id:
            statement = statement.where(SalesOrder.id < query.before_id)

        statement = statement.order_by(SalesOrder.id.desc()).limit(query.limit + 1)
        rows = list(self.session.scalars(statement).all())
        has_more = len(rows) > query.limit
        items = rows[: query.limit]
        next_before_id = items[-1].id if has_more and items else None
        return SalesOrderPage(items=items, next_before_id=next_before_id)

    def get_by_id(self, order_id: int) -> SalesOrder | None:
        statement = (
            select(SalesOrder)
            .options(joinedload(SalesOrder.customer))
            .where(SalesOrder.id == order_id)
        )
        return self.session.scalar(statement)

    def get_for_material_requirements(self, order_id: int) -> SalesOrder | None:
        statement = (
            select(SalesOrder)
            .options(
                selectinload(SalesOrder.lines).joinedload(SalesOrderLine.product),
                selectinload(SalesOrder.lines)
                .joinedload(SalesOrderLine.bom_version)
                .selectinload(BomVersion.items)
                .joinedload(BomItem.material),
            )
            .where(SalesOrder.id == order_id)
        )
        return self.session.scalar(statement)
