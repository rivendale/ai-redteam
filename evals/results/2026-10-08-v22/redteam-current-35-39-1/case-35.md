**Redteam review: PR #131, audit record on cancellation**

*Single reviewer with no tools. Nothing was run, so test results and library behaviour are unverified.*

**VERDICT: SHIP WITH FIXES.** The change does what was asked, but its only evidence that the shared library is called correctly is a stub that accepts any arguments. Two checks and one small guard should happen before merge.

**CONFIDENCE: medium.** Three things limit it: I have no tools, `company_audit` was not supplied, and I saw only the files the patch changes, not the rest of the repository.

**INPUTS LEDGER**
- **Seen:**
  - The original request.
  - `context.md`.
  - `PR.md`.
  - `change.patch`.
  - `base/handlers.py`, `base/orders.py` and `base/README.md`.
- **Not seen:**
  - **`company_audit` source or docs.** This matters: whether `record("order.cancelled", order_id=..., actor=...)` is a valid call depends on it.
  - **The rest of the repository.** This matters: the claim that `handlers.cancel` is the "only caller" depends on it.
  - **The type of `request["user"]` and the login middleware.** This matters somewhat: it decides what actually lands in the audit record.
  - **Whether `db` writes are transactional per request.** This matters for the ordering finding (#3).
  - **Commits 8a41c7e and 2d90b53.** These cannot be checked against the patch. This matters little.
- **Instructions in the work addressed to the reviewer:** none found.

**SEATS AND GATE**
- One reviewer ran: this session, independent of the author.
- No subagent or cross-vendor seats were available.
- Sensitivity gate passed. The work contains invented code with no personal data or credentials.

**FINDINGS**

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Medium | UNVERIFIED | B | `tests/test_orders.py:6`; `orders.py` (`record(...)` call) | The test replaces `company_audit` with `lambda event, **fields`, which accepts any keyword arguments. Nothing in the PR shows the real `record` takes `order_id=` and `actor=`, or takes the event name positionally. | Suppose the real signature differs, for example `record(event, *, subject, actor)` or a required `tenant`. Every cancellation then raises `TypeError` after `set_status` has already run. Users get errors, and orders are cancelled with no audit record. All tests stay green. | Check the call against the library's signature. Better, add one test that imports the real `company_audit` (or uses `create_autospec` on it) so a signature mismatch makes the test fail. | Not a Critical or High finding, so no confirm round was needed. It stays unverified until someone reads the library. |
| 2 | Medium | UNVERIFIED | B | `orders.py` `def cancel_order(db, order_id, actor)`; PR.md "The only caller, `handlers.cancel`" | `actor` is now a required positional argument. The "only caller" claim is backed by no search shown in the PR, and I was given only the changed files. | An admin script, background job or other handler that calls `cancel_order(db, id)` raises `TypeError` at runtime. Python checks arguments only when the call happens, so the failure appears in production rather than at import. | Run `grep -rn "cancel_order" .` across the whole repo. First confirm the search finds `handlers.py`, so you know a zero result is real. Update or list every hit. | — |
| 3 | Medium | CONFIRMED (traced) | B | `orders.py` status checks plus `set_status` then `record` | The function refuses only `shipped` orders. An already-cancelled order passes both checks, is cancelled again, and gets a second audit record naming whoever made the second request. | 1. User A cancels the order. 2. A double-click, client retry, or user B posts cancel again. 3. The audit trail now shows two cancellations with different actors. Support and finance cannot tell who actually cancelled. The same happens when `record` fails after `set_status`: the retry re-cancels and records. | Return early without recording when the status is already `cancelled`, or make the record idempotent per order. Add a test that cancels twice and asserts one audit call. | — |
| 4 | Medium | PROBABLE | B | `orders.py` `db.set_status(...)` followed by `record(...)`, with no error handling | The status write and the audit write are not atomic. If `record` raises or the process dies between the two calls, the order stays cancelled with no audit record, unless `db` rolls back per request, which I could not see. | The audit backend is down. Cancellations still go through and the handler returns 500, but nothing is audited and nothing is retried. | Decide the policy. Either write the audit record inside the same transaction or outbox as the status change, or fail before the status change. Add a test where `record` raises and assert the intended outcome. | — |
| 5 | Low | UNVERIFIED | B/R | `handlers.py` `request["user"]` | It is unclear whether `request["user"]` is a user ID or a whole user object. | If it is an object, the audit record may hold an unserialisable value. It may also copy personal data such as email or name into audit storage, beyond what "who cancelled it" needs. | Pass a stable user ID (for example `request["user"].id`) and add a test asserting the type. | — |
| 6 | Low | CONFIRMED | B | `tests/test_orders.py:5-6` | The stub is installed in `sys.modules` at import time and never removed. | Other test modules in the same run that import `company_audit` get the stub, which can hide failures elsewhere. | Use `unittest.mock.patch.dict(sys.modules, ...)` or patch `orders.record` per test. | — |

**WHAT HOLDS UP**
- **Requirement fit.** The change records who cancelled, through the shared library, only after a successful status change. Shipped orders and missing orders raise before any record is written.
- **Handler.** It passes the signed-in user as the docstring describes.
- **Test strength.** The tests would fail on these mutations, as far as I can trace them by reading:
  - Deleting the `record` call fails test 1.
  - Moving the `record` call above the shipped check fails test 2.
  - Passing the wrong user from the handler fails test 3.
- **Untested cases.** Ordering relative to `set_status`, the missing-order path, and failure of the audit call are not tested.

**UNVERIFIED CLAIMS**
- **"Tests pass."** To confirm, run `python -m unittest discover` from the repo root.
- **"The only caller."** To confirm, run a repo-wide search with a positive control.
- **The call shape matches `company_audit.record`.** To confirm, read the library or run an autospec or contract test.
- **The patch equals head 8a41c7e.** To confirm, diff the actual commit.

**QUESTIONS FOR THE AUTHOR**
1. What is the real signature of `company_audit.record`, and does it require any other fields such as a tenant or source?
2. Did you search the whole repo for `cancel_order`, and what did the search return?
3. Should cancelling an already-cancelled order be a no-op, and should an audit failure block the cancellation?

**DECISION-MAKER SUMMARY:** The change does what was asked, but nothing in the PR proves it calls the real audit library correctly or that no other code calls `cancel_order`. Both are quick to check. Merge after those two checks plus a guard against double-cancellation, which would otherwise put misleading duplicate entries in the audit trail. Proceeding as is risks cancellations that error out or go unaudited if the library's call shape differs.

**OWNER SUMMARY:** The change adds a record of who cancelled each order, which is what was asked. Before it goes live, someone should confirm it talks to the shared audit system the way that system expects, and that nothing else in the codebase breaks because of it. A small fix is also needed so an order cancelled twice doesn't show two different people as the canceller.

```json
{
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "company_audit library", "status": "not_seen", "matters": true},
    {"item": "rest of repository (other callers)", "status": "not_seen", "matters": true},
    {"item": "type of request['user'] / login middleware", "status": "not_seen", "matters": true},
    {"item": "db transaction semantics", "status": "not_seen", "matters": true},
    {"item": "commits 8a41c7e / 2d90b53", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "invented code, no personal data or credentials"},
  "findings": [
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "track": "B", "location": "tests/test_orders.py:6; orders.py record(...) call",
     "scenario": "Test stub accepts any kwargs; if the real company_audit.record signature differs, every cancellation raises TypeError after set_status, leaving orders cancelled without audit while tests stay green.",
     "fix": "Verify against the library's signature; add an autospec/contract test against the real module.", "status": "open"},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "track": "B", "location": "orders.py def cancel_order(db, order_id, actor); PR.md 'only caller'",
     "scenario": "Any unseen caller using cancel_order(db, id) fails with TypeError at runtime.",
     "fix": "Repo-wide grep for cancel_order with a positive control (must find handlers.py); update all callers.", "status": "open"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "B", "location": "orders.py status checks before set_status/record",
     "scenario": "Already-cancelled order passes checks; a retry or second user re-cancels and writes a second audit record with a different actor, corrupting 'who cancelled'.",
     "fix": "No-op without recording when status is already 'cancelled'; test that cancelling twice records once.", "status": "open"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "B", "location": "orders.py db.set_status then record",
     "scenario": "If record raises or the process dies between the writes, the order is cancelled with no audit record (unless db rolls back per request).",
     "fix": "Same transaction/outbox, or define fail-closed policy; test with record raising.", "status": "open"},
    {"severity": "Low", "evidence_level": "UNVERIFIED", "track": "B", "location": "handlers.py request['user']",
     "scenario": "If request['user'] is a full user object, the audit record may be unserialisable or copy personal data beyond the actor identity.",
     "fix": "Pass a stable user id; assert its type in the handler test.", "status": "open"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "B", "location": "tests/test_orders.py:5-6",
     "scenario": "Global sys.modules stub leaks into other test modules in the same run, masking failures elsewhere.",
     "fix": "Use mock.patch.dict(sys.modules, ...) or patch orders.record per test.", "status": "open"}
  ]
}
```