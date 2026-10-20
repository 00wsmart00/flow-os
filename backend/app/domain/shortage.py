from dataclasses import dataclass
from decimal import Decimal


class ShortageCalculationError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


@dataclass(frozen=True)
class ShortageInput:
    required_quantity: Decimal
    on_hand_quantity: Decimal
    reserved_quantity: Decimal
    safety_stock_quantity: Decimal
    eligible_inbound_quantity: Decimal


@dataclass(frozen=True)
class ShortageResult:
    available_quantity: Decimal
    shortage_quantity: Decimal


def calculate_shortage(data: ShortageInput) -> ShortageResult:
    for field, value in (
        ("required_quantity", data.required_quantity),
        ("on_hand_quantity", data.on_hand_quantity),
        ("reserved_quantity", data.reserved_quantity),
        ("safety_stock_quantity", data.safety_stock_quantity),
        ("eligible_inbound_quantity", data.eligible_inbound_quantity),
    ):
        if not value.is_finite() or value < 0:
            raise ShortageCalculationError(
                "invalid_supply_quantity",
                f"{field} must be a finite value greater than or equal to zero",
            )

    available = (
        data.on_hand_quantity
        - data.safety_stock_quantity
        - data.reserved_quantity
        + data.eligible_inbound_quantity
    )
    shortage = max(Decimal("0"), data.required_quantity - available)
    return ShortageResult(available_quantity=available, shortage_quantity=shortage)
