from __future__ import annotations

from .models import Claim


class InvalidClaimError(ValueError):
    pass


def validate_claim(claim: Claim) -> None:
    """Reject claims that are structurally invalid before any money math happens."""
    if not claim.line_items:
        raise InvalidClaimError(f"Claim {claim.claim_id} has no line items")
    for item in claim.line_items:
        if item.amount <= 0:
            raise InvalidClaimError(
                f"Claim {claim.claim_id} has a non-positive line item: {item.description}"
            )
