from claims_service.payments.disbursement import (
    WIRE_THRESHOLD,
    issue_payment,
    select_payment_method,
)


def test_select_payment_method_uses_ach_at_wire_threshold():
    assert select_payment_method(WIRE_THRESHOLD) == "ach"


def test_select_payment_method_uses_wire_above_threshold():
    """Regression: amounts above WIRE_THRESHOLD must use wire, not raise PaymentMethodError."""
    assert select_payment_method(17_000.00) == "wire"
    assert select_payment_method(WIRE_THRESHOLD + 0.01) == "wire"


def test_issue_payment_schedules_wire_for_large_amount():
    result = issue_payment("CLM-WIRE-1", 17_000.00)
    assert result == {
        "claim_id": "CLM-WIRE-1",
        "amount": 17_000.00,
        "method": "wire",
        "status": "scheduled",
    }


def test_select_payment_method_uses_ach_below_threshold():
    assert select_payment_method(0) == "ach"
    assert select_payment_method(1.0) == "ach"
