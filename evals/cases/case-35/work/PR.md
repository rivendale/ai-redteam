# PR #131: audit record on cancellation
Head 8a41c7e, merge base 2d90b53.

`cancel_order` now takes a required `actor` and calls `company_audit.record("order.cancelled", ...)` after the status change. The only
caller, `handlers.cancel`, passes the signed-in user. Tests pass (they stub the library).
