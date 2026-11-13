from datetime import date

import pytest

from claims_service.models import Claim, LineItem, Policy
from claims_service.payments.disbursement import (
    DisbursementError,
    WIRE_THRESHOLD,
    issue_payment,
    select_payment_method,
)
from claims_service.payouts import calculate_payout


def make_policy(deductible=500.0, limit=25_000.0):
    return Policy(
        policy_number="POL-0000000",
        holder_name="Test Holder",
        deductible=deductible,
        coverage_limit=limit,
    )


def test_single_line_item_subtracts_deductible():
    claim = Claim("CLM-1", make_policy(), date(2026, 1, 5), [LineItem("Roof repair", 2_000.0)])
    assert calculate_payout(claim) == 1_500.0


def test_payout_is_capped_at_coverage_limit():
    claim = Claim(
        "CLM-2",
        make_policy(limit=10_000.0),
        date(2026, 1, 5),
        [LineItem("Full kitchen rebuild", 50_000.0)],
    )
    assert calculate_payout(claim) == 10_000.0


def test_disbursement_rejects_negative_amounts():
    with pytest.raises(DisbursementError):
        issue_payment("CLM-3", -10.0)


def test_select_payment_method_uses_ach_up_to_wire_threshold():
    assert select_payment_method(WIRE_THRESHOLD) == "ach"


def test_select_payment_method_uses_wire_above_wire_threshold():
    # Regression for incident fingerprint 4bfc8f02938a: $17k payouts failed in production.
    assert select_payment_method(17_000.00) == "wire"


def test_issue_payment_schedules_wire_for_amount_above_threshold():
    result = issue_payment("CLM-4", 17_000.00)
    assert result == {
        "claim_id": "CLM-4",
        "amount": 17_000.00,
        "method": "wire",
        "status": "scheduled",
    }
