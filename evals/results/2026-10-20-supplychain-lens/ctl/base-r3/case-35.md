# PR #131 review: audit record on cancellation

**Review report**

**REVIEWED:** PR #131, head `8a41c7e`, merge base `2d90b53`.
- Both SHAs come from PR.md. I could not check them against a repository.
- I reviewed only the supplied `change.patch` against `work/base/`. I had no worktree and no tools, so I ran nothing, including the tests.
- If the head is no longer `8a41c7e`, any later commits were not reviewed.

**TIER:** Standard.
- The change is an ordinary code change to cancellation logic. It touches no auth, permissions, secrets, migrations or money movement, and the requester set the stakes as standard.
- One caveat: the audit record stores a user id. If your data policy treats user ids as personal data, this PR is High tier and needs a second round on another approved vendor before it counts as reviewed.

**REVIEWERS:**
- Reviewer: one independent round, this instance (Claude Opus 5.5, `claude-opus-5-5`). It had no part in writing the change.
- Author: unknown. The commit trailers were not provided, so I could not read `Co-Authored-By`.

**Data handling:** Only the material already in this session was used. Nothing was sent to a subagent or an external endpoint.

**Against the request:** The change does what was asked. It records `order.cancelled` with the actor through `company_audit`, and adds nothing beyond that.

### FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 (unverified: library not provided) | `orders.py:16` (`record("order.cancelled", order_id=..., actor=...)`) | The tests replace `company_audit` with a stub, `record(event, **fields)`, that raises on failure. Two things about the real library are unknown: its signature, and how it reports a failed write. **(a)** If the real signature is different (positional fields, a required `source`, or a different name for `actor`), every cancellation raises `TypeError`. Cancellation would be down in production while the tests stay green. **(b)** If the library signals failure by returning a value, or by logging and swallowing the error, the code ignores that return value. The order is then cancelled with no audit record. That breaks the PR's central claim that "a cancellation is never made without its record". | Write a contract test against the real `company_audit`, not the stub, with a sink that fails. Assert that `cancel_order` leaves the order open. If `record` returns a status rather than raising, assert that a falsy return also leaves the order open. |
| 2 | P2 | `orders.py:16-17` | The record is written before the status change, and the two steps are not atomic. If `db.set_status` raises (connection drop, lock timeout, constraint) after `record` has succeeded, the audit log says the order was cancelled by this user, but it is still open. Support and finance then act on a cancellation that never happened. The PR describes only the opposite failure, where the audit write fails. | Build a `FakeDb` whose `set_status` raises. Assert either that no `order.cancelled` record remains, or that a compensating record (for example `order.cancel_failed`) is written. Fix options: write both in one transaction or outbox, or record a compensating event on failure. |
| 3 | P2 | `orders.py:11-16` | The "cancelling twice records once" guarantee holds only for sequential calls. Two concurrent requests (a double-click, or a client retry) can both read `status == "open"`. Both then call `record`, and both call `set_status`. Finance sees two cancellation records, possibly with two different actors. | Build a `FakeDb` whose `get_order` returns `open` to two interleaved calls. Assert there is exactly one record. Fix: a conditional update (`UPDATE ... WHERE status='open'`) or a row lock, with the record tied to the update that succeeded. |
| 4 | P2 (unverified) | `orders.py:6` (`actor` now required); "only caller" claim in PR.md | `actor` is now a required positional parameter. If anything else calls `cancel_order(db, order_id)`, it raises `TypeError` after merge. PR.md says `handlers.cancel` is the only caller, but I was given two files, not the repository, so this is a claim. Examples of callers it could miss: admin scripts, batch jobs, other services. | Grep the repository for `cancel_order(`. Add an import-and-call smoke test for every caller found. |
| 5 | P3 | `tests/test_orders.py:15` | The test installs its stub with `sys.modules["company_audit"] = ...` at import time and never restores it. **(a)** Any other test module that imports `company_audit` in the same run gets the stub. **(b)** If another module imported `orders` first, with the real library, `orders.record` is already bound to the real function. The stub would then be bypassed, and these tests would call the real audit sink. | Run the suite in a different order, with another test importing `orders` first, and assert that `calls` is still populated. Fix: use `mock.patch("orders.record")` per test. |

**FILES NEEDED BUT NOT PROVIDED:**
- `company_audit`: its source, or documentation of the signature and failure behaviour of `record`.
- The rest of the repository, to confirm `handlers.cancel` is the only caller of `cancel_order`.
- The `db` implementation, for the atomicity of `get_order`/`set_status` and the behaviour of transactions.
- The commit trailers, to identify the author.
- CI check results.

**Close-out**

The close-out is not written here. The author adjudicates the findings and whoever closes the PR writes the close-out, so a reviewer never adjudicates its own findings.

The current state is:
- Five findings are open, with no decision yet.
- Finding 1 is P1, so it cannot be deferred.
- No CI checks were shown to me, and a missing check is not green.

**MERGE RECOMMENDATION (reviewer's view): do not merge yet.**
- Finding 1 must be resolved by checking the real `company_audit` contract.
- Findings 2 to 4 each need a written decision.
- The tier question needs an owner answer: is a user id personal data here? If yes, a second round is required.

```json
{
  "verdict": "do not merge yet (merge after fixes)",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "unverified: real company_audit not provided; tests only exercise a stub",
      "location": "orders.py:16",
      "scenario": "Real company_audit.record may have a different signature (every cancel raises TypeError) or may report write failure by return value or swallowing the error, which the code ignores. The order is then cancelled with no audit record, contradicting the PR's guarantee.",
      "fix": "Confirm the real signature and failure contract. Check the return value if needed. Add a contract test against the real library with a failing sink."
    },
    {
      "severity": "P2",
      "evidence_level": "confirmed from code",
      "location": "orders.py:16-17",
      "scenario": "record succeeds, then db.set_status raises. The audit log shows a cancellation by the user while the order stays open.",
      "fix": "Make the audit write and the status change atomic (same transaction or outbox), or write a compensating audit event when set_status fails."
    },
    {
      "severity": "P2",
      "evidence_level": "confirmed from code (check-then-act without lock)",
      "location": "orders.py:11-16",
      "scenario": "Two concurrent cancel requests both read status 'open'. Both write an order.cancelled record, possibly with different actors.",
      "fix": "Use a conditional update or row lock, and write the record only for the update that actually changed the status."
    },
    {
      "severity": "P2",
      "evidence_level": "unverified: only two files provided",
      "location": "orders.py:6",
      "scenario": "actor is now required. Any caller other than handlers.cancel that still calls cancel_order(db, order_id) raises TypeError after merge.",
      "fix": "Grep the repository for all callers, update them, and add smoke tests."
    },
    {
      "severity": "P3",
      "evidence_level": "confirmed from code",
      "location": "tests/test_orders.py:15",
      "scenario": "The global sys.modules stub is never restored. It leaks into other tests, and if orders was imported earlier with the real library, these tests call the real audit sink.",
      "fix": "Patch orders.record per test with unittest.mock.patch instead of replacing sys.modules at import time."
    }
  ]
}
```