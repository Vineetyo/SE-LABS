"""Fuzz the public input contracts; invalid input must fail predictably."""
import math
import re

import pytest
from hypothesis import example, given, strategies as st

from processor import parse_booking, tag_label, total_weight


WRONG_TYPES = st.one_of(
    st.none(), st.integers(), st.booleans(), st.floats(),
    st.lists(st.integers()), st.dictionaries(st.text(), st.integers()),
)
LETTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
BOOKING_PATTERN = r"[A-Za-z]+-[0-9]+-[0-9]+[A-Za-z]"


@given(st.text(LETTERS, min_size=1, max_size=8),
       st.integers(1, 10**12), st.integers(1, 10**12), st.sampled_from(LETTERS))
def test_booking_valid(airline, flight, row, seat):
    assert parse_booking(f"{airline}-{flight}-{row}{seat}") == (
        airline.upper(), flight, seat.upper())


@given(st.text())
@example("AI-0-1A")
@example("AI-1-0A")
@example("AI-1-A")
@example("-1-1A")
@example("AI-1-1!")
def test_booking_text_contract(code):
    match = re.fullmatch(BOOKING_PATTERN, code)
    valid = match is not None
    if valid:
        airline, flight, seat = code.split("-")
        valid = int(flight) > 0 and int(seat[:-1]) > 0
    if valid:
        assert parse_booking(code) == (airline.upper(), int(flight), seat[-1].upper())
    else:
        with pytest.raises(ValueError):
            parse_booking(code)


@given(WRONG_TYPES)
def test_booking_wrong_type(value):
    with pytest.raises(TypeError):
        parse_booking(value)


@given(st.lists(st.integers(0, 10**12), max_size=40))
def test_weights_valid(weights):
    # Empty CSV represents no bags; whitespace around each weight is accepted.
    csv = ",".join(f" {weight} " for weight in weights)
    assert total_weight(csv) == float(sum(weights))


@given(st.lists(st.floats(min_value=0, max_value=1e100,
                         allow_nan=False, allow_infinity=False), min_size=1, max_size=20))
def test_weights_decimal(weights):
    assert total_weight(",".join(map(str, weights))) == pytest.approx(sum(weights))


@given(st.text())
@example("")
@example(" ")
@example("nan")
@example("inf")
@example("-1")
@example("1,,2")
@example("1e309")
@example("1e308,1e308")
def test_weights_text_contract(csv):
    if not csv.strip():
        assert total_weight(csv) == 0.0
        return
    try:
        weights = [float(token) for token in csv.split(",")]
    except ValueError:
        valid = False
    else:
        valid = all(math.isfinite(w) and w >= 0 for w in weights)
        valid = valid and math.isfinite(sum(weights))
    if valid:
        assert total_weight(csv) == sum(weights)
    else:
        with pytest.raises(ValueError):
            total_weight(csv)


@given(WRONG_TYPES)
def test_weights_wrong_type(value):
    with pytest.raises(TypeError):
        total_weight(value)


@given(st.integers(max_value=-1))
def test_weights_negative(value):
    with pytest.raises(ValueError):
        total_weight(str(value))


@given(st.sampled_from(["nan", "inf", "-inf", "1e309", "1e308,1e308"]))
def test_weights_nonfinite(value):
    with pytest.raises(ValueError):
        total_weight(value)


@given(st.lists(st.text(LETTERS, min_size=1, max_size=30), min_size=2, max_size=6))
def test_name_valid(parts):
    # Preserve the original first-initial / second-name behavior for extra names.
    assert tag_label("  " + " \t ".join(parts) + "  ") == (
        parts[0][0].upper() + ". " + parts[1].upper())


@given(st.text())
@example("")
@example("Ada")
@example("  \t ")
def test_name_text_contract(name):
    parts = name.split()
    if len(parts) < 2:
        with pytest.raises(ValueError):
            tag_label(name)
    else:
        assert tag_label(name) == parts[0][0].upper() + ". " + parts[1].upper()


@given(WRONG_TYPES)
def test_name_wrong_type(value):
    with pytest.raises(TypeError):
        tag_label(value)


@given(st.integers(min_value=4301, max_value=5000))
def test_booking_extreme_digits(length):
    # Oversized numeric fields must not leak interpreter conversion errors.
    with pytest.raises(ValueError):
        parse_booking("AI-" + "9" * length + "-1A")
