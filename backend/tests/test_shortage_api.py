from datetime import date, datetime
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.database import get_session
from app.main import app
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


def seed_shortage_scenario(session: Session) -> tuple[SalesOrder, InventorySnapshot]:
    product = Product(code="SYN-SHORT-PROD", name="Synthetic Shirt", base_unit="piece")
    material = Material(code="SYN-SHORT-MAT", name="Synthetic Fabric", unit="meter")
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
                quantity_per=Decimal("1.8"),
                unit="meter",
                waste_rate=Decimal("5"),
                rounding_increment=Decimal("0.1"),
            )
        ],
    )
    order = SalesOrder(
        order_number="SYN-SHORT-SO",
        customer=Customer(code="SYN-SHORT-CUST", name="Synthetic Customer"),
        status="confirmed",
        order_date=date(2026, 10, 1),
        lines=[
            SalesOrderLine(
                line_number=1,
                product=product,
                bom_version=bom,
                quantity=Decimal("100"),
                unit="piece",
            )
        ],
    )
    snapshot = InventorySnapshot(
        code="SYN-SHORT-SNAPSHOT",
        status="final",
        captured_at=datetime(2026, 10, 20, 8, 0, 0),
        source="synthetic-test",
        positions=[
            MaterialSupplyPosition(
                material=material,
                location_code="SYN-WH-A",
                unit="meter",
                on_hand_quantity=Decimal("150"),
                reserved_quantity=Decimal("10"),
                safety_stock_quantity=Decimal("5"),
                eligible_inbound_quantity=Decimal("20"),
                excluded_inbound_quantity=Decimal("12"),
            )
        ],
    )
    session.add_all([order, snapshot])
    session.commit()
    return order, snapshot


def make_client(session: Session) -> TestClient:
    def override_session():
        yield session

    app.dependency_overrides[get_session] = override_session
    return TestClient(app)


def test_shortage_analysis_returns_traceable_breakdown(test_session: Session) -> None:
    order, snapshot = seed_shortage_scenario(test_session)

    with make_client(test_session) as client:
        response = client.get(
            f"/api/v1/sales-orders/{order.id}/shortage-analysis",
            params={"snapshot_id": snapshot.id},
        )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    body = response.json()
    assert body["shortage_rule_version"] == "shortage-v1"
    assert body["snapshot_code"] == "SYN-SHORT-SNAPSHOT"
    assert len(body["items"]) == 1
    item = body["items"][0]
    assert Decimal(item["required_quantity"]) == Decimal("189")
    assert Decimal(item["available_quantity"]) == Decimal("155")
    assert Decimal(item["shortage_quantity"]) == Decimal("34")
    assert item["warnings"] == ["excluded_inbound_supply"]
    assert item["requirement_sources"][0]["bom_item_id"] > 0
    assert item["supply_position_ids"][0] > 0


def test_shortage_analysis_reports_missing_snapshot(test_session: Session) -> None:
    order, _ = seed_shortage_scenario(test_session)

    with make_client(test_session) as client:
        response = client.get(
            f"/api/v1/sales-orders/{order.id}/shortage-analysis",
            params={"snapshot_id": 999999},
        )

    app.dependency_overrides.clear()
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "inventory_snapshot_not_found"


def test_shortage_analysis_requires_final_snapshot(test_session: Session) -> None:
    order, snapshot = seed_shortage_scenario(test_session)
    snapshot.status = "draft"
    test_session.commit()

    with make_client(test_session) as client:
        response = client.get(
            f"/api/v1/sales-orders/{order.id}/shortage-analysis",
            params={"snapshot_id": snapshot.id},
        )

    app.dependency_overrides.clear()
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "inventory_snapshot_not_final"
