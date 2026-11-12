import pytest

from claims_service.payments.disbursement import (
    WIRE_THRESHOLD,
    issue_payment,
    select_payment_method,
)


def test_select_payment_method_uses_ach_at_or_below_wire_threshold():
    assert select_payment_method(WIRE_THRESHOLD) == "ach"
    assert select_payment_method(5_000.0) == "ach"


def test_select_payment_method_uses_wire_above_wire_threshold():
    assert select_payment_method(WIRE_THRESHOLD + 0.01) == "wire"
    assert select_payment_method(17_000.0) == "wire"


def test_issue_payment_schedules_wire_for_large_amount():
    result = issue_payment("CLM-WIRE-1", 17_000.0)
    assert result == {
        "claim_id": "CLM-WIRE-1",
        "amount": 17_000.0,
        "method": "wire",
        "status": "scheduled",
    }
