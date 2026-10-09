# Redteam review: PR #131, audit record on cancellation

**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent or tools were available. Nothing was run, so every claim about tests passing is unverified.

**VERDICT: SHIP WITH FIXES.** The change does what was asked and its tests match the code. One confirmed Medium defect remains: a failed database write after a successful audit write leaves a record of a cancellation that never happened. Three open questions should be answered before merge: the real audit library's behaviour, other callers of `cancel_order`, and concurrent cancels.

**CONFIDENCE: medium-low.** Three things limit it:
- `company_audit` was not supplied.
- The rest of the repository was not supplied, so other callers and the dependency manifest could not be checked.
- No tools: nothing was run.

**INPUTS LEDGER**

| Item | Status | Matters? |
|---|---|---|
| request.md, context.md | seen | yes |
| work/PR.md | seen | yes |
| work/change.patch | seen | yes |
| base/README.md, base/handlers.py, base/orders.py | seen | yes |
| `company_audit` (source, docs, signature, failure semantics) | not supplied | **yes**: the PR's core guarantee depends on it |
| Rest of repository (other callers of `cancel_order`, requirements/dependency manifest, other tests) | not supplied | **yes**: the "only caller" claim and the deploy depend on it |
| `db` implementation (transactions, row locking) | not supplied | yes: decides whether concurrent cancels double-record |
| CI output for "tests pass" | not supplied | low: tests stub the library anyway |
| Head 8a41c7e / merge base 2d90b53 | not openable | low |

**COVERAGE**
- **Scope:** the diff in change.patch, read against base/.
- **Checked:**
  - PR.md, change.patch, base/README.md, base/handlers.py, base/orders.py
  - `orders.cancel_order` and `handlers.cancel`
  - all 5 tests
  - the PR's claims: "only caller", "already cancelled records nothing", "failed audit leaves order open", "tests pass"
- **Not checked:**
  - `company_audit`: not supplied.
  - Other callers and the dependency manifest: not supplied.
  - The `db` layer: not supplied.
  - Hidden or zero-width characters: no tools to scan for them.
  - Test execution: no tools.

**SEATS AND GATE**
- Seats: only this same-context reviewer ran. No subagent or cross-vendor seats were available because there are no tools.
- Sensitivity gate: not sensitive. The only names are test fixtures ("alice", "bo").

## Pass 1: Reconstruct

The PR adds a required `actor` to `cancel_order`. The handler passes `request["user"]` as that actor. `company_audit.record("order.cancelled", order_id=…, actor=…)` is called after the not-found, shipped and already-cancelled guards, and before `db.set_status`.

The PR claims three things:
- A failed audit write aborts the cancellation.
- A repeat cancel records nothing.
- The handler is the only caller.

For the PR to be correct, all of the following must be true:
- `record` exists with that keyword signature.
- `record` raises synchronously on failure, rather than queueing or swallowing errors.
- `request["user"]` is always a real user id.
- No other code calls `cancel_order(db, id)`.
- The audit write and the status write cannot diverge in a way that misleads support or finance.

Track: B.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED (traced) | B | change.patch orders.py, new lines `record(...)` then `db.set_status(...)` (orders.py:16-17 after patch); docstring "a cancellation is never made without its record" | The ordering guards only one direction. If `record` succeeds and `db.set_status` then raises, an `order.cancelled` record names an actor for a cancellation that never happened. No compensating record is written and no test covers it. The docstring presents the guarantee as complete. | A DB timeout, dropped connection or constraint error occurs on `set_status` after the audit write. The order stays open, the client gets a 500, and support and finance see an audit trail saying user X cancelled it. A retry then writes a second record. | **Fix:** write both in one transaction or outbox if `company_audit` supports it. Otherwise, catch the `set_status` failure and record `order.cancel_failed` (or similar), then re-raise, and document the residual window. **Reproduction:** add a test with a `FakeDb` whose `set_status` raises `OSError`. Call `orders.cancel_order(db, "o1", actor="alice")`, assert it raises, then assert `calls` holds no unqualified `order.cancelled` record. On the current code `calls == [("order.cancelled", {"order_id": "o1", "actor": "alice"})]`, so the test goes red. | a yes, b yes, c no, d no |

