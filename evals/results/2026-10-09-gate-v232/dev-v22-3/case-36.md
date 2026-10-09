# Redteam review: PR #131 (audit record on cancellation)

**Review conditions:** single reviewer, no subagent and no tools. Nothing was run. Every check below is a reading of the supplied text.

**VERDICT: SHIP WITH FIXES.** The change does what was asked: it uses the shared library and records the signed-in user before the status change. I found no Critical or High defect. Two Medium weaknesses in the audit trail's accuracy should be decided on before merge.

**CONFIDENCE: medium.** It is limited by three things:
- Nothing was run, so "Tests pass" is unverified.
- The real `db` implementation was not supplied.
- The rest of the repository was not supplied, so "the only caller" cannot be checked.

**INPUTS LEDGER**

| Item | Status | Matters? |
|---|---|---|
| request.md, context.md, PR.md, change.patch (incl. tests/test_orders.py), base/README.md, base/company_audit.py, base/handlers.py, base/orders.py | seen | n/a |
| Real `db` implementation (does `get_order` lock, or is there a transaction?) | not seen | yes: it settles F2 |
| Rest of repository (other callers of `cancel_order`, other writers of status `"cancelled"`) | not seen | yes: it settles S1 and S2 |
| Login middleware (can `request["user"]` be missing or None?) | not seen | yes: it settles S3 |
| Test run output for head 8a41c7e | not seen | yes: "Tests pass" is unverified |

**COVERAGE**
- **Checked:** `orders.cancel_order`, `handlers.cancel` and `company_audit.record`, each traced line by line. All five tests were read, and I worked through by hand whether each would go red under a mutation. I also checked every PR.md claim.
- **Not checked:** the db layer, the middleware, the other modules in the repository, and actual execution.

**SEATS AND GATE:** One local reviewer ran. No cross-vendor seats were used: the user did not ask for them and the depth is standard. The sensitivity gate passed; the work contains only invented user ids.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED | B | `orders.py` (patched), `record(...)` then `db.set_status(...)` | Writing the record first prevents unaudited cancellations, but it allows the opposite: an audit record for a cancellation that never happened. The PR states only the first direction, so the cost of the design is not disclosed. | `db.set_status` raises (connection drop, constraint, timeout) after `record` has fsynced. The audit log then says `order.cancelled` by user X, while the order is still open and may later ship. Support and finance see a contradiction. | Choose and document a policy. Options: a compensating `record("order.cancel_failed", ...)` in an `except` around `set_status` that then re-raises, or the same transaction/outbox as the status write. **Repro:** use a FakeDb whose `set_status` raises `RuntimeError`, call `cancel_order(db,"o1",actor="alice")`, then read the audit log. Expected: no `order.cancelled` line, or a matching failure line. Observed (by reading the code): one `order.cancelled` line and nothing else. | a✔ b✔ c✘ d✘ |
| F2 | Medium | PROBABLE | B | `orders.py` read-check-write: `get_order` → status check → `record` → `set_status` | There is no lock or transaction between the status check and the write. Two concurrent cancels can both see `"open"`, and both will write a record. This contradicts the PR's claim that cancelling twice "records nothing". | A double-clicked cancel button, or support and the customer cancelling at the same moment. Two `order.cancelled` records appear, possibly with two different actors, so "who cancelled it" becomes ambiguous. | Make the transition conditional: an atomic `UPDATE ... WHERE status='open'`, or `SELECT ... FOR UPDATE` inside a transaction. Record only if the transition wins, ideally in the same transaction. **Repro:** use a FakeDb whose `get_order` blocks on a barrier until two threads have both read `"open"`, then count audit lines. Expected 1; observed 2. | a✔ b✘ c✘ d✘ |

**Notes on the findings**
- **Why F2 is PROBABLE:** the real db was not seen. If `get_order` locks the row, F2 is refuted.
- **Test name overclaims:** `test_cancelling_twice_records_once` does not cancel twice. It calls `cancel_order` once against an order that is already cancelled, so it cannot catch F2.

## NEEDS VALIDATION
- **S1, other callers.** The PR says `handlers.cancel` is the only caller of `cancel_order`. `actor` is now required and positional, so any other caller (a batch job, an admin tool, a script) would raise `TypeError`.
  - **Settles it:** a repository-wide search for `cancel_order(`, with a positive control: the search must find `handlers.py`.
- **S2, other cancellation paths.** The request is "when an order is cancelled", which covers every path. If other code writes the status `"cancelled"` without going through `cancel_order`, those cancellations go unaudited.
  - **Settles it:** a search for `set_status(` and `"cancelled"` outside `orders.py`, with `orders.py` itself as the positive control.
- **S3, missing user.** `request["user"]` may be absent or None on this route. If it is absent, the handler now fails with `KeyError` before cancelling. If it is None, the record carries `actor: null`, which does not say who cancelled.
  - **Settles it:** whether the login middleware is mandatory on `POST /orders/<id>/cancel` and always sets a non-empty string.

## REFUTED
- **"Patching `company_audit.AUDIT_PATH` in tests has no effect because `orders` imported `record` directly."** Refuted: `record` reads the module global `AUDIT_PATH` at call time, so setting the module attribute redirects the writes.
- **"The PR's fsync claim is false."** Refuted: `company_audit.record` calls `f.flush()` and then `os.fsync(f.fileno())` before returning. A newly created log file's directory entry is not fsynced, but that is a library property outside this PR.

