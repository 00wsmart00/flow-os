from decimal import Decimal

from app.models import Customer, SalesOrder
from app.repositories.sales_orders import SalesOrderRepository
from app.schemas.orders import SalesOrderQuery
from app.services.sales_orders import SalesOrderService


def test_models_repository_and_service_keep_contract_boundary(test_session) -> None:
    customer = Customer(code="SYN-CUST-001", name="Synthetic Sample Customer")
    order = SalesOrder(
        order_number="SYN-SO-0001",
        customer=customer,
        status="confirmed",
        total_amount=Decimal("1234.50"),
    )
    test_session.add(order)
    test_session.commit()

    result = SalesOrderService(SalesOrderRepository(test_session)).search(
        SalesOrderQuery(customer_code="SYN-CUST-001")
    )

    assert len(result) == 1
    assert result[0].order_number == "SYN-SO-0001"
    assert result[0].customer_id == customer.id
    assert result[0].total_amount == Decimal("1234.50")
    assert result[0].__class__.__module__.startswith("app.schemas")


def test_order_query_rejects_unbounded_result_size() -> None:
    try:
        SalesOrderQuery(limit=201)
    except ValueError:
        pass
    else:
        raise AssertionError("query limit above 200 must be rejected")
