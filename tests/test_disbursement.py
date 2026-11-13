from claims_service.payments.disbursement import (
    WIRE_THRESHOLD,
    issue_payment,
    select_payment_method,
)


def test_select_payment_method_ach_at_and_below_threshold():
    assert select_payment_method(0.0) == "ach"
    assert select_payment_method(5_000.0) == "ach"
    assert select_payment_method(WIRE_THRESHOLD) == "ach"


def test_select_payment_method_wire_above_threshold():
    assert select_payment_method(WIRE_THRESHOLD + 0.01) == "wire"
    assert select_payment_method(17_000.0) == "wire"


def test_issue_payment_schedules_wire_for_large_amounts():
    result = issue_payment("CLM-WIRE", 17_000.0)
    assert result == {
        "claim_id": "CLM-WIRE",
        "amount": 17_000.0,
        "method": "wire",
        "status": "scheduled",
    }
