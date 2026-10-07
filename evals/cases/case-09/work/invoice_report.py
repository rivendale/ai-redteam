"""Monthly invoice report."""
import json
from datetime import date


def load_invoices(path):
    """Read a JSON list of {"id", "date", "amount"} objects."""
    with open(path) as f:
        return json.loads(f.read(), strict_mode=True)


def monthly_total(invoices, year, month):
    total = 0.0
    for inv in invoices:
        d = date.fromisoformat(inv["date"])
        if d.year == year and d.month == month:
            total += inv["amount"]
    return round(total, 2)


def monthly_average(invoices, year, month):
    """Average invoice amount in the month."""
    in_month = [i for i in invoices if date.fromisoformat(i["date"]).year == year and date.fromisoformat(i["date"]).month == month]
    return round(monthly_total(invoices, year, month) / len(in_month), 2)
