# Redteam review: PR #131 (audit record on cancellation)

*Single-reviewer pass with no tools. I could not run the code or tests. The work was not written in this conversation, so I have no author anchoring, but no second seat ran.*

**VERDICT: SHIP WITH FIXES.** The change does what was asked: it records who cancelled the order, using the shared library, after the status change. Two Medium weaknesses should be fixed first, and one open question decides whether it works in production at all: what `request["user"]` actually is.

**CONFIDENCE: medium.** Three things limit it:
- I had no tools, so "Tests pass" and every behaviour claim below are read from the code, not run.
- The login middleware, the real `db`, and the rest of the repository were not supplied.

**INPUTS LEDGER**

| Item | Status | Matters? |
|---|---|---|
| request.md, context.md, PR.md, change.patch | Seen | — |
| base/README.md, base/company_audit.py, base/handlers.py, base/orders.py | Seen | — |
| Login middleware (sets `request["user"]`) | Not supplied | **Yes.** Its type decides whether `json.dumps` succeeds (S1). |
| Real `db` implementation and transaction behaviour | Not supplied | **Yes.** It decides whether F1 leaves a committed, unaudited cancellation. |
| Rest of the repository (other callers of `cancel_order`) | Not supplied | **Yes.** The new required `actor` breaks any other caller (S2). |
| Test run output / CI for head 8a41c7e | Not supplied | Moderate. "Tests pass" is unverified. |

**COVERAGE**
- Checked:
  - orders.py:cancel_order (base and patched)
  - handlers.py:cancel (base and patched)
  - company_audit.py:record
  - tests/test_orders.py (all three tests)
  - PR.md claims: only caller, writes and fsyncs before return, tests pass
- Not checked:
  - Middleware
  - db layer
  - Other callers
  - Audit-file consumers (support/finance tooling)
  - Test discovery / CI configuration

**SEATS AND GATE:** Local reviewer only. No cross-vendor seats were requested, and the depth is standard. Sensitivity gate: the code is invented sample code and holds no personal data. The audit record will carry an actor identifier in production (see S1).

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | PROBABLE | B | orders.py (patched) `db.set_status(...)` then `record(...)` | The audit write comes after the status change, and nothing handles its failure. | The audit file is unwritable (disk full, permissions, bad `AUDIT_PATH`), so `record` raises after `set_status`. If `set_status` has already committed, the order is cancelled with no audit record and the caller gets a 500. | Decide the policy explicitly. Either write the audit record inside the same transaction / before commit, or catch the failure and roll back or alert. **Repro:** in a scratch copy, set `company_audit.AUDIT_PATH` to a path in a nonexistent directory and call `cancel_order(FakeDb("open"), "o1", actor="a")`. Observe `FileNotFoundError` with `db.set == "cancelled"`. Expected: either no cancellation or a recorded audit. | a Y, b N (commit semantics unseen), c Y, d N |
| F2 | Medium | CONFIRMED | B | orders.py (patched) status checks | An order that is already cancelled is not refused, so each repeat call writes another `order.cancelled` record. | Alice cancels o1. Later a support agent, Bo, clicks cancel on the same order. The second call succeeds and logs `actor="bo"`, so the trail shows two cancellations, and a consumer reading the latest record attributes the cancellation to Bo. | Return early without recording when `row["status"] == "cancelled"`, or record a distinct event. **Repro:** `db = FakeDb("cancelled"); cancel_order(db, "o1", actor="bo")` returns True and appends a second `order.cancelled` line. Expected: no new cancellation record. | a Y, b Y, c N, d N |
| F3 | Low | CONFIRMED | B | tests/test_orders.py `test_cancel_is_on_disk_before_it_returns`; `setUp` | The test name claims durability, but it only checks that the line is readable after return, which also passes without `fsync`. `setUp` overwrites the global `AUDIT_PATH` and never restores it or removes the temp directory. | Someone removes `os.fsync` from `company_audit.record` and this test stays green. Other test modules that run later inherit the temp `AUDIT_PATH`. | Rename the test to what it asserts, or mock `os.fsync` and assert it was called. Restore `AUDIT_PATH` and clean up in `tearDown`/`addCleanup`. | a Y, b Y, c N, d N |

