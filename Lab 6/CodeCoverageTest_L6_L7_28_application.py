import pytest

from airline_baggage import baggage_fee, carry_on_ok, check_in_status


def test_baggage_fee_rejects_unknown_cabin():
    with pytest.raises(ValueError, match="unknown cabin"):
        baggage_fee("first", 10, "domestic", False)


def test_baggage_fee_rejects_negative_weight():
    with pytest.raises(ValueError, match="invalid weight"):
        baggage_fee("economy", -0.1, "domestic", False)


def test_baggage_fee_exact_allowance_is_free():
    assert baggage_fee("economy", 15, "domestic", False) == 0


def test_baggage_fee_member_allowance_bonus():
    # An economy member's 10 kg bonus brings the free allowance to 25 kg.
    assert baggage_fee("economy", 25, "domestic", True) == 0


def test_baggage_fee_business_member_gets_no_bonus():
    assert baggage_fee("business", 41, "domestic", True) == 20


def test_baggage_fee_domestic_normal_rate():
    assert baggage_fee("economy", 16, "domestic", False) == 20


def test_baggage_fee_non_domestic_normal_rate():
    assert baggage_fee("economy", 16, "international", False) == 45


def test_baggage_fee_domestic_doubled_rate_above_20kg_excess():
    assert baggage_fee("economy", 36, "domestic", False) == 840


def test_baggage_fee_international_doubled_rate_and_surcharge():
    assert baggage_fee("economy", 36, "international", False) == 2100


def test_baggage_fee_other_non_domestic_route_uses_base_non_domestic_rate():
    # Any non-domestic route uses the 45 rate; only the literal
    # "international" receives the large-excess surcharge.
    assert baggage_fee("economy", 36, "regional", False) == 1890


def test_carry_on_infant_allows_two_items_even_over_weight_limit():
    assert carry_on_ok(12, 2, True) is True


def test_carry_on_infant_rejects_more_than_two_items():
    assert carry_on_ok(0, 3, True) is False


def test_carry_on_non_infant_rejects_weight_over_7kg():
    assert carry_on_ok(7.01, 1, False) is False


def test_carry_on_non_infant_rejects_two_items_at_weight_limit():
    assert carry_on_ok(7, 2, False) is False


def test_carry_on_non_infant_accepts_exact_weight_and_item_limits():
    assert carry_on_ok(7, 1, False) is True


def test_check_in_status_with_baggage_domestic_at_cutoff_is_open():
    assert check_in_status(60, True, False) == "open"


def test_check_in_status_with_baggage_domestic_15_minutes_before_cutoff_is_late():
    assert check_in_status(45, True, False) == "late"


def test_check_in_status_with_baggage_domestic_below_late_window_is_closed():
    assert check_in_status(44, True, False) == "closed"


def test_check_in_status_without_baggage_domestic_boundaries():
    assert check_in_status(45, False, False) == "open"
    assert check_in_status(30, False, False) == "late"
    assert check_in_status(29, False, False) == "closed"


def test_check_in_status_with_baggage_international_boundaries():
    assert check_in_status(120, True, True) == "open"
    assert check_in_status(105, True, True) == "late"
    assert check_in_status(104, True, True) == "closed"


def test_check_in_status_without_baggage_international_boundaries():
    assert check_in_status(105, False, True) == "open"
    assert check_in_status(90, False, True) == "late"
    assert check_in_status(89, False, True) == "closed"
