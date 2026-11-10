from __future__ import annotations

import logging
import traceback

from .intake import validate_claim
from .logging_config import get_logger, log_json
from .models import Claim
from .payments.disbursement import issue_payment
from .payouts import calculate_payout

logger = get_logger()


def process_claim(claim: Claim) -> dict:
    """End-to-end claim processing: validate, calculate payout, schedule payment."""
    try:
        validate_claim(claim)
        amount = calculate_payout(claim)
        result = issue_payment(claim.claim_id, amount)
        log_json(logger, logging.INFO, {
            "level": "INFO",
            "event": "claim_processed",
            "claim_id": claim.claim_id,
            "amount": result["amount"],
        })
        return result
    except Exception as exc:
        # Note: this log line includes policyholder PII on purpose. Real systems
        # leak PII into logs all the time, and the incident agent must redact it.
        log_json(logger, logging.ERROR, {
            "level": "ERROR",
            "event": "claim_processing_failed",
            "claim_id": claim.claim_id,
            "policy_number": claim.policy.policy_number,
            "holder_name": claim.policy.holder_name,
            "error_type": type(exc).__name__,
            "message": str(exc),
            "stack": traceback.format_exc(),
        })
        raise
