# PR #131 review: audit record on cancellation

## Review report

**REVIEWED:** PR #131, head `8a41c7e`, merge base `2d90b53`, as stated in `PR.md`.
- I reviewed the supplied `change.patch` against `work/base/`, not a worktree checked out at `8a41c7e`.
- I cannot confirm the patch matches that commit. If the head has moved since, the later commits are not reviewed.
- I did not run the tests. This session has no tools, so every result below comes from reading the code.

**TIER:** Standard, one round.
- The change adds an audit call. It does not change who can cancel an order, and it does not touch secrets, network exposure or a migration.
- The context also rates the stakes as standard.
- One caveat: the PR writes a user id into a finance-relevant audit trail. If the owner treats that trail as a regulated or controlled record, this becomes High tier and needs a second round. That is the owner's call.

**REVIEWERS:**
- Reviewer: this instance (Claude Opus 5.5). It did not write the change, and no code was sent anywhere else.
- Author: unknown. No commit trailers were provided, so this needs recording at close-out.

**Text addressed to the reviewer:** none found in the PR description, diff or files.

**Against the original request:** the change covers the request. It writes an audit record with the actor, using `company_audit`, and adds nothing beyond it. Recording the audit *before* the status change is a design choice the request did not ask for. Findings 1 and 2 cover its consequences.

### FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 (unverified: library not provided) | `orders.py:2`, `orders.py:16` | The real contract of `company_audit.record` is never exercised; the tests replace it with a stub that accepts `(event, **fields)` and raises on failure. Two ways this goes wrong: **(a)** if the real function takes different arguments (for example a `fields` dict, required `actor_type` or `timestamp`, or a different keyword than `actor`), every cancellation raises `TypeError` at line 16 and no order can be cancelled. **(b)** If the real function buffers, writes asynchronously, or swallows I/O errors, the PR's main guarantee ("a failed audit write leaves the order open") is false: the order is cancelled and the record is silently lost. | A contract test that imports the real `company_audit` (no stub) and calls `record("order.cancelled", order_id="o1", actor="alice")` against its test sink. Assert that the record lands with those fields, and that an injected sink failure raises synchronously. |
| 2 | P2 | `orders.py:16-17` | `record()` succeeds, then `db.set_status` raises (DB timeout, lock, constraint). The audit trail now says user X cancelled the order, but the order is still open. Support and finance will read a cancellation that never happened. If the user retries and it succeeds, the audit trail holds two cancellation records for one cancellation. | Use a `FakeDb` whose `set_status` raises. Call `cancel_order`, expect the exception, then assert that either no `order.cancelled` record exists, or a compensating record such as `order.cancel_failed` follows it. This fails today, because the record exists and nothing follows it. |
| 3 | P3 | `orders.py:9-17` | Two concurrent cancel requests for the same open order both read `status == "open"` at line 9. Both call `record()` and both call `set_status`. The result is two audit records with possibly different actors, which contradicts the PR's claim that cancelling twice records once. The check-then-set race existed before this PR, but it now produces a wrong audit trail. | Use a `FakeDb` whose `get_order` returns `"open"` to two callers before either calls `set_status`, for example with a barrier between two threads. Assert there is exactly one `order.cancelled` record. |
| 4 | P3 | `tests/test_orders.py:15-17` | The stub is installed into `sys.modules` when the test module is imported, and never removed. If any earlier test module has already imported `orders`, its `record` is bound to the real library, so these tests call the real audit library and the assertions on `calls` fail or write real records. The stub also leaks into every test that runs after this one. | Import `orders` from a test that runs earlier in the same test session, then run this module. Its tests fail. With the fix (patch `orders.record` per test, for example with `unittest.mock.patch("orders.record")`), they pass in any order. |

**Possible fixes (for the author to choose):**
- **Finding 1:** read the `company_audit` API and add the contract test above.
- **Findings 2 and 3:** write the status change and the audit event in one transaction, or through an outbox. Alternatively, make the update conditional (`set_status ... WHERE status = 'open'`) and record only when that update actually changes the status. Note that a conditional update alone reopens the "cancelled without a record" gap if the audit write then fails.

### FILES NEEDED BUT NOT PROVIDED

- **`company_audit`:** its source or API docs, especially the signature of `record` and whether it fails synchronously. These are needed to confirm or reject Finding 1.
- **The `db` implementation:** needed to see whether `set_status` can fail and whether a transaction or conditional update is available (Findings 2 and 3).
- **Every other caller of `cancel_order`:** admin tools, jobs, other services, scripts. `actor` is now required, so any caller not updated raises `TypeError`. The PR says `handlers.cancel` is the only caller, but `work/base/` is too small to confirm that.
- **Commit trailers for `8a41c7e`:** needed to record the author.
- **CI results for `8a41c7e`.**

---

## Close-out

*Not written by this reviewer.* A reviewer does not adjudicate its own findings. The author must give each finding a written decision, and whoever closes the PR completes this section.

**ADJUDICATION:** pending for findings 1 to 4.
- Finding 1 is P1. It cannot be deferred; it must be fixed, or rejected with evidence from the real `company_audit` API.

**VERIFIED AFTER FIXES:** none yet.

**MERGE RECOMMENDATION (provisional):** do not merge yet. The PR stays blocked until:
- Finding 1 (P1) is resolved, with the library contract confirmed or the call fixed;
- findings 2 to 4 each have a written decision;
- CI checks for the final head are present and green (none were provided);
- the other callers of `cancel_order` are confirmed;
- the author is recorded;
- the owner confirms Standard tier is enough for a finance audit trail.

```json
{
  "verdict": "do not merge yet: P1 unresolved, findings unadjudicated, CI not seen",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "unverified: depends on company_audit, which was not provided; tests only exercise a stub",
      "location": "orders.py:2, orders.py:16",
      "scenario": "If the real company_audit.record signature differs from record(event, order_id=..., actor=...), every cancellation raises TypeError and no order can be cancelled. If record writes asynchronously or swallows errors, the PR's guarantee fails: the order is cancelled and the record is lost.",
      "fix": "Confirm the real API and its failure behaviour; add a contract test against the real library's test sink."
    },
    {
      "severity": "P2",
      "evidence_level": "read from diff",
      "location": "orders.py:16-17",
      "scenario": "record() succeeds, then db.set_status raises: the audit trail says the order was cancelled but it is still open; a retry adds a second cancellation record.",
      "fix": "Write the audit event and the status change atomically (same transaction or outbox), or emit a compensating record when set_status fails; add a test with a set_status that raises."
    },
    {
      "severity": "P3",
      "evidence_level": "read from diff (the check-then-set race existed before this PR)",
      "location": "orders.py:9-17",
      "scenario": "Two concurrent cancels of the same open order both pass the status check and both write order.cancelled, possibly with different actors.",
      "fix": "Make the update conditional (WHERE status='open') and record only for the call that actually changed the status, inside the same transaction as the audit write."
    },
    {
      "severity": "P3",
      "evidence_level": "read from tests",
      "location": "tests/test_orders.py:15-17",
      "scenario": "The stub is installed in sys.modules at import time: if orders was already imported, the real library is called and the assertions fail; the stub also leaks into later tests.",
      "fix": "Patch orders.record per test with unittest.mock.patch."
    }
  ]
}
```