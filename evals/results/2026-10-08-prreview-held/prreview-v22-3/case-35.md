# PR #131 review: audit record on cancellation

**Review report**

**REVIEWED:** PR #131, head `8a41c7e`, merge base `2d90b53`. Both SHAs come from PR.md. I could not check them against the repository because this session has no tools. I reviewed the patch and the base files as provided. I did not use a checkout, so anything committed beyond this patch was not reviewed.

**TIER:** Standard. The change adds an audit write to an existing state change. It does not alter authentication, permissions, secrets, network exposure, migrations or money movement. The context also gives the stakes as standard. The audit record does carry a user id. That is a pseudonymous identifier, and nothing was sent outside this session, so Step 3 did not limit the review.

**REVIEWERS:** One round by this instance (Claude Opus 5.5, model `claude-opus-5-5`). This session did not write the change. The author is unknown: no commit trailers were provided. That leaves the authorship part of Step 4 unrecorded.

**What checks out by reading:**
- The change matches the request. The audit record names the actor, uses `company_audit`, and adds nothing beyond that.
- The only caller passes `request["user"]`, which the handler's docstring documents as the signed-in user's id string.
- Already-cancelled and shipped orders are not recorded.
- A failed `record` call raises before `set_status`, so the order stays open.
- The five tests appear consistent with the code and should pass. "Tests pass" is still the author's claim: I could not run them.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `orders.py:16-17` | The audit write comes first and is not undone. If `record` succeeds and `db.set_status` then fails (DB timeout, lost connection), the log says `order.cancelled` while the order is still open. Support and finance read that record. If the user retries and it succeeds, the log holds two cancellation records for one cancellation, possibly with different actors. The PR closes one gap: no cancellation without a record. It opens the reverse one: a record without a cancellation. Neither the PR nor the docstring states this trade-off. | Use a `FakeDb` whose `set_status` raises. Assert that `cancel_order` raises AND that the log does not show the order as cancelled: either no `order.cancelled` record, or a compensating `order.cancel_failed` record follows it. This fails today because `calls` holds one `order.cancelled` and nothing else. Possible fixes: a transactional outbox, or a compensating record on failure. At minimum, document the trade-off. |
| 2 | P3 | `orders.py:14-16` | The status check and the record are not atomic. A double-clicked Cancel button, or a client retry, sends two concurrent requests. Both read `status == "open"`, both pass the check on line 14, and both call `record`. The result is two `order.cancelled` records, which contradicts the PR's claim that "cancelling an order that is already cancelled … records nothing". Before this PR the duplicate `set_status` was harmless. The duplicate audit record is new. | Use a `FakeDb` whose `get_order` returns `"open"` for the first two reads, simulating two requests interleaved before either write. Call `cancel_order` twice and assert exactly one `order.cancelled` record. This fails today with two. Fix: a conditional update (`open → cancelled`, returning whether a row changed) that gates the record, in the same transaction as finding 1's fix. |
| 3 | P3 | `tests/test_orders.py:9-15` | The stub `_record(event, **fields)` accepts any keyword arguments, and every test uses it. Suppose the real `company_audit.record` has a different signature, for example `user=` instead of `actor=`, or a required `source`. The tests still pass, but every production cancellation raises `TypeError`. Because the record is written first, no order can then be cancelled at all. The stub is also installed into `sys.modules` at import and never removed, so it leaks into any other test module in the same run. | Add a contract test against the real `company_audit`, or its published test double, calling `record("order.cancelled", order_id="o1", actor="u1")`. Install the stub with `unittest.mock.patch.dict(sys.modules, ...)` inside setup, so it is removed after the tests. |

**FILES NEEDED BUT NOT PROVIDED:**
- **`company_audit` (the shared library).** Two of the PR's central claims depend on it:
  - The call signature `record(event, order_id=, actor=)` (finding 3).
  - That `record` writes synchronously and raises on failure. If it buffers, queues or swallows errors, a failed write would not raise. "A failed audit write leaves the order open" would then be false, and orders could be cancelled with no record.
- The login middleware, which should confirm that `request["user"]` is always present on this route.
- CI configuration and check results.
- The commit trailers, to record authorship.

**Close-out**

Pending. As the reviewer, I cannot adjudicate my own findings. The author or whoever closes the PR must record Accepted, Deferred or Rejected for findings 1 to 3. Findings 1 and 2 may be deferred with a tracking issue, since they are P2 and P3.

**ADJUDICATION:** not yet written.

**VERIFIED AFTER FIXES:** nothing yet.

**MERGE RECOMMENDATION (reviewer's view, not a close-out):** Merge after adjudication. There is no P0 or P1. Before merge, these must be done:
1. Every finding gets a written decision.
2. Someone with access confirms against `company_audit` that `record` has this signature and raises synchronously on failure. If it does not, the PR's core guarantee does not hold and this recommendation becomes "do not merge".
3. CI checks are confirmed present and green on `8a41c7e`. I have seen none.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "confirmed by reading the diff",
      "location": "orders.py:16-17",
      "scenario": "record() succeeds, then db.set_status raises: the audit log says order.cancelled but the order stays open; a retry writes a second cancellation record.",
      "fix": "Write the record and the status change atomically (transactional outbox), or write a compensating order.cancel_failed record on failure; at minimum document the trade-off. Test: FakeDb.set_status raises, assert no unmatched order.cancelled."
    },
    {
      "severity": "P3",
      "evidence_level": "confirmed by reading the diff (race, not run)",
      "location": "orders.py:14-16",
      "scenario": "Two concurrent cancel requests (double-click or retry) both read status open and both call record(), producing duplicate order.cancelled records, contrary to the PR's claim.",
      "fix": "Conditional update open->cancelled that reports whether a row changed, gating the record in the same transaction."
    },
    {
      "severity": "P3",
      "evidence_level": "confirmed by reading the tests; real library not provided",
      "location": "tests/test_orders.py:9-15",
      "scenario": "The stub accepts any kwargs, so a signature mismatch with the real company_audit.record passes the tests but raises TypeError on every production cancellation; the sys.modules stub is never removed and leaks into other test modules.",
      "fix": "Add a contract test against the real library or its official fake; install the stub with mock.patch.dict(sys.modules) in setup."
    }
  ]
}
```