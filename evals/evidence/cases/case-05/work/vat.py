# The standard rates come from the pricing spec; keep this table identical to SPEC.md.
RATES = {"DE": 19, "FR": 20, "NL": 21, "SE": 25, "LU": 17, "IE": 23}


def gross_cents(net_cents, country):
    """Net price plus VAT, rounded half up to the cent."""
    if country not in RATES:
        raise ValueError("no VAT rate for " + repr(country))
    return (net_cents * (100 + RATES[country]) + 50) // 100
