from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Customer, SalesOrder
from app.schemas.orders import SalesOrderQuery


class SalesOrderRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def search(self, query: SalesOrderQuery) -> list[SalesOrder]:
        statement = select(SalesOrder).join(Customer)
        if query.order_number:
            statement = statement.where(SalesOrder.order_number == query.order_number)
        if query.customer_code:
            statement = statement.where(Customer.code == query.customer_code)
        statement = statement.order_by(SalesOrder.id.desc()).limit(query.limit)
        return list(self.session.scalars(statement).all())
