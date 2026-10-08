# PR #131 review: audit record on cancellation

## Review report

**REVIEWED:** PR #131, head `8a41c7e`, merge base `2d90b53`. These SHAs come from PR.md. I had no tools, so I could not check them against the repository or make a throwaway checkout. I reviewed the provided `change.patch` against `work/base/`. Nothing was run, including the tests: "Tests pass" is still the author's claim.

**TIER:** Standard. The owner marked the stakes as standard. The change adds an audit write to an ordinary order operation. It does not touch authentication, permissions, secrets, network exposure, migrations or money movement.

One caveat: the record stores the signed-in user's id. If your data policy treats user ids in log files as personal data, this PR becomes High tier and needs a second round before it counts as reviewed.

**REVIEWERS:**
- **Reviewer:** this session (Claude, `claude-opus-5-5`). It is a separate instance that did not write the change. The code was not sent to any other endpoint.
- **Author:** unknown. No commit trailers were provided, so the author should be recorded from the head commit before close-out.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `orders.py:16-17` (the `record(...)` call, then `db.set_status(...)`) | The audit line is written and fsynced. Then `db.set_status` raises, for example on a DB timeout, a lost connection or a constraint error. The order stays open, but the audit file permanently says `order.cancelled` with an actor. Support or finance reading the trail would treat an open order as cancelled. A retry then writes a second `order.cancelled` record for the same order. The same happens if `os.fsync` raises after `f.write` has already appended the line (`company_audit.py:13-15`). The PR guards only one direction: no cancellation without a record. It does not prevent a record without a cancellation. | A `FakeDb` whose `set_status` raises. Call `cancel_order` and assert it raises. Then assert either that the audit file has no `order.cancelled` line, or that it has a compensating record such as `order.cancel_failed` for the same `order_id`. This fails today. |
| 2 | P2 | `orders.py:14-17` (status read, then record, then set, with no lock or conditional update) | Two cancel requests for the same open order arrive at once: a double-click, a client retry, or two support agents. Both read `status == "open"`, both pass the `cancelled` check, and both write a record. The audit trail then shows two cancellations, possibly by two different actors, so "who cancelled it" has no single answer. This contradicts the PR's claim that cancelling twice records once. `test_cancelling_twice_records_once` only cancels an order that is already cancelled. It never runs two cancels against an open order. | A `FakeDb` whose `get_order` returns `"open"` to two threads held at a barrier before `set_status`. Run `cancel_order` from both. Assert exactly one `order.cancelled` line, and that one call returns `True` and the other `False`. This fails today. The fix is likely a conditional update such as `UPDATE ... WHERE status='open'`, with the record tied to its result. |

**FILES NEEDED BUT NOT PROVIDED:**
- The real `db` implementation, to see whether `set_status` can fail and whether a conditional or transactional update exists for the fixes.
- The login middleware, to confirm `request["user"]` is always set on this route. The handler now raises `KeyError` (a 500) if it is missing.
- A repo-wide search for other `cancel_order` callers. `actor` is now a required positional argument, and the claim that `handlers.cancel` is the only caller is unverified.
- CI results for the head commit.

Other points checked, none of which are findings:
- `from company_audit import record` still sees the patched `AUDIT_PATH`, because the path is read at call time.
- The missing-directory test raises `FileNotFoundError`, which is an `OSError`, so it tests what it claims.
- The change matches the request: an audit record of who cancelled, made through the shared library, with nothing extra.

## Close-out

Pending. The reviewer does not adjudicate its own findings. The author must give each finding a decision:
- **Accepted:** name the fix commit and a regression test that fails without the fix.
- **Deferred:** allowed because both findings are P2. Link the tracking issue.
- **Rejected:** give the evidence.

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | — | — |
| 2 | — | — |

**VERIFIED AFTER FIXES:** none yet.

**MERGE RECOMMENDATION:** merge after fixes, but not yet. There are no P0 or P1 findings, so nothing structural blocks the merge. These conditions are still open:
- Both P2 findings need a written decision. Each can be fixed, or deferred with a linked issue.
- CI checks for `8a41c7e` must be present and green. They have not been seen.
- The owner must confirm the tier, specifically whether user ids in the audit log count as personal data, which would require a second round.
- If fixes move the head, the fix diffs need a targeted read.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "code-read (not executed)",
      "location": "orders.py:16-17; company_audit.py:13-15",
      "scenario": "Audit record is written and fsynced, then db.set_status raises (or fsync raises after the line was appended): the order stays open but the audit trail permanently says order.cancelled with an actor; a retry writes a second record.",
      "fix": "Make record and status change consistent: perform the status change in a transaction and write the record inside it, or write a compensating 'order.cancel_failed' record on failure; add a test with a FakeDb whose set_status raises."
    },
    {
      "severity": "P2",
      "evidence_level": "code-read (not executed)",
      "location": "orders.py:14-17",
      "scenario": "Two concurrent cancels of the same open order both read status 'open' and both write order.cancelled, possibly with different actors, so the trail has two cancellations and no single answer to who cancelled.",
      "fix": "Use a conditional update (set status to cancelled only where status is open) and record only when that update succeeded, inside the same transaction; add a two-thread barrier test asserting exactly one record."
    }
  ]
}
```