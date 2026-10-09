# Redteam report: PR #131 (audit record on cancellation)

**Review mode:** no tools and no subagent in this session. I did not write this work, so there is no same-context anchoring. I ran nothing. Every statement about runtime behaviour comes from reading the code.

**VERDICT: SHIP WITH FIXES.** The change does what was asked and its central claim holds. One Medium gap remains: if the status write fails, the audit log keeps a cancellation that never happened, and no test covers that case.

**CONFIDENCE: medium.** Three things limit it:
- I had no tools, so "Tests pass" is unverified.
- The rest of the repository was not supplied, so I cannot confirm `handlers.cancel` is the only caller.
- The DB implementation, its transactions and its concurrency behaviour were not supplied.

## Inputs ledger

| Item | Status | Matters? |
|---|---|---|
| request.md, context.md, PR.md, change.patch | seen | — |
| base/README.md, base/company_audit.py, base/handlers.py, base/orders.py | seen | — |
| Rest of the repository (other `cancel_order` callers) | not supplied | Yes. The signature now has a required `actor`, so any other caller would raise `TypeError`. |
| Real `db` implementation | not supplied | Yes, for the concurrency question and for how `set_status` can fail. |
| Test run output or CI | not supplied | Partly. I checked the tests by reading them and by reasoning through mutations. |

## Coverage

**Scope:** the diff, plus the base files it touches and the audit library.

**Checked:**
- `orders.cancel_order` on every branch: missing, shipped, cancelled, open.
- `handlers.cancel`.
- `company_audit.record`, including the claim that it fsyncs before returning.
- All 5 tests.
- Every claim in PR.md.

**Not checked:**
- Other callers in the full repository (not supplied).
- DB semantics (not supplied).
- Login middleware (out of scope).

**Seats and gate:**
- Local reviewer only. No cross-vendor seats; the depth is standard and none were requested.
- Sensitivity gate passed. There is no personal or confidential data, only invented user ids.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED (traced) | B | orders.py:16-17 (post-patch) | `record("order.cancelled", ...)` runs before `db.set_status`. Nothing compensates if `set_status` raises or the process dies between the two lines. The PR guarantees "never a cancellation without a record" but not the reverse. | The DB write fails (connection drop, constraint, timeout) after the fsynced audit line is written. Support and finance then see `order.cancelled` by user X for an order that is still open. | **Fix:** wrap `set_status` in try/except. On failure, `record("order.cancel_failed", order_id=..., actor=..., error=...)` and re-raise. Alternatively, record an intent event and a completion event. **Reproduction:** add a test with a `FakeDb` whose `set_status` raises `RuntimeError`. Call `cancel_order(db, "o1", actor="alice")`. Expected: no unqualified `order.cancelled` line (or a following failure line). Observed on current code: one `order.cancelled` line and no compensating record. | a✓ b✓ c✗ d✗ |

## Needs validation (no severity)

- **S1: concurrent double cancel.** Two simultaneous requests could both read `status == "open"` (orders.py:9-17) and both write `order.cancelled`. That contradicts "Cancelling an order that is already cancelled … records nothing" under concurrency. This is a check-then-act race; the race on the status itself already existed in base. To settle it: does `db.get_order`/`set_status` run in a row-locked transaction, or is `set_status` a conditional update?
- **S2: other callers.** "The only caller, `handlers.cancel`" holds within the supplied files. As a positive control, searching base/ for `cancel_order` finds handlers.py:7. The full repository was not supplied. To settle it: run `git grep -n cancel_order` at head 8a41c7e, covering scripts, jobs and admin tools.

## Refuted

- **"The tests don't guard the ordering."** Refuted by mutation reasoning. If `record` moves after `set_status`, `test_a_failed_audit_write_leaves_the_order_open` goes red, because `db.set == "cancelled"`. If `record` moves above the `cancelled` check, `test_cancelling_twice_records_once` goes red, because the file exists.
- **"Tests write to the real audit.log because `orders` imported `record` by name."** Refuted. `record` reads the module global `AUDIT_PATH` at call time, so the override in `setUp` takes effect.
- **"PR overstates the fsync."** Refuted. `company_audit.py` calls `f.flush()` and then `os.fsync(f.fileno())` before returning, as the PR claims. Not fsyncing the directory on first file creation is a library concern and is outside the diff.

