# Redteam review: PR #131, audit record on cancellation

**VERDICT: SHIP WITH FIXES.** The change does what was asked on the main path, but re-cancelling an already-cancelled order now writes a second audit record naming the wrong person. One open question, the type of `request["user"]`, could turn this into REWORK.

**CONFIDENCE: medium.** No tools were available, so nothing was run and "Tests pass" is unverified. The login middleware and the rest of the repository were not supplied. This was a single reviewer, not a fresh subagent, although the work was not written in this conversation.

**INPUTS LEDGER**
- **Seen:** request.md, context.md, PR.md, change.patch, base/README.md, base/company_audit.py, base/handlers.py, base/orders.py.
- **Not seen: login middleware.** This matters, because it decides what `request["user"]` contains (see S1, S2).
- **Not seen: the rest of the repository.** This matters for the claim that `handlers.cancel` is the only caller (S3).
- **Not seen: real DB adapter.** This matters for whether `set_status` commits on its own (F2).
- **Not seen: commits 8a41c7e and 2d90b53, and CI output.** I could not confirm that the patch matches the PR head or that the tests pass.

**COVERAGE**
- **Checked:** `orders.cancel_order`, `handlers.cancel`, `company_audit.record`, `tests/test_orders.py` (all three tests), and PR.md's claims about fsync, the only caller, and tests passing.
- **Not checked:** the middleware, other callers, the DB layer, test execution, and the PR head commit.

**SEATS AND GATE:** I reviewed it myself with no tools; no cross-vendor seats. Sensitivity: no personal data, credentials or client material in the work, so the gate passed. S2 notes that the audit line may later carry user data.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED | B | orders.py:9-12 (post-patch) | Only `"shipped"` is refused, so an order that is already `"cancelled"` goes through `set_status` and `record` again. | User A cancels. A retry, a double-click, or user B cancels the same order again. The audit trail then holds two `order.cancelled` lines, and the second names B as the canceller. Support or finance reading "who cancelled it" get the wrong or an ambiguous answer. | Either return early without recording when `row["status"] == "cancelled"`, or record a distinct event. **Repro:** `db=FakeDb("cancelled")`, call `cancel_order(db,"o1",actor="bo")`. Expected: no audit line. Observed: a line with `actor="bo"`. | a Y, b Y, c N (the first record is still there), d N (how often re-cancels happen is unknown) |
| F2 | Low | CONFIRMED | B | orders.py:11-12 | The audit write happens after the status change, with no transaction or compensation. | The audit file cannot be written (disk full, permissions, bad `AUDIT_PATH`). `record` raises after `set_status` has run, so the order is cancelled with no audit record. The client gets an error; a retry would record it, but only if someone retries. | Make the two writes consistent: record inside the DB transaction, or catch the error, log it loudly and alert. **Repro:** set `company_audit.AUDIT_PATH` to an unwritable path and call `cancel_order` with an open order. Observed: `db.set=="cancelled"` and `OSError` raised. | a Y, b Y, c N (the failure is loud, not silent), d N |
| F3 | Low | CONFIRMED | B | tests/test_orders.py:27 | `test_cancel_is_on_disk_before_it_returns` only reads the file back. It would pass without `flush` or `fsync`, so the test name claims more than it checks. The `KeyError` (missing order) path also has no "not recorded" test, even though `FakeDb` supports `"missing"`. | A later edit drops the fsync, or records before the existence check, and the tests stay green. | Rename the test or patch `os.fsync` to assert it is called. Add `test_missing_is_not_recorded`. | a Y, b Y, c N, d N |

## Needs validation (no severity)

- **S1:** Can `request["user"]` be serialized by `json.dumps`? Unresolved fact: what type the login middleware stores there. If it is a User object, `record` raises `TypeError` after `set_status`. Every real cancellation would then return an error and write no audit record, while the tests stay green because they pass the string `"bo"`. This one would be High or worse.
- **S2:** If `request["user"]` is a dict holding email or name, that personal data goes into the plain audit log. Unresolved fact: the user representation, and whether the audit log is approved to hold it.
- **S3:** Is `handlers.cancel` really the only caller? `actor` has no default, so any other caller (an admin tool, a batch job, a webhook) will now raise `TypeError`. Unresolved fact: a repository-wide search for `cancel_order(`, with a positive control showing the search finds `handlers.py`.
- **S4:** Are there routes where the middleware leaves `request["user"]` unset, such as service tokens? Unresolved fact: the middleware code. On those routes the handler would now raise `KeyError`, where before it cancelled.
- **S5:** "Tests pass." Unresolved fact: the CI log for 8a41c7e. Also, the tests import `handlers`, `orders` and `company_audit` from the repository root, so whether they run depends on how the runner sets `sys.path`.

## Refuted

- **R1:** "Patching `company_audit.AUDIT_PATH` will not reach `record` because `orders` imported the function." Refuted: `record` looks up the module-global `AUDIT_PATH` at call time (company_audit.py, inside `open(AUDIT_PATH, "a")`), so the test's override takes effect.
- **R2:** "The PR's fsync claim is false." Refuted: company_audit.py calls `write`, then `flush`, then `os.fsync(f.fileno())` before returning.

## What holds up

- The main path matches the request. A successful cancel records `order.cancelled` with `order_id` and `actor` through the shared library.
- The record comes after the shipped and missing-order checks, so refused cancels are not recorded. The shipped case is tested.
- The handler takes the actor from the server-side login context, not from the request body, so a client cannot choose the actor.
- The library's durability claim matches its code.

## Unverified claims

