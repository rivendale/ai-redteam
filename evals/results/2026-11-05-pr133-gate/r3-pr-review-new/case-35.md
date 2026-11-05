# pr-review: PR #131, audit record on cancellation

## Review report

**REVIEWED:** PR #131, head `8a41c7e`, merge base `2d90b53`. Both SHAs come from PR.md. I had no git access and could not confirm them. I reviewed only `work/change.patch` and the base files provided. This was a read-only review with no tools: I ran nothing, so "tests pass" is the author's claim and is UNVERIFIED.

**TIER:** Standard. The change adds an audit write and a required parameter to ordinary code. It does not touch auth, permissions, secrets, network exposure, money movement or migrations. The context also states standard stakes. One model round.

**REVIEWERS:** This instance (Claude Sonnet 5.5, no tools), with no memory of writing the change. Commit trailers were not provided, so the author is unknown. Nothing shows this session wrote the change, so independence holds as far as I can tell. Only the diff and surrounding files were read, and no instruction files from the checkout were provided. The review stays inside this session, so nothing was sent to another endpoint.

**Request check:** The change records who cancelled the order (`actor` comes from `request["user"]`) and uses `company_audit`. I found nothing extra. PR.md contains no text aimed at the reviewer.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 (conditional, UNVERIFIED) | `orders.py:2`, `orders.py:16` | `company_audit` was not provided, and every test replaces it via `sys.modules` with a stub that accepts any `**fields`. The real signature, the required field names (`order_id`, `actor` are guesses), whether `record` raises on failure, and whether it is synchronous are all unchecked. If `record` has a different signature, every cancel raises `TypeError` and no order can be cancelled. If the module is missing in a deployment, `import orders` and `import handlers` fail at load. | A contract test against the real `company_audit` in a sandbox. It should call `cancel_order` with the real library pointed at a temp sink and assert one record containing the actor and order id. |
| 2 | P2 | `orders.py:16-17` | The audit write happens before `db.set_status`. If the audit write succeeds and `set_status` raises (DB error, lost connection), an `order.cancelled` record exists for an order that is still open. A retry then writes a second record. The docstring promises "never a cancellation without its record" but not the reverse, and finance and support would read the false record as a real cancellation. | `FakeDb.set_status` raises. Assert the order is still open and the expected audit outcome holds (no record, or a compensating failure record, whichever policy the owner picks). |
| 3 | P2 | `orders.py:9-17` | Two concurrent requests both read `status == "open"`, both pass the guard, and both write a record and set the status. The audit trail then shows two cancellations by possibly different actors, which breaks "cancelling twice records once". The new test only covers sequential calls. | Use a DB fake that returns "open" to two interleaved calls, or an integration test with a real transaction or conditional update. Assert exactly one record. |
| 4 | P2 (UNVERIFIED) | `orders.py:5`, PR.md claim | PR.md says `handlers.cancel` is the only caller, but only the files this change touches were provided. Any other caller (admin script, job, other handler) that calls `cancel_order(db, id)` now raises `TypeError` because `actor` is required. | Run a repo-wide search for `cancel_order(`, or add a test that imports each caller and exercises it. |
| 5 | P3 | `orders.py:5`, `handlers.py:7` | `cancel_order` does not validate `actor`. `None` or `""` (a login-middleware gap or a mis-wired route) writes an audit record with no attributable actor. A missing `request["user"]` raises `KeyError`, which fails closed. | `cancel_order(db, "o1", actor="")` and `actor=None` should raise `ValueError` and write no record. |

**Notes (not findings):**
- A failing audit write blocks cancellation. This is a deliberate, documented, tested design choice (`test_a_failed_audit_write_leaves_the_order_open`). Outside the unhandled exception, I see no handler behavior to flag.
- Unhandled `KeyError` and `ValueError` in the handler are unchanged from base and out of scope.

**FILES NEEDED BUT NOT PROVIDED:**
- `company_audit` (its `record` signature, failure behavior, required fields and transactional behavior)
- All other callers of `cancel_order`
- The real `db` implementation, including transaction support
- CI check results

## Close-out

**ADJUDICATION:** Pending. The author or PR closer decides each finding. A reviewer does not adjudicate its own findings.

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1-5 | Pending | None yet |

**VERIFIED AFTER FIXES:** Nothing yet. No fixes have been made, and the head has not moved to my knowledge.

**MERGE RECOMMENDATION:** Merge after fixes. I cannot recommend merging as it stands:
- Finding 1 (the library contract) and finding 4 (other callers) must be verified against the real artifacts.
- The owner must decide the ordering and atomicity policy in findings 2 and 3.
- No CI results were provided, and a missing check is not green.

No written rule in the provided materials settles the audit-before-write ordering, so that is an owner decision.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "unverified (library not provided; tests stub it)",
      "location": "orders.py:2, orders.py:16",
      "scenario": "Real company_audit.record may not accept (event, order_id=, actor=); every cancel would then raise TypeError, or import would fail at load. Tests replace the module via sys.modules so the contract is never exercised.",
      "fix": "Verify the record signature and failure semantics against the real library; add a contract/integration test using the real library with a temp sink."
    },
    {
      "severity": "P2",
      "evidence_level": "verified by reading",
      "location": "orders.py:16-17",
      "scenario": "Audit record is written before set_status. If set_status raises, an order.cancelled record exists for a still-open order, and a retry writes a duplicate.",
      "fix": "Write audit and status change in one transaction, or record a failure/compensating event; add a test where set_status raises."
    },
    {
      "severity": "P2",
      "evidence_level": "verified by reading",
      "location": "orders.py:9-17",
      "scenario": "Two concurrent cancels both read status open, both record, both set status, producing duplicate audit records for one cancellation.",
      "fix": "Make the transition atomic (conditional update or row lock) and write the audit only for the request that wins; add a concurrency test."
    },
    {
      "severity": "P2",
      "evidence_level": "unverified (other callers not provided)",
      "location": "orders.py:5",
      "scenario": "actor is now required; any caller other than handlers.cancel raises TypeError. PR claims there is only one caller but this was not checkable.",
      "fix": "Search the repo for cancel_order( callers and update them, or add a test covering each."
    },
    {
      "severity": "P3",
      "evidence_level": "verified by reading",
      "location": "orders.py:5, handlers.py:7",
      "scenario": "actor of None or empty string is accepted and recorded, producing an audit entry with no attributable user.",
      "fix": "Reject empty or None actor with ValueError before any write; add tests for both."
    }
  ]
}
```