**Review report**

**REVIEWED:** PR #131 "audit record on cancellation". Head `8a41c7e`, merge base `2d90b53`, both as stated in PR.md. I had no tools, so I could not check out a worktree or confirm the SHAs. This review covers the provided `change.patch` and `base/` files only, read as the content of `8a41c7e`.

**TIER:** Standard. The change adds an audit write to an ordinary order operation. It touches no auth, permissions, secrets, network exposure, migrations or money movement, and the context sets the stakes as standard. One caveat: the change starts writing user ids into an audit file. If the owner treats user ids as personal data, this becomes High, needs a second round, and Step 3 endpoint approval applies.

**REVIEWERS:** Reviewed by this session (Claude, `claude-opus-5-5`, single round, no tools, nothing executed). This session did not write the change. Author: unknown. No commit trailers were provided, so authorship could not be read.

**Claims checked:**
- *"`record` writes and fsyncs before it returns"*: confirmed in `base/company_audit.py:13-16`.
- *"Audit record is written first, so a failed write leaves the order open"*: confirmed at `orders.py:16-17` (post-patch) and by `test_a_failed_audit_write_leaves_the_order_open`.
- *"Only caller is `handlers.cancel`"*: true for the files provided. I could not search the whole repo.
- *"Tests pass"*: not verified. I could not run them.
- The test's `company_audit.AUDIT_PATH` override does take effect, because `record` reads the module global at call time.
- The change matches the request (who cancelled, via the shared library) and adds nothing extra.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `orders.py:16-17` (post-patch) | The audit line is fsynced before `db.set_status`. If `set_status` then raises (DB error, timeout, constraint) or the process dies between the two calls, the audit trail says "order.cancelled by bo" while the order stays open and can still ship. Support and finance see a cancellation that never happened. A retry writes a second record. The docstring guarantees "never cancelled without a record" but not the converse, and the PR does not mention this case. | Use a `FakeDb` whose `set_status` raises `RuntimeError`. Assert the error propagates and that the audit log contains no unqualified `order.cancelled` line, or that it contains a compensating `order.cancel_failed` line, whichever the author adopts. This fails today: the log holds one `order.cancelled` line. |
| 2 | P2 | `orders.py:14-17` (post-patch), `handlers.py:7` | The check and the write are not atomic. Two concurrent POSTs for one open order (a double-click, or two support agents) both read `status == "open"`, and both write `order.cancelled`, possibly with two different actors. This breaks the PR's claim that cancelling an already-cancelled order "records nothing". The pre-patch race was harmless (an idempotent `set_status`). Now it produces duplicate or contradictory audit records. The real DB's locking and transaction semantics were not provided. | Use a `FakeDb` whose `get_order` blocks on a barrier until two threads have both read. Run two `cancel_order` calls concurrently and assert exactly one `order.cancelled` line and exactly one `True` return. This fails today unless the DB layer serializes the calls. |
| 3 | P3 | `tests/test_orders.py:23-25, 28-32, 52-54` | (a) `setUp` overwrites the global `company_audit.AUDIT_PATH` and never restores it, and the temp dir is never removed. Later tests in the same process write audit lines to a stale temp path. (b) `test_cancel_is_on_disk_before_it_returns` never asserts `db.set == "cancelled"`, so a regression that drops `set_status` still passes. It also cannot detect a missing fsync, despite its name. (c) `test_cancelling_twice_records_once` never cancels twice: it starts from an already-cancelled row. | Add `self.assertEqual(db.set, "cancelled")` to the first test, and confirm it fails when the `set_status` line is deleted. Add a true double-cancel test that cancels an open order, flips the fake's status, cancels again, and asserts one log line. Restore `AUDIT_PATH` and remove the dir in `tearDown`/`addCleanup`. |

**FILES NEEDED BUT NOT PROVIDED:**
- The real DB layer behind `db.get_order` / `db.set_status`: transactions and locking, which decide finding 2.
- The login middleware: is `request["user"]` always set on this route? If not, the handler now raises `KeyError` where it previously succeeded.
- A repo-wide search for other `cancel_order` callers (the new required `actor` breaks them).
- The CI config and its results.
- The commit trailers for authorship.

---

**Close-out**

Not written by me. A reviewer does not adjudicate its own findings. The author decides findings 1–3. All are P2/P3, so each may be fixed with a regression test, deferred with a linked issue, or rejected with evidence.

**ADJUDICATION:** pending author.

**VERIFIED AFTER FIXES:** none yet. Fixes should be verified by reading the correction diff and running the named tests, not by another full round.

**MERGE RECOMMENDATION:** merge after fixes. There is no P0 or P1 blocker. Before merge:
- every finding needs a written decision;
- the "Tests pass" claim needs green CI at `8a41c7e`, which I could not see;
- the authorship needs recording;
- the owner needs to confirm the tier, specifically whether user ids in the audit file count as personal data. If they do, a second round is required before merge.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "read in code (orders.py post-patch: record() fsynced before db.set_status); not executed",
      "location": "orders.py:16-17",
      "scenario": "db.set_status raises or the process dies after record() has fsynced 'order.cancelled'; the audit trail shows a cancellation by the actor while the order stays open and can ship; a retry writes a duplicate record",
      "fix": "Write the record inside the same DB transaction as the status change, or write a compensating 'order.cancel_failed' record when set_status fails; add a test with a FakeDb whose set_status raises"
    },
    {
      "severity": "P2",
      "evidence_level": "inferred from code; real DB locking semantics not provided",
      "location": "orders.py:14-17",
      "scenario": "Two concurrent cancels of one open order both read status 'open' and both write order.cancelled (possibly with different actors), contradicting the PR's claim that a re-cancel records nothing",
      "fix": "Make check-and-set atomic (conditional update e.g. set_status where status='open' returning rowcount, or row lock) and write the record only for the winner; add a barrier-based concurrency test"
    },
    {
      "severity": "P3",
      "evidence_level": "read in code (tests/test_orders.py)",
      "location": "tests/test_orders.py:23-25, 28-32, 52-54",
      "scenario": "AUDIT_PATH global is mutated and never restored; the success test does not assert db.set == 'cancelled', so dropping set_status still passes; 'cancelling twice' test never cancels twice",
      "fix": "Restore AUDIT_PATH and clean the temp dir via addCleanup; assert db.set == 'cancelled'; add a true cancel-then-recancel test asserting one audit line"
    }
  ]
}
```