No High or Critical findings. The confirm-or-refute and sibling rounds were therefore not required.

I checked F1 for siblings anyway. There is no other write path in the supplied code.

## NEEDS VALIDATION

- **S1, `company_audit.record` failure semantics** (orders.py import and call). The guarantee "a failed audit write leaves the order open" holds only if `record` raises synchronously. If it buffers, queues asynchronously or swallows errors, cancellations can proceed with no record at all.
  - To settle: the library's documentation or source for `record`, covering whether it raises on write failure and whether it flushes before returning.
- **S2, signature of `record`** (orders.py call site). The stub `_record(event, **fields)` accepts any keyword arguments. If the real function expects different names, for example `actor_id=` or `subject=`, or positional fields, every cancellation fails with `TypeError` in production while the tests stay green.
  - To settle: the real signature of `company_audit.record`.
- **S3, other callers of `cancel_order`** (PR.md: "The only caller, `handlers.cancel`"). `actor` is a new required positional argument. Any other caller, such as an admin script, batch job or another handler, breaks with `TypeError`.
  - To settle: a repository-wide search for `cancel_order`, with a positive control showing the search finds `handlers.py`.
- **S4, concurrent double cancel** (orders.py read-check-write). Two simultaneous requests can both read `open`, both record and both set status. That gives two `order.cancelled` records, possibly naming different actors, which contradicts "cancelling twice records once". The test covers only the sequential case.
  - To settle: whether `db.get_order` and `set_status` run in a transaction with row locking, or whether `set_status` is a conditional update.
- **S5, `company_audit` as a deploy dependency.** The patch adds an import but no dependency declaration. If the package is missing from the service's manifest, the module fails at import time.
  - To settle: the service's requirements or lockfile.
- **S6, `request["user"]` always set** (handlers.py). The docstring says the login middleware sets it. If an unauthenticated route can reach the handler, the actor may be absent (`KeyError`) or a placeholder.
  - To settle: the middleware and route configuration.
- **S7, test module installs the stub in `sys.modules` globally.** This can leak into other test modules that expect the real library.
  - To settle: whether other test files import `company_audit`.

## REFUTED

- **Shipped orders or missing orders might get recorded.** Refuted: `KeyError` and `ValueError` are raised before `record`, in both the code and `test_shipped_is_refused_and_not_recorded`.
- **The audit record might omit who cancelled.** Refuted: `actor=actor` is passed, and the handler supplies `request["user"]`, which the docstring describes as the signed-in user's id. `test_the_handler_passes_the_signed_in_user` asserts it.

## WHAT HOLDS UP

- `record` is placed correctly after all three guards. An already-cancelled order returns `False` with no record, as the PR states.
- An audit failure does propagate, and `set_status` is skipped, provided the library raises (see S1).
- By reading, the tests would go red under the obvious mutations. I could not run them.
  - Removing `record` fails `test_cancel_records_an_audit_event`.
  - Moving `record` after `set_status` fails `test_a_failed_audit_write_leaves_the_order_open`, because `db.set` becomes `"cancelled"`.
  - Passing the wrong actor in the handler fails the handler test.
- The scope is tight: there are no changes beyond what was asked.

## UNVERIFIED CLAIMS

- **"Tests pass."** To confirm, run `python -m unittest discover -s tests` from the repository root in a scratch copy.
- **"The only caller."** See S3.
- **"A failed audit write leaves the order open."** This depends on S1 and S2.

## QUESTIONS FOR THE AUTHOR

1. Does `company_audit.record` raise synchronously on failure, and what is its exact signature?
2. Did you search the whole repository, including scripts and jobs, for `cancel_order`?
3. Is cancellation transactional or row-locked in the database layer?
4. What should the audit trail show when the status write fails after the record was written?

## DECISION-MAKER SUMMARY

Merge after two things:
- The author confirms the audit library raises synchronously with this signature (S1, S2) and that there are no other callers (S3).
- F1 is handled: add a test and a compensating record or a transaction.

If you proceed anyway, the most likely harm is audit records for cancellations that did not happen, or, if the library's signature differs, every cancellation failing in production while CI stays green.

## OWNER SUMMARY

