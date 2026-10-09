# Redteam review: PR #131 (audit record on cancellation)

**VERDICT: SHIP WITH FIXES.** The change does what was asked on the normal path: one record of who cancelled, written durably before the status changes. But a database failure after the audit write leaves a record of a cancellation that never happened, and no test checks that the order's status actually changes.

**CONFIDENCE: medium.** I had no tools, so nothing was run; every finding below comes from tracing the code by hand. The database layer, the login middleware and the rest of the repository were not supplied. The work was not written in this conversation, so I did not inherit the author's reasoning, but this is a single-reviewer pass.

**INPUTS LEDGER**
- **Seen:**
  - request.md, context.md
  - work/PR.md, work/change.patch
  - base/README.md, base/company_audit.py, base/handlers.py, base/orders.py
- **Not seen:**
  - **The real `db` implementation.** This matters: the concurrency and partial-failure behavior depend on it.
  - **The login middleware.** This matters: what `request["user"]` holds for anonymous or service calls.
  - **The rest of the repository.** This matters: the PR says `handlers.cancel` is the only caller, and nothing else should set an order to cancelled.
  - **The head commit 8a41c7e itself** (only the patch). This is a minor gap.
  - **The test or CI output behind "Tests pass".** This matters for the claim only.

**COVERAGE**
- **Scope:** the diff, plus the base files it touches and the audit library.
- **Checked:**
  - Documents: PR.md, README.md, change.patch
  - Functions: `company_audit.record`, `handlers.cancel`, `orders.cancel_order` (before and after)
  - All five tests in tests/test_orders.py
  - Every claim in PR.md
- **Not checked:**
  - db layer and middleware (not supplied)
  - Other callers and other cancellation paths (not supplied)
  - Running the tests (no tools)

**SEATS AND GATE**
- **Seats:** a single local reviewer. No subagent or cross-vendor seats were available because this session has no tools.
- **Sensitivity gate:** passed. The material is invented service code with no personal data or secrets.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED (traced) | B | orders.py:16-17 (patched) | The audit record is written before `db.set_status`, and nothing handles a failure in `set_status`. | `db.set_status` raises (timeout, lost connection, constraint error). The audit log now says "order.cancelled by alice" but the order is still open. Support and finance read a false record. When the user retries, a second `order.cancelled` record is written for the same order. | **Fix:** on an exception from `set_status`, write a compensating `record("order.cancel_failed", ...)` and re-raise. Alternatively, record an attempt plus an outcome, or keep both writes in one transaction. **Repro:** use a FakeDb whose `set_status` raises `RuntimeError` and call `cancel_order(db,"o1",actor="alice")`. Expected: no `order.cancelled` line. Observed by trace: one line, and the order is still open. | a✓ b✓ c✗ d✗ |
| F2 | Low | CONFIRMED (traced) | B | tests/test_orders.py (all tests); orders.py:17 | No test asserts that the status actually changes. `FakeDb.set` is only checked as `None` in the failure test. | A regression that drops or reorders `db.set_status` would leave the order open while still logging a cancellation, and every test would still pass. | **Fix:** add `self.assertEqual(db.set, "cancelled")` to `test_cancel_is_on_disk_before_it_returns`. Also add tests for a `set_status` failure (see F1) and for a missing order (`FakeDb` already supports `"missing"`). **Mutation, by trace and not run:** in a scratch copy, delete orders.py:17 and run the tests; all five still pass. | a✓ b✓ c✗ d✗ |
| F3 | Low | PROBABLE | B | tests/test_orders.py:24-25, 46 | `setUp` overwrites the module global `company_audit.AUDIT_PATH` and never restores it. The last test may leave it pointing at `<tmp>/missing/audit.log`. | Later test modules in the same process that call `record` get `FileNotFoundError` or write into stray temp directories. This depends on test order. | **Fix:** save the old value and restore it in `tearDown`, or use `unittest.mock.patch.object(company_audit, "AUDIT_PATH", ...)`. Also remove the temp directory. **Repro:** run this module before any other test that calls `record()`, with `test_a_failed_audit_write_leaves_the_order_open` last; the next `record()` raises `OSError`. | a✓ b✗ c✗ d✗ |

