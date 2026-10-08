# PR #131 review: audit record on cancellation

**Review report**

**REVIEWED:** PR #131, head `8a41c7e`, merge base `2d90b53`. These SHAs come from PR.md. I had no tools, so I could not check out the head or confirm the patch matches it. I reviewed `work/change.patch` against `work/base/` as provided. If the head differs from `8a41c7e`, this review does not cover it.

**TIER:** Standard.
- The change adds an audit call to an ordinary code path. It does not touch auth, permissions, secrets, network exposure, migrations or money movement. The owner also stated the stakes as standard.
- The one borderline point is that the audit line now holds a user id. That is an internal identifier going into an existing shared audit trail whose purpose is to record actors.
- If the owner treats that id as personal data in scope, the tier is High and a second round is still owed.

**REVIEWERS:**
- Reviewer: this session (Claude Opus 5.5). It did not write or help write the change. No code left this session.
- Author: unknown. No commit trailers were provided, so authorship could not be read from them.

**What I checked and found sound:**
- **The fsync claim holds.** `company_audit.record` writes, flushes and calls `os.fsync` before returning (`base/company_audit.py:10-14`).
- **The order of steps matches the PR.** Not found, shipped and already-cancelled orders all exit before `record` (`orders.py:9-15`). `record` runs before `set_status` (`orders.py:16-17`). A failed write therefore raises and leaves the order open, and `test_a_failed_audit_write_leaves_the_order_open` covers this. A missing directory raises `FileNotFoundError`, which is a subclass of `OSError`.
- **Re-cancelling records nothing.** `orders.py:14-15` returns `False` before `record`, and `test_cancelling_twice_records_once` covers the sequential case.
- **The actor is the signed-in user id string.** `handlers.py:8` passes `request["user"]`, which the handler docstring defines as the user id, a string. `test_the_handler_records_the_signed_in_user` asserts it.
- **The tests redirect the audit path correctly.** They set `company_audit.AUDIT_PATH` at runtime. This works because `record` reads the module global at call time, even though `orders` imports `record` by name.
- **"Tests pass" is a claim, not a result.** I read the tests and they look correct, but I could not run them.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `orders.py:16-17` | The audit line is written and fsynced, then `db.set_status` raises (DB timeout, lost connection, constraint error). The order stays open, but the audit trail permanently says `order.cancelled` by that actor. Support and finance, who rely on this trail, see a cancellation that never happened, and nothing records that it failed. The PR guarantees "no cancellation without a record" but not the reverse, and does not say so. Workaround: reconcile the audit log against order status. | Use a FakeDb whose `set_status` raises `RuntimeError`. Call `cancel_order`, expect the raise, then assert the audit log has no unqualified `order.cancelled` line for `o1`. For example, it should hold a compensating `order.cancel_failed` line, or the outcome should be recorded some other way. This fails today: the log holds one `order.cancelled` line. |
| 2 | P3 | `orders.py:9-17` | Two cancel requests for the same open order arrive at the same time (double-click, client retry). Both read `status == "open"`, both pass line 14, and both call `record`. The trail then shows two cancellations, possibly by different actors, so "records once" holds only for sequential calls. The check-then-act race existed before this PR, but it now produces wrong audit data. Severity depends on DB semantics I could not see (`db` is not provided). | Use a FakeDb whose `get_order` returns `open` on the first two calls, simulating the interleaving. Call `cancel_order` twice and assert exactly one audit line. This fails today with two. |

**FILES NEEDED BUT NOT PROVIDED:**
- The rest of the repository. I need it to confirm that `handlers.cancel` is the only caller of `cancel_order`, because `actor` is now required and positional, so any other caller breaks.
- The `db` implementation, to see whether `set_status` can be a conditional or atomic update (relevant to finding 2).
- CI configuration and check results.
- The commit trailers for `8a41c7e`.

**Close-out**

The author has not adjudicated these findings yet. A reviewer does not adjudicate its own findings, so the close-out is pending.

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | Pending author | Can be fixed, deferred with an issue (it is P2), or rejected with evidence |
| 2 | Pending author | Same as finding 1 (it is P3) |

**VERIFIED AFTER FIXES:** None yet.

**MERGE RECOMMENDATION:** Merge after fixes. That is, merge once the findings are adjudicated, not necessarily fixed. The change meets the request and has no P0 or P1 findings. Two things are still open:
- Findings 1 and 2 need a written decision. Both may be deferred with linked issues.
- No check results were provided, and a missing check is not green. Expected CI must be present and green at the reviewed head.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "code-read",
      "location": "orders.py:16-17",
      "scenario": "record() fsyncs an order.cancelled line, then db.set_status raises; the order stays open but the audit trail permanently says it was cancelled by the actor, with no failure record.",
      "fix": "On set_status failure, write a compensating order.cancel_failed record (or record the outcome after the status change in a way that still guarantees no unrecorded cancellation), and document the guarantee; add a test with a raising set_status."
    },
    {
      "severity": "P3",
      "evidence_level": "inferred (db implementation not provided)",
      "location": "orders.py:9-17",
      "scenario": "Two concurrent cancels of the same open order both read status open and both write order.cancelled, giving duplicate audit records, possibly with different actors.",
      "fix": "Make the status change conditional/atomic (e.g. set_status only if still open, returning whether it changed) and record only for the winner, or serialise per order; add an interleaving test."
    }
  ]
}
```