The change correctly records who cancelled an order and skips the record when nothing changes. If the database fails at the wrong moment, the log can say an order was cancelled when it was not. A few facts about the shared logging library and the rest of the codebase still need confirming before this is safe to merge.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP WITH FIXES",
  "confidence": "low",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "work/PR.md", "status": "seen", "matters": true},
    {"item": "work/change.patch", "status": "seen", "matters": true},
    {"item": "work/base/README.md", "status": "seen", "matters": false},
    {"item": "work/base/handlers.py", "status": "seen", "matters": true},
    {"item": "work/base/orders.py", "status": "seen", "matters": true},
    {"item": "company_audit library", "status": "not_seen", "matters": true},
    {"item": "rest of repository (other callers, dependency manifest)", "status": "not_seen", "matters": true},
    {"item": "db implementation", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "only test fixture names"},
  "coverage": {
    "checked": [
      {"unit": "PR.md", "kind": "document"},
      {"unit": "change.patch", "kind": "file"},
      {"unit": "base/README.md", "kind": "document"},
      {"unit": "base/handlers.py", "kind": "file"},
      {"unit": "base/orders.py", "kind": "file"},
      {"unit": "orders.py:cancel_order", "kind": "function"},
      {"unit": "handlers.py:cancel", "kind": "function"},
      {"unit": "tests/test_orders.py", "kind": "file"},
      {"unit": "PR.md: only caller is handlers.cancel", "kind": "claim"},
      {"unit": "PR.md: failed audit write leaves order open", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "company_audit", "reason": "not_supplied"},
      {"unit": "rest of repository", "reason": "not_supplied"},
      {"unit": "db layer", "reason": "not_supplied"},
      {"unit": "test execution and hidden-character scan", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "orders.py:16-17 (after patch): record(...) then db.set_status(...)",
     "scenario": "record succeeds, then db.set_status raises (timeout, dropped connection); the order stays open but the audit trail says the actor cancelled it, and a retry adds a second record.",
     "fix": "Write both atomically (transaction/outbox) or catch the set_status failure, record a cancel-failed event, re-raise; add a test.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Test with FakeDb whose set_status raises OSError; call orders.cancel_order(db, 'o1', actor='alice'); expect no unqualified order.cancelled record; observe calls == [('order.cancelled', {'order_id': 'o1', 'actor': 'alice'})]."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "orders.py: from company_audit import record",
     "suspicion": "If record buffers, queues or swallows errors, cancellations proceed without a record.",
     "unresolved_fact": "Whether company_audit.record raises synchronously on write failure."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "orders.py: record('order.cancelled', order_id=..., actor=...)",
     "suspicion": "The stub accepts any kwargs; a real signature mismatch would fail every cancel in production while tests pass.",
     "unresolved_fact": "The real signature of company_audit.record."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "orders.py: def cancel_order(db, order_id, actor)",
     "suspicion": "Other callers break with TypeError on the new required argument.",
     "unresolved_fact": "Repository-wide search for cancel_order, with a positive control."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "orders.py: get_order / status check / set_status",
     "suspicion": "Concurrent cancels both record, giving duplicate records with possibly different actors.",
     "unresolved_fact": "Whether the db layer locks the row or uses a conditional update."},
    {"id": "S5", "status": "needs_validation", "track": "B", "location": "change.patch: new import with no manifest change",
     "suspicion": "company_audit missing from deploy dependencies causes an ImportError.",
     "unresolved_fact": "The service's requirements or lockfile contents."},
    {"id": "S6", "status": "needs_validation", "track": "B", "location": "handlers.py: request['user']",
     "suspicion": "Actor absent or a placeholder on a route the login middleware does not cover.",
     "unresolved_fact": "Middleware and route configuration."},
    {"id": "S7", "status": "needs_validation", "track": "B", "location": "tests/test_orders.py:15",
     "suspicion": "A global sys.modules stub leaks into other test modules.",
     "unresolved_fact": "Whether other tests import company_audit."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Shipped or missing orders get recorded.",
     "evidence": "KeyError and ValueError are raised before record; test_shipped_is_refused_and_not_recorded asserts calls == []."},
    {"id": "C2", "candidate": "The record omits who cancelled.",
     "evidence": "actor=actor is passed and the handler supplies request['user']; the handler test asserts it."}
  ]
}
```