from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
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

SYNTHETIC_CUSTOMERS = (
    {"code": "SYN-CUST-001", "name": "Synthetic Sunrise Apparel"},
    {"code": "SYN-CUST-002", "name": "Synthetic Northwind Studio"},
)

SYNTHETIC_ORDERS = (
    {
        "order_number": "SYN-SO-0001",
        "customer_code": "SYN-CUST-001",
        "status": "confirmed",
        "order_date": date(2026, 10, 1),
        "promised_date": date(2026, 11, 15),
        "currency": "CNY",
        "total_amount": Decimal("12800.00"),
    },
    {
        "order_number": "SYN-SO-0002",
        "customer_code": "SYN-CUST-002",
        "status": "draft",
        "order_date": date(2026, 10, 5),
        "promised_date": date(2026, 11, 30),
        "currency": "CNY",
        "total_amount": Decimal("8600.00"),
    },
)

SYNTHETIC_PRODUCT = {
    "code": "SYN-STYLE-001",
    "name": "Synthetic Everyday Shirt",
    "base_unit": "piece",
}

SYNTHETIC_MATERIALS = (
    {"code": "SYN-MAT-FABRIC-001", "name": "Synthetic Cotton Fabric", "unit": "meter"},
    {"code": "SYN-MAT-BUTTON-001", "name": "Synthetic Button", "unit": "piece"},
)


@dataclass(frozen=True)
class SeedResult:
    customers: int = 0
    sales_orders: int = 0
    products: int = 0
    materials: int = 0
    bom_versions: int = 0
    bom_items: int = 0
    order_lines: int = 0
    inventory_snapshots: int = 0
    supply_positions: int = 0


