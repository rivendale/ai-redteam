"""Shared audit trail. record() appends one JSON line to the audit file and flushes it to disk before it returns."""
import json
import os
import time

AUDIT_PATH = os.environ.get("AUDIT_PATH", "audit.log")


def record(event, **fields):
    line = json.dumps({"ts": time.time(), "event": event, **fields}, sort_keys=True)
    with open(AUDIT_PATH, "a") as f:
        f.write(line + "\n")
        f.flush()
        os.fsync(f.fileno())
