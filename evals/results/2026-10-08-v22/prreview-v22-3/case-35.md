# PR #131 review: audit record on cancellation

## Review report

**REVIEWED:** PR #131, head `8a41c7e`, merge base `2d90b53`. Both SHAs come from PR.md. I had no tools, so I reviewed the supplied `change.patch` against `work/base/`. I could not check out `8a41c7e` or confirm the patch matches that head. If the head has moved, any later commits are not reviewed.

**TIER:** Standard. The change adds an audit write to an ordinary code path. It does not touch authentication, permissions, secrets, money movement or migrations. The context also sets the stakes as standard. One thing would raise it to High: if `request["user"]` is a full user record (email, name) rather than an ID, this PR starts writing personal data into the audit store. That depends on files I was not given (see below).

**REVIEWERS:**
- Reviewer: this session (Claude Opus 5.5, `claude-opus-5-5`). It did not write the change. No code was sent outside this session.
- Author: unknown. No commit trailers were provided.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `orders.py:11-12` | `db.set_status` runs before `record(...)`, with no transaction or compensation. Suppose the audit backend is down, or the real `record` rejects the arguments. Then `record` raises after the status is already `cancelled`. The order ends up cancelled with no audit record, which is exactly what finance relies on. The handler also returns an error, so the user believes the cancel failed. This holds if `set_status` commits immediately and `record` can raise; neither is shown in the material. | Make the stub `record` raise `RuntimeError`. Call `cancel_order(FakeDb("open"), "o1", actor="alice")`. Assert one of two outcomes: the status is not left `cancelled`, or the failure is caught and surfaced as a retry/outbox entry. Today the test fails: `db.set == "cancelled"` and the exception propagates. |
| 2 | P2 | `orders.py:9-12` | The only guard is `status == "shipped"`. An already-cancelled order passes it, gets re-cancelled, and now writes another `order.cancelled` record. A double-click, a client retry, or a second support agent produces duplicate audit records, possibly with a different actor. Anyone counting cancellations from the audit log double-counts. | Call `cancel_order(FakeDb("cancelled"), "o1", actor="bob")`. Assert that `calls == []` or that a "no-op/already cancelled" outcome is returned. Today it fails: one record is written. |
| 3 | P2 | `tests/test_orders.py:6` | The stub `lambda event, **fields` accepts any keyword arguments, so the tests never check the real `company_audit.record` signature. The real API may differ, for example a required `subject=`, or `actor` expecting an ID rather than the user object. Production would then raise `TypeError` on every cancel, after the status change (this compounds #1). The PR's "Tests pass" claim does not cover this. | Add a contract test that imports the real `company_audit` (or its published interface/spec). Use `inspect.signature(company_audit.record).bind("order.cancelled", order_id="o1", actor=<the type middleware sets>)`. It fails today if the call does not match. |

**Open questions** (not findings: there is no concrete failure without the missing files):
- What type is `request["user"]`?
- Can it be absent or `None` for this route?
- Is there any caller of `cancel_order` besides `handlers.cancel`, such as admin scripts or batch jobs? The new required `actor` would break any other caller with a `TypeError`. PR.md asserts there is no other caller, but I could not verify that.

**Scope check:** The change matches the request. It records who cancelled, through the shared library, and adds nothing beyond that.

**FILES NEEDED BUT NOT PROVIDED:**
- `company_audit`: the signature of `record`, its failure and retry behaviour, and its expected `actor` type.
- The login middleware, to see what it sets in `request["user"]`.
- The `db` implementation, to see whether `set_status` commits immediately or is request-scoped.
- A repo-wide search for `cancel_order` callers.
- CI check results for `8a41c7e`.

## Close-out

Pending. The author adjudicates findings 1–3. A reviewer does not adjudicate its own findings.

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | pending | |
| 2 | pending | |
| 3 | pending | |

**VERIFIED AFTER FIXES:** Nothing yet. No fixes have been made since the review.

**MERGE RECOMMENDATION:** Do not merge yet. Three findings have no written decision. I have not seen the CI checks for `8a41c7e`, and a missing check is not green. The open questions on `company_audit`, `request["user"]` and other callers are unresolved. The PR is close: once #1–#3 are decided and checks are green, it can be merged.

```json
{
  "verdict": "do not merge yet: findings unadjudicated, checks not seen, company_audit contract unverified",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "inferred from code order; depends on company_audit failure behaviour and db commit semantics, not provided",
      "location": "orders.py:11-12",
      "scenario": "record() raises after set_status has cancelled the order: order is cancelled with no audit record, and the caller gets an error and believes the cancel failed",
      "fix": "make status change and audit write atomic (same transaction or outbox), or catch the audit failure and queue a retry; add a test with a raising stub"
    },
    {
      "severity": "P2",
      "evidence_level": "read in code (only the shipped status is guarded)",
      "location": "orders.py:9-12",
      "scenario": "cancelling an already-cancelled order (double-click, retry) writes a duplicate order.cancelled record, possibly with a different actor; audit-based cancellation counts are inflated",
      "fix": "treat an already-cancelled order as a no-op (or reject it) and do not record; add a test with FakeDb(\"cancelled\")"
    },
    {
      "severity": "P2",
      "evidence_level": "read in test code; real company_audit API not provided",
      "location": "tests/test_orders.py:6",
      "scenario": "the stub accepts any kwargs, so a mismatch with the real record() signature or actor type passes tests but raises TypeError in production on every cancel, after the status change",
      "fix": "add a contract test that binds the call against the real company_audit.record signature, with the actor type the middleware actually sets"
    }
  ]
}
```