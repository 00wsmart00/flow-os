from datetime import date
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.database import get_session
from app.main import app
from app.models import (
    BomItem,
    BomVersion,
    Customer,
    Material,
    Product,
    SalesOrder,
    SalesOrderLine,
)


def seed_requirement_order(
    session: Session,
    *,
    status: str = "confirmed",
    with_bom: bool = True,
) -> SalesOrder:
    customer = Customer(code=f"SYN-REQ-CUST-{status}", name="Synthetic Requirement Customer")
    product = Product(code=f"SYN-REQ-PROD-{status}", name="Synthetic Shirt", base_unit="piece")
    material = Material(
        code=f"SYN-REQ-MAT-{status}", name="Synthetic Fabric", unit="meter"
    )
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
        order_number=f"SYN-REQ-SO-{status}",
        customer=customer,
        status=status,
        order_date=date(2026, 10, 1),
        lines=[
            SalesOrderLine(
                line_number=1,
                product=product,
                bom_version=bom if with_bom else None,
                quantity=Decimal("100"),
                unit="piece",
            )
        ],
    )
    session.add(order)
    session.commit()
    return order


def make_client(session: Session) -> TestClient:
    def override_session():
        yield session

    app.dependency_overrides[get_session] = override_session
    return TestClient(app)


def test_material_requirements_are_traceable_and_deterministic(test_session: Session) -> None:
    order = seed_requirement_order(test_session)

    with make_client(test_session) as client:
        response = client.get(f"/api/v1/sales-orders/{order.id}/material-requirements")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    body = response.json()
    assert body["rule_version"] == "material-requirement-v1"
    assert len(body["items"]) == 1
    assert body["items"][0]["material_code"] == "SYN-REQ-MAT-confirmed"
    assert Decimal(body["items"][0]["raw_quantity"]) == Decimal("189")
    assert Decimal(body["items"][0]["required_quantity"]) == Decimal("189")
    assert body["items"][0]["bom_item_id"] > 0


def test_material_requirements_reject_unconfirmed_order(test_session: Session) -> None:
    order = seed_requirement_order(test_session, status="draft")

    with make_client(test_session) as client:
        response = client.get(f"/api/v1/sales-orders/{order.id}/material-requirements")

    app.dependency_overrides.clear()
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "sales_order_not_eligible"


def test_material_requirements_report_missing_bom(test_session: Session) -> None:
    order = seed_requirement_order(test_session, with_bom=False)

    with make_client(test_session) as client:
        response = client.get(f"/api/v1/sales-orders/{order.id}/material-requirements")

    app.dependency_overrides.clear()
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "bom_version_missing"
