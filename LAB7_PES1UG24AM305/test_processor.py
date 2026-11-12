"""Property-based fuzz tests for the Lab 7 processor functions."""
import math

import pytest
from hypothesis import given, strategies as st

from processor import (
    calculate_pulse_pressure,
    parse_donor_registry,
    validate_blood_type,
)


# The starter implementation should fail these broad no-crash tests. The
# hardened implementation rejects malformed values with ValueError.
@given(st.one_of(st.text(), st.none(), st.integers(), st.floats(allow_nan=True, allow_infinity=True)))
def test_validate_blood_type_no_unexpected_crash(value):
    try:
        result = validate_blood_type(value)
    except ValueError:
        return
    assert isinstance(result, str)
    assert result in {
        "A Positive", "A Negative", "B Positive", "B Negative",
        "AB Positive", "AB Negative", "O Positive", "O Negative",
    }


@given(st.one_of(st.text(), st.none(), st.integers(), st.floats(allow_nan=True, allow_infinity=True)))
def test_calculate_pulse_pressure_safe(value):
    try:
        result = calculate_pulse_pressure(value)
    except ValueError:
        return
    assert isinstance(result, str)
    assert result.startswith("Diff: ") and ", Ratio: " in result


@given(st.one_of(st.text(), st.none(), st.integers(), st.floats(allow_nan=True, allow_infinity=True)))
def test_parse_donor_registry_safe(value):
    try:
        result = parse_donor_registry(value)
    except ValueError:
        return
    assert isinstance(result, str)
    assert result.startswith("Donor ") and result.endswith(("Eligible", "Deferred"))


# Valid-domain properties ensure that the functions do more than merely avoid
# crashing: they preserve the expected normalization and calculations.
@given(
    antigen=st.sampled_from(["A", "B", "AB", "O"]),
    rh=st.sampled_from(["+", "-"]),
    whitespace=st.text(alphabet=" \t", max_size=3),
)
def test_valid_blood_types_are_normalized(antigen, rh, whitespace):
    expected_rh = "Positive" if rh == "+" else "Negative"
    assert validate_blood_type(f"{whitespace}{antigen.lower()}{rh}{whitespace}") == (
        f"{antigen} {expected_rh}"
    )


@given(
    systolic=st.integers(min_value=2, max_value=300),
    diastolic=st.integers(min_value=1, max_value=299),
)
def test_valid_blood_pressure_calculation(systolic, diastolic):
    if systolic <= diastolic:
        with pytest.raises(ValueError):
            calculate_pulse_pressure(f"{systolic}/{diastolic}")
    else:
        expected = f"Diff: {systolic - diastolic}, Ratio: {round(systolic / diastolic, 2)}"
        assert calculate_pulse_pressure(f"{systolic}/{diastolic}") == expected


@given(
    donor_id=st.text(min_size=1, max_size=20).filter(lambda value: "|" not in value and value.strip()),
    weight=st.floats(min_value=0, max_value=250, allow_nan=False, allow_infinity=False),
    hemoglobin=st.floats(min_value=0, max_value=30, allow_nan=False, allow_infinity=False),
)
def test_donor_eligibility_boundaries(donor_id, weight, hemoglobin):
    result = parse_donor_registry(f"{donor_id}|{weight}|{hemoglobin}")
    expected_status = "Eligible" if weight >= 50.0 and hemoglobin >= 12.5 else "Deferred"
    assert result == f"Donor {donor_id.strip()}: {expected_status}"


@pytest.mark.parametrize("value", ["", "A", "AB", "X+", "A++", "O-xyz", None, 42])
def test_invalid_blood_types_raise_value_error(value):
    with pytest.raises(ValueError):
        validate_blood_type(value)


@pytest.mark.parametrize("value", ["", "120", "120/80/70", "x/80", "120/x", "120/0", "80/120", None])
def test_invalid_blood_pressure_raises_value_error(value):
    with pytest.raises(ValueError):
        calculate_pulse_pressure(value)


@pytest.mark.parametrize(
    "value",
    [
        "", "D1|50", "D1|50|13|extra", "|50|13", "D1|abc|13",
        "D1|50|nan", "D1|inf|13", "D1|-1|13", None,
    ],
)
def test_invalid_donor_records_raise_value_error(value):
    with pytest.raises(ValueError):
        parse_donor_registry(value)
