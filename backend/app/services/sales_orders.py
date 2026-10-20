from app.repositories.sales_orders import SalesOrderRepository
from app.schemas.orders import SalesOrderQuery, SalesOrderResponse


class SalesOrderService:
    def __init__(self, repository: SalesOrderRepository) -> None:
        self.repository = repository

    def search(self, query: SalesOrderQuery) -> list[SalesOrderResponse]:
        return [
            SalesOrderResponse.model_validate(order, from_attributes=True)
            for order in self.repository.search(query)
        ]
