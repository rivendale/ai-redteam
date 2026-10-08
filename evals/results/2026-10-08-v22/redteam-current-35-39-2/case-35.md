# Redteam review: PR #131, audit record on cancellation

**VERDICT: SHIP WITH FIXES.** The change does what was asked, but it relies on two things nobody has checked: the real `company_audit.record` signature and the claim that `handlers.cancel` is the only caller. It also writes the audit record in a way that can leave a cancelled order without one.

**CONFIDENCE: medium.** I had no tools, so nothing was run or searched. `company_audit` was not provided, and I only saw the files the patch changes, not the whole repo. This was a single reviewer that did not write the work, so there is no shared-context anchoring.

**INPUTS LEDGER**
- **Seen:** request.md, context.md, PR.md, base/README.md, base/handlers.py, base/orders.py, change.patch (including the new tests/test_orders.py).
- **Not seen: the `company_audit` library** (signature, failure behaviour, accepted field types). **This matters.** The tests stub it, so nothing shows the real call works.
- **Not seen: the rest of the repository.** **This matters.** The claim that this is "the only caller" of `cancel_order` cannot be checked with a search, and with no positive control a "no other callers" result would mean nothing anyway.
- **Not seen: CI output for head 8a41c7e.** This matters little, because passing tests against a stub do not show the change is correct.
- **Not seen: the login middleware**, which defines what `request["user"]` contains. **This matters** for what ends up in the audit record.

**SEATS AND GATE:** One local reviewer ran; no subagent or cross-vendor seats were available. The sensitivity check passed: this is invented service code with no personal or confidential data.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | High | UNVERIFIED | B | orders.py (patched) `record("order.cancelled", order_id=order_id, actor=actor)`; tests/test_orders.py:6 | The call shape is assumed, not taken from the library. The test stub `record(event, **fields)` accepts any keyword arguments, so the test was written to match the assumption. | Suppose the real `record` needs different arguments (for example `resource=`, `actor_id=`, a required `source`, or a non-string actor). Then every cancellation raises `TypeError` after `set_status` has already run. The order is cancelled, no audit record is written, and the client gets a 500. | Quote the real `company_audit.record` signature in the PR. Add one integration test against the real library, or its test double if one is published. | confirmed: the PR itself says "they stub the library", and nothing ties the call to the real API |
| 2 | High | UNVERIFIED | B | orders.py (patched) `def cancel_order(db, order_id, actor)`; PR.md "The only caller, `handlers.cancel`" | `actor` is a new required positional argument. Any other caller breaks, and only the changed files were supplied, so the "only caller" claim cannot be checked. | Suppose a batch job, admin tool or other module calls `cancel_order(db, id)`. After merge it raises `TypeError` and those cancellations stop working, possibly unnoticed if the job swallows errors. | Run a repo-wide search for `cancel_order`, with a positive control (the search must find `handlers.py`), and record the result in the PR. Alternatively, accept `actor` as keyword-only and fail with a clear message. | confirmed as an open gap; the risk is real but the evidence is UNVERIFIED |
| 3 | Medium | CONFIRMED | B | orders.py (patched), `set_status` followed by `record` | The status change and the audit write are not atomic, and the audit write happens second. | `record` fails (network, library outage). The order is already cancelled with no audit record, and the 500 tells the client it was not. Support and finance then see a cancellation with no recorded actor. | Decide the policy: audit before the status change, write both in one transaction or outbox, or catch the failure and enqueue a retry. Add a test where `record` raises. | n/a |
| 4 | Medium | CONFIRMED | B | orders.py `cancel_order`: there is no `status == "cancelled"` check | Cancelling an already-cancelled order succeeds again, so it now writes a second audit record. | A user double-clicks, or retries after finding 3. Two `order.cancelled` records appear, possibly with different actors, so "who cancelled it" becomes ambiguous for finance. | Return early, without recording, when the order is already cancelled, or have the second attempt raise. Add a test. | n/a |
| 5 | Medium | UNVERIFIED | B / R | handlers.py (patched) `request["user"]` | The whole "signed-in user" value is passed as the actor, and its type is unknown. | If it is a user object, the audit record may fail to serialize (finding 1 then applies), or it may store more personal data than the audit needs, such as email or name. | Pass a stable identifier such as `request["user"].id`, confirmed against the middleware, and assert that type in the handler test. | n/a |
| 6 | Low | CONFIRMED | B | tests/test_orders.py:6 | The test overwrites `sys.modules["company_audit"]` at import time and never restores it. | Other test modules collected in the same run get the stub instead of the real library, which can hide failures elsewhere. | Use `unittest.mock.patch.dict(sys.modules, ...)` in `setUp` or a fixture. | n/a |
| 7 | Low | CONFIRMED | B | tests/test_orders.py:16 | `FakeDb` supports `"missing"`, but no test checks that a missing order raises `KeyError` and writes no record. | A later refactor that moves `record` earlier would write audit records for orders that do not exist, and no test would catch it. | Add `test_missing_is_not_recorded`. | n/a |

