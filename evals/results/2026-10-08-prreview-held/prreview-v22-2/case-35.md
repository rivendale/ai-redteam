# PR #131 review: audit record on cancellation

**Review report**

**REVIEWED:** PR #131, head `8a41c7e`, merge base `2d90b53` (both as stated in PR.md). I had no tools, so I could not check out the head or confirm the patch matches `8a41c7e`. I reviewed `work/change.patch` against `work/base/`. If the head has moved past `8a41c7e`, those later commits are not reviewed.

**TIER:** Standard. The change is an ordinary code path. It adds an audit write and threads through an actor id the login middleware already supplies. It does not touch authentication, permissions, secrets, network exposure, money movement or migrations. The context also sets the stakes at standard. One round is required, and this is that round.

**REVIEWERS:** One read by Claude Opus 5.5 (`claude-opus-5-5`) in this session. Nothing was sent to any other model or endpoint. This session did not write the change, but the author could not be determined because commit trailers were not provided. Fill that in from `git log 2d90b53..8a41c7e` before close-out.

**What I checked**

- **Matches the request.** The cancellation now writes `record("order.cancelled", order_id=..., actor=...)` through `company_audit`. The actor is `request["user"]`, the signed-in user's id string from the login middleware. The change does nothing beyond the request.
- **Write order is correct.** The audit write happens after the guards for missing, shipped and already-cancelled orders, and before `db.set_status`. A failed audit write raises and leaves the order open, so a cancellation never happens without its record. This is the right order and should not be reversed.
- **Re-cancel is a no-op.** An already-cancelled order returns `False` before `record`, so nothing is written twice on the normal path.
- **Signature change has no other callers.** `actor` is a new required argument. PR.md says `handlers.cancel` is the only caller and it is updated. I could only see the given files and found no other caller there.
- **Tests read as correct.** I read the five tests. Each would pass against the patched code and exercise the claim it names: success, shipped, handler actor, failed write and re-cancel. I could not run them.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P3 | `orders.py:16-17` (patched) | The audit write succeeds, then `db.set_status(order_id, "cancelled")` raises (for example, a lost DB connection). The audit log now says user X cancelled the order, but the order is still open. If the user retries, a second `order.cancelled` record is written for the same order. Support or finance reading the log would see a cancellation that never happened, or two. This is the accepted cost of the correct record-first order, not a reason to reverse it. Possible fixes: put the audit write and the status change in one transaction if `company_audit` supports that, or record a compensating `order.cancel_failed` event when `set_status` raises. | A `FakeDb` whose `set_status` raises. Assert that `cancel_order` raises and that the audit log has no unqualified `order.cancelled` record for an order that is still open. The test fails today because `calls` holds the record. |

No P0, P1 or P2 findings.

**Unverified claims (not findings, no evidence of a defect):**

- **The audit library's real behaviour.** The tests stub `company_audit` with `record(event, **fields)`, and the "failed write leaves the order open" guarantee rests on the real `record` raising on failure. If the real `record` buffers or writes asynchronously, or swallows errors, the guarantee does not hold. If it has a different signature, every cancellation fails. Someone should confirm this against the library before merge.
- **"Tests pass."** I read the tests but could not run them. CI output should confirm it.

**FILES NEEDED BUT NOT PROVIDED:**

- the `company_audit` source, or the API docs for `record`: its signature, how it reports failure, and whether it writes synchronously;
- the commit log with trailers for `2d90b53..8a41c7e`;
- the CI check results for `8a41c7e`;
- a repository-wide search confirming there are no other callers of `cancel_order`.

**Close-out**

This is not written yet. The author adjudicates finding #1 as Accepted, Deferred with an issue link, or Rejected with evidence. Whoever closes the PR then fills in ADJUDICATION, VERIFIED AFTER FIXES and the final recommendation. As the reviewer, I do not adjudicate my own finding.

**MERGE RECOMMENDATION (reviewer's view, pending close-out):** Merge, once these hold:

1. finding #1 has a written decision;
2. CI checks for `8a41c7e` are present and green (I have not seen them);
3. the real `company_audit.record` signature and failure behaviour are confirmed to match the stub.

There are no blockers in the code as read.

```json
{
  "verdict": "merge (pending adjudication of the P3, green CI on 8a41c7e, and confirmation that company_audit.record matches the stub)",
  "findings": [
    {
      "severity": "P3",
      "evidence_level": "code-read (not executed; no tools)",
      "location": "orders.py:16-17 (patched)",
      "scenario": "The audit record is written, then db.set_status raises (e.g. a lost DB connection). The audit log says the actor cancelled the order while it is still open; a retry writes a second order.cancelled record. This is the accepted cost of the correct record-first order, which should not be reversed.",
      "fix": "If company_audit supports it, write the audit record and the status change in one transaction; otherwise catch the set_status failure, record a compensating 'order.cancel_failed' event, and re-raise. Add a test with a FakeDb whose set_status raises."
    }
  ]
}
```