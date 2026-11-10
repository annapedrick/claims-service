# claims-service (demo)

A small, deliberately buggy claims-processing service used as the target repo for
the incident-response agent prototype.

- `claims_service/payouts.py`: payout math (deductible, coverage limit)
- `claims_service/payments/`: disbursement, human-owned and protected
- `scripts/trigger_error.py`: processes a claim that triggers the bug and logs an ERROR

Run the tests: `python -m pytest`
