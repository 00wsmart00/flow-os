from fastapi import status

from app.core.errors import ApplicationError
from app.domain.material_requirements import (
    RequirementCalculationError,
    RequirementInput,
    calculate_material_requirement,
)
from app.repositories.sales_orders import SalesOrderRepository
from app.schemas.material_requirements import (
    MaterialRequirementResponse,
    SalesOrderRequirementsResponse,
)
from app.schemas.orders import SalesOrderListResponse, SalesOrderQuery, SalesOrderResponse


class SalesOrderNotFoundError(ApplicationError):
    def __init__(self, order_id: int) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            code="sales_order_not_found",
            message="Sales order was not found",
            details={"order_id": order_id},
        )


class MaterialRequirementsUnavailableError(ApplicationError):
    def __init__(
        self,
        code: str,
        message: str,
        details: dict[str, int | str] | None = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            code=code,
            message=message,
            details=details,
        )


class SalesOrderService:
    def __init__(self, repository: SalesOrderRepository) -> None:
        self.repository = repository

    def search(self, query: SalesOrderQuery) -> SalesOrderListResponse:
        page = self.repository.search(query)
        return SalesOrderListResponse(
            items=[
                SalesOrderResponse.model_validate(order, from_attributes=True)
                for order in page.items
            ],
            next_before_id=page.next_before_id,
        )

    def get_by_id(self, order_id: int) -> SalesOrderResponse:
        order = self.repository.get_by_id(order_id)
        if order is None:
            raise SalesOrderNotFoundError(order_id)
        return SalesOrderResponse.model_validate(order, from_attributes=True)

    def calculate_material_requirements(
        self, order_id: int
    ) -> SalesOrderRequirementsResponse:
        order = self.repository.get_for_material_requirements(order_id)
        if order is None:
            raise SalesOrderNotFoundError(order_id)
        if order.status != "confirmed":
            raise MaterialRequirementsUnavailableError(
                "sales_order_not_eligible",
                "Only confirmed sales orders can be expanded into material requirements",
                {"order_id": order_id, "status": order.status},
            )
        if not order.lines:
            raise MaterialRequirementsUnavailableError(
                "sales_order_lines_missing",
                "Sales order has no lines to expand",
                {"order_id": order_id},
            )

        requirements: list[MaterialRequirementResponse] = []
        for line in order.lines:
            bom = line.bom_version
            if bom is None:
                raise MaterialRequirementsUnavailableError(
                    "bom_version_missing",
                    "Sales order line has no selected BOM version",
                    {"order_line_id": line.id},
                )
            if bom.product_id != line.product_id:
                raise MaterialRequirementsUnavailableError(
                    "bom_product_mismatch",
                    "Selected BOM version belongs to a different product",
                    {"order_line_id": line.id, "bom_version_id": bom.id},
                )
            if bom.status != "active" or not (
                bom.effective_from <= order.order_date
                and (bom.effective_to is None or order.order_date <= bom.effective_to)
            ):
                raise MaterialRequirementsUnavailableError(
                    "bom_version_not_effective",
                    "Selected BOM version is not active on the order date",
                    {"order_line_id": line.id, "bom_version_id": bom.id},
                )
            if not bom.items:
                raise MaterialRequirementsUnavailableError(
                    "bom_items_missing",
                    "Selected BOM version has no material items",
                    {"bom_version_id": bom.id},
                )

            for item in bom.items:
                try:
                    calculated = calculate_material_requirement(
                        RequirementInput(
                            order_quantity=line.quantity,
                            order_unit=line.unit,
                            product_unit=line.product.base_unit,
                            bom_base_quantity=bom.base_quantity,
                            quantity_per=item.quantity_per,
                            component_unit=item.unit,
                            material_unit=item.material.unit,
                            waste_rate=item.waste_rate,
                            rounding_increment=item.rounding_increment,
                        )
                    )
                except RequirementCalculationError as exc:
                    raise MaterialRequirementsUnavailableError(
                        exc.code,
                        str(exc),
                        {"order_line_id": line.id, "bom_item_id": item.id},
                    ) from exc
                requirements.append(
                    MaterialRequirementResponse(
                        order_line_id=line.id,
                        bom_version_id=bom.id,
                        bom_version=bom.version,
                        bom_item_id=item.id,
                        material_id=item.material_id,
                        material_code=item.material.code,
                        material_name=item.material.name,
                        order_quantity=line.quantity,
                        order_unit=line.unit,
                        bom_base_quantity=bom.base_quantity,
                        quantity_per=item.quantity_per,
                        waste_rate=item.waste_rate,
                        rounding_increment=item.rounding_increment,
                        raw_quantity=calculated.raw_quantity,
                        required_quantity=calculated.required_quantity,
                        unit=item.unit,
                    )
                )

        return SalesOrderRequirementsResponse(
            sales_order_id=order.id,
            order_number=order.order_number,
            rule_version="material-requirement-v1",
            items=requirements,
        )
