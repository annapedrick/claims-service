from __future__ import annotations

from .models import Claim


def calculate_payout(claim: Claim) -> float:
    """Calculate the amount the carrier owes on a claim.

    Business rule (from the claims handbook):
      payout = (sum of all covered line items) - (policy deductible)
      * The deductible is applied ONCE per claim, not per line item.
      * The payout is never negative: if damages are below the deductible, payout is 0.
      * The payout is capped at the policy's coverage limit.
    """
    total = sum(item.amount for item in claim.line_items) - claim.policy.deductible
    total = max(total, 0.0)
    return round(min(total, claim.policy.coverage_limit), 2)