## Needs validation

These are open suspicions, not findings, and have no severity.

- **S1: other callers of `cancel_order`.** The new required `actor` parameter breaks any other caller with a `TypeError`, and the PR's "only caller" claim is unsupported.
  - To settle: run `grep -rn "cancel_order" .` across the repository, including scripts, jobs and admin tools.
  - A positive control is needed so a zero result means something: the search must return `handlers.py`.
- **S2: concurrent cancels.** Two simultaneous requests (for example a double-click) could both read `open` and both record. That would give two `order.cancelled` lines, possibly with different actors, which contradicts "records nothing" on a repeat.
  - To settle: check whether `db.get_order` and `set_status` run in a transaction with a row lock or a conditional update (`UPDATE ... WHERE status='open'`).
- **S3: other cancellation paths.** The request says "when an order is cancelled", so any path that sets the status to `cancelled` without going through `cancel_order` (bulk admin, timeouts, payment failure) would produce no record.
  - To settle: search the repository for `"cancelled"` and for `set_status(` call sites.
- **S4: "Tests pass".** This is unverified.
  - To settle: run `python -m unittest tests.test_orders` against head 8a41c7e and attach the output.
- **S5: missing or empty actor.** `actor` is not validated. If the middleware can set `request["user"]` to `None` or `""` (anonymous or service tokens), the record says nobody cancelled the order.
  - To settle: check what the login middleware sets when no user is signed in.

## Refuted

- **"The tests' `AUDIT_PATH` override has no effect because orders.py does `from company_audit import record`."** Refuted: `record` reads the module global `AUDIT_PATH` when it is called (company_audit.py, inside `record`), so setting `company_audit.AUDIT_PATH` takes effect.
- **"Shipped or missing orders get an audit record."** Refuted: the `KeyError` and `ValueError` checks (orders.py:10-13) come before `record` at line 16.
- **"The fsync claim in PR.md is false."** Refuted: `record` calls `f.flush()` and then `os.fsync(f.fileno())` before returning.

## What holds up

- Fail-closed ordering: if the audit write fails, the order stays open. This is tested.
- The actor comes from `request["user"]`, which the handler's docstring says the middleware sets.
- Repeat cancels of an already-cancelled order and refused cancels of shipped orders write no record, at least without concurrency.
- The audit library really does flush and fsync each line.
- The diff is minimal and stays on the request.

## Unverified claims

- **"The only caller is `handlers.cancel`."** Confirm with a repository-wide search (S1).
- **"Tests pass."** Confirm with a CI log or a local run (S4).
- **"Records nothing" on a repeat cancel.** This holds only without concurrency; confirm the db locking behavior (S2).

## Questions for the author

1. If `set_status` fails after the record is written, what should the audit log show, and who reconciles it?
2. Does the db serialize concurrent cancels of the same order?
3. Are there other code paths that set an order to `cancelled`?

## Decision-maker summary

Merge after adding a compensating record (or a transaction) for `set_status` failures and a test that asserts the status changes. Also confirm there are no other callers or other cancellation paths. If you merge as is, a database error during cancellation leaves the support and finance audit trail showing cancellations that never happened, and a retry duplicates them.

## Owner summary

