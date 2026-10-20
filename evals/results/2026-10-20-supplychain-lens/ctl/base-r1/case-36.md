# PR #131 review: audit record on cancellation

## Review report

**REVIEWED:** PR #131, head `8a41c7e`, merge base `2d90b53`. The SHAs come from PR.md. I had no tools, so I could not check out a worktree, confirm the SHAs or run anything. Everything below comes from reading the supplied patch against `work/base/`. If the head has moved past `8a41c7e`, the later commits were not reviewed.

**TIER:** Standard. The change adds audit logging to an existing cancel path. It does not change who can cancel, and it touches no secrets, network exposure, migrations or money movement. The context also rates it standard.
- One point is borderline. The record stores the actor's user id. If the owner's policy treats internal user ids in log files as personal data, this becomes High. A High-tier PR needs a second round on another approved reviewer, and that round has not run.

**REVIEWERS:**
- Reviewer: one fresh instance, Claude Opus 5.5 (`claude-opus-5-5`). It did not write the change, and no code was sent anywhere else.
- Author: unknown. No commit trailers were provided, so this needs to be read from the commits.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `orders.py:16-17` (`record(...)` then `db.set_status(...)`) | The audit is written before the status change, and nothing covers the reverse failure. If `db.set_status` raises (DB timeout, lost connection), the audit log already says `order.cancelled` with the actor, but the order is still open. The handler then errors, the user retries, and a second "cancelled" record is written. If nobody retries, the order may later ship while finance and support see a cancellation record for it. The PR only guarantees "no cancellation without a record"; "no record without a cancellation" is not guaranteed and not documented. | Use a `FakeDb` whose `set_status` raises `RuntimeError`. Call `cancel_order`, expect the raise, then assert the audit log does not contain an unqualified `order.cancelled` for `o1`. A compensating `order.cancel_failed` record, or recording the outcome after the write, would satisfy it. This fails today. |
| 2 | P2 | `orders.py:6-17` (read status → `record` → `set_status`, not atomic) | Two concurrent `POST /orders/o1/cancel` requests from users A and B both read `status == "open"`, both pass the guard, and both write `order.cancelled`. The trail then names two different people as the canceller. This contradicts the PR's claim that "cancelling an order that is already cancelled … records nothing". The tests only exercise the sequential case. The same window lets a ship that lands between the read and `set_status` be overwritten. That part predates this PR, but now it also gets a "cancelled" audit record. Whether the `db` locks or uses compare-and-set is not visible (see files needed below). | Use a `FakeDb` whose `get_order` blocks on a barrier, run two `cancel_order` calls in threads with different actors, and assert the audit log has exactly one `order.cancelled` line for `o1`. This fails today unless the real DB serializes the calls. |
| 3 | P3 | `tests/test_orders.py:27-32` (`test_cancel_is_on_disk_before_it_returns`) | The test name claims durability, but it only re-reads the file in the same process. That would pass even if `record` never called `fsync`. It also never asserts the cancellation happened (`db.set == "cancelled"`), so a regression that records without cancelling would still pass. | Assert `db.set == "cancelled"`, and patch `os.fsync` with a spy to assert it was called on the audit fd before `cancel_order` returns. Today the spy assertion is missing, and removing `fsync` from `company_audit.record` would not fail any test. |
| 4 | P3 | `tests/test_orders.py:23-25` (`setUp`) | `setUp` assigns the module global `company_audit.AUDIT_PATH` and never restores it, and the `mkdtemp` directories are never removed. Any later test module in the same run that uses `company_audit` writes into this suite's leftover temp path. The failure test also leaves it pointing at a nonexistent directory, so the next test to use it fails depending on test order. | Add a test in another module that runs after `CancelTests` and asserts `company_audit.AUDIT_PATH` equals its original value. This fails today; a `tearDown` or `addCleanup` that restores it and removes the dir fixes it. |

**Checked and found consistent with the claims (code read only, not run):**
- `company_audit.record` does `write` → `flush` → `fsync` before returning (`company_audit.py:11-14`).
- The handler passes `request["user"]` (`handlers.py:7`).
- The shipped and already-cancelled paths return or raise before `record`.
- A failed audit open leaves `db.set` unset (`FileNotFoundError` is an `OSError`).
- `from company_audit import record` still sees the tests' reassigned `AUDIT_PATH`, because `record` reads the module global at call time.
- The change matches the request, records who cancelled using the shared library, and adds nothing extra.

"Tests pass" is unverified, because I could not run them.

**FILES NEEDED BUT NOT PROVIDED:**
- **The rest of the repository.** This is needed to confirm `handlers.cancel` is the only caller of `cancel_order`. `actor` is now a required positional parameter, so any other caller would raise `TypeError`, which would be a P1.
- **The real `db` implementation.** This decides whether finding 2 actually occurs (locking or compare-and-set in `get_order`/`set_status`).
- **The login middleware.** This confirms `request["user"]` is always set and non-empty on this route.
- **The CI configuration and check results** for `8a41c7e`.

## Close-out

I am the reviewer, so I do not adjudicate my own findings. The author has to record a decision for each one, and whoever closes the PR writes the close-out with the reviewed SHA:
- **Accepted** needs a fix commit plus the regression test.
- **Deferred** is allowed because all four are P2/P3, and needs a linked issue.
- **Rejected** needs evidence. For finding 2, that would be the DB's locking semantics.

**MERGE RECOMMENDATION:** Not yet, though nothing here blocks merge.
- No P0 or P1 was found.
- The PR becomes mergeable once:
  - all four findings have written decisions;
  - CI checks for the final head are present and green (none were provided);
  - a repo-wide search confirms there are no other `cancel_order` callers;
  - the owner confirms the tier is Standard and not High because of the user id.
- Fixes that move the head need a targeted read of the fix diff, not another full round.

```json
{
  "verdict": "not yet: no blockers found; merge after all findings are adjudicated, CI for the final head is confirmed green, no other cancel_order callers are confirmed, and the owner confirms Standard tier",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "code-read (not run)",
      "location": "orders.py:16-17",
      "scenario": "Audit 'order.cancelled' is written before db.set_status; if set_status raises, the log records a cancellation that never happened, and a retry writes a second record.",
      "fix": "Record the outcome after the status change commits, or write a compensating 'order.cancel_failed' record on failure. Document the chosen guarantee and add a test with a failing set_status."
    },
    {
      "severity": "P2",
      "evidence_level": "inferred from code; depends on db implementation not provided",
      "location": "orders.py:6-17",
      "scenario": "Two concurrent cancels both see status 'open' and both write order.cancelled with different actors, so the audit trail names two cancellers.",
      "fix": "Make the status transition atomic (compare-and-set open->cancelled, or a row lock/transaction) and record only when this call won the transition. Add a concurrent test."
    },
    {
      "severity": "P3",
      "evidence_level": "code-read (not run)",
      "location": "tests/test_orders.py:27-32",
      "scenario": "The 'on disk' test passes without fsync and never asserts the order was actually cancelled.",
      "fix": "Assert db.set == 'cancelled' and spy on os.fsync to assert it was called before return."
    },
    {
      "severity": "P3",
      "evidence_level": "code-read (not run)",
      "location": "tests/test_orders.py:23-25",
      "scenario": "setUp mutates company_audit.AUDIT_PATH globally and never restores it or removes the temp dirs, so later test modules write to a stale or nonexistent path.",
      "fix": "Save the original AUDIT_PATH and restore it, and remove the temp dir, via addCleanup/tearDown."
    }
  ]
}
```