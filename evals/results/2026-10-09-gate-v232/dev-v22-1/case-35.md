# Redteam report: PR #131, audit record on cancellation

**No tools in this session.** I could not run the tests, open `company_audit`, or search the repository. Everything below comes from reading the supplied text. This is also a same-context review: anchoring risk; re-run in a fresh session for anything high-stakes.

**VERDICT: SHIP WITH FIXES.** The change does what was asked and fails safe when the audit write fails. Nothing High or Critical is confirmed. But every test stubs the audit library, so whether the real `company_audit.record` takes these arguments and raises on failure is unverified, and the safety argument depends on it.

**CONFIDENCE: low.** Three things limit it: there were no tools, the review is same-context, and the shared library and the rest of the repository were not supplied.

**INPUTS LEDGER**
- **Seen:** `request.md`, `context.md`, `PR.md`, `change.patch`, `base/README.md`, `base/handlers.py`, `base/orders.py`.
- **Not seen: `company_audit` (its signature, error behaviour, and whether it is synchronous).** This matters. The fail-closed claim and the call itself depend on it.
- **Not seen: the rest of the repository.** This matters. "The only caller is `handlers.cancel`" is a zero I cannot check against a positive control. The parameter is now required, so any other caller would crash.
- **Not seen: the login middleware.** This matters a little. The handler now reads `request["user"]`.
- **Not seen: CI or test output.** "Tests pass" is unverified.

**COVERAGE**
- **Checked:**
  - `orders.py:cancel_order` (after the patch)
  - `handlers.py:cancel`
  - `tests/test_orders.py`: all five tests and the stub setup
  - `PR.md` claims
- **Not checked:**
  - `company_audit` (not supplied)
  - other callers (repository not supplied)
  - login middleware (not supplied)
  - DB transaction and locking semantics (not supplied)

**SEATS AND GATE:** Only a local same-context reviewer ran. No subagent or cross-vendor seats were available. Sensitivity gate: nothing sensitive (code only, invented service).

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED | B | `orders.py:16-17` (after patch) | The audit record is written before the status change, so a record can exist for a cancellation that never happened. The PR only guards the other direction. | `record(...)` succeeds, then `db.set_status` raises (DB error or timeout). The order stays open, but an `order.cancelled` record names the actor. Support and finance see a cancellation that did not occur. | Write both in one transaction or use an outbox. Alternatively, on `set_status` failure write a compensating `order.cancel_failed` record and re-raise. **Repro:** a FakeDb whose `set_status` raises `OSError`. Call `cancel_order(db, "o1", actor="a")`. Expected: no `order.cancelled` record. Observed: `calls == [("order.cancelled", …)]` and the order is not cancelled. | a✔ b✔ c✘ d✘ |
| F2 | Medium | PROBABLE | B | `orders.py:9-17` | Check-then-act with no lock: two concurrent cancels both see `open` and both record. | A double-click or client retry sends two requests in parallel. Both read status `open`, both call `record`, and both set `cancelled`. The result is two audit records, which contradicts the PR's claim "records nothing" on a repeat. | Use a conditional update (`UPDATE … WHERE status='open'`, then check the row count) or `SELECT … FOR UPDATE`. Record only if this call won. **Repro:** a FakeDb with a barrier in `get_order` and two threads. Expected: 1 record. Observed: 2. | a✔ b✘ c✘ d✘ |
| F3 | Low | CONFIRMED | B | `tests/test_orders.py:~62-65` | `test_cancelling_twice_records_once` never cancels twice. It cancels an order that is already `cancelled` once and asserts zero records. | The name suggests the open-then-cancelled sequence is covered, so someone may rely on that. It is not tested, and F2 is the untested case. | Rename it, or cancel the same stateful FakeDb twice and assert exactly one record. | a✔ b✔ c✘ d✘ |
| F4 | Low | PROBABLE | B | `tests/test_orders.py:16` | The test installs a `sys.modules["company_audit"]` stub at import time and never removes it. | Another test module imports `orders` first, which binds the real `record`, or later expects the real library. Results then depend on test order. | Use `unittest.mock.patch("orders.record")` per test instead of the global stub. | a✔ b✘ c✘ d✘ |

## NEEDS VALIDATION

- **S1 (`orders.py:2,16`):** All five tests stub `company_audit.record(event, **fields)`, so the real call is untested. **Unresolved:** whether the real library exposes `record` with that signature and these keyword names (`order_id`, `actor`).
- **S2 (`orders.py:16`):** The fail-closed guarantee in the docstring holds only if `record` raises on failure. **Unresolved:** whether the real `record` is synchronous and raises, rather than queueing or swallowing errors.
- **S3 (`orders.py:5`):** `actor` is now a required parameter. **Unresolved:** whether any caller other than `handlers.cancel` exists (jobs, admin scripts, other handlers). Settle it with a repo-wide search for `cancel_order(`, after confirming that the search finds the known caller in `handlers.py`.
- **S4 (`handlers.py:8`):** `request["user"]` raises `KeyError` (a 500 response) if it is absent. **Unresolved:** whether the login middleware guarantees `user` is set on this route, including for service or API-key callers.

## REFUTED

- **R1:** The candidate was that the test for the failed audit write would pass even if the code were wrong. Refuted by reading the code. If `record` moved after `set_status`, `db.set` would be `"cancelled"` and `assertIsNone(db.set)` would fail. The test guards the ordering, though I did not run this mutation.
- **R2:** The candidate was that `from company_audit import record` defeats the stub. Refuted by the import order. The stub is installed before `import orders` (test lines 16-18), so `record` binds to `_record`.

