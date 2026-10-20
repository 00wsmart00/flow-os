from datetime import date
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.database import get_session
from app.main import app
from app.models import Customer, SalesOrder


def seed_orders(session: Session) -> list[SalesOrder]:
    customer = Customer(code="SYN-CUST-API", name="Synthetic API Customer")
    orders = [
        SalesOrder(
            order_number=f"SYN-SO-API-{index:04d}",
            customer=customer,
            status="confirmed" if index != 2 else "draft",
            order_date=date(2026, 10, index),
            total_amount=Decimal(f"{index * 100}.00"),
        )
        for index in range(1, 4)
    ]
    session.add_all(orders)
    session.commit()
    return orders


def make_client(session: Session) -> TestClient:
    def override_session():
        yield session

    app.dependency_overrides[get_session] = override_session
    return TestClient(app)


def test_list_sales_orders_filters_and_paginates(test_session: Session) -> None:
    seed_orders(test_session)

    with make_client(test_session) as client:
        first_page = client.get("/api/v1/sales-orders", params={"limit": 2})
        filtered = client.get(
            "/api/v1/sales-orders",
            params={"customer_code": "SYN-CUST-API", "status": "confirmed"},
        )
        second_page = client.get(
            "/api/v1/sales-orders",
            params={"limit": 2, "before_id": first_page.json()["next_before_id"]},
        )

    app.dependency_overrides.clear()
    assert first_page.status_code == 200
    assert len(first_page.json()["items"]) == 2
    assert first_page.json()["next_before_id"] is not None
    assert len(filtered.json()["items"]) == 2
    assert {item["status"] for item in filtered.json()["items"]} == {"confirmed"}
    assert len(second_page.json()["items"]) == 1
    assert second_page.json()["next_before_id"] is None


def test_get_sales_order_and_not_found(test_session: Session) -> None:
    orders = seed_orders(test_session)

    with make_client(test_session) as client:
        response = client.get(f"/api/v1/sales-orders/{orders[0].id}")
        missing = client.get("/api/v1/sales-orders/999999")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["order_number"] == orders[0].order_number
    assert response.json()["customer"]["code"] == "SYN-CUST-API"
    assert missing.status_code == 404
    assert missing.json() == {
        "error": {
            "code": "sales_order_not_found",
            "message": "Sales order was not found",
            "details": {"order_id": 999999},
        }
    }


def test_list_sales_orders_validates_limit(test_session: Session) -> None:
    with make_client(test_session) as client:
        response = client.get("/api/v1/sales-orders", params={"limit": 201})

    app.dependency_overrides.clear()
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "request_validation_error"


def test_openapi_documents_bounded_sales_order_contract() -> None:
    schema = app.openapi()
    list_operation = schema["paths"]["/api/v1/sales-orders"]["get"]
    detail_operation = schema["paths"]["/api/v1/sales-orders/{order_id}"]["get"]
    requirements_operation = schema["paths"][
        "/api/v1/sales-orders/{order_id}/material-requirements"
    ]["get"]
    shortage_operation = schema["paths"][
        "/api/v1/sales-orders/{order_id}/shortage-analysis"
    ]["get"]

    parameters = {parameter["name"] for parameter in list_operation["parameters"]}
    assert parameters == {"order_number", "customer_code", "status", "before_id", "limit"}
    assert "200" in list_operation["responses"]
    assert "404" in detail_operation["responses"]
    assert "409" in requirements_operation["responses"]
    assert "409" in shortage_operation["responses"]