## NEEDS VALIDATION
- **S1: actor serialization.** `handlers.cancel` passes `request["user"]` straight through. `record` calls `json.dumps(...)` on it, with no `default=`.
  - If the middleware sets a user object, `json.dumps` raises `TypeError` after `set_status`. Every production cancellation would then 500 and go unaudited.
  - If it sets a full user dict, the audit file receives more personal data than "who".
  - The tests use plain strings (`"alice"`, `"bo"`), so they cannot catch either case.
  - *Settles it:* the type and contents of `request["user"]` as set by the login middleware. If it is an object, pass a stable id (e.g. `request["user"].id`).
- **S2: "The only caller, `handlers.cancel`."** `actor` is now a required positional parameter, so any other caller of `cancel_order` will raise `TypeError`. Examples would be an admin tool, a batch job, or a refund flow.
  - *Settles it:* a repository-wide search for `cancel_order`, with a positive control. The same search must find `handlers.py`.
- **S3: "Tests pass."**
  - *Settles it:* the CI log for head 8a41c7e, plus confirmation that `tests/` is actually discovered. The test file has no visible `__init__.py` and imports top-level modules, so a misconfigured discovery could run zero tests and still report success.

## REFUTED
- **"The tests write to the real `audit.log`, because `orders.py` binds `record` at import time."** Refuted. `record` reads the module global `company_audit.AUDIT_PATH` on every call, so setting it in `setUp` takes effect.
- **"A shipped or missing order still writes an audit record."** Refuted. `KeyError` and `ValueError` are raised before `set_status` and `record`. `test_shipped_is_refused_and_not_recorded` asserts the file is absent, and the absence is meaningful because `setUp` creates a fresh empty directory each test.
- **"PR.md misstates the library's durability."** Refuted. `company_audit.record` does call `write`, `flush` and `os.fsync` inside the `with` block before returning, as claimed. The parent directory is not fsynced when the file is first created, but that is a pre-existing library property and outside this PR.

## WHAT HOLDS UP
- **Fits the request.** It uses the shared library, records the event name, the order id and the actor, and writes only after a successful status change.
- **Failure paths stay quiet.** Refused paths (missing order, shipped order) write nothing.
- **The handler is wired correctly.** It passes the signed-in user, and the third test covers that path.
- **The key tests would catch a regression.** Deleting the `record(...)` line would turn tests 1 and 3 red.

## UNVERIFIED CLAIMS
- **"Tests pass"**: confirm with the CI log for 8a41c7e or a local `python -m unittest` from the repo root that reports 3 tests run.
- **"The only caller"**: confirm with a repository-wide search for `cancel_order` (see S2).
- **"Passes the signed-in user"**: true as a value, but whether it serializes is unverified (S1).

## QUESTIONS FOR THE AUTHOR
1. What type is `request["user"]`: a string id, a dict, or an object?
2. Does `db.set_status` commit immediately, or does the request run in a transaction that rolls back on exception?
3. Should cancelling an already-cancelled order be refused, or should it be recorded as a distinct event?

## DECISION-MAKER SUMMARY
The PR does what was asked. Before merging, confirm `request["user"]` serializes to a stable id; if it does not, every real cancellation will fail. Also decide what happens when the audit write fails and when an order is cancelled twice; merging as-is risks unaudited or misattributed cancellations in rare cases.