- **"The only caller":** settle with a repository-wide search (S3).
- **"Tests pass":** settle with the CI log or a local run at 8a41c7e.
- **Patch equals head 8a41c7e:** settle with `git diff 2d90b53 8a41c7e`.

## Questions for the author

1. What exactly does the middleware put in `request["user"]`: an ID string, an object, or a dict?
2. Should re-cancelling an already-cancelled order be a no-op, an error, or a separately audited event?
3. Are there any other callers of `cancel_order` outside `handlers.py`?

## Decision-maker summary

Merge after fixing duplicate records on re-cancel (F1) and after the author confirms that `request["user"]` is a plain, serializable ID (S1). If S1 is wrong, every real cancellation errors out with no audit record, and the tests would not catch it.

## Owner summary

The change adds a record of who cancelled each order, and it works in the normal case. One gap needs fixing: if someone cancels an order that is already cancelled, the record wrongly names them as the canceller. Before merging, the team should also confirm what the "signed-in user" value looks like, because one kind of value would make every cancellation fail.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "login middleware (sets request[\"user\"])", "status": "not_seen", "matters": true},
    {"item": "rest of repository (other cancel_order callers)", "status": "not_seen", "matters": true},
    {"item": "real DB adapter", "status": "not_seen", "matters": true},
    {"item": "commits 8a41c7e / 2d90b53 and CI output", "status": "not_seen", "matters": true},
    {"item": "work/change.patch and work/base/*", "status": "seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-self", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "No personal data, credentials or client material in the work."},
  "coverage": {
    "checked": [
      {"unit": "PR.md", "kind": "file"},
      {"unit": "change.patch", "kind": "file"},
      {"unit": "base/README.md", "kind": "file"},
      {"unit": "base/orders.py", "kind": "file"},
      {"unit": "base/orders.py:cancel_order", "kind": "function"},
      {"unit": "base/handlers.py", "kind": "file"},
      {"unit": "base/handlers.py:cancel", "kind": "function"},
      {"unit": "base/company_audit.py", "kind": "file"},
      {"unit": "base/company_audit.py:record", "kind": "function"},
      {"unit": "tests/test_orders.py", "kind": "file"},
      {"unit": "PR claim: record() fsyncs before returning", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "login middleware", "reason": "not supplied"},
      {"unit": "other callers of cancel_order", "reason": "repository not supplied; no tools to search"},
      {"unit": "PR claim: tests pass", "reason": "no tools to run tests; CI output not supplied"},
      {"unit": "PR claim: handlers.cancel is the only caller", "reason": "repository not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "orders.py:9-12 (post-patch)",
     "scenario": "An order already in status cancelled is cancelled again (retry, double-click, or a second user); set_status and record run again, writing a second order.cancelled line naming the second user as the canceller.",
     "fix": "Return early without recording when row[\"status\"] == \"cancelled\", or record a distinct event; add a test.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "cancel_order(FakeDb(\"cancelled\"), \"o1\", actor=\"bo\"); expected no audit line, observed one with actor bo."},
    {"id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "orders.py:11-12 (post-patch)",
     "scenario": "The audit file is unwritable; record raises after set_status, leaving the order cancelled with no audit record unless the client retries.",
     "fix": "Make status change and audit write consistent (same transaction, or catch, log and alert on audit failure).",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Point company_audit.AUDIT_PATH at an unwritable path, cancel an open order; observe db.set == \"cancelled\" and OSError raised."},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "tests/test_orders.py:27",
     "scenario": "The test named on_disk_before_it_returns passes without flush or fsync, and the missing-order path has no not-recorded test, so regressions there stay green.",
     "fix": "Assert os.fsync is called (mock it) or rename the test; add test_missing_is_not_recorded.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Remove os.fsync from record(); the test still passes."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "handlers.py:7 (post-patch)",
     "suspicion": "If request[\"user\"] is a non-JSON-serializable object, json.dumps raises TypeError after set_status on every real cancellation; the tests pass a string and would not catch it.",
     "unresolved_fact": "The type the login middleware stores in request[\"user\"]."},
    {"id": "S2", "status": "needs_validation", "track": "R", "location": "handlers.py:7 (post-patch)",
     "suspicion": "If request[\"user\"] is a dict or object holding email or name, personal data goes into the plain audit log.",
     "unresolved_fact": "The user representation, and whether the audit log is approved to hold personal data."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "orders.py:5 (post-patch)",
     "suspicion": "actor is required with no default; any caller other than handlers.cancel now raises TypeError.",
     "unresolved_fact": "A repository-wide search for cancel_order( with a positive control that finds handlers.py."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "handlers.py:7 (post-patch)",
     "suspicion": "Routes where the middleware leaves request[\"user\"] unset now raise KeyError where they previously cancelled.",
     "unresolved_fact": "Whether the middleware always sets request[\"user\"] on this route."},
    {"id": "S5", "status": "needs_validation", "track": "B", "location": "PR.md: \"Tests pass.\"",
     "suspicion": "The pass claim is unverified, and the test imports depend on the runner's sys.path.",
     "unresolved_fact": "The CI log or a local run at 8a41c7e."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Overriding company_audit.AUDIT_PATH in tests does not reach the imported record().",
     "evidence": "record() looks up the module-global AUDIT_PATH at call time inside open(AUDIT_PATH, \"a\")."},
    {"id": "R2", "candidate": "PR.md's claim that record() fsyncs before returning is false.",
     "evidence": "company_audit.py calls f.write, f.flush, then os.fsync(f.fileno()) inside the with block before returning."}
  ]
}
```