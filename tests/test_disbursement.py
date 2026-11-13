from claims_service.payments.disbursement import (
    WIRE_THRESHOLD,
    issue_payment,
    select_payment_method,
)


def test_select_payment_method_ach_at_or_below_threshold():
    assert select_payment_method(WIRE_THRESHOLD) == "ach"
    assert select_payment_method(5_000.0) == "ach"


def test_select_payment_method_wire_above_threshold():
    # Regression for incident fingerprint 4bfc8f02938a (amount 17000.00).
    assert select_payment_method(17_000.0) == "wire"
    assert select_payment_method(WIRE_THRESHOLD + 0.01) == "wire"


def test_issue_payment_schedules_wire_for_amounts_above_threshold():
    result = issue_payment("CLM-WIRE", 17_000.0)
    assert result == {
        "claim_id": "CLM-WIRE",
        "amount": 17_000.0,
        "method": "wire",
        "status": "scheduled",
    }
