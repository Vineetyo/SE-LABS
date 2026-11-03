import pytest

from airline_baggage import baggage_fee, carry_on_ok, check_in_status


def test_baggage_fee_unknown_cabin_raises_value_error():
    with pytest.raises(ValueError, match="unknown cabin"):
        baggage_fee("first", 10, "domestic", False)


def test_baggage_fee_known_cabin_does_not_raise():
    assert baggage_fee("economy", 10, "domestic", False) == 0


def test_baggage_fee_negative_weight_raises_value_error():
    with pytest.raises(ValueError, match="invalid weight"):
        baggage_fee("economy", -1, "domestic", False)


def test_baggage_fee_zero_weight_is_valid():
    assert baggage_fee("economy", 0, "domestic", False) == 0


def test_baggage_fee_nonmember_short_circuits_membership_bonus():
    assert baggage_fee("economy", 16, "domestic", False) == 20


def test_baggage_fee_member_nonbusiness_cabin_gets_bonus():
    assert baggage_fee("economy", 25, "domestic", True) == 0


def test_baggage_fee_business_member_does_not_get_bonus():
    assert baggage_fee("business", 41, "domestic", True) == 20


def test_baggage_fee_excess_at_free_allowance_boundary_is_zero():
    assert baggage_fee("economy", 15, "domestic", False) == 0


def test_baggage_fee_excess_over_allowance_is_charged():
    assert baggage_fee("economy", 16, "domestic", False) == 20


def test_baggage_fee_domestic_route_selects_domestic_rate():
    assert baggage_fee("economy", 16, "domestic", False) == 20


def test_baggage_fee_international_route_selects_other_base_rate():
    assert baggage_fee("economy", 16, "international", False) == 45


def test_baggage_fee_excess_of_exactly_20kg_is_not_doubled():
    assert baggage_fee("economy", 35, "domestic", False) == 400


def test_baggage_fee_excess_over_20kg_is_doubled():
    assert baggage_fee("economy", 36, "domestic", False) == 840


def test_baggage_fee_large_international_excess_gets_surcharge():
    assert baggage_fee("economy", 36, "international", False) == 2100


def test_baggage_fee_large_other_non_domestic_excess_has_no_surcharge():
    assert baggage_fee("economy", 36, "regional", False) == 1890


def test_carry_on_infant_items_at_limit_are_allowed():
    assert carry_on_ok(12, 2, True) is True


def test_carry_on_infant_items_over_limit_are_rejected():
    assert carry_on_ok(0, 3, True) is False


def test_carry_on_noninfant_weight_over_7kg_is_rejected():
    assert carry_on_ok(7.01, 1, False) is False


def test_carry_on_noninfant_weight_at_7kg_passes_weight_check():
    assert carry_on_ok(7, 1, False) is True


def test_carry_on_noninfant_two_items_are_rejected():
    assert carry_on_ok(7, 2, False) is False


def test_carry_on_noninfant_one_item_is_allowed():
    assert carry_on_ok(7, 1, False) is True


@pytest.mark.parametrize(
    ("minutes_before", "has_baggage", "is_international", "expected"),
    [
        # Domestic with baggage: cutoff 60; late boundary 45.
        (60, True, False, "open"),
        (45, True, False, "late"),
        (44, True, False, "closed"),
        # Domestic without baggage: cutoff 45; late boundary 30.
        (45, False, False, "open"),
        (30, False, False, "late"),
        (29, False, False, "closed"),
        # International with baggage: cutoff 120; late boundary 105.
        (120, True, True, "open"),
        (105, True, True, "late"),
        (104, True, True, "closed"),
        # International without baggage: cutoff 105; late boundary 90.
        (105, False, True, "open"),
        (90, False, True, "late"),
        (89, False, True, "closed"),
    ],
)
def test_check_in_status_cutoff_and_late_window_boundaries(
    minutes_before, has_baggage, is_international, expected
):
    assert check_in_status(minutes_before, has_baggage, is_international) == expected
