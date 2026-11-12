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


def test_select_payment_method_ach_at_or_below_wire_threshold():
    assert select_payment_method(WIRE_THRESHOLD) == "ach"
    assert select_payment_method(5_000.0) == "ach"


def test_select_payment_method_wire_above_wire_threshold():
    assert select_payment_method(17_000.0) == "wire"


def test_issue_payment_schedules_wire_for_large_amounts():
    result = issue_payment("CLM-4", 17_000.0)
    assert result["method"] == "wire"
    assert result["amount"] == 17_000.0
    assert result["status"] == "scheduled"
