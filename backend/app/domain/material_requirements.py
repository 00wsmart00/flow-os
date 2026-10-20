from dataclasses import dataclass
from decimal import ROUND_CEILING, Decimal


class RequirementCalculationError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


@dataclass(frozen=True)
class RequirementInput:
    order_quantity: Decimal
    order_unit: str
    product_unit: str
    bom_base_quantity: Decimal
    quantity_per: Decimal
    component_unit: str
    material_unit: str
    waste_rate: Decimal
    rounding_increment: Decimal


@dataclass(frozen=True)
class RequirementResult:
    raw_quantity: Decimal
    required_quantity: Decimal


def _require_positive(value: Decimal, field: str) -> None:
    if not value.is_finite() or value <= 0:
        raise RequirementCalculationError(
            "invalid_quantity", f"{field} must be a finite value greater than zero"
        )


def calculate_material_requirement(data: RequirementInput) -> RequirementResult:
    _require_positive(data.order_quantity, "order_quantity")
    _require_positive(data.bom_base_quantity, "bom_base_quantity")
    _require_positive(data.quantity_per, "quantity_per")
    _require_positive(data.rounding_increment, "rounding_increment")

    if not data.waste_rate.is_finite() or not Decimal("0") <= data.waste_rate <= Decimal(
        "100"
    ):
        raise RequirementCalculationError(
            "invalid_waste_rate", "waste_rate must be between 0 and 100"
        )
    if data.order_unit != data.product_unit:
        raise RequirementCalculationError(
            "order_unit_mismatch", "order line unit does not match product base unit"
        )
    if data.component_unit != data.material_unit:
        raise RequirementCalculationError(
            "material_unit_mismatch", "BOM item unit does not match material unit"
        )

    raw_quantity = (
        data.order_quantity
        / data.bom_base_quantity
        * data.quantity_per
        * (Decimal("1") + data.waste_rate / Decimal("100"))
    )
    increments = (raw_quantity / data.rounding_increment).to_integral_value(
        rounding=ROUND_CEILING
    )
    required_quantity = increments * data.rounding_increment
    return RequirementResult(
        raw_quantity=raw_quantity,
        required_quantity=required_quantity,
    )
