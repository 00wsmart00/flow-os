from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class RequirementSourceResponse(BaseModel):
    order_line_id: int
    bom_version_id: int
    bom_item_id: int
    required_quantity: Decimal


class MaterialShortageResponse(BaseModel):
    material_id: int
    material_code: str
    material_name: str
    unit: str
    required_quantity: Decimal
    on_hand_quantity: Decimal
    reserved_quantity: Decimal
    safety_stock_quantity: Decimal
    eligible_inbound_quantity: Decimal
    excluded_inbound_quantity: Decimal
    available_quantity: Decimal
    shortage_quantity: Decimal
    requirement_sources: list[RequirementSourceResponse]
    supply_position_ids: list[int]
    warnings: list[str]


class ShortageAnalysisResponse(BaseModel):
    sales_order_id: int
    order_number: str
    snapshot_id: int
    snapshot_code: str
    snapshot_captured_at: datetime
    requirement_rule_version: str
    shortage_rule_version: str
    items: list[MaterialShortageResponse]
