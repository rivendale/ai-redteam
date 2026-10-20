# PR #131 Review: Audit Record on Cancellation

**Review report**

**REVIEWED:** PR #131, head `8a41c7e`, merge base `2d90b53`. Both SHAs are taken from PR.md. I could not check them against a repository. This session has no tools, so I reviewed the supplied `change.patch` against `work/base/` rather than in a throwaway worktree of the head. Nothing was run, so the claim "Tests pass" is unverified. If the head has moved past `8a41c7e`, the later commits were not reviewed.

**TIER:** Standard. This is an ordinary code change to business logic. It does not touch authentication, permissions, secrets, network exposure, migrations or money movement. The audit record holds an internal user id and an order id. The context sets the stakes as standard, and finance uses the audit trail, which raises the weight of the audit-correctness findings below. One round was run.

**REVIEWERS:** One read by this session (Claude Opus 5.5, `claude-opus-5-5`). This session did not write the change. No code left the session, and no subagent or external endpoint was used. The author is unknown: no commit trailers were provided, only the patch.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `orders.py:16-17` | The audit record is written first, then `db.set_status` runs. If `set_status` raises (DB timeout, lock, connection drop), the audit log says "order.cancelled by alice" but the order stays open. The handler returns 500 and the user retries. On retry the status is still open, so a second record is written. Support and finance then see a cancellation, or two, for an order that was never cancelled. The PR only guards one direction ("never cancelled without a record"). The reverse case, a record without a cancellation, is unhandled and untested. | Make `FakeDb.set_status` raise. Assert that the error propagates and that either no `order.cancelled` record remains, or a compensating or failure record is written. The test fails today because `calls` holds one `order.cancelled` entry. |
| 2 | P2 | `orders.py:9-17` | Two concurrent cancel requests for the same open order (a double-click, a client retry) both read `status == "open"` at line 9. Both pass line 14, and both call `record` and `set_status`. The result is two `order.cancelled` audit records, possibly with different actors, for one cancellation. That contradicts the PR's "cancelling twice records once", which holds only for sequential calls. | Write a fake DB whose `get_order` returns `open` to two interleaved calls, for example with a barrier between `get_order` and `set_status`. Assert exactly one record. The test fails today with two. A fix could be a conditional update (`set_status ... WHERE status='open'`) or a row lock, with the record written inside the same guard. |
| 3 | P3 | `tests/test_orders.py:15` | The test assigns `sys.modules["company_audit"]` at import time and never restores it. (a) Any other test module collected after this one that imports `company_audit` gets the stub, which silently hides real-library failures. (b) If another test imports `orders` first, `from company_audit import record` is already bound to the real library, so these tests call the real audit library and the `FAIL` and `calls` assertions break or produce real side effects. | Run the suite with a second test file that imports `orders` before `test_orders.py`, in either order. Today the results depend on collection order. Fix by using `unittest.mock.patch("orders.record", ...)` per test. |

**Notes that are not findings:**

- The change satisfies the request: the actor is passed from `request["user"]` (`handlers.py:8`) and recorded through the shared library. Nothing extra was added.
- The shipped, already-cancelled and missing-order paths do not record. That behavior is correct.

**FILES NEEDED BUT NOT PROVIDED:**

- **`company_audit` source or its documented contract for `record`.** The tests stub it as `record(event, **fields)`, which raises on failure. If the real function has a different signature, different required fields (for example `actor_type` or `timestamp`) or different keyword names, `orders.py:16` fails in production while the tests pass. If it returns a status, buffers asynchronously or swallows errors instead of raising, the PR's central guarantee is false. That guarantee is "a failed audit write leaves the order open" (docstring at `orders.py:6-8`). This is an unresolved coverage gap, not a supported finding.
- **A repo-wide search for callers of `cancel_order`.** The PR claims `handlers.cancel` is the only caller. I was given only two files. Any other caller, such as an admin tool, batch job or another test, now fails with a `TypeError` because `actor` is required.
- **CI check results for head `8a41c7e`.**

---

**Close-out**

*A reviewer never adjudicates its own findings, so this section is left for the author or whoever closes the PR.*

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | Pending (author) | |
| 2 | Pending (author) | |
| 3 | Pending (author) | |

**VERIFIED AFTER FIXES:** Nothing yet. No fixes have been made.

**MERGE RECOMMENDATION:** Not yet mergeable.

- **Open adjudications:** findings 1–3 have no written decision. As P2/P3 findings they may be deferred, but only with a linked issue.
- **Unverified contract:** the `company_audit.record` contract (signature and failure behavior) is unverified, and the PR's main safety claim depends on it.
- **Unconfirmed caller claim:** the "only caller" claim is unconfirmed.
- **Unknown CI status:** CI status at `8a41c7e` is unknown, and a missing check is not green.

Once those are resolved, the change is likely "merge" or "merge after fixes"; I found no P0 or P1 issue.

```json
{
  "verdict": "not ready: pending adjudication of findings, verification of company_audit.record contract and caller search, and CI status",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "code-read (not executed)",
      "location": "orders.py:16-17",
      "scenario": "Audit record written, then db.set_status raises; audit log shows a cancellation for an order that stays open, and a retry writes a second record.",
      "fix": "Write the record and status change atomically (same transaction or outbox), or emit a compensating/failure record when set_status fails; add a test where set_status raises."
    },
    {
      "severity": "P2",
      "evidence_level": "code-read (not executed)",
      "location": "orders.py:9-17",
      "scenario": "Two concurrent cancels both read status 'open' and both write order.cancelled, giving duplicate (possibly different-actor) audit records for one cancellation.",
      "fix": "Use a conditional update (set status where status='open') or a row lock, and write the record only when the update took effect; add an interleaving test."
    },
    {
      "severity": "P3",
      "evidence_level": "code-read (not executed)",
      "location": "tests/test_orders.py:15",
      "scenario": "Module-level sys.modules stub leaks into other tests and is bypassed if orders was imported first, making results depend on collection order.",
      "fix": "Patch orders.record per test with unittest.mock.patch instead of replacing sys.modules globally."
    }
  ]
}
```