## OWNER SUMMARY
The change correctly adds a record of who cancelled each order. Before it goes live, someone should check that the "who" value the system passes in can actually be saved. If it cannot, cancellations will start failing. Two smaller gaps should also be closed: a cancellation can go unrecorded if saving the record fails, and cancelling the same order twice creates a second record that can name the wrong person.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "PR.md", "status": "seen", "matters": true},
    {"item": "change.patch", "status": "seen", "matters": true},
    {"item": "base/README.md", "status": "seen", "matters": false},
    {"item": "base/company_audit.py", "status": "seen", "matters": true},
    {"item": "base/handlers.py", "status": "seen", "matters": true},
    {"item": "base/orders.py", "status": "seen", "matters": true},
    {"item": "login middleware (sets request[\"user\"])", "status": "not_seen", "matters": true},
    {"item": "real db implementation / transaction behaviour", "status": "not_seen", "matters": true},
    {"item": "rest of repository (other callers of cancel_order)", "status": "not_seen", "matters": true},
    {"item": "CI / test run output for 8a41c7e", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Invented sample code; no personal or confidential data in the work."},
  "coverage": {
    "checked": [
      {"unit": "PR.md", "kind": "file"},
      {"unit": "change.patch", "kind": "file"},
      {"unit": "base/README.md", "kind": "file"},
      {"unit": "base/company_audit.py", "kind": "file"},
      {"unit": "base/handlers.py", "kind": "file"},
      {"unit": "base/orders.py", "kind": "file"},
      {"unit": "tests/test_orders.py", "kind": "file"},
      {"unit": "orders.py:cancel_order", "kind": "function"},
      {"unit": "handlers.py:cancel", "kind": "function"},
      {"unit": "company_audit.py:record", "kind": "function"},
      {"unit": "PR.md: record writes and fsyncs before it returns", "kind": "claim"},
      {"unit": "PR.md: the only caller is handlers.cancel", "kind": "claim"},
      {"unit": "PR.md: tests pass", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "login middleware", "reason": "not supplied"},
      {"unit": "db layer / transaction semantics", "reason": "not supplied"},
      {"unit": "other callers of cancel_order", "reason": "repository not supplied; no search tools"},
      {"unit": "test execution and discovery", "reason": "no tools in this session"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "orders.py (patched): db.set_status(order_id, \"cancelled\") followed by record(...)",
     "scenario": "The audit file is unwritable, so record() raises after set_status; if set_status already committed, the order is cancelled with no audit record and the caller gets a 500.",
     "fix": "Write the audit record inside the same transaction or before commit, or catch the failure and roll back or alert.",
     "answers": {"a": true, "b": false, "c": true, "d": false},
     "reproduction": "In a scratch copy set company_audit.AUDIT_PATH to a path in a nonexistent directory and call cancel_order(FakeDb(\"open\"), \"o1\", actor=\"a\"); observe FileNotFoundError with db.set == \"cancelled\"; expected no cancellation or a recorded audit."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "orders.py (patched): status checks before db.set_status",
     "scenario": "An order already cancelled by alice is cancelled again by bo; the call succeeds and appends a second order.cancelled record with actor=bo, misattributing the cancellation to anyone reading the latest record.",
     "fix": "Return early without recording when row[\"status\"] == \"cancelled\", or record a distinct event.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "cancel_order(FakeDb(\"cancelled\"), \"o1\", actor=\"bo\") returns True and appends an order.cancelled line; expected no new cancellation record."},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "tests/test_orders.py: test_cancel_is_on_disk_before_it_returns and setUp",
     "scenario": "Removing os.fsync from company_audit.record leaves the test green despite its name; setUp overwrites the global AUDIT_PATH and leaves temp directories behind, so later tests inherit the temp path.",
     "fix": "Rename the test or mock os.fsync and assert it is called; restore AUDIT_PATH and remove the temp directory with addCleanup.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "In a scratch copy delete os.fsync(f.fileno()) from company_audit.record and run the tests; observe all pass."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "handlers.py (patched): request[\"user\"] passed as actor",
     "suspicion": "If the middleware sets a non-JSON-serializable user object, json.dumps raises TypeError after set_status, so every production cancellation fails and is unaudited; a full user dict would also put excess personal data in the audit file.",
     "unresolved_fact": "The type and contents of request[\"user\"] as set by the login middleware."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "orders.py (patched): def cancel_order(db, order_id, actor)",
     "suspicion": "Any caller other than handlers.cancel now raises TypeError because actor is required.",
     "unresolved_fact": "A repository-wide search for cancel_order (with handlers.py as the positive control)."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "PR.md: \"Tests pass.\"",
     "suspicion": "The tests may not run in CI (discovery of tests/ without __init__.py), or may not have been run at head 8a41c7e.",
     "unresolved_fact": "CI log for 8a41c7e showing 3 tests run and passed."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Tests write to the real audit.log because orders.py binds record at import time.",
     "evidence": "record() reads the module global company_audit.AUDIT_PATH on each call, so the setUp assignment takes effect."},
    {"id": "C2", "candidate": "A shipped or missing order still writes an audit record.",
     "evidence": "KeyError and ValueError are raised before set_status and record; test_shipped_is_refused_and_not_recorded checks the absent file in a fresh temp directory."},
    {"id": "C3", "candidate": "PR.md misstates the library's durability.",
     "evidence": "company_audit.record calls write, flush and os.fsync before returning, as claimed."}
  ]
}
```