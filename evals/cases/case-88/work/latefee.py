def late_fee(amount, days_late):
    """Late fee for an invoice, in dollars, rounded to cents (see SPEC.md)."""
    if days_late <= 0:
        return 0.0
    months = days_late // 30 + 1
    fee = amount * 0.015 * months
    return round(min(max(fee, 5.0), amount * 0.25), 2)