def seed_synthetic_data(session: Session) -> SeedResult:
    created_customers = 0
    created_orders = 0
    created_products = 0
    created_materials = 0
    created_bom_versions = 0
    created_bom_items = 0
    created_order_lines = 0
    created_inventory_snapshots = 0
    created_supply_positions = 0
    customers: dict[str, Customer] = {}
    orders: dict[str, SalesOrder] = {}

    for data in SYNTHETIC_CUSTOMERS:
        customer = session.scalar(select(Customer).where(Customer.code == data["code"]))
        if customer is None:
            customer = Customer(**data)
            session.add(customer)
            session.flush()
            created_customers += 1
        customers[customer.code] = customer

    for data in SYNTHETIC_ORDERS:
        existing = session.scalar(
            select(SalesOrder).where(SalesOrder.order_number == data["order_number"])
        )
        if existing is None:
            order_data = dict(data)
            customer_code = str(order_data.pop("customer_code"))
            existing = SalesOrder(customer=customers[customer_code], **order_data)
            session.add(existing)
            session.flush()
            created_orders += 1
        orders[existing.order_number] = existing

    product = session.scalar(
        select(Product).where(Product.code == SYNTHETIC_PRODUCT["code"])
    )
    if product is None:
        product = Product(**SYNTHETIC_PRODUCT)
        session.add(product)
        session.flush()
        created_products += 1

    materials: dict[str, Material] = {}
    for data in SYNTHETIC_MATERIALS:
        material = session.scalar(select(Material).where(Material.code == data["code"]))
        if material is None:
            material = Material(**data)
            session.add(material)
            session.flush()
            created_materials += 1
        materials[material.code] = material

    bom = session.scalar(
        select(BomVersion).where(
            BomVersion.product_id == product.id,
            BomVersion.version == "SYN-V1",
        )
    )
    if bom is None:
        bom = BomVersion(
            product=product,
            version="SYN-V1",
            status="active",
            base_quantity=Decimal("1.000"),
            effective_from=date(2026, 1, 1),
        )
        session.add(bom)
        session.flush()
        created_bom_versions += 1

    bom_item_data = (
        (
            1,
            "SYN-MAT-FABRIC-001",
            Decimal("1.800000"),
            "meter",
            Decimal("5.0000"),
            Decimal("0.100000"),
        ),
        (
            2,
            "SYN-MAT-BUTTON-001",
            Decimal("6.000000"),
            "piece",
            Decimal("2.0000"),
            Decimal("1.000000"),
        ),
    )
    for line_number, material_code, quantity_per, unit, waste_rate, increment in bom_item_data:
        item = session.scalar(
            select(BomItem).where(
                BomItem.bom_version_id == bom.id,
                BomItem.line_number == line_number,
            )
        )
        if item is None:
            session.add(
                BomItem(
                    bom_version=bom,
                    line_number=line_number,
                    material=materials[material_code],
                    quantity_per=quantity_per,
                    unit=unit,
                    waste_rate=waste_rate,
                    rounding_increment=increment,
                )
            )
            created_bom_items += 1

    order = orders["SYN-SO-0001"]
    order_line = session.scalar(
        select(SalesOrderLine).where(
            SalesOrderLine.sales_order_id == order.id,
            SalesOrderLine.line_number == 1,
        )
    )
    if order_line is None:
        session.add(
            SalesOrderLine(
                sales_order=order,
                line_number=1,
                product=product,
                bom_version=bom,
                quantity=Decimal("100.000"),
                unit="piece",
                color="synthetic-blue",
                size="mixed",
                unit_price=Decimal("128.00"),
            )
        )
        created_order_lines += 1

    snapshot = session.scalar(
        select(InventorySnapshot).where(
            InventorySnapshot.code == "SYN-SNAPSHOT-2026-10-20"
        )
    )
    if snapshot is None:
        snapshot = InventorySnapshot(
            code="SYN-SNAPSHOT-2026-10-20",
            status="final",
            captured_at=datetime(2026, 10, 20, 8, 0, 0),
            source="synthetic-seed",
        )
        session.add(snapshot)
        session.flush()
        created_inventory_snapshots += 1

    supply_data = (
        (
            "SYN-MAT-FABRIC-001",
            "meter",
            Decimal("150"),
            Decimal("10"),
            Decimal("5"),
            Decimal("20"),
            Decimal("0"),
        ),
        (
            "SYN-MAT-BUTTON-001",
            "piece",
            Decimal("700"),
            Decimal("100"),
            Decimal("50"),
            Decimal("0"),
            Decimal("40"),
        ),
    )
    for material_code, unit, on_hand, reserved, safety, inbound, excluded in supply_data:
        position = session.scalar(
            select(MaterialSupplyPosition).where(
                MaterialSupplyPosition.snapshot_id == snapshot.id,
                MaterialSupplyPosition.material_id == materials[material_code].id,
                MaterialSupplyPosition.location_code == "SYN-WH-A",
            )
        )
        if position is None:
            session.add(
                MaterialSupplyPosition(
                    snapshot=snapshot,
                    material=materials[material_code],
                    location_code="SYN-WH-A",
                    unit=unit,
                    on_hand_quantity=on_hand,
                    reserved_quantity=reserved,
                    safety_stock_quantity=safety,
                    eligible_inbound_quantity=inbound,
                    excluded_inbound_quantity=excluded,
                )
            )
            created_supply_positions += 1

    session.commit()
    return SeedResult(
        customers=created_customers,
        sales_orders=created_orders,
        products=created_products,
        materials=created_materials,
        bom_versions=created_bom_versions,
        bom_items=created_bom_items,
        order_lines=created_order_lines,
        inventory_snapshots=created_inventory_snapshots,
        supply_positions=created_supply_positions,
    )


def main() -> None:
    if settings.env.lower() == "production":
        raise RuntimeError("Synthetic seed data is disabled in production")
    with SessionFactory() as session:
        result = seed_synthetic_data(session)
    counts = ", ".join(f"{key}={value}" for key, value in result.__dict__.items())
    print(f"Synthetic seed complete: {counts}")


if __name__ == "__main__":
    main()
