# PR #131 Review: Audit Record on Cancellation

**Review report**

**REVIEWED:** PR #131, head `8a41c7e`, merge base `2d90b53`.
- Both SHAs come from PR.md. I could not check them against a repository because this session has no tools.
- I reviewed the provided `change.patch` against the provided `base/` files. I did not use a worktree checkout.
- If the head has moved past `8a41c7e`, the later commits are not reviewed.

**TIER:** Standard.
- This is an ordinary code change, and the context sets the stakes as standard.
- It writes a user id (the actor) into an audit file. That file is already the shared library's existing sink, so the change adds no new network exposure, permissions or secrets.
- It touches no auth, migration or money movement. Finance reads these records but no money moves.
- One round, this one, satisfies the tier.

**DATA:** Nothing left this session. No subagent or external endpoint was used.

**REVIEWERS:**
- Reviewer: this instance, Claude Opus 5.5 (`claude-opus-5-5`). It did not write or help write the change.
- Author: unknown. No commit trailers were provided.

**EXECUTION:** I did not run the tests because no tools are available. The claim "Tests pass" in PR.md is unverified. I checked each test's logic by reading it.

**Checks against the request:**
- "Write an audit record saying who cancelled it": done. `orders.py` records `actor`, and `handlers.py` passes `request["user"]`.
- "Using the shared audit library": done, via `company_audit.record`.
- Nothing extra was added.
- The claim that `record()` fsyncs before returning is confirmed in `base/company_audit.py:13-16`.
- Patching `company_audit.AUDIT_PATH` in tests works, because `record` reads the module global at call time.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `orders.py:16-17` (head) | The record is written before `db.set_status`. If `set_status` then raises (DB timeout, lost connection, constraint error), the audit file says `order.cancelled` by `actor`, but the order is still open. Support and finance see a cancellation that never happened. Nothing records the failure or compensates for it. The PR deliberately trades a missing record for a phantom one but does not document or handle the phantom case. | Use a `FakeDb` whose `set_status` raises `RuntimeError`. Call `cancel_order` and assert the error propagates. Then assert the audit log either has no `order.cancelled` line, or has a following `order.cancel_failed` (or similar) line for the same `order_id`. This fails today: there is one unqualified `order.cancelled` line. |
| 2 | P2 | `orders.py:14-17` (head) | The PR says "Cancelling an order that is already cancelled … records nothing". That only holds for sequential calls. Take two concurrent POSTs for the same open order (double-click, or a client retry). Both read `status == "open"`, both pass the check, and both call `record`. The audit trail shows two cancellations, possibly by two different actors, for one order. The read-then-write race already existed in base, but it was harmless there because `set_status` is idempotent. It now produces duplicate records. `tests/test_orders.py:52-54` only covers the sequential case. | Use a `FakeDb` whose `get_order` blocks on a barrier until two threads have both read `"open"`. Run `cancel_order` from both threads and assert the audit log has exactly one `order.cancelled` line for `o1`. This fails today with two lines. A fix needs an atomic conditional update, such as `UPDATE … WHERE status='open'` checking the rowcount, ordered with the record. |
| 3 | P3 | `tests/test_orders.py:23-25` | `setUp` reassigns the module global `company_audit.AUDIT_PATH`, and there is no `tearDown` to restore it or remove the temp dir. Any test module that runs later in the same process and relies on the default or env-configured `AUDIT_PATH` writes into a stale temp path, or into `.../missing/audit.log` left behind by `test_a_failed_audit_write_leaves_the_order_open`, and fails with `OSError`. That failure depends on test order. | Add a second test module that runs after this one and asserts `company_audit.AUDIT_PATH == os.environ.get("AUDIT_PATH", "audit.log")`. It fails today. The fix is `addCleanup` or `mock.patch.object(company_audit, "AUDIT_PATH", ...)`. |
| 4 | P3 | `tests/test_orders.py:27-32`, `38-41` | The test `test_cancel_is_on_disk_before_it_returns` overclaims: it reads the file back but cannot detect a missing fsync. Neither it nor the handler test asserts `db.set == "cancelled"`. A regression that records the event but drops `set_status`, for example an early `return True` after `record`, would pass every test. | Add `self.assertEqual(db.set, "cancelled")` to both tests. Rename the first test, or assert `os.fsync` is called via `mock.patch("os.fsync")`. |

**FILES NEEDED BUT NOT PROVIDED:**
- **Full repository at `8a41c7e`.** I need it to confirm that `handlers.cancel` is the only caller of `cancel_order`, as PR.md claims. Any other caller now raises `TypeError` because `actor` is a required argument.
- **The DB layer behind `db.get_order` / `db.set_status`.** I need it to see whether a transaction or row lock already prevents finding 2.
- **The login middleware.** I need it to confirm that `request["user"]` is always present on this route. If it is missing, the handler now raises `KeyError` (a 500) where it previously cancelled.
- **CI check results for `8a41c7e`.** None were provided.

---

**Close-out**

Not written. The author has not yet adjudicated findings 1–4, and as the reviewer I do not adjudicate my own findings.

**ADJUDICATION:** pending, findings 1–4.

**VERIFIED AFTER FIXES:** none yet.

**MERGE RECOMMENDATION:** Merge after fixes, not yet.
- There are no P0 or P1 findings.
- Findings 1–4 need written decisions. They are P2/P3, so they may be deferred with a tracking issue.
- CI results for `8a41c7e` are not available. A missing check is not green.
- The sole-caller claim is unverified.
- The author or owner needs to decide whether the phantom-record trade-off in finding 1 is acceptable for the finance audit.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "code-read (patch lines), not executed",
      "location": "orders.py:16-17",
      "scenario": "record() runs before db.set_status(); if set_status raises, the audit log contains order.cancelled by actor while the order remains open, with no failure or compensating record.",
      "fix": "Write a compensating/failure record when set_status raises (or record after a transactional status update with an outbox), and test with a FakeDb whose set_status raises."
    },
    {
      "severity": "P2",
      "evidence_level": "code-read (check-then-act race), not executed; DB layer not provided",
      "location": "orders.py:14-17",
      "scenario": "Two concurrent cancels of the same open order both read status 'open' and both call record(), producing two order.cancelled records (possibly with different actors) for one cancellation.",
      "fix": "Make the open->cancelled transition atomic (conditional update / row lock) and record only when this call won the transition; add a barrier-based two-thread test asserting one record."
    },
    {
      "severity": "P3",
      "evidence_level": "code-read",
      "location": "tests/test_orders.py:23-25",
      "scenario": "setUp mutates company_audit.AUDIT_PATH without restoring it, so later tests in the same process write to a stale temp or nonexistent path and fail order-dependently.",
      "fix": "Use mock.patch.object or addCleanup to restore AUDIT_PATH and remove the temp dir."
    },
    {
      "severity": "P3",
      "evidence_level": "code-read",
      "location": "tests/test_orders.py:27-32,38-41",
      "scenario": "Tests never assert db.set == 'cancelled' and cannot detect a missing fsync, so a regression that records but skips set_status passes.",
      "fix": "Assert db.set == 'cancelled' in the success and handler tests; assert os.fsync is called via mock or rename the test."
    }
  ]
}
```