## What holds up
- **Placement:** the `record` call comes after the shipped and missing guards, so refused cancellations are not audited. The test for shipped orders covers this.
- **Handler:** it passes the signed-in user from the middleware-set field described in the docstring, not anything taken from the request body, so the actor cannot be forged by the client.
- **Scope:** the change stays within the request: an audit record of who cancelled, made through the shared library. There is no drift.
- **Test strength, reasoned rather than run:** deleting the `record` line should fail test 1, and moving it above the shipped guard should fail test 2. I am treating this as PROBABLE because I could not run a mutation check.

## Unverified claims
- **"Tests pass":** settle it with the CI log for 8a41c7e.
- **"The only caller":** settle it with a repo-wide search that has a positive control.
- **That `record(event, **fields)` matches the library:** settle it with the library source or docs.

## Questions for the author
1. What is the real signature of `company_audit.record`, and what does it raise when it fails?
2. Have you searched the whole repo for `cancel_order`, including jobs and scripts? What did the search return?
3. What type is `request["user"]`?
4. If the audit write fails after the order is cancelled, should the cancellation stand?

## Decision-maker summary
Merge once the author confirms the real audit-library signature and that no other code calls `cancel_order`. If either is wrong, every cancellation could fail after the order has already been cancelled, with no audit trail. Fixing the duplicate records on repeat cancels and the failure ordering is cheap and should go in the same PR.

## Owner summary
The change records who cancelled each order, which is what was asked. Before it goes live, someone needs to check that it calls the shared audit tool correctly and that nothing else in the system relies on the old way of cancelling. Otherwise cancellations could break or go unrecorded. It should also avoid recording the same cancellation twice.

```json
{
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "company_audit library", "status": "not_seen", "matters": true},
    {"item": "rest of repository (other cancel_order callers)", "status": "not_seen", "matters": true},
    {"item": "login middleware (type of request['user'])", "status": "not_seen", "matters": true},
    {"item": "CI output for 8a41c7e", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "local-reviewer", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "findings": [
    {"severity": "High", "evidence_level": "UNVERIFIED", "track": "B", "location": "orders.py (patched) record(...) call; tests/test_orders.py:6",
     "scenario": "Real company_audit.record has a different signature than the permissive stub; every cancellation raises TypeError after set_status, so the order is cancelled, unaudited, and returns 500.",
     "fix": "Quote the real signature in the PR and add an integration test against the real library or its published test double.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "UNVERIFIED", "track": "B", "location": "orders.py (patched) def cancel_order(db, order_id, actor); PR.md 'The only caller'",
     "scenario": "A caller outside the supplied files calls cancel_order(db, id) and breaks with TypeError after merge.",
     "fix": "Repo-wide search for cancel_order with a positive control (it must find handlers.py); record the result in the PR.", "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "B", "location": "orders.py (patched) set_status then record",
     "scenario": "record fails after the status change: the order is cancelled with no audit record and the client sees 500.",
     "fix": "Audit first, use a transaction or outbox, or retry; test with record raising.", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "B", "location": "orders.py cancel_order (no already-cancelled check)",
     "scenario": "A repeated cancel writes duplicate order.cancelled records, possibly with different actors.",
     "fix": "Return early or raise when already cancelled, without recording; add a test.", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "track": "B", "location": "handlers.py (patched) request['user']",
     "scenario": "A user object is passed as actor: serialization fails or excess personal data is written to the audit log.",
     "fix": "Pass a stable user id; assert its type in the handler test.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "B", "location": "tests/test_orders.py:6",
     "scenario": "The module-level sys.modules stub leaks into other tests in the same run.",
     "fix": "Use mock.patch.dict(sys.modules) in setUp.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "B", "location": "tests/test_orders.py:16",
     "scenario": "No test asserts that a missing order raises KeyError and writes no record; a refactor moving record earlier goes uncaught.",
     "fix": "Add a missing-order test asserting calls == [].", "status": "n/a"}
  ]
}
```