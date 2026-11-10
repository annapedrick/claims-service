"""Process a claim that hits the payout bug, producing a real ERROR log line.

  python scripts/trigger_error.py               # log to the terminal only
  python scripts/trigger_error.py --cloudwatch  # also ship the log line to CloudWatch

In a real deployment this code runs in Lambda, which sends stdout to CloudWatch
automatically. On a laptop we ship the line ourselves with PutLogEvents.
"""
from __future__ import annotations

import argparse
import logging
import os
import sys
import time
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from claims_service.app import process_claim  # noqa: E402
from claims_service.logging_config import get_logger  # noqa: E402
from claims_service.models import Claim, LineItem, Policy  # noqa: E402


def build_failing_claim() -> Claim:
    # Water damage claim with several small items. Each item is below the
    # deductible, but together they exceed it, so the correct payout is positive.
    policy = Policy(
        policy_number="POL-4471932",
        holder_name="Dana Whitfield",
        deductible=500.0,
        coverage_limit=25_000.0,
    )
    return Claim(
        claim_id=f"CLM-{int(time.time()) % 100000}",
        policy=policy,
        incident_date=date(2026, 11, 3),
        line_items=[
            LineItem("Drywall repair", 420.0),
            LineItem("Carpet replacement", 380.0),
            LineItem("Dehumidifier rental", 150.0),
        ],
    )


class CloudWatchHandler(logging.Handler):
    """Collects log lines, then sends them to CloudWatch in one call."""

    def __init__(self, log_group: str, region: str):
        super().__init__()
        import boto3

        self.client = boto3.client("logs", region_name=region)
        self.log_group = log_group
        self.stream = f"trigger-{time.strftime('%Y%m%d-%H%M%S')}"
        self.records: list[dict] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append({"timestamp": int(record.created * 1000), "message": record.getMessage()})

    def flush_to_cloudwatch(self) -> None:
        if not self.records:
            return
        try:
            self.client.create_log_group(logGroupName=self.log_group)
        except self.client.exceptions.ResourceAlreadyExistsException:
            pass
        self.client.create_log_stream(logGroupName=self.log_group, logStreamName=self.stream)
        self.client.put_log_events(
            logGroupName=self.log_group, logStreamName=self.stream, logEvents=self.records
        )
        print(f"Sent {len(self.records)} log line(s) to {self.log_group}/{self.stream}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cloudwatch", action="store_true")
    args = parser.parse_args()

    handler = None
    if args.cloudwatch:
        handler = CloudWatchHandler(
            os.environ.get("CLOUDWATCH_LOG_GROUP", "/demo/claims-service"),
            os.environ.get("AWS_REGION", "us-west-2"),
        )
        get_logger().addHandler(handler)

    try:
        process_claim(build_failing_claim())
        return 0
    except Exception:
        return 1
    finally:
        if handler:
            handler.flush_to_cloudwatch()


if __name__ == "__main__":
    sys.exit(main())
