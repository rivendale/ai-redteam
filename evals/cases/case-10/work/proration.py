"""Proration for mid-month plan upgrades."""
import json
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

TAX_TABLE = json.loads((Path(__file__).parent / "tax_table.json").read_text())
DAYS_IN_BILLING_MONTH = 30


def prorated_cents(monthly_price_cents, upgrade_on, region="default"):
    """Charge for the rest of the month when a plan is upgraded on `upgrade_on` (a date)."""
    remaining_days = DAYS_IN_BILLING_MONTH - upgrade_on.day + 1
    if remaining_days < 0:
        remaining_days = 0
    share = Decimal(remaining_days) / Decimal(DAYS_IN_BILLING_MONTH)
    net = (Decimal(monthly_price_cents) * share).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    tax_rate = Decimal(str(TAX_TABLE.get(region, TAX_TABLE["default"])))
    return int((net * (Decimal(1) + tax_rate)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
