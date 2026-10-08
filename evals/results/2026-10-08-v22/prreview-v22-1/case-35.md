# PR #131 review: audit record on cancellation

**Review report**

**REVIEWED:** PR #131, head `8a41c7e`, merge base `2d90b53`. Both SHAs come from PR.md. I had no tools, so I could not check out the head or confirm these SHAs against git. The review covers only `change.patch` applied to the `base/` files I was given.

**TIER:** Standard. The change adds one side effect, an audit write, to an ordinary code path. It does not touch authentication, permissions, secrets, network exposure, migrations or money movement. One open point: the actor is a user identity, written to a store I cannot see. If `request["user"]` is a personal identifier and `company_audit` sends it outside the service, the owner should confirm whether this is personal data. If it is, the tier becomes High and a second round is required.

**REVIEWERS:** This instance (Opus 5.5, `claude-opus-5-5`). It is independent and did not write the change. The commit trailers were not provided, so I cannot record the author. That needs to be filled in from the commits.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 (P1 if `record` can raise, which I cannot check) | `orders.py:12-13` (`db.set_status` then `record(...)`) | The status is committed before the audit write. If `company_audit.record` raises (library or store unavailable, bad field), the order stays `cancelled` with no audit record, and `handlers.cancel` returns an error to a user whose cancellation actually succeeded. Support and finance then see a cancelled order with no record of who cancelled it, which is the gap this PR exists to close. | Stub `record` to raise `RuntimeError`, call `cancel_order(FakeDb("open"), "o1", actor="alice")`, and assert one of two things, depending on the chosen design: the status is not set (record first, or the two are made atomic), or the failure is caught and reported somewhere durable. This fails today: `db.set == "cancelled"`, the exception propagates and nothing is recorded. |
| 2 | P2 | `orders.py:8-13` (no check for `status == "cancelled"`) | Alice cancels order o1, then Bo cancels o1 again (double-click, retry, or a second support agent). The second call passes both guards, sets `cancelled` again and writes a second `order.cancelled` record with `actor="bo"`. The audit trail now names two people, and the latest names someone who did not cancel the order. This answers "who cancelled it" wrongly. Re-cancelling was harmless before this PR; it now corrupts the audit trail. | Use `FakeDb("cancelled")` and call `cancel_order(..., actor="bo")`. Assert that no audit record is written, and either that the call is a no-op or that it raises. This fails today because `calls` has one entry with `actor="bo"`. |
| 3 | P3 | `tests/test_orders.py:6` | `sys.modules["company_audit"]` is replaced at import time and never restored. If another test module imports the real `company_audit` or `orders` first, `orders.record` is already bound to the real function. These tests would then call the real library or fail, depending on test order. If this module runs first, the stub leaks into every later test in the run. | Run the suite in two orders (`pytest -p no:randomly` and `pytest -p randomly`), or import `orders` in another test module before this one. A per-test `unittest.mock.patch("orders.record")` fixes both directions. |

**Checked against the request:** The change does what was asked: an audit record with the actor, through the shared library. Nothing extra was added. `actor` is a required positional argument, so any caller not updated will fail with `TypeError`. PR.md says `handlers.cancel` is the only caller. I saw only two source files, so I could not confirm that. A repo-wide search for `cancel_order(` would.

**Claims I could not verify:**
- **"Tests pass."** I could not run them. Even if they pass, they replace the library with a stub that accepts any keyword arguments. They do not show that `record("order.cancelled", order_id=..., actor=...)` matches the real `company_audit.record` signature or accepts this event name. If the signature differs, every cancellation would set the status and then raise, which is the same failure as finding 1.
- **The shape of `request["user"]`.** It might be an id, a user object, or absent when the request is unauthenticated. Nothing shows that `company_audit` can serialise it.

**FILES NEEDED BUT NOT PROVIDED:**
- The `company_audit` module, for the signature of `record` and whether it is synchronous, raises, or retries.
- The login middleware that sets `request["user"]`.
- A repo-wide search for other `cancel_order` callers.
- CI check results for `8a41c7e`.
- The commit trailers.

**Close-out**

The author adjudicates the findings, and whoever closes the PR writes this section. I don't adjudicate my own findings.

**ADJUDICATION:** pending for #1, #2 and #3.

**VERIFIED AFTER FIXES:** not applicable yet.

**MERGE RECOMMENDATION:** Not yet. As reviewer, my view is "merge after fixes" for #1 and #2. Either could be deferred as P2 with tracked issues, but #2 directly undermines the purpose of the PR. If the `company_audit` source shows that `record` can raise, #1 becomes P1 and cannot be deferred. Also still open:
- The CI checks have not been seen.
- The author is unknown.
- The owner has not confirmed whether the actor counts as personal data, which decides the tier.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "inferred: order of calls read in the diff; whether company_audit.record can raise is not seen, and if it can this is P1",
      "location": "orders.py:12-13",
      "scenario": "Status is set to cancelled before record() runs. If record raises, the order is cancelled with no audit record and the handler returns an error for a cancellation that succeeded.",
      "fix": "Write the audit record before the status change or atomically with it, or catch and durably report the audit failure; add a test with a raising record stub."
    },
    {
      "severity": "P2",
      "evidence_level": "read in code: no status == 'cancelled' guard in orders.py",
      "location": "orders.py:8-13",
      "scenario": "Cancelling an already-cancelled order passes both guards and writes a second order.cancelled record naming a different actor, so the audit trail misstates who cancelled it.",
      "fix": "Treat an already-cancelled order as a no-op (or an error) that writes no audit record; add a test with FakeDb('cancelled')."
    },
    {
      "severity": "P3",
      "evidence_level": "read in code: tests/test_orders.py:6 replaces sys.modules at import time and never restores it",
      "location": "tests/test_orders.py:6",
      "scenario": "The global sys.modules stub depends on test order: if orders or the real company_audit is imported first, the tests use the real library; if this module runs first, the stub leaks into later tests.",
      "fix": "Use unittest.mock.patch('orders.record') per test instead of replacing sys.modules."
    }
  ]
}
```