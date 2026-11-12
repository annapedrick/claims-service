from claims_service.payments.disbursement import (
    WIRE_THRESHOLD,
    issue_payment,
    select_payment_method,
)


def test_ach_for_amount_at_or_below_wire_threshold():
    assert select_payment_method(WIRE_THRESHOLD) == "ach"
    assert select_payment_method(9_999.99) == "ach"


def test_wire_for_amount_above_wire_threshold():
    assert select_payment_method(WIRE_THRESHOLD + 0.01) == "wire"


def test_issue_payment_selects_wire_for_large_payout_regression():
    """Regression for incident fingerprint 4bfc8f02938a (amount 17000.00)."""
    result = issue_payment("CLM-WIRE-1", 17_000.0)
    assert result["method"] == "wire"
    assert result["amount"] == 17_000.0
    assert result["status"] == "scheduled"
