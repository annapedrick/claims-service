# Guidance for automated agents working in this repo

This is a claims-processing service for an insurance carrier. Mistakes here move real money.

## Hard rules
- `claims_service/payments/` is protected, human-owned code. Do not modify it unless your
  task explicitly says "AUTHORIZATION FOR THIS TASK" for protected code. Without that, stop
  and explain why in your summary instead.
- When you are authorized, the change is a draft for the owning team: make the smallest
  possible change, say clearly in the PR that it needs owner review, and never merge it.
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