## WHAT HOLDS UP

- The change meets the request: it records who cancelled (`actor` = the signed-in user id) through the shared library.
- Shipped, missing and already-cancelled orders produce no record.
- The audit-first ordering is deliberate and documented, and a test guards it.
- The change is minimal, with no scope creep.

## UNVERIFIED CLAIMS

- "Tests pass": run `python -m unittest discover -s tests` from the repository root.
- "The only caller is `handlers.cancel`": see S3.
- "A failed audit write leaves the order open": true only under S2.

## QUESTIONS FOR THE AUTHOR

1. What is the real signature and failure behaviour of `company_audit.record`, and is it synchronous?
2. Are there other callers of `cancel_order`?
3. Is blocking all cancellations during an audit-library outage an accepted trade-off for support?

## DECISION-MAKER SUMMARY

The PR is sound for the single-request happy path, and nothing serious is confirmed. Before merging, confirm the real audit API (S1/S2) and the "only caller" claim (S3), because the tests cannot show either. The remaining risks are a spurious audit record if the DB write fails after the record (F1), and duplicate records under concurrent cancels (F2).

## OWNER SUMMARY

The change records who cancelled an order and looks correct for normal use. Its tests use a stand-in for the shared audit system, so someone should confirm the real system works the way the code expects before it goes live. In rare cases, such as a database error or two cancels at once, the audit log may show a cancellation that did not happen or show the same one twice.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP WITH FIXES",
  "confidence": "low",
  "inputs_ledger": [
    {"item": "company_audit library", "status": "not_seen", "matters": true},
    {"item": "rest of repository (other callers of cancel_order)", "status": "not_seen", "matters": true},
    {"item": "login middleware", "status": "not_seen", "matters": true},
    {"item": "test/CI output", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "orders.py", "kind": "file"},
      {"unit": "orders.py:cancel_order", "kind": "function"},
      {"unit": "handlers.py", "kind": "file"},
      {"unit": "handlers.py:cancel", "kind": "function"},
      {"unit": "tests/test_orders.py", "kind": "file"},
      {"unit": "PR.md", "kind": "file"},
      {"unit": "README.md", "kind": "file"}
    ],
    "not_checked": [
      {"unit": "company_audit", "reason": "not supplied"},
      {"unit": "other callers of cancel_order", "reason": "repository not supplied; no tools"},
      {"unit": "login middleware", "reason": "not supplied"},
      {"unit": "DB locking/transaction semantics", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "orders.py:16-17",
     "scenario": "record() succeeds, then db.set_status raises; the order stays open but an order.cancelled audit record exists naming the actor.",
     "fix": "Write audit and status in one transaction/outbox, or emit a compensating order.cancel_failed record on set_status failure and re-raise.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "FakeDb whose set_status raises OSError; call cancel_order(db,'o1',actor='a'); expected no order.cancelled record, observed one recorded and order not cancelled."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "orders.py:9-17",
     "scenario": "Two concurrent cancel requests both read status 'open'; both call record() and set_status, producing two audit records.",
     "fix": "Conditional update (UPDATE ... WHERE status='open') or row lock; record only when this call performed the transition.",
     "answers": {"a": true, "b": false, "c": false, "d": false},
     "reproduction": "FakeDb with a barrier in get_order, two threads cancel 'o1'; expected 1 record, observed 2."},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "tests/test_orders.py:62-65 (test_cancelling_twice_records_once)",
     "scenario": "Test never cancels twice; it cancels an already-cancelled order once, so the open-then-repeat sequence is untested.",
     "fix": "Rename, or cancel the same stateful FakeDb twice and assert exactly one record.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Read the test: single call on FakeDb('cancelled')."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "PROBABLE", "track": "B",
     "location": "tests/test_orders.py:16",
     "scenario": "Global sys.modules stub is never removed; if another test imports orders first or needs the real library, results depend on test order.",
     "fix": "Use unittest.mock.patch('orders.record') per test.",
     "answers": {"a": true, "b": false, "c": false, "d": false},
     "reproduction": "Add a test module that imports orders before test_orders and run discovery; the stub is not applied to orders.record."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "orders.py:2,16",
     "suspicion": "Real company_audit.record may not match the stubbed signature record(event, **fields).",
     "unresolved_fact": "The real library's record() signature and accepted field names."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "orders.py:16",
     "suspicion": "Fail-closed guarantee holds only if record() raises synchronously on failure.",
     "unresolved_fact": "Whether company_audit.record is synchronous and propagates write errors."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "orders.py:5",
     "suspicion": "Other callers of cancel_order would break with TypeError on the new required actor.",
     "unresolved_fact": "Repo-wide search for 'cancel_order(' with handlers.py as positive control."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "handlers.py:8",
     "suspicion": "request['user'] raises KeyError (500) if middleware does not set it on this route.",
     "unresolved_fact": "Whether the login middleware always sets request['user'] for POST /orders/<id>/cancel."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "The failed-audit-write test cannot detect wrong ordering.",
     "evidence": "If record moved after set_status, db.set would be 'cancelled' and assertIsNone(db.set) would fail."},
    {"id": "R2", "candidate": "from company_audit import record bypasses the stub.",
     "evidence": "The stub is installed in sys.modules before import orders (test lines 16-18)."}
  ]
}
```