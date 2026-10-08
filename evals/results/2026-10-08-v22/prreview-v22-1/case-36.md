# Review report: PR #131 (audit record on cancellation)

**REVIEWED:** PR #131, head `8a41c7e`, merge base `2d90b53` (both SHAs come from PR.md).

- I had no tools in this session, so I could not check out `8a41c7e` in a worktree.
- I reviewed `work/change.patch` against `work/base/`. I could not confirm that the patch matches what is at `8a41c7e`.
- If the head has moved since `8a41c7e`, any later commits were not reviewed.

**TIER:** Standard.

- This is an ordinary code change.
- It does not touch auth, permissions, secrets, network exposure, migrations or money movement.
- The audit trail matters to support and finance, so audit completeness is the main risk I looked at.
- **Re-tier condition:** if `request["user"]` is a full user record (email, name and so on) rather than an ID, then personal data is being written to a plain file, and the PR becomes High tier (see F2).

**REVIEWERS:**

- **Reviewer:** this instance (claude-opus-5-5, fresh session, no part in writing the change). This is one Standard round, and no code was sent to any other endpoint.
- **Author:** unknown. No commit trailers were provided, so record the author from the `8a41c7e` trailers at close-out.

**Claims checked:**

- *"`record` writes and fsyncs before it returns"*: confirmed in `company_audit.py:13-16`.
- *"The only caller is `handlers.cancel`"*: not verifiable. Only `handlers.py` was provided, and no repo-wide search was available.
- *"Tests pass"*: not seen run. On reading, the three tests look like they would pass.

**Scope against the request:** the change does what was asked. It records who cancelled the order, using the shared library, and adds nothing extra.

## FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| F1 | P1 | `orders.py:12-13` (`db.set_status` then `record`) | The status is committed before the audit write, so any failure in `record` leaves a cancelled order with no audit record. The handler then raises, and the client gets a 500 for an order that was in fact cancelled. Possible causes: `open` fails on permissions or a missing directory, `write`/`fsync` fails with `OSError` (disk full, EIO), or `json.dumps` raises `TypeError` on a non-serializable `actor` (see F2). Support and finance then see a cancellation with no "who". Nothing catches, retries or compensates. | Point `company_audit.AUDIT_PATH` at an unwritable path, such as a directory that does not exist. Call `cancel_order(FakeDb("open"), "o1", actor="alice")`. Assert that either the call raises **and** `db.set` is still `None`, or the cancel and the record both happen. This fails today because `db.set == "cancelled"` and no record exists. |
| F2 | P1 (conditional on the type of `request["user"]`) | `handlers.py:7`, flowing into `company_audit.py:11` | The handler passes `request["user"]` exactly as the login middleware sets it. That value is described as "the signed-in user", not a user ID. If it is an object or model instance, `json.dumps` raises `TypeError` after the status change, and every real cancellation hits F1. If it is a dict, the whole user record, possibly including personal data, is written to the audit file. The tests only pass the string `"bo"`, so neither case is exercised. | A handler test that passes a request whose `user` has the shape the real middleware produces, for example `{"id": "u1", "email": "bo@x"}` or the real user class. Assert that the call succeeds and that the record's `actor` is the stable user ID only. |
| F3 | P2 | `orders.py:8-13` | `cancel_order` refuses `shipped` but not orders that are already `cancelled`. Suppose alice cancels `o1` and bob then POSTs cancel on `o1`. A second `order.cancelled` record is written with `actor="bob"`, and the trail now names two cancellers for one event. The re-cancel was harmless before this PR. Now it corrupts the audit record. | `FakeDb("cancelled")`, call `cancel_order(db, "o1", actor="bob")`. Assert that it either raises or writes no audit line. This fails today because one line is written. |
| F4 | P3 | `tests/test_orders.py:27-32` | The test `test_cancel_is_on_disk_before_it_returns` only reads the file back in the same process. That passes with `flush()` alone, or with no flush at all once the `with` block closes the file. It does not test what its name claims. The fsync guarantee rests on reading `company_audit.py`, not on this test. Also, `setUp` reassigns a module global and never restores it or removes the temp directory, so later tests in the same process inherit the path. | Rename the test to match what it checks, or mock `os.fsync` and assert it was called. Restore `AUDIT_PATH` in `tearDown`, or use `addCleanup`. |

## FILES NEEDED BUT NOT PROVIDED

- **A repo-wide list of callers of `orders.cancel_order`.** The new required positional `actor` raises `TypeError` in any caller other than `handlers.cancel`. Examples would be jobs, admin tools or other handlers.
- **The login middleware**, to see the type and contents of `request["user"]`. F2 and the tier decision depend on it.
- **The `db` implementation**, to see whether `set_status` commits immediately or runs inside a transaction that could be rolled back. This changes how F1 should be fixed.
- **CI check status for `8a41c7e`.**

## Close-out

A reviewer does not adjudicate its own findings. The author must write the decisions.

**ADJUDICATION:** pending.

| # | Decision | Evidence or fix commit |
|---|---|---|
| F1 | pending (P1, cannot be deferred) | |
| F2 | pending (P1, cannot be deferred) | |
| F3 | pending | |
| F4 | pending | |

**VERIFIED AFTER FIXES:** none yet. Verify each fix with a targeted read of its diff and its regression test, not with another full round.

**MERGE RECOMMENDATION: merge after fixes. Do not merge at `8a41c7e`.**

- F1 and F2 are P1 findings with no decision yet.
- The "only caller" claim has not been verified.
- The type of `request["user"]` is unknown, and the tier decision depends on it.
- No CI checks have been seen, and a missing check is not green.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "confirmed by reading the code (orders.py:12-13, company_audit.py:13-16); not run",
      "location": "orders.py:12-13",
      "scenario": "db.set_status commits 'cancelled' before company_audit.record runs. If record raises (OSError on open/write/fsync, or TypeError from json.dumps), the order stays cancelled with no audit record and the handler returns an error for a cancellation that happened.",
      "fix": "Make the status change and the audit write succeed or fail together: write inside the same transaction, record an intent before the change and confirm it after, or catch the failure and roll the status back. Add a test with an unwritable AUDIT_PATH asserting that no cancellation happens without its record."
    },
    {
      "severity": "P1",
      "evidence_level": "inferred; depends on the middleware's user type, which was not provided",
      "location": "handlers.py:7",
      "scenario": "request['user'] is 'the signed-in user', not necessarily an ID. A user object makes json.dumps raise TypeError after the status change, so every real cancel hits F1. A user dict writes the whole user record, possibly personal data, to the audit file. Tests only pass the string 'bo'.",
      "fix": "Pass a stable user identifier (e.g. request['user']['id']) as actor, and add a handler test using the real middleware user shape."
    },
    {
      "severity": "P2",
      "evidence_level": "confirmed by reading the code (orders.py:8-13)",
      "location": "orders.py:8-13",
      "scenario": "An already-cancelled order can be cancelled again. Each repeat writes another order.cancelled record with the new actor, so the audit trail names more than one canceller for the same order.",
      "fix": "Refuse or no-op when status is already 'cancelled' without writing a record, and add a test with FakeDb('cancelled')."
    },
    {
      "severity": "P3",
      "evidence_level": "confirmed by reading the test",
      "location": "tests/test_orders.py:27-32",
      "scenario": "test_cancel_is_on_disk_before_it_returns would pass without fsync or flush, so it does not test what its name claims. setUp also mutates the module global AUDIT_PATH without restoring it.",
      "fix": "Mock os.fsync and assert it was called, or rename the test. Restore AUDIT_PATH and remove the temp directory via addCleanup."
    }
  ]
}
```