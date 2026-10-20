from decimal import Decimal

import pytest

from app.domain.shortage import (
    ShortageCalculationError,
    ShortageInput,
    calculate_shortage,
)


def test_calculates_available_supply_and_shortage() -> None:
    result = calculate_shortage(
        ShortageInput(
            required_quantity=Decimal("189"),
            on_hand_quantity=Decimal("150"),
            reserved_quantity=Decimal("10"),
            safety_stock_quantity=Decimal("5"),
            eligible_inbound_quantity=Decimal("20"),
        )
    )

    assert result.available_quantity == Decimal("155")
    assert result.shortage_quantity == Decimal("34")


def test_shortage_never_falls_below_zero() -> None:
    result = calculate_shortage(
        ShortageInput(
            required_quantity=Decimal("50"),
            on_hand_quantity=Decimal("100"),
            reserved_quantity=Decimal("0"),
            safety_stock_quantity=Decimal("0"),
            eligible_inbound_quantity=Decimal("0"),
        )
    )

    assert result.shortage_quantity == Decimal("0")


def test_preserves_negative_available_supply_for_explanation() -> None:
    result = calculate_shortage(
        ShortageInput(
            required_quantity=Decimal("10"),
            on_hand_quantity=Decimal("5"),
            reserved_quantity=Decimal("8"),
            safety_stock_quantity=Decimal("2"),
            eligible_inbound_quantity=Decimal("0"),
        )
    )

    assert result.available_quantity == Decimal("-5")
    assert result.shortage_quantity == Decimal("15")


def test_rejects_negative_supply_inputs() -> None:
    with pytest.raises(ShortageCalculationError) as error:
        calculate_shortage(
            ShortageInput(
                required_quantity=Decimal("10"),
                on_hand_quantity=Decimal("-1"),
                reserved_quantity=Decimal("0"),
                safety_stock_quantity=Decimal("0"),
                eligible_inbound_quantity=Decimal("0"),
            )
        )

    assert error.value.code == "invalid_supply_quantity"