The change correctly records who cancelled an order, and it refuses to cancel if the record cannot be saved. If the order database fails at the wrong moment, though, the record can claim a cancellation that never happened. The tests also would not notice if orders stopped actually being cancelled. Both are small fixes before merging.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "work/PR.md", "status": "seen", "matters": true},
    {"item": "work/change.patch", "status": "seen", "matters": true},
    {"item": "work/base/README.md", "status": "seen", "matters": false},
    {"item": "work/base/company_audit.py", "status": "seen", "matters": true},
    {"item": "work/base/handlers.py", "status": "seen", "matters": true},
    {"item": "work/base/orders.py", "status": "seen", "matters": true},
    {"item": "db implementation", "status": "not_seen", "matters": true},
    {"item": "login middleware", "status": "not_seen", "matters": true},
    {"item": "rest of repository (other callers / cancellation paths)", "status": "not_seen", "matters": true},
    {"item": "test run output for 'Tests pass'", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "local-single-reviewer", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "PR.md", "kind": "document"},
      {"unit": "base/README.md", "kind": "document"},
      {"unit": "change.patch", "kind": "file"},
      {"unit": "base/company_audit.py", "kind": "file"},
      {"unit": "base/company_audit.py:record", "kind": "function"},
      {"unit": "base/handlers.py", "kind": "file"},
      {"unit": "base/handlers.py:cancel", "kind": "function"},
      {"unit": "base/orders.py", "kind": "file"},
      {"unit": "orders.py:cancel_order", "kind": "function"},
      {"unit": "tests/test_orders.py", "kind": "file"},
      {"unit": "PR.md claims (ordering, idempotence, only caller, fsync, tests pass)", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "db implementation", "reason": "not_supplied"},
      {"unit": "login middleware", "reason": "not_supplied"},
      {"unit": "other callers and cancellation paths", "reason": "not_supplied"},
      {"unit": "test execution", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "orders.py:16-17 (patched)",
     "scenario": "db.set_status raises after record() succeeded: the audit log says the order was cancelled by the actor while the order stays open; a retry writes a second order.cancelled record.",
     "fix": "On exception from set_status, write a compensating order.cancel_failed record and re-raise, or record attempt plus outcome, or put both writes in one transaction.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "FakeDb whose set_status raises RuntimeError; call cancel_order(db, 'o1', actor='alice'); expected no order.cancelled line, observed (by trace) one line and the order open."},
    {"id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "tests/test_orders.py (all tests); orders.py:17",
     "scenario": "A regression removing db.set_status leaves orders open while logging cancellations, and all five tests still pass.",
     "fix": "Assert db.set == 'cancelled' in the success test; add tests for set_status failure and for a missing order.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "In a scratch copy delete orders.py:17 and run python -m unittest tests.test_orders; expected a failure, observed (by trace, not run) all pass."},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "PROBABLE", "track": "B",
     "location": "tests/test_orders.py:24-25, 46",
     "scenario": "AUDIT_PATH is never restored; later tests in the same process calling record() can hit FileNotFoundError on <tmp>/missing/audit.log.",
     "fix": "Use unittest.mock.patch.object(company_audit, 'AUDIT_PATH', ...) or restore it in tearDown; remove the temp directory.",
     "answers": {"a": true, "b": false, "c": false, "d": false},
     "reproduction": "Run this module with the failed-write test last, then another test calling company_audit.record(); observe OSError."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "orders.py:5 (signature change)",
     "suspicion": "Other callers of cancel_order break with TypeError on the new required actor.",
     "unresolved_fact": "Repository-wide search for cancel_order call sites, with handlers.py as the positive control."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "orders.py:9-17",
     "suspicion": "Concurrent cancels both pass the status check and both record, possibly with different actors.",
     "unresolved_fact": "Whether the db serializes get_order/set_status (row lock or conditional update)."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "repository (not supplied)",
     "suspicion": "Other code paths set status to cancelled without going through cancel_order, so no record is written.",
     "unresolved_fact": "Search for set_status( and 'cancelled' across the repository."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "PR.md 'Tests pass.'",
     "suspicion": "The claim that tests pass is unverified.",
     "unresolved_fact": "Output of python -m unittest tests.test_orders at head 8a41c7e."},
    {"id": "S5", "status": "needs_validation", "track": "B", "location": "handlers.py:7 (patched)",
     "suspicion": "request['user'] may be None or empty for anonymous or service calls, producing a record with no actor.",
     "unresolved_fact": "What the login middleware sets when no user is signed in."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The test AUDIT_PATH override has no effect because orders.py imports record directly.",
     "evidence": "record() reads the module global AUDIT_PATH at call time, so setting company_audit.AUDIT_PATH applies."},
    {"id": "C2", "candidate": "Shipped or missing orders get an audit record.",
     "evidence": "The KeyError and ValueError checks at orders.py:10-13 come before record() at line 16."},
    {"id": "C3", "candidate": "The PR's fsync claim is false.",
     "evidence": "company_audit.record calls f.flush() then os.fsync(f.fileno()) before returning."}
  ]
}
```