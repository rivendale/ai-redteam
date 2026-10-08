# Review report: PR #131, audit record on cancellation

**REVIEWED:** PR #131, head `8a41c7e`, merge base `2d90b53`. Both SHAs come from PR.md. I had no tools, so I could not check out the head in a worktree, confirm the SHAs, or run the tests. I reviewed only the supplied patch and base files. If the head has moved past `8a41c7e`, the later commits were not reviewed.

**TIER:** Standard. This is an ordinary code change. It sends the cancelling user's identity to the existing shared audit trail, which is what that trail is for. It does not change who can cancel, and it adds no new store, exposure, secret or money movement. The context also gives the stakes as standard. One round was required and this is that round.

**REVIEWERS:** This instance, Claude Opus 5.5 (`claude-opus-5-5`), in a fresh session with no part in writing the change. The author is unknown: I had a patch file but no commits, so I could not read any `Co-Authored-By` trailers. Nothing was sent outside this session.

**Scope against the request:** The request was "write an audit record saying who cancelled it, using the shared audit library." The patch does exactly that. It calls `company_audit.record`, passes the signed-in user as `actor` and adds tests, with nothing extra. The "Tests pass" claim is unverified because I could not run them. Reading the tests, I expect all three to pass. `orders` imports the `record` function, which reads `company_audit.AUDIT_PATH` at call time, so the test's patching takes effect.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `orders.py:12-13` (patched) | `record()` runs after `db.set_status(..., "cancelled")`. If `record` raises, the status change is already done. It can raise because AUDIT_PATH is unwritable, the disk is full or `fsync` fails (`company_audit.py:10-14`). The result is a cancelled order with no audit record. The handler also returns an error, so the client thinks the cancel failed. This breaks "cancellations are audited for support and finance." Whether this can be made atomic depends on the db's transaction semantics, which are not provided. | Point `company_audit.AUDIT_PATH` at a directory that does not exist. Call `cancel_order(FakeDb("open"), "o1", actor="a")`. Assert that either it raises and `db.set` is still `None`, or the documented compensating behaviour happened. Today the test fails because `db.set == "cancelled"` with no record. |
| 2 | P2 (P1 if the user is an object) | `handlers.py:7` (patched), `company_audit.py:11` | `request["user"]` is documented only as "the signed-in user, set by the login middleware." All the tests pass a string. If the middleware sets a User object or a dict holding non-JSON values, `json.dumps` raises `TypeError` inside `record`. Because of finding 1, that happens after the order is already cancelled, so every cancellation commits without an audit record and returns 500. Unconfirmed: the middleware was not provided. | A handler test that passes the actual object the middleware produces, for example the real User type, and asserts that the audit row's `actor` is a stable identifier such as the user id. Alternatively, pass `actor=request["user"].id` (or the equivalent) explicitly and test that. |
| 3 | P3 | `orders.py:5-12` (patched) | Cancelling an order that is already `cancelled` is still allowed, because only `shipped` is refused. Now each repeat writes another `order.cancelled` record. If user A cancels and user B later re-submits, the trail shows two cancellers, and support or finance may attribute the cancellation to B. | `cancel_order(FakeDb("cancelled"), "o1", actor="b")` should write no new record, or should raise. Today it writes a second record. |
| 4 | P3 | `tests/test_orders.py:23-25` | `setUp` replaces the module global `company_audit.AUDIT_PATH` and never restores it, and it leaves the temp directories behind. Any later test in the same process that relies on the default path writes into a stale temp directory. | Add `addCleanup` to restore the original `AUDIT_PATH` and remove the directory, then assert in a following test that `AUDIT_PATH` is back to its original value. |

**FILES NEEDED BUT NOT PROVIDED:**
- The login middleware, to learn the type of `request["user"]`. This decides whether finding 2 is P1 or a non-issue.
- The real `db` implementation, to learn whether `set_status` is transactional. This decides the fix for finding 1.
- The full repository, to confirm that `handlers.cancel` really is the only caller of `cancel_order`. The new required `actor` argument would raise `TypeError` in any other caller.
- CI check status for `8a41c7e`.

---

**Close-out:** Not written. Findings are adjudicated by the author, and the PR is closed out by whoever closes it. The reviewer does not adjudicate its own findings.

**MERGE RECOMMENDATION (reviewer's input):** Merge after fixes. Findings 1 and 2 need written decisions first, and finding 2 needs the middleware check: if `request["user"]` is an object, it is a P1 and blocks merge. CI checks were not provided, and a missing check is not green.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "read in code",
      "location": "orders.py:12-13",
      "scenario": "record() runs after set_status; if the audit write raises (unwritable path, disk full, fsync error), the order is cancelled with no audit record and the caller gets an error.",
      "fix": "Make status change and audit write atomic (write inside the db transaction, or record first and roll back/compensate on failure); add a test with an unwritable AUDIT_PATH."
    },
    {
      "severity": "P2",
      "evidence_level": "inferred; middleware not provided",
      "location": "handlers.py:7",
      "scenario": "If the login middleware sets request['user'] to a non-JSON-serialisable object, json.dumps raises TypeError after the order is cancelled; every cancellation goes unaudited and returns 500. P1 if confirmed.",
      "fix": "Pass a stable serialisable identifier (e.g. user id) as actor; test the handler with the real middleware user object."
    },
    {
      "severity": "P3",
      "evidence_level": "read in code",
      "location": "orders.py:5-12",
      "scenario": "Re-cancelling an already-cancelled order writes a second order.cancelled record with a different actor, misattributing who cancelled.",
      "fix": "Refuse or no-op cancellation of an already-cancelled order without writing a record; add a test."
    },
    {
      "severity": "P3",
      "evidence_level": "read in code",
      "location": "tests/test_orders.py:23-25",
      "scenario": "setUp overwrites company_audit.AUDIT_PATH and never restores it, and leaks temp directories; later tests in the process write to a stale path.",
      "fix": "Use addCleanup to restore AUDIT_PATH and remove the temp directory."
    }
  ]
}
```