"""Import customers from a CSV into the billing system."""
import csv
import logging

log = logging.getLogger("customer_import")
PLANS = {"basic", "pro", "team"}


def parse_row(row):
    if not row["email"] or "@" not in row["email"]:
        raise ValueError("bad email")
    if row["plan"] not in PLANS:
        raise ValueError("unknown plan")
    return {"id": int(row["id"]), "email": row["email"].lower(), "plan": row["plan"], "ssn": row["ssn"] or None}


def import_file(path, sink):
    ok, failed = 0, 0
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            try:
                sink(parse_row(row))
                ok += 1
            except (ValueError, KeyError) as e:
                log.error("could not import row %s: %s", dict(row), e)
                failed += 1
    return ok, failed
