# Guidance for automated agents working in this repo

This is a claims-processing service for an insurance carrier. Mistakes here move real money.

## Hard rules
- Never modify anything under `claims_service/payments/`. It is human-owned code.
  If a fix seems to require changing it, stop and explain why in your summary instead.
- Never weaken or delete existing tests to make a change pass.
- Never log or hardcode policyholder data (names, policy numbers, emails, phone numbers).

## How to fix a bug here
1. Reproduce it first: add a regression test in `tests/` that fails on the current code.
2. Make the smallest change that makes that test pass.
3. Run the full suite with `python -m pytest` and confirm everything passes.
4. In your summary, state the root cause, the fix, and which tests you added.

## Business rules worth knowing
- The policy deductible is applied once per claim, never per line item.
- Payouts are never negative and never exceed the coverage limit.
