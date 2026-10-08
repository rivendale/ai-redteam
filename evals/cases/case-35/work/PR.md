# PR #131: audit record on cancellation
Head 8a41c7e, merge base 2d90b53.

`cancel_order` now calls `company_audit.record("order.cancelled", ...)` after the status change. `actor` is optional, so existing
callers are unaffected. Tests pass (they stub the library).
