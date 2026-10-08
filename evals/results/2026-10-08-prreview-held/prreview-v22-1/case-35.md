# pr-review: PR #131, audit record on cancellation

**Review report**

**REVIEWED:** PR #131, head `8a41c7e`, merge base `2d90b53`. Both SHAs come from PR.md. I could not check them against the repository, and I could not open a worktree because this session has no tools. I reviewed the supplied `change.patch` against `work/base/` as if it were that head. Nothing was run: "Tests pass" is still the author's claim.

**TIER:** Standard. This is an ordinary code change to cancellation. It touches no authentication, permissions, secrets, network exposure, migrations or money movement. The new data written is an order id and an internal user id, sent to the company's own audit library. Two things would move this to High: if the owner treats that user id as personal data, or if the finance audit trail counts as regulated. If either applies, a second round is required before merge.

**REVIEWERS:** This instance (Claude Opus 5.5). It had no part in writing the change, and no data was sent outside this session. **Author:** unknown. No commit trailers were provided.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `orders.py:16-17` | The audit record is written before the status change, and the two are not atomic. Suppose `record(...)` succeeds and then `db.set_status(order_id, "cancelled")` raises (database unavailable, constraint error, timeout). The order stays open, but the audit trail says `order.cancelled` by `alice`. Support and finance would read that as a cancellation that never happened. A retry by the user writes a second `order.cancelled` record. The PR guarantees "never a cancellation without a record", but not the reverse: a record can exist without a cancellation. | A `FakeDb` whose `set_status` raises `OSError`. Call `cancel_order(db, "o1", actor="alice")` and assert it raises. Then assert either that `calls` holds no `order.cancelled` entry, or that it is followed by a compensating event (for example `order.cancel_failed`). This fails today, because `calls == [("order.cancelled", …)]`. |
| 2 | P3 | `orders.py:9,14-17` | The status is checked on a row read earlier (line 9), then recorded and set, with no lock or conditional update. Two concurrent cancels of the same open order both see `"open"`, and both write `order.cancelled` with different actors. That contradicts the PR's "already cancelled… records nothing". An order that ships between the read and the write gets a cancellation record and is set to cancelled. The second case is a race that already existed, but the audit trail now makes it visible. Whether this happens depends on database isolation, which is not shown. | A `FakeDb` whose `get_order` returns `"open"` to two interleaved callers (for example, a barrier in `get_order`). Run two `cancel_order` calls and assert exactly one `order.cancelled` record. This fails today with two. |

**Checked and not raised:**
- The shipped, missing and already-cancelled paths all exit before `record`. This is correct, and it is covered by `test_shipped_is_refused_and_not_recorded` and `test_cancelling_twice_records_once`. That second test never actually cancels twice, but it does cover the already-cancelled path.
- The handler passes `request["user"]`. If the middleware did not set it, a `KeyError` fails closed before any write.

**FILES NEEDED BUT NOT PROVIDED:**
- **`company_audit`, the module itself or its documented contract.** The tests stub it as `record(event, **fields)`, which raises synchronously on failure. The PR's central guarantee ("if that write fails the error propagates and the order stays open") holds only if the real `record`:
  - accepts this signature,
  - raises rather than swallowing or queueing asynchronously, and
  - persists before it returns.

  None of this is verified.
- **A repository-wide search for callers of `orders.cancel_order`.** `actor` is now a required positional argument. The PR says `handlers.cancel` is the only caller, but I only had the two changed files. Any other caller would raise `TypeError`.
- **CI results for head `8a41c7e`.**

---

**Close-out**: pending. The author adjudicates the findings above, and whoever closes the PR writes this section. A reviewer does not adjudicate its own findings.

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | *pending* | |
| 2 | *pending* | |

**VERIFIED AFTER FIXES:** nothing yet.

**MERGE RECOMMENDATION:** Not yet ready; the expected path is **merge after fixes**. There is no P0 or P1. Merge stays blocked until:
- both findings have a written decision (each is P2 or P3, so it may be Deferred with a linked issue);
- the expected checks for `8a41c7e` are present and green;
- the `company_audit` contract is confirmed to raise synchronously on a failed write;
- a full-repo search confirms there are no other callers of `cancel_order`;
- the owner confirms the tier (Standard as recorded, or High if the user id or finance audit counts as personal or regulated data).

```json
{
  "verdict": "merge after fixes (pending adjudication, CI, and confirmation of the company_audit contract and other callers)",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "code-read (not executed)",
      "location": "orders.py:16-17",
      "scenario": "record() succeeds, then db.set_status raises; the order stays open but the audit trail says order.cancelled by the actor, and a retry writes a second record.",
      "fix": "Make the record and the status change consistent: record after a successful conditional update with a compensating or failed event on audit failure, or write a compensating 'order.cancel_failed' event when set_status raises; add a test with a raising set_status."
    },
    {
      "severity": "P3",
      "evidence_level": "inferred from code; depends on db isolation not shown",
      "location": "orders.py:9,14-17",
      "scenario": "Two concurrent cancels of the same open order both pass the status check on a stale read and both write order.cancelled; an order that ships between the read and the write gets a cancellation record.",
      "fix": "Use a conditional update (set status to cancelled only where the status is open, returning the affected rows) or a row lock, and record only when this call made the transition; add an interleaved-callers test."
    }
  ]
}
```