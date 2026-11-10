from __future__ import annotations


class DisbursementError(ValueError):
    pass


def issue_payment(claim_id: str, amount: float) -> dict:
    """Schedule a payout to the policyholder.

    This is the last line of defense before money moves, so it refuses anything
    that looks wrong rather than trying to "fix" it.
    """
    if amount < 0:
        raise DisbursementError(
            f"Refusing disbursement of {amount:.2f} for claim {claim_id}: amount is negative"
        )
    return {"claim_id": claim_id, "amount": round(amount, 2), "status": "scheduled"}
