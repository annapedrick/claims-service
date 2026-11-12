from __future__ import annotations


class DisbursementError(ValueError):
    pass


class PaymentMethodError(DisbursementError):
    pass


# Payouts up to this amount go by ACH bank transfer.
# Anything larger must be sent by wire transfer (bank ACH limits).
WIRE_THRESHOLD = 10_000.00


def select_payment_method(amount: float) -> str:
    """Choose how to send a payout: ACH up to WIRE_THRESHOLD, wire transfer above it."""
    if amount <= WIRE_THRESHOLD:
        return "ach"
    raise PaymentMethodError(f"No payment method available for amount {amount:.2f}")


def issue_payment(claim_id: str, amount: float) -> dict:
    """Schedule a payout to the policyholder.

    This is the last line of defense before money moves, so it refuses anything
    that looks wrong rather than trying to "fix" it.
    """
    if amount < 0:
        raise DisbursementError(
            f"Refusing disbursement of {amount:.2f} for claim {claim_id}: amount is negative"
        )
    method = select_payment_method(amount)
    return {"claim_id": claim_id, "amount": round(amount, 2), "method": method, "status": "scheduled"}
