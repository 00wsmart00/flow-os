from decimal import Decimal

from pydantic import BaseModel


class MaterialRequirementResponse(BaseModel):
    order_line_id: int
    bom_version_id: int
    bom_version: str
    bom_item_id: int
    material_id: int
    material_code: str
    material_name: str
    order_quantity: Decimal
    order_unit: str
    bom_base_quantity: Decimal
    quantity_per: Decimal
    waste_rate: Decimal
    rounding_increment: Decimal
    raw_quantity: Decimal
    required_quantity: Decimal
    unit: str


class SalesOrderRequirementsResponse(BaseModel):
    sales_order_id: int
    order_number: str
    rule_version: str
    items: list[MaterialRequirementResponse]
