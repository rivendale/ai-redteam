# Review of PR #131: audit record on cancellation

**Review report**

**REVIEWED:** PR #131, head `8a41c7e`, merge base `2d90b53`. Both SHAs come from PR.md. I could not check them, because this session has no tools and no checkout. I reviewed the patch text and base files as provided, not a worktree at that head.

**TIER:** Standard. This is an ordinary code change that adds an audit write. It does not touch auth, permissions, secrets, migrations, money movement or personal data. The audit record matters to support and finance, which is reflected in the severities below.

**REVIEWERS:**
- Reviewer: this instance (claude-opus-5-5), one round. This session did not write the change.
- Author: unknown. The commit trailers were not provided.
- Data handling (Step 3): only the supplied files were read, and nothing was sent elsewhere.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 (conditional) | `handlers.py:7`, `orders.py:12` | The docstring only says `request["user"]` is "the signed-in user, set by the login middleware". If the middleware sets a user object or dict with non-JSON values, `json.dumps` in `company_audit.record` raises `TypeError`. This happens after `db.set_status` has already run. Every HTTP cancellation would then cancel the order, write no audit record, and return a 500. The tests only pass a string (`"bo"`, `"alice"`), so they cannot catch this. The fix is to pass an explicit identifier such as `request["user"].id` (or whatever the middleware provides) and assert its type. | Build the request the way the real login middleware does and call `handlers.cancel`. Assert a 204 and that `audit.log` has one line whose `actor` is the user's id. This fails today if the user is an object. |
| 2 | P2 | `orders.py:11-12` | The status change and the audit write are not atomic. If `record` raises, the order stays cancelled with no audit line, and the caller sees an error for a cancellation that did happen. Triggers include an unwritable `AUDIT_PATH`, a full disk, an `fsync` failure, or finding 1. The request is that cancellations are audited, so silent gaps defeat it. Options: write the audit record inside the same transaction or outbox as the status change, or roll the status back on audit failure. Choose deliberately and document the choice. | Point `company_audit.AUDIT_PATH` at an unwritable path and call `cancel_order`. Assert that it either raises and leaves `db.set` as `None`, or that the failure is otherwise handled as designed. Today `db.set == "cancelled"` and there is no audit record. |
| 3 | P2 | `orders.py:9-12` | `cancel_order` does not reject an order that is already `"cancelled"`. A second cancel by a different user, for example bob, writes a second `order.cancelled` record with `actor="bob"`. The audit trail then has two "cancelled by" entries, and the later one is wrong about who cancelled the order. The re-cancel itself existed before this PR, but the misleading audit record is new. | Use `FakeDb("cancelled")`, call `cancel_order(db, "o1", actor="bob")`, and assert that it raises or writes no audit line. Today it writes one. |

**Notes, not findings:**
- "Tests pass" is unverified because I could not run them. The tests as written look correct. `record` reads `AUDIT_PATH` at call time, so the `setUp` patch takes effect.
- `test_cancel_is_on_disk_before_it_returns` does not actually test `fsync`. It only proves the line is readable in the same process. That is acceptable, but the test name claims more than it checks.
- The change otherwise matches the request: the actor is required, the shared library is used, and nothing extra is added.

**FILES NEEDED BUT NOT PROVIDED:**
- The login middleware, to learn the type of `request["user"]`. This decides whether finding 1 is real.
- The DB layer, to learn whether `set_status` commits immediately and whether transactions exist.
- A repository-wide search for other callers of `cancel_order`. The new `actor` argument is required, so any caller other than `handlers.cancel` would break. PR.md says there are none, but I could not check that.
- CI check results.
- Commit trailers.

**Close-out**

I am the reviewer, so I do not adjudicate my own findings. The author adjudicates them, and whoever closes the PR records the result.

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | Pending | |
| 2 | Pending | |
| 3 | Pending | |

**VERIFIED AFTER FIXES:** None yet.

**MERGE RECOMMENDATION:** Do not merge yet.
- Finding 1 is a possible P1. It must be confirmed against the middleware and then fixed or rejected with evidence. A P1 cannot be deferred.
- Findings 2 and 3 need a written decision each.
- CI checks were not shown. A missing check is not green.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "inferred (depends on the type of request[\"user\"]; middleware not provided)",
      "location": "handlers.py:7, orders.py:12",
      "scenario": "If the middleware sets request[\"user\"] to a non-JSON-serializable user object, json.dumps in company_audit.record raises TypeError after db.set_status has run: the order is cancelled, no audit record is written, and the handler returns 500. The tests only pass strings.",
      "fix": "Pass an explicit serializable identifier (e.g. the user id) as actor, and add a handler test that uses the real middleware's user shape."
    },
    {
      "severity": "P2",
      "evidence_level": "code read",
      "location": "orders.py:11-12",
      "scenario": "The status change and the audit write are not atomic; any failure in record (unwritable AUDIT_PATH, full disk, fsync error) leaves the order cancelled with no audit record and returns an error to the caller.",
      "fix": "Write the audit inside the same transaction/outbox as the status change, or roll back the status on audit failure; test with an unwritable AUDIT_PATH."
    },
    {
      "severity": "P2",
      "evidence_level": "code read",
      "location": "orders.py:9-12",
      "scenario": "Cancelling an already-cancelled order succeeds and writes another order.cancelled record with a different actor, so the audit trail misattributes who cancelled the order.",
      "fix": "Reject or no-op (with no audit record) when the status is already 'cancelled'; test with FakeDb('cancelled')."
    }
  ]
}
```