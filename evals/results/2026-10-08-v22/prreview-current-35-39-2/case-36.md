# pr-review: PR #131, audit record on cancellation

**Review report**

**REVIEWED:** PR #131, head `8a41c7e`, merge base `2d90b53`. Both SHAs come from PR.md. I had no tools, so I could not check out the head in a throwaway worktree, confirm the SHAs or confirm that `change.patch` matches `8a41c7e`. The review covers the patch and the base files as provided. If the head has moved past `8a41c7e`, those later commits were not reviewed.

**TIER:** Standard. The change is ordinary code on an audited path, and the context gives the stakes as standard. One caveat: the change writes `request["user"]` into the audit log. If that value is personal data (an email or a name rather than an opaque ID), the change handles personal data and the tier becomes **High**. That would need a second round, ideally from another vendor, and this review would then be incomplete. The owner should confirm what `request["user"]` holds.

**REVIEWERS:** One round, by Claude Opus 5.5 (`claude-opus-5-5`) in this session. This session did not write the change. The author is unknown: no commit trailers were provided, so I could not read `Co-Authored-By`. No code was sent anywhere else, because there are no tools and no subagent.

**Checked and holding:**
- `company_audit.record` does `write`, `flush` and `os.fsync` before it returns (`base/company_audit.py:13-16`), as PR.md says.
- The tests set `company_audit.AUDIT_PATH` on the module. `record` reads that global at call time, so the test redirect works even with `from company_audit import record`.
- A shipped order raises before `record`, so no audit line is written for it.
- A missing order raises `KeyError` before `record`, so no audit line is written for it.
- The scope matches the request, with nothing extra added.
- "Tests pass" is the author's claim. I could not run the tests.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 (suspected; depends on the login middleware, which was not provided) | `orders.py:12` (post-patch), fed by `handlers.py:7` | `request["user"]` is described only as "the signed-in user, set by the login middleware". The tests pass a string (`"bo"`). If the middleware sets a `User` object, a dict containing non-JSON types, or anything else `json.dumps` cannot serialize, `record` raises `TypeError` in production on **every** cancellation. That happens after `db.set_status(..., "cancelled")` has run, so the order is cancelled, the client gets a 500, and no audit record exists. The tests cannot catch this because they use a plain string. | Call `handlers.cancel` with a `user` value of the type the real middleware sets (for example the `User` class). Assert it returns 204 and the audit line holds a stable identifier. The fix should pass an explicit ID (for example `request["user"].id`) rather than the raw object. |
| 2 | P2 | `orders.py:11-12` (post-patch) | The status change happens before the audit write, and the two are not atomic. Suppose `record` fails because `AUDIT_PATH` cannot be written, the disk is full (`ENOSPC` on write or fsync), or there is an `EIO`. The order then stays cancelled with no audit record, and the handler returns an error, so the user thinks the cancellation failed. That defeats the request ("when an order is cancelled, write an audit record") on exactly the path finance relies on. Whether `set_status` commits right away depends on the db layer, which was not provided. | Set `company_audit.AUDIT_PATH` to a path inside a directory that does not exist, then call `cancel_order(FakeDb("open"), "o1", actor="alice")`. Assert that either the status was not changed (`db.set is None`) or an audit record exists. Today the status is `"cancelled"` with no record. |
| 3 | P2 | `orders.py:9-12` (post-patch) | Cancelling an order that is already cancelled is not refused, because only `"shipped"` is checked. Alice cancels `o1`, then Bob sends POST `/orders/o1/cancel`. That writes a second `order.cancelled` record with `actor="bob"`, so support and finance see two cancellations and cannot tell who actually cancelled. Before this PR the repeat was harmless; with the audit record it is misleading. | `FakeDb("cancelled")`: call `cancel_order(..., actor="bob")`. Assert no audit line is written, or that the call is rejected or treated as a no-op. Today a line with `actor="bob"` is written. |

**FILES NEEDED BUT NOT PROVIDED:**
- The login middleware: what type `request["user"]` is, and whether it can be absent or `None`. This confirms or refutes finding 1 and settles the tier question.
- The db layer (`get_order`, `set_status`): whether there are transactions or commit semantics. This is relevant to finding 2.
- A repository-wide search for callers of `cancel_order`. PR.md says `handlers.cancel` is the "only caller". Any other caller (an admin script or batch job) would now fail with `TypeError` because `actor` is required.
- The test runner and CI configuration, to confirm that `tests/test_orders.py` is collected and can import `orders`, `handlers` and `company_audit`. A CI run on `8a41c7e`.

---

**Close-out** (for the author or whoever closes the PR; a reviewer does not adjudicate its own findings)

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | Pending | Accept with a fix and a regression test, or reject with the middleware code showing `request["user"]` is always a JSON-safe identifier. As a P1 it cannot be deferred. |
| 2 | Pending | Accept with a fix and a test, or defer with a linked issue. |
| 3 | Pending | Accept with a fix and a test, or defer with a linked issue. |

**VERIFIED AFTER FIXES:** None yet. Verify fixes by reading the correction diff and rerunning `tests/test_orders.py` plus the new tests, not with another full review.

**MERGE RECOMMENDATION:** **Do not merge yet.** Finding 1 (P1) needs a decision backed by the middleware code. All findings need written decisions. CI on the head has not been seen; a missing check is not green. The owner also needs to confirm the tier: if `request["user"]` is personal data, a second round is required. Once finding 1 is resolved, findings 2 and 3 are decided, and checks are green: merge after fixes.

```json
{
  "verdict": "do not merge yet: P1 finding 1 needs a decision (fix, or middleware evidence that request['user'] is JSON-serializable); P2 findings 2-3 need decisions; CI not seen; tier depends on whether actor is personal data",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "suspected: type of request['user'] is set by login middleware not provided; tests only use a string",
      "location": "orders.py:12 (post-patch), via handlers.py:7",
      "scenario": "If the middleware sets a non-JSON-serializable user object, json.dumps in company_audit.record raises TypeError after db.set_status has cancelled the order: every cancellation returns 500, the order stays cancelled, and no audit record is written.",
      "fix": "Pass an explicit stable identifier (e.g. request['user'].id) as actor; add a handler test using the real user type."
    },
    {
      "severity": "P2",
      "evidence_level": "confirmed from code (ordering); commit semantics of db not provided",
      "location": "orders.py:11-12 (post-patch)",
      "scenario": "Status is set before the audit write and the two are not atomic. If record fails (unwritable AUDIT_PATH, ENOSPC, EIO), the order stays cancelled with no audit record and the caller gets an error.",
      "fix": "Make the status change and the audit write atomic, or order them so that a failed audit means no cancellation (same transaction or outbox); add a test with an unwritable AUDIT_PATH."
    },
    {
      "severity": "P2",
      "evidence_level": "confirmed from code",
      "location": "orders.py:9-12 (post-patch)",
      "scenario": "An already-cancelled order is not refused. A second cancel by another user writes a second order.cancelled record with that user as actor, misattributing the cancellation.",
      "fix": "Refuse or no-op when status is already 'cancelled' and write no audit record; add a test with FakeDb('cancelled')."
    }
  ]
}
```