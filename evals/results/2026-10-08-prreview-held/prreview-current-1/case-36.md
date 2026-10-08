# PR Review: #131, audit record on cancellation

## Review report

**REVIEWED:** PR #131, head `8a41c7e`, merge base `2d90b53`. These SHAs come from PR.md. I have no tools in this session, so I could not check out the head or confirm that `change.patch` matches it. I reviewed the patch as provided against the base files in `work/base/`.

**TIER: Standard.** The change adds an audit write to an ordinary code path. It does not touch authentication, permissions, secrets, network exposure, migrations or money movement, and the context sets the stakes at standard. One open question is for the owner: the audit log now stores a user id. If the owner treats that log as personal-data handling, the tier becomes High and a second round is required before merge.

**REVIEWERS:** One round, by this instance (Claude Opus 5.5, `claude-opus-5-5`). This instance did not write the change. The author is not recorded: no commit trailers were provided, so authorship needs to be read from the commits at `8a41c7e`. All code stayed in this session; nothing was sent to a subagent or another endpoint.

**What checks out (read, not run):**
- **Actor passed through.** `handlers.cancel` passes `request["user"]`, the signed-in user's id per the handler docstring, as `actor`. This matches the request.
- **Audit written before the status change.** The record is written before `db.set_status`. A failed write raises out of `cancel_order` and leaves the order open, and `test_a_failed_audit_write_leaves_the_order_open` covers this. A missing directory raises `FileNotFoundError`, which is an `OSError`, so the test is valid.
- **No record for no-op cases.** Already-cancelled, shipped and missing orders return or raise before `record`, so none of them is recorded.
- **Write and fsync before return.** `company_audit.record` does write and fsync before it returns, as PR.md claims.
- **Tests can redirect the audit path.** `record` reads the module global `AUDIT_PATH` at call time, so the tests' reassignment takes effect even though `orders` imports `record` by name.
- **"Tests pass" is unverified.** I could not run the tests and saw no CI output, so this remains the author's claim.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `orders.py:16` (`record(...)` before `db.set_status(...)`) | The audit write succeeds, then `db.set_status` raises (DB timeout, lost connection). The audit log now says `order.cancelled` with an actor, but the order is still open. Support and finance read the log as the record of cancellations, so it now contains a cancellation that never happened. A retry adds a second record. The PR guarantees "no cancellation without a record" but not the reverse, and no record marks the failed attempt. | Use a `FakeDb` whose `set_status` raises `RuntimeError`. Call `cancel_order(db, "o1", actor="alice")` and expect the `RuntimeError`. Then assert the audit log does not show `o1` as cancelled without a following failure or compensation record, for example an `order.cancel_failed` line. This fails today. |
| 2 | P2 | `orders.py:11-17` (status check, then `record`, then `set_status`, with no lock or conditional update) | Two requests cancel the same open order at the same time: a double-click, or two support agents. Both read `status == "open"`, both write an `order.cancelled` record, possibly with different actors, and both set the status. The log then shows two cancellations of one order and does not say who actually cancelled it. The PR says "cancelling twice records once", which holds only for sequential calls. | Use a `FakeDb` whose `get_order` always returns `{"status": "open"}`, simulating two reads that interleave before either write. Call `cancel_order` twice with actors `"alice"` and `"bo"`. Assert the log holds exactly one `order.cancelled` line for the order. This fails today with two lines. A fix needs a conditional update, for example `set_status_if(order_id, from="open", to="cancelled")` returning whether it changed anything, with the record tied to that result. |

Two items were considered and dropped as findings:
- **Test name overstates its coverage.** `test_cancelling_twice_records_once` never cancels twice; it only checks an already-cancelled order. That is a naming issue, not a failure.
- **Directory not fsynced on file creation.** `company_audit.record` does not fsync the directory when it creates the audit file. That is in the shared library, which this PR does not change, so it is out of scope.

**FILES NEEDED BUT NOT PROVIDED:**
- **Callers of `orders.cancel_order` across the repo.** PR.md says `handlers.cancel` is the only caller. If any other caller exists, the new required `actor` argument makes it fail with `TypeError` at runtime, which would be P1. This needs a repo-wide search at `8a41c7e`.
- **The login middleware.** It is needed to confirm `request["user"]` is always set, and always set to the authenticated id, on this route.
- **CI / test run output at `8a41c7e`.**
- **Commit trailers at `8a41c7e`** for authorship.

## Close-out

Not written by this reviewer. A reviewer never adjudicates its own findings.

**ADJUDICATION:** Pending. Findings 1 and 2 are P2, so the author may accept them (fix with a regression test), defer them (with an issue link) or reject them (with evidence).

**VERIFIED AFTER FIXES:** None yet.

**MERGE RECOMMENDATION:** Merge after adjudication. No P0 or P1 was found. Four things are still open:
1. Written decisions on findings 1 and 2.
2. Green CI at the head SHA.
3. Confirmation that `handlers.cancel` is the only caller of `cancel_order`.
4. The owner's call on whether the audit log counts as personal-data handling. If it does, the tier is High and a second round must run before merge.

```json
{
  "verdict": "merge after adjudication: no blockers found; pending P2 decisions, CI at 8a41c7e, caller check, and owner tier decision",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "code reading (not executed)",
      "location": "orders.py:16",
      "scenario": "Audit record written, then db.set_status raises; the log shows order.cancelled with an actor while the order stays open, and a retry adds a duplicate record.",
      "fix": "On set_status failure, write a compensating record (e.g. order.cancel_failed) before re-raising, or record the outcome together with the status change; add a test with a FakeDb whose set_status raises."
    },
    {
      "severity": "P2",
      "evidence_level": "code reading (not executed)",
      "location": "orders.py:11-17",
      "scenario": "Two concurrent cancels of the same open order both pass the status check and both write order.cancelled, possibly with different actors, leaving two cancellation records for one order.",
      "fix": "Use a conditional update (cancel only if status is open, returning whether it changed) and tie the audit record to that single winning transition; add a test simulating interleaved reads."
    }
  ]
}
```