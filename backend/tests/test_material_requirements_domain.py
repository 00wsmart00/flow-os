from decimal import Decimal

import pytest

from app.domain.material_requirements import (
    RequirementCalculationError,
    RequirementInput,
    calculate_material_requirement,
)


def valid_input(**overrides) -> RequirementInput:
    values = {
        "order_quantity": Decimal("100"),
        "order_unit": "piece",
        "product_unit": "piece",
        "bom_base_quantity": Decimal("1"),
        "quantity_per": Decimal("1.8"),
        "component_unit": "meter",
        "material_unit": "meter",
        "waste_rate": Decimal("5"),
        "rounding_increment": Decimal("0.1"),
    }
    values.update(overrides)
    return RequirementInput(**values)


def test_calculates_waste_and_rounding_with_decimal_precision() -> None:
    result = calculate_material_requirement(valid_input())

    assert result.raw_quantity == Decimal("189.00")
    assert result.required_quantity == Decimal("189.0")


def test_rounds_up_to_explicit_increment() -> None:
    result = calculate_material_requirement(
        valid_input(
            order_quantity=Decimal("3"),
            quantity_per=Decimal("0.333"),
            waste_rate=Decimal("0"),
            rounding_increment=Decimal("0.05"),
        )
    )

    assert result.raw_quantity == Decimal("0.999")
    assert result.required_quantity == Decimal("1.00")


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("order_quantity", Decimal("0")),
        ("quantity_per", Decimal("-1")),
        ("rounding_increment", Decimal("0")),
    ],
)
def test_rejects_non_positive_quantities(field: str, value: Decimal) -> None:
    with pytest.raises(RequirementCalculationError, match="greater than zero"):
        calculate_material_requirement(valid_input(**{field: value}))


def test_rejects_unit_mismatch() -> None:
    with pytest.raises(RequirementCalculationError) as error:
        calculate_material_requirement(valid_input(material_unit="kilogram"))

    assert error.value.code == "material_unit_mismatch"


def test_rejects_waste_rate_outside_supported_range() -> None:
    with pytest.raises(RequirementCalculationError) as error:
        calculate_material_requirement(valid_input(waste_rate=Decimal("100.01")))

    assert error.value.code == "invalid_waste_rate"
