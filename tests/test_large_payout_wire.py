"""Payouts above the ACH limit must be scheduled by wire.

These tests describe the disbursement behavior claim processing is supposed to
have. They fail while select_payment_method refuses every amount above
WIRE_THRESHOLD, and they pass once that amount is scheduled as a wire transfer.
"""

from datetime import date

from claims_service.app import process_claim
from claims_service.models import Claim, LineItem, Policy
from claims_service.payments.disbursement import issue_payment, select_payment_method


def make_policy(deductible=1_000.0, limit=50_000.0):
    return Policy(
        policy_number="POL-0000000",
        holder_name="Test Holder",
        deductible=deductible,
        coverage_limit=limit,
    )


def make_claim(claim_id, line_amount, deductible=1_000.0, limit=50_000.0):
    return Claim(
        claim_id,
        make_policy(deductible=deductible, limit=limit),
        date(2026, 1, 15),
        [LineItem("Covered structural repair", line_amount)],
    )


def test_select_payment_method_uses_wire_above_threshold():
    assert select_payment_method(10_001.0) == "wire"
    assert select_payment_method(17_000.0) == "wire"
    assert select_payment_method(50_000.0) == "wire"


def test_select_payment_method_keeps_ach_at_threshold():
    assert select_payment_method(10_000.0) == "ach"
    assert select_payment_method(1_500.0) == "ach"


def test_issue_payment_schedules_wire_above_threshold():
    result = issue_payment("CLM-WIRE-DIRECT", 17_000.0)
    assert result == {
        "claim_id": "CLM-WIRE-DIRECT",
        "amount": 17_000.0,
        "method": "wire",
        "status": "scheduled",
    }


def test_issue_payment_schedules_ach_at_threshold():
    result = issue_payment("CLM-ACH-LIMIT", 10_000.0)
    assert result == {
        "claim_id": "CLM-ACH-LIMIT",
        "amount": 10_000.0,
        "method": "ach",
        "status": "scheduled",
    }


def test_process_claim_schedules_wire_for_payout_above_ach_threshold():
    """Attack path: one covered line of 18000, deductible 1000, limit 50000.

    Settlement is 17000, inside the coverage limit and above the ACH cap, so
    claim processing must schedule a wire for that amount.
    """
    claim = make_claim("CLM-WIRE-17000", line_amount=18_000.0)
    result = process_claim(claim)
    assert result == {
        "claim_id": "CLM-WIRE-17000",
        "amount": 17_000.0,
        "method": "wire",
        "status": "scheduled",
    }


def test_process_claim_schedules_wire_when_payout_is_capped_at_coverage_limit():
    """Damages above the limit still pay the limit, by wire when that exceeds 10000."""
    claim = make_claim("CLM-WIRE-CAP", line_amount=80_000.0, deductible=1_000.0, limit=50_000.0)
    result = process_claim(claim)
    assert result == {
        "claim_id": "CLM-WIRE-CAP",
        "amount": 50_000.0,
        "method": "wire",
        "status": "scheduled",
    }


def test_process_claim_schedules_ach_when_payout_is_within_threshold():
    claim = make_claim("CLM-ACH-SMALL", line_amount=2_000.0, deductible=500.0, limit=25_000.0)
    result = process_claim(claim)
    assert result == {
        "claim_id": "CLM-ACH-SMALL",
        "amount": 1_500.0,
        "method": "ach",
        "status": "scheduled",
    }
