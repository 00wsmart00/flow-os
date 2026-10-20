import os
from datetime import date, datetime
from decimal import Decimal

import pytest
from sqlalchemy.orm import Session

from app.db.database import SessionFactory
from app.models import (
    BomItem,
    BomVersion,
    Customer,
    InventorySnapshot,
    Material,
    MaterialSupplyPosition,
    Product,
    SalesOrder,
    SalesOrderLine,
)
from app.repositories.inventory import InventoryRepository
from app.repositories.sales_orders import SalesOrderRepository
from app.schemas.orders import SalesOrderQuery
from app.services.sales_orders import SalesOrderService
from app.services.shortage_analysis import ShortageAnalysisService

pytestmark = pytest.mark.integration


@pytest.fixture
def postgres_session() -> Session:
    if os.getenv("FLOWOS_RUN_POSTGRES_TESTS") != "1":
        pytest.skip("set FLOWOS_RUN_POSTGRES_TESTS=1 to run PostgreSQL integration tests")
    session = SessionFactory()
    transaction = session.begin()
    try:
        yield session
    finally:
        transaction.rollback()
        session.close()


def test_repository_queries_postgres(postgres_session: Session) -> None:
    customer = Customer(code="SYN-INT-CUST", name="Synthetic Integration Customer")
    postgres_session.add(
        SalesOrder(
            order_number="SYN-INT-SO-0001",
            customer=customer,
            status="confirmed",
            total_amount=Decimal("100.00"),
        )
    )
    postgres_session.flush()

    result = SalesOrderRepository(postgres_session).search(
        SalesOrderQuery(customer_code="SYN-INT-CUST")
    )

    assert len(result.items) == 1
    assert result.items[0].order_number == "SYN-INT-SO-0001"
    assert result.items[0].customer.code == "SYN-INT-CUST"


def test_postgres_loads_versioned_bom_for_requirement_expansion(
    postgres_session: Session,
) -> None:
    product = Product(code="SYN-INT-PROD", name="Synthetic Integration Product", base_unit="piece")
    material = Material(code="SYN-INT-MAT", name="Synthetic Integration Fabric", unit="meter")
    bom = BomVersion(
        product=product,
        version="SYN-V1",
        status="active",
        base_quantity=Decimal("1"),
        effective_from=date(2026, 1, 1),
        items=[
            BomItem(
                line_number=1,
                material=material,
                quantity_per=Decimal("1.25"),
                unit="meter",
                waste_rate=Decimal("4"),
                rounding_increment=Decimal("0.1"),
            )
        ],
    )
    order = SalesOrder(
        order_number="SYN-INT-REQ-SO",
        customer=Customer(code="SYN-INT-REQ-CUST", name="Synthetic Requirement Customer"),
        status="confirmed",
        order_date=date(2026, 10, 1),
        lines=[
            SalesOrderLine(
                line_number=1,
                product=product,
                bom_version=bom,
                quantity=Decimal("10"),
                unit="piece",
            )
        ],
    )
    postgres_session.add(order)
    snapshot = InventorySnapshot(
        code="SYN-INT-SNAPSHOT",
        status="final",
        captured_at=datetime(2026, 10, 20, 8, 0, 0),
        source="synthetic-integration-test",
        positions=[
            MaterialSupplyPosition(
                material=material,
                location_code="SYN-WH-A",
                unit="meter",
                on_hand_quantity=Decimal("10"),
                reserved_quantity=Decimal("1"),
                safety_stock_quantity=Decimal("1"),
                eligible_inbound_quantity=Decimal("0"),
                excluded_inbound_quantity=Decimal("0"),
            )
        ],
    )
    postgres_session.add(snapshot)
    postgres_session.flush()

    result = SalesOrderService(
        SalesOrderRepository(postgres_session)
    ).calculate_material_requirements(order.id)

    assert len(result.items) == 1
    assert result.items[0].material_code == "SYN-INT-MAT"
    assert result.items[0].required_quantity == Decimal("13.000000")

    shortage = ShortageAnalysisService(
        SalesOrderRepository(postgres_session),
        InventoryRepository(postgres_session),
    ).analyze(order.id, snapshot.id)

    assert shortage.items[0].available_quantity == Decimal("8.000000")
    assert shortage.items[0].shortage_quantity == Decimal("5.000000")
