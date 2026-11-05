# PR #131 review report

**REVIEWED:** PR #131 "audit record on cancellation", head `8a41c7e`, merge base `2d90b53`. These SHAs are taken from PR.md. I had no git checkout, so I could not confirm that `change.patch` is exactly the diff between them. I read the patch and the base files in `work/base/`.

**TIER:** Standard. The change adds a call to a shared audit library inside an ordinary code path. It does not touch authentication, permissions, secrets, network exposure, migrations or money movement. The actor is a user id, which I treated as ordinary data. One model round applies.

**REVIEWERS:** This is a fresh instance (Claude Sonnet 5.5) with no part in writing the change. The commit trailers were not provided, so I cannot say who wrote it (FILES NEEDED below). No code left this session.

**What I checked**
- **Audit write order:** `record(...)` is called at `orders.py:16`, before `db.set_status` at line 17. This matches the PR text.
- **Durability:** `company_audit.record` flushes and fsyncs before returning (`base/company_audit.py`). The PR's claim is verified.
- **Already-cancelled and shipped paths:** both return or raise before `record`, so neither writes an audit line.
- **Callers:** the handler now passes `request["user"]`. "The only caller is `handlers.cancel`" is unverified, because I only have the files in `work/base/`.
- **Tests:** "Tests pass" is a claim. I could not run them and no CI status was provided.
- **Instructions in the PR text:** none address the reviewer.
- **Scope against the request:** the change does what was asked and nothing extra.

## FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `orders.py:16-17` | The audit line is written and fsynced, then `db.set_status` raises (DB outage, connection drop). The order stays open, but the permanent log says `order.cancelled` by `actor`. Finance and support then see a cancellation that never happened. A retry writes a second `order.cancelled` line. The docstring promises only "never a cancellation without its record", and the reverse case (a record without a cancellation) is unhandled and untested. | Use a `FakeDb` whose `set_status` raises. Cancel, then retry with a working DB. Assert the log has exactly one `order.cancelled` line for the order, or that the first attempt wrote a distinct "attempted" event. It fails today with two identical lines. |
| 2 | P2 | `orders.py:9-17` | Two concurrent requests both read status `open`, both pass the checks, and both write `order.cancelled`. The log holds two cancellations for one order. The "cancelling twice records once" test is sequential only. Whether the DB layer serializes this is unknown. | Run two `cancel_order` calls against a shared `FakeDb` with a barrier between `get_order` and `set_status`. Assert one audit line. It fails today. The real fix needs an atomic conditional status update, so confirm the DB semantics first. |
| 3 | P3 | `tests/test_orders.py` (`test_cancel_is_on_disk_before_it_returns`; `setUp`) | The test name claims durability and ordering, but it only reads the file back after `cancel_order` returns. It would pass if `record` were moved after `set_status`, or if the fsync were removed. `setUp` also overwrites the global `company_audit.AUDIT_PATH` and never restores it, so the temp path leaks into other test modules in the same process. | Make `FakeDb.set_status` assert that the audit file already contains the line when it is called. Restore `AUDIT_PATH` in `addCleanup`. |
| 4 | P3 | `handlers.py:8` | When the audit write fails, `OSError` propagates out of `cancel` and the client gets an unhandled 500. The order stays open, which is correct fail-closed behavior, but the failure is not mapped or logged as an audit failure. This is also untested at handler level. | Call `handlers.cancel` with an unwritable `AUDIT_PATH` and assert the intended response (for example 503) and that the order is still open. |

Missing-order (`KeyError`) behavior is unchanged and untested. I did not count it as a finding.

**FILES NEEDED BUT NOT PROVIDED:**
- Commit trailers (`Co-Authored-By`) for authorship.
- The DB layer (`db.get_order` and `db.set_status`), to judge finding 2.
- Any other callers of `cancel_order`.
- CI results for the head.

## Close-out

Not yet written. A reviewer does not adjudicate its own findings. The author must give each of #1-#4 a decision under Step 7.

**ADJUDICATION:** pending.

**VERIFIED AFTER FIXES:** none yet. Any fix commit needs a targeted read of its diff and a regression test that fails without it.

**MERGE RECOMMENDATION:** merge after fixes. No finding is P0 or P1, so #1-#3 can be fixed or deferred with tracking issues. No written rule covers this case, so I cite none.

Still open before merge:
- Written decisions on all four findings.
- Green CI evidence for the head. "Tests pass" is currently an unverified claim.
- An owner decision on the audit-before-status design (#1). The PR chose fail-closed deliberately, but it produces phantom records. It could instead record an "attempted" event, or write the audit line in the same transaction as the status change.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "code-read",
      "location": "orders.py:16-17",
      "scenario": "record() succeeds and fsyncs, then db.set_status raises; the order stays open but the audit log permanently says order.cancelled, and a retry writes a duplicate line.",
      "fix": "Write the audit in the same transaction as the status change, or record an 'attempted' event and a separate 'cancelled' event after success; add a test with a set_status that raises."
    },
    {
      "severity": "P2",
      "evidence_level": "inferred (DB semantics not provided)",
      "location": "orders.py:9-17",
      "scenario": "Two concurrent cancels both read status 'open', both call record(), producing two order.cancelled lines for one order; the 'twice records once' test is sequential only.",
      "fix": "Use an atomic conditional update (set status where status='open') and record only when it changes a row; add a concurrent test."
    },
    {
      "severity": "P3",
      "evidence_level": "code-read",
      "location": "tests/test_orders.py:setUp, test_cancel_is_on_disk_before_it_returns",
      "scenario": "The test does not verify audit-before-status ordering or the fsync, so it passes if record() is moved after set_status; setUp leaks a modified AUDIT_PATH global across tests.",
      "fix": "Assert in FakeDb.set_status that the audit line already exists; restore AUDIT_PATH with addCleanup."
    },
    {
      "severity": "P3",
      "evidence_level": "code-read",
      "location": "handlers.py:8",
      "scenario": "An audit write failure raises OSError out of the handler as an unhandled 500 with no audit-specific mapping or test.",
      "fix": "Map the failure to a deliberate response (e.g. 503), log it, and add a handler-level test."
    }
  ]
}
```