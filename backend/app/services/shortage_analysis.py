from collections import defaultdict
from decimal import Decimal

from fastapi import status

from app.core.errors import ApplicationError
from app.domain.shortage import ShortageInput, calculate_shortage
from app.repositories.inventory import InventoryRepository
from app.repositories.sales_orders import SalesOrderRepository
from app.schemas.material_requirements import MaterialRequirementResponse
from app.schemas.shortage import (
    MaterialShortageResponse,
    RequirementSourceResponse,
    ShortageAnalysisResponse,
)
from app.services.sales_orders import SalesOrderService


class InventorySnapshotNotFoundError(ApplicationError):
    def __init__(self, snapshot_id: int) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            code="inventory_snapshot_not_found",
            message="Inventory snapshot was not found",
            details={"snapshot_id": snapshot_id},
        )


class ShortageAnalysisUnavailableError(ApplicationError):
    def __init__(self, code: str, message: str, details: dict[str, int | str]) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            code=code,
            message=message,
            details=details,
        )


class ShortageAnalysisService:
    def __init__(
        self,
        sales_orders: SalesOrderRepository,
        inventory: InventoryRepository,
    ) -> None:
        self.sales_orders = sales_orders
        self.inventory = inventory

    def analyze(self, order_id: int, snapshot_id: int) -> ShortageAnalysisResponse:
        requirements = SalesOrderService(
            self.sales_orders
        ).calculate_material_requirements(order_id)
        snapshot = self.inventory.get_snapshot(snapshot_id)
        if snapshot is None:
            raise InventorySnapshotNotFoundError(snapshot_id)
        if snapshot.status != "final":
            raise ShortageAnalysisUnavailableError(
                "inventory_snapshot_not_final",
                "Only final inventory snapshots can be used for shortage analysis",
                {"snapshot_id": snapshot_id, "status": snapshot.status},
            )

        grouped_requirements: dict[
            tuple[int, str], list[MaterialRequirementResponse]
        ] = defaultdict(list)
        for item in requirements.items:
            grouped_requirements[(item.material_id, item.unit)].append(item)

        positions_by_material = defaultdict(list)
        for position in snapshot.positions:
            positions_by_material[position.material_id].append(position)

        items: list[MaterialShortageResponse] = []
        for (material_id, unit), sources in grouped_requirements.items():
            positions = positions_by_material[material_id]
            mismatched = [position for position in positions if position.unit != unit]
            if mismatched:
                raise ShortageAnalysisUnavailableError(
                    "supply_unit_mismatch",
                    "Supply position unit does not match material requirement unit",
                    {
                        "snapshot_id": snapshot_id,
                        "material_id": material_id,
                        "required_unit": unit,
                    },
                )

            required = sum(
                (source.required_quantity for source in sources), start=Decimal("0")
            )
            on_hand = sum(
                (position.on_hand_quantity for position in positions), start=Decimal("0")
            )
            reserved = sum(
                (position.reserved_quantity for position in positions), start=Decimal("0")
            )
            safety_stock = sum(
                (position.safety_stock_quantity for position in positions),
                start=Decimal("0"),
            )
            eligible_inbound = sum(
                (position.eligible_inbound_quantity for position in positions),
                start=Decimal("0"),
            )
            excluded_inbound = sum(
                (position.excluded_inbound_quantity for position in positions),
                start=Decimal("0"),
            )
            result = calculate_shortage(
                ShortageInput(
                    required_quantity=required,
                    on_hand_quantity=on_hand,
                    reserved_quantity=reserved,
                    safety_stock_quantity=safety_stock,
                    eligible_inbound_quantity=eligible_inbound,
                )
            )
            warnings: list[str] = []
            if not positions:
                warnings.append("no_supply_position")
            if excluded_inbound > 0:
                warnings.append("excluded_inbound_supply")
            if result.available_quantity < 0:
                warnings.append("negative_available_supply")

            first = sources[0]
            items.append(
                MaterialShortageResponse(
                    material_id=material_id,
                    material_code=first.material_code,
                    material_name=first.material_name,
                    unit=unit,
                    required_quantity=required,
                    on_hand_quantity=on_hand,
                    reserved_quantity=reserved,
                    safety_stock_quantity=safety_stock,
                    eligible_inbound_quantity=eligible_inbound,
                    excluded_inbound_quantity=excluded_inbound,
                    available_quantity=result.available_quantity,
                    shortage_quantity=result.shortage_quantity,
                    requirement_sources=[
                        RequirementSourceResponse(
                            order_line_id=source.order_line_id,
                            bom_version_id=source.bom_version_id,
                            bom_item_id=source.bom_item_id,
                            required_quantity=source.required_quantity,
                        )
                        for source in sources
                    ],
                    supply_position_ids=[position.id for position in positions],
                    warnings=warnings,
                )
            )

        items.sort(key=lambda item: item.material_code)
        return ShortageAnalysisResponse(
            sales_order_id=requirements.sales_order_id,
            order_number=requirements.order_number,
            snapshot_id=snapshot.id,
            snapshot_code=snapshot.code,
            snapshot_captured_at=snapshot.captured_at,
            requirement_rule_version=requirements.rule_version,
            shortage_rule_version="shortage-v1",
            items=items,
        )
