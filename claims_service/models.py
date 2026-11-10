from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass
class LineItem:
    """One damaged item or expense on a claim (e.g. drywall repair, hotel night)."""

    description: str
    amount: float


@dataclass
class Policy:
    policy_number: str
    holder_name: str
    deductible: float
    coverage_limit: float


@dataclass
class Claim:
    claim_id: str
    policy: Policy
    incident_date: date
    line_items: list[LineItem] = field(default_factory=list)