## WHAT HOLDS UP
- **Requirement fit:** the change uses the shared library and records the signed-in user's id as `actor`, as the request asks, and it adds nothing beyond that.
- **Shipped and already-cancelled orders:** in both cases, `cancel_order` returns or raises before `record` runs.
- **Failed audit write:** the error propagates, so the order stays open. `test_a_failed_audit_write_leaves_the_order_open` would go red if `record` were moved after `set_status`. The missing directory raises `FileNotFoundError`, which is a subclass of `OSError`.
- **Mutation check:** deleting the `record` call would turn the first and third tests red. Passing the wrong field from the handler would turn the third test red.

## UNVERIFIED CLAIMS
- **"Tests pass":** settled by running `python -m unittest tests.test_orders` at head 8a41c7e.
- **"The only caller":** settled by the search in S1.

## QUESTIONS FOR THE AUTHOR
1. Does the real db serialise `get_order`/`set_status`, through a row lock or a conditional update?
2. Should a failed status write leave a compensating audit entry?
3. Are there any other code paths that set an order to cancelled?

## DECISION-MAKER SUMMARY
The PR is safe to merge for its stated goal once the db concurrency question (F2) is answered, and once the team has decided how a failed status write should appear in the audit log (F1). If it merges as is, the risk is an occasional phantom or duplicated cancellation record, not a missing one.

## OWNER SUMMARY
The change does what was asked: every cancellation now leaves a record of who did it, and a cancellation cannot happen without one. In rare cases, such as a database error or two people pressing cancel at the same moment, the log could show a cancellation that did not happen or show it twice. It is worth deciding how to handle those cases before relying on the log for finance.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "PR.md", "status": "seen", "matters": true},
    {"item": "change.patch", "status": "seen", "matters": true},
    {"item": "base/company_audit.py", "status": "seen", "matters": true},
    {"item": "base/handlers.py", "status": "seen", "matters": true},
    {"item": "base/orders.py", "status": "seen", "matters": true},
    {"item": "base/README.md", "status": "seen", "matters": false},
    {"item": "real db implementation", "status": "not_seen", "matters": true},
    {"item": "rest of repository (other callers and cancellation paths)", "status": "not_seen", "matters": true},
    {"item": "login middleware", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "local-reviewer", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "PR.md", "kind": "file"},
      {"unit": "change.patch", "kind": "file"},
      {"unit": "tests/test_orders.py", "kind": "file"},
      {"unit": "base/README.md", "kind": "file"},
      {"unit": "base/company_audit.py", "kind": "file"},
      {"unit": "base/handlers.py", "kind": "file"},
      {"unit": "base/orders.py", "kind": "file"},
      {"unit": "orders.py:cancel_order", "kind": "function"},
      {"unit": "handlers.py:cancel", "kind": "function"},
      {"unit": "company_audit.py:record", "kind": "function"},
      {"unit": "PR claim: record fsyncs before return", "kind": "claim"},
      {"unit": "PR claim: failed audit write leaves order open", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "db implementation", "reason": "not supplied"},
      {"unit": "login middleware", "reason": "not supplied"},
      {"unit": "rest of repository", "reason": "not supplied"},
      {"unit": "test execution", "reason": "no tools in this session"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "orders.py (patched): record(...) before db.set_status(...)",
     "scenario": "db.set_status raises after record has fsynced; the audit log shows order.cancelled by the actor while the order stays open.",
     "fix": "Write a compensating audit event on set_status failure and re-raise, or commit the record and status change atomically (same transaction or outbox).",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "FakeDb whose set_status raises RuntimeError; call cancel_order(db, 'o1', actor='alice'); expect no unmatched order.cancelled line, observe one."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "orders.py (patched): get_order -> status check -> record -> set_status",
     "scenario": "Two concurrent cancels both read status 'open'; both write order.cancelled, possibly with different actors.",
     "fix": "Make the open->cancelled transition atomic (conditional UPDATE or row lock) and record only when it wins; add a true double-cancel test.",
     "answers": {"a": true, "b": false, "c": false, "d": false},
     "reproduction": "FakeDb whose get_order waits on a two-party barrier; run cancel_order in two threads; expect 1 audit line, observe 2."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "orders.py:cancel_order signature",
     "suspicion": "Other callers of cancel_order would now raise TypeError because actor is required.",
     "unresolved_fact": "Whether a repo-wide search for 'cancel_order(' (positive control: finds handlers.py) returns any other caller."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "repository (not supplied)",
     "suspicion": "Other code paths may set status 'cancelled' without going through cancel_order, leaving those cancellations unaudited.",
     "unresolved_fact": "Whether any code outside orders.py calls set_status with 'cancelled'."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "handlers.py:cancel request['user']",
     "suspicion": "A missing or None user would fail with KeyError or record actor null.",
     "unresolved_fact": "Whether login middleware is mandatory on this route and always sets a non-empty user id."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Tests' patching of company_audit.AUDIT_PATH does not affect orders.record.",
     "evidence": "record reads the module global AUDIT_PATH at call time, so setting the module attribute redirects writes."},
    {"id": "C2", "candidate": "PR's claim that record fsyncs before returning is false.",
     "evidence": "company_audit.record calls f.flush() then os.fsync(f.fileno()) inside the with block before returning."}
  ]
}
```