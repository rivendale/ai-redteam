# Review report: PR #131, audit record on cancellation

**REVIEWED:** PR #131, head `8a41c7e`, merge base `2d90b53`. I could not check the SHAs against a checkout: this session has no tools, and only `PR.md`, `change.patch` and `base/` were supplied. Nothing was run.

**TIER:** Standard. The change touches audit logging and an internal function signature. It does not touch auth, secrets, network exposure, personal data beyond a user id, or money movement. The context also says "standard".

**REVIEWERS:**
- Reviewer: a fresh instance (Sonnet 5.5) with no part in writing the change.
- Author: unknown, because no commit trailers were supplied.
- Instruction files: no checkout was opened, so none could have loaded. I did not confirm this by inspecting the session. The patch changes no `AGENTS.md`, `CLAUDE.md` or skill files, and I found no text aimed at reviewers.

**Scope check against the request:** the request asked for an audit record of who cancelled, written through the shared library. The patch does that with `actor` and `order_id`, and `ts` comes from the library. It adds nothing else.

**Claims checked:**
- "`record` writes and fsyncs before it returns" is confirmed at `base/company_audit.py`, which does flush then `os.fsync`.
- "Already cancelled changes nothing and records nothing" is confirmed by the early `return False` before `record`.
- "A failed audit write leaves the order open" is confirmed for `record` failures, because the exception propagates before `set_status`.
- "Tests pass" is an assertion. I did not run them, and no CI result was supplied.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `orders.py:16-17` (`record(...)` then `db.set_status(...)`) | The audit is written before the status change, and the two writes are not atomic. If `set_status` raises (DB outage, lock timeout), the log already says `order.cancelled` while the order is still open. Finance and support then see a cancellation that never happened. A retry writes a second record. The docstring's "never made without its record" is true, but the reverse case (a record without a cancellation) is unhandled. | A `FakeDb` whose `set_status` raises. Assert either that no `order.cancelled` line remains, or that a compensating or failure event is recorded and a retry does not produce an ambiguous duplicate. |
| 2 | P2 | `orders.py:13-17` (check, record, set are not guarded) | Two concurrent cancel requests for the same open order both read `open`, both pass the check, and both write an audit record. The log then shows two cancellations, and possibly two actors, for one order. The "records once" guarantee holds only for sequential calls. | A `FakeDb` whose `get_order` returns `open` for two interleaved calls. Assert exactly one record, which needs a conditional update such as `set_status` only `WHERE status='open'` and recording based on that result. |
| 3 | P3 | `orders.py:6` (`actor` is not validated) | `actor` is accepted as `None` or `""` and recorded as-is. A middleware regression that sets `request["user"]` to an empty string produces a cancellation with no identifiable actor, which defeats the purpose of the audit. A missing key fails closed with `KeyError` in the handler. | `cancel_order(db, "o1", actor="")` and `actor=None` should raise `ValueError` and leave the order open with no record. |
| 4 | P3 (UNVERIFIED) | `orders.py:6` (signature change) | `actor` is now a required positional argument. The PR says `handlers.cancel` is the only caller, but only `base/` was supplied. A job, admin script or other module calling `cancel_order(db, id)` would raise `TypeError` at runtime. | A repo-wide search or a test importing every caller. This is a coverage gap, not a confirmed defect. |

Test gaps: no test covers a failure of `set_status` (finding 1), concurrency (finding 2), or an invalid `actor` (finding 3). `test_cancel_is_on_disk_before_it_returns` only shows the record is readable after the call. It does not show the record was written before the status change.

**FILES NEEDED BUT NOT PROVIDED:**
- Callers of `cancel_order` outside `base/`.
- The real `db` implementation, to check transactionality and conditional updates.
- CI results for head `8a41c7e`.
- Commit trailers.

---

**Close-out** (to be completed by the author and whoever closes the PR; a reviewer does not adjudicate its own findings)

ADJUDICATION: pending for findings 1-4. Findings 1-4 are P2 or P3, so each may be fixed, deferred with a tracking issue, or rejected with evidence. A fix needs a regression test and a read of its own diff.

VERIFIED AFTER FIXES: nothing yet.

**MERGE RECOMMENDATION: merge after fixes.** There are no P0 or P1 findings. Before merging:
- Every finding needs a written decision.
- Green CI must be shown for the final head, because "Tests pass" in the description is an assertion and a missing check is not green.
- Finding 4 (other callers) must be resolved.

No written rule was supplied that settles this, so I cite none. If the owner treats finding 1 as acceptable, it can be deferred with an issue link.

```json
{
  "verdict": "merge_after_fixes",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "code-read",
      "location": "orders.py:16-17",
      "scenario": "record() runs before db.set_status(); if set_status raises, the audit log shows order.cancelled but the order stays open, and a retry writes a duplicate record.",
      "fix": "Make the audit and status change atomic or compensating; add a test with a set_status that raises."
    },
    {
      "severity": "P2",
      "evidence_level": "code-read",
      "location": "orders.py:13-17",
      "scenario": "Two concurrent cancels of the same open order both pass the status check and both write an audit record, so the log shows duplicate cancellations.",
      "fix": "Use a conditional status update (only if still open) and record only for the caller that won; add an interleaving test."
    },
    {
      "severity": "P3",
      "evidence_level": "code-read",
      "location": "orders.py:6",
      "scenario": "actor of None or empty string is accepted and recorded, producing a cancellation audit entry with no identifiable actor.",
      "fix": "Validate actor as a non-empty string before recording; test None and '' raise and leave the order open."
    },
    {
      "severity": "P3",
      "evidence_level": "unverified",
      "location": "orders.py:6",
      "scenario": "actor is now required; any caller outside the supplied files that calls cancel_order(db, id) would raise TypeError.",
      "fix": "Search the whole repo for cancel_order callers and update or test them."
    }
  ]
}
```