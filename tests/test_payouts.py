from datetime import date

import pytest

from claims_service.models import Claim, LineItem, Policy
from claims_service.payments.disbursement import DisbursementError, issue_payment
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


def test_deductible_applied_once_per_claim_not_per_line_item():
    """Regression for CLM-12179: per-line deductible subtraction produced -550.00."""
    claim = Claim(
        "CLM-12179",
        make_policy(deductible=500.0),
        date(2026, 1, 5),
        [
            LineItem("Item A", 450.0),
            LineItem("Item B", 250.0),
            LineItem("Item C", 250.0),
        ],
    )
    assert calculate_payout(claim) == 450.0


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
