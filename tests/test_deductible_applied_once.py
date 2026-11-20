"""Settlement must subtract the policy deductible once per claim.

These tests exercise process_claim, which validates the claim, calculates the
payout, and schedules disbursement. They fail while the payout subtracts the
deductible from every line item.
"""

from datetime import date

import pytest

from claims_service.app import process_claim
from claims_service.models import Claim, LineItem, Policy
from claims_service.payouts import calculate_payout


def _claim(claim_id: str, deductible: float, limit: float, items: list[tuple[str, float]]) -> Claim:
    policy = Policy(
        policy_number="POL-0000000",
        holder_name="Test Holder",
        deductible=deductible,
        coverage_limit=limit,
    )
    return Claim(
        claim_id,
        policy,
        date(2026, 1, 5),
        [LineItem(description, amount) for description, amount in items],
    )


# (claim_id, deductible, coverage_limit, line items, payout owed)
# Expected payouts follow: max(0, sum(lines) - deductible) then cap at the limit.
CASES = [
    (
        "CLM-MULTI-UNDER",
        100.0,
        25_000.0,
        [("Repair A", 1_000.0), ("Repair B", 1_000.0)],
        1_900.0,
    ),
    (
        "CLM-MULTI-REJECT",
        500.0,
        25_000.0,
        [("Drywall repair", 420.0), ("Carpet replacement", 380.0), ("Dehumidifier rental", 150.0)],
        450.0,
    ),
    (
        "CLM-BELOW-DED",
        500.0,
        25_000.0,
        [("Small repair A", 200.0), ("Small repair B", 200.0)],
        0.0,
    ),
    (
        "CLM-CAP",
        1_500.0,
        10_000.0,
        [("Rebuild A", 6_000.0), ("Rebuild B", 6_000.0)],
        10_000.0,
    ),
    (
        "CLM-CENTS",
        50.25,
        25_000.0,
        [("Parts", 100.25), ("Labor", 200.50)],
        250.50,
    ),
]


@pytest.mark.parametrize(("claim_id", "deductible", "limit", "items", "expected"), CASES)
def test_calculate_payout_applies_deductible_once(claim_id, deductible, limit, items, expected):
    claim = _claim(claim_id, deductible, limit, items)
    assert calculate_payout(claim) == expected


@pytest.mark.parametrize(("claim_id", "deductible", "limit", "items", "expected"), CASES)
def test_process_claim_schedules_single_deductible(claim_id, deductible, limit, items, expected):
    claim = _claim(claim_id, deductible, limit, items)
    assert process_claim(claim) == {
        "claim_id": claim_id,
        "amount": expected,
        "method": "ach",
        "status": "scheduled",
    }
