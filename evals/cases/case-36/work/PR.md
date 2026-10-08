# PR #131: audit record on cancellation
Head 8a41c7e, merge base 2d90b53.

`cancel_order` now takes a required `actor` and calls `company_audit.record("order.cancelled", ...)` before the status change, so a
failed audit write leaves the order open. Cancelling an order that is already cancelled changes nothing and records nothing. The only
caller, `handlers.cancel`, passes the signed-in user's id. `company_audit.record` writes and fsyncs before it returns (see
base/company_audit.py). Tests pass.