## What holds up

- The original request is met: an audit record with `actor` set to the signed-in user, written through the shared library.
- Shipped, missing and already-cancelled orders record nothing.
- A failed audit write propagates and leaves the order open. The test confirms this, and it fails as it should under the mutations above.
- The handler passes `request["user"]`, which matches its documented contract.

## Unverified claims

- **"Tests pass."** Confirm by running `python -m unittest tests/test_orders.py` in a scratch copy.
- **"The only caller."** Confirm with the `git grep` in S2.

## Questions for the author

1. Is the DB update atomic or conditional, so that two concurrent cancels cannot both pass the status check?
2. Should a failed `set_status` leave a compensating audit event, or is a stray `order.cancelled` acceptable to finance?

## Decision-maker summary

Safe to merge once F1 is addressed, or once someone explicitly accepts it. That means adding a failure record and a test, then confirming there are no other callers (S2). If it ships as is, a rare DB failure leaves an audit entry claiming a cancellation that did not happen. A concurrent double-click may produce two entries.

## Owner summary

The change correctly records who cancelled an order and refuses to cancel if the record cannot be saved. One gap remains: if saving the cancellation itself fails, the record still says the order was cancelled. A small follow-up fix and a test would close that gap before finance relies on these records.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "full repository (other cancel_order callers)", "status": "not_seen", "matters": true},
    {"item": "real db implementation", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "local-reviewer", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "PR.md", "kind": "document"},
      {"unit": "change.patch", "kind": "file"},
      {"unit": "base/README.md", "kind": "document"},
      {"unit": "base/company_audit.py", "kind": "file"},
      {"unit": "base/handlers.py", "kind": "file"},
      {"unit": "base/orders.py", "kind": "file"},
      {"unit": "orders.py:cancel_order", "kind": "function"},
      {"unit": "handlers.py:cancel", "kind": "function"},
      {"unit": "company_audit.py:record", "kind": "function"},
      {"unit": "tests/test_orders.py", "kind": "file"}
    ],
    "not_checked": [
      {"unit": "rest of repository", "reason": "not_supplied"},
      {"unit": "db implementation", "reason": "not_supplied"},
      {"unit": "running the tests", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "orders.py:16-17 (post-patch)",
     "scenario": "db.set_status raises (or the process dies) after record() has fsynced 'order.cancelled'; the audit trail shows a cancellation by the actor for an order that is still open.",
     "fix": "Wrap set_status in try/except; on failure record 'order.cancel_failed' with order_id, actor and error, then re-raise. Add a test for it.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "FakeDb whose set_status raises RuntimeError; call cancel_order(db, 'o1', actor='alice'); expect no unqualified order.cancelled line (or a following failure line); current code leaves one order.cancelled line and nothing else."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "orders.py:9-17",
     "suspicion": "Two concurrent cancels both read status 'open' and both write order.cancelled.",
     "unresolved_fact": "Whether get_order/set_status run in a row-locked transaction or set_status is a conditional update."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "orders.py:5 (new required actor parameter)",
     "suspicion": "Another caller outside the supplied files would now raise TypeError.",
     "unresolved_fact": "Output of git grep -n cancel_order at head 8a41c7e."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Tests do not guard the record/status ordering.",
     "evidence": "Moving record after set_status fails test_a_failed_audit_write_leaves_the_order_open; moving it above the cancelled check fails test_cancelling_twice_records_once."},
    {"id": "C2", "candidate": "Tests write to the real audit.log because orders imports record by name.",
     "evidence": "record reads the module global AUDIT_PATH at call time; setUp overrides it."},
    {"id": "C3", "candidate": "PR overstates durability of record().",
     "evidence": "company_audit.record calls f.flush() and os.fsync(f.fileno()) before returning."}
  ]
}
```