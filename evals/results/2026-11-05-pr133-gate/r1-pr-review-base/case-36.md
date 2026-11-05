# PR #131 review report

**REVIEWED:** PR #131 "audit record on cancellation", head `8a41c7e`, merge base `2d90b53`. Both SHAs are taken from `PR.md`. I could not check them against a repository. I read the patch, not a checkout, and ran nothing.

**TIER:** Standard. The change touches ordinary application logic and adds an audit write. It does not change auth, permissions, secrets, network exposure, migrations or money movement. The audit trail matters to finance, but it is not a control that moves money. One model round.

**REVIEWERS:** This is a fresh instance with no part in writing the change. Commit trailers were not provided, so the author is unknown (UNVERIFIED). The PR text contains no instructions aimed at the reviewer.

## What I checked
- **Request coverage:** the audit record with `actor` is written on a successful cancel, via `company_audit.record`. The request is met.
- **Audit durability:** `record` flushes and fsyncs before returning, as the PR claims (`base/company_audit.py`).
- **Test patching:** `orders` imports `record` by name, but `record` reads the module-level `AUDIT_PATH` at call time. Tests that set `company_audit.AUDIT_PATH` therefore take effect.
- **Idempotent and refused paths:** already-cancelled and shipped orders return or raise before the `record` call, so nothing is written. This matches the PR.
- **Handler:** `handlers.cancel` passes `request["user"]`, matching the docstring.
- **"Tests pass":** a claim only. I could not run the tests, and no CI status was provided.

## FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `orders.py:16-17` | The audit write succeeds, then `db.set_status` raises (DB outage, lock timeout). The log now says `order.cancelled` by alice, but the order is still open. Support and finance read a cancellation that did not happen. A client retry writes a second record. The docstring guarantees only "no cancellation without a record", not the reverse. | `FakeDb.set_status` raises. Call `cancel_order` and assert the audit log does not claim a completed cancellation (for example it has an `attempted` event plus a `completed` event, or no record). It fails today because one `order.cancelled` line exists. |
| 2 | P2 | `orders.py:9-17` | Check-then-act with no locking. Two concurrent cancels of one open order both read `open`, both pass the checks, and both write `order.cancelled`, possibly with different actors. This breaks "cancelling twice records once", which holds only sequentially. | Fake DB whose `get_order` returns `open` to two interleaved callers, for example with a barrier. Assert exactly one audit line. It fails today with two. |
| 3 | P3 | `tests/test_orders.py` | Gaps in test coverage. There is no test for `set_status` failing after the audit write (finding 1), none for the missing-order `KeyError` path (which should record nothing), and none for a missing or `None` `request["user"]`. The `AUDIT_PATH` patch is never restored after the tests. | Add the missing cases. Restore `AUDIT_PATH` with `addCleanup`. |

Fix suggestions for 1 and 2 are **UNVERIFIED**. I could not see the audit schema, its consumers, or whether `db` offers transactions or row locks.

## Not an issue
- The signature change to a required `actor` is safe if `handlers.cancel` is the only caller, as the PR states. I could only see the provided files.

## FILES NEEDED BUT NOT PROVIDED
- The rest of the repository, to confirm `handlers.cancel` is the only caller of `cancel_order` (jobs, admin scripts).
- The real `db` implementation, for transaction and locking behavior.
- CI results. A missing check is not green.
- Commit trailers, to name the author.

## Close-out (pending)
The author must adjudicate each finding (Accepted with a regression test, Deferred with an issue link for P2/P3, or Rejected with evidence). A reviewer does not adjudicate its own findings.

**MERGE RECOMMENDATION (provisional): merge after fixes.** The change meets the request, and there is no P0 or P1. Open items:
1. The author writes a decision for each of the three findings.
2. CI is shown green.
3. The caller check above is confirmed.

Findings 1 and 2 can be Deferred with tracked issues if the owner accepts the audit-first ordering as a deliberate tradeoff. No written rule in the provided materials settles that question, so it is an owner decision.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "static-read",
      "location": "orders.py:16-17",
      "scenario": "record() succeeds, then db.set_status raises. The audit log shows order.cancelled by the actor while the order stays open, and a retry writes a duplicate record.",
      "fix": "Record an attempted/completed pair, or write the audit entry in the same transaction as the status change. UNVERIFIED against the audit schema and consumers."
    },
    {
      "severity": "P2",
      "evidence_level": "static-read",
      "location": "orders.py:9-17",
      "scenario": "Two concurrent cancels of the same open order both read status open and both write an audit record, so 'records once' fails under concurrency.",
      "fix": "Make the status change a conditional update (open to cancelled) and write the audit record only when it affected a row, or lock the row. UNVERIFIED against the real db."
    },
    {
      "severity": "P3",
      "evidence_level": "static-read",
      "location": "tests/test_orders.py",
      "scenario": "No tests cover set_status failure after the audit write, the missing-order path, or a missing user. AUDIT_PATH is not restored after tests.",
      "fix": "Add those tests and use addCleanup to restore AUDIT_PATH."
    }
  ]
}
```