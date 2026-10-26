# PR #131 review report: audit record on cancellation

**REVIEWED:** PR #131, head `8a41c7e`, merge base `2d90b53`. Both SHAs are taken from PR.md. I had no checkout or git access, so I could not confirm that `change.patch` matches the head. I reviewed the patch and the base files as given, and I did not run anything.

**TIER:** Standard. The change touches order state and an audit trail, not auth, secrets, migrations or money movement. The audit data is for support and finance, but the change does not alter who can do what. One model round.

**REVIEWERS:** One fresh instance (Claude Sonnet 5.5) with no part in writing the change. No commit trailers were provided, so the author is unknown. Only the PR description, patch and base files were reviewed, and nothing was sent to any other endpoint.

**Request check:** The request asked for an audit record of who cancelled the order, via the shared library. The patch does that: `actor` is threaded from `request["user"]` through `handlers.cancel` into `record(...)`. The already-cancelled and shipped paths record nothing, which matches the docstring. The scope is otherwise minimal. The PR text contains no instructions aimed at the reviewer.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 (coverage gap, UNVERIFIED) | `orders.py:2`, `orders.py:16` | `company_audit` was not provided, so the `record(event, **fields)` signature, the `order_id` and `actor` field names, the event name `order.cancelled`, and the failure behaviour (raise vs. swallow) are unchecked. The tests replace the module with a stub the author wrote, so they only prove the code matches the author's assumption. If the real signature differs, every cancellation raises `TypeError` and no order can be cancelled. If the library is missing from the service's dependencies, the top-level import breaks `orders`, and `handlers` with it, at import time. | Contract test against the real library, or its published schema: call `record("order.cancelled", order_id="o1", actor="alice")` and read the record back. |
| 2 | P2 | `orders.py:16-17` | The audit record is written before `db.set_status`. If `set_status` raises (DB error or timeout), an `order.cancelled` record exists for an order that is still open. Finance and support would see a cancellation that never happened. A client retry then writes a second record. The docstring guarantees "never a cancellation without its record" but not the reverse, and the PR does not acknowledge this. | A `FakeDb` whose `set_status` raises. Assert the intended behaviour: either no audit record remains, or the record is marked as an attempt and a retry does not duplicate it. |
| 3 | P2 | `orders.py:11-17` | There is a check-then-act race. Two concurrent cancels of the same open order both read `status == "open"`, both pass the check, and both write an audit record. The PR claims "records nothing" for repeat cancels, but that holds only for sequential calls. A sequential-only test cannot catch this. | Interleave two calls with a `FakeDb` whose `get_order` returns "open" to both before either `set_status`. Assert exactly one record, or use a conditional status update that returns whether it changed a row. |
| 4 | P3 | `tests/test_orders.py:13` | `sys.modules["company_audit"] = ...` at import time permanently replaces the module for the whole test process. Any other test module that imports the real library, or collects after this one, gets the stub. | Use `unittest.mock.patch.dict(sys.modules, ...)` in `setUpModule`/`tearDownModule`, then assert `sys.modules` is restored afterwards. |
| 5 | P3 | `orders.py:5` (signature) | `actor` is now a required positional argument. The PR says `handlers.cancel` is the only caller, but only `handlers.py` and `orders.py` were provided. A script, admin tool or job elsewhere that calls `cancel_order(db, id)` would raise `TypeError`. The claim is unverified. | Run a repo-wide search for `cancel_order(` and add a test or lint rule that every call passes `actor`. |

Minor: `test_cancelling_twice_records_once` makes a single call on an already-cancelled order, so its name overstates what it checks. It is covered by finding 3's test.

**FILES NEEDED BUT NOT PROVIDED:** `company_audit` (source, signature, failure semantics, version pin in the dependency manifest). The full repository, to confirm that `handlers.cancel` is the only caller. CI results for head `8a41c7e`.

## Close-out

**ADJUDICATION:** Pending. The author must decide on each finding; a reviewer does not adjudicate its own findings.

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | pending | |
| 2 | pending | |
| 3 | pending | |
| 4 | pending | |
| 5 | pending | |

**VERIFIED AFTER FIXES:** Nothing yet. The head has not moved since this review.

**MERGE RECOMMENDATION:** Merge after fixes. This does not meet Step 8 yet: "every finding has a written decision" is not met, and no CI check results were provided ("a missing check is not green"). Resolve finding 1 by supplying the real `company_audit` contract or an integration test. For findings 2 and 3, the author must decide on the ordering and idempotency semantics, with the finance and support owners' input if needed. Nothing here is a P0, but the contract question cannot be waved through on the strength of a self-written stub.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "unverified (library not provided; tests use author-written stub)",
      "location": "orders.py:2, orders.py:16",
      "scenario": "The real company_audit.record signature, field names and failure behaviour were not seen. If they differ from record(event, order_id=, actor=), every cancel raises TypeError. If the dependency is missing, the top-level import breaks orders and handlers.",
      "fix": "Supply the library contract or add a contract/integration test against the real library; confirm the dependency is declared."
    },
    {
      "severity": "P2",
      "evidence_level": "confirmed by reading",
      "location": "orders.py:16-17",
      "scenario": "The audit record is written before set_status. If set_status raises, the audit log shows a cancellation of an order that is still open, and a retry writes a duplicate record.",
      "fix": "Decide the ordering semantics: write the record after the status change, use a transaction, or mark the record as an attempt and make it idempotent. Test with a set_status that raises."
    },
    {
      "severity": "P2",
      "evidence_level": "inferred from code (check-then-act, no locking)",
      "location": "orders.py:11-17",
      "scenario": "Two concurrent cancels of the same open order both pass the status check and both record an audit event, contradicting the 'records once' claim.",
      "fix": "Use a conditional or atomic status update that reports whether it changed a row and record only on success; add an interleaving test."
    },
    {
      "severity": "P3",
      "evidence_level": "confirmed by reading",
      "location": "tests/test_orders.py:13",
      "scenario": "The test module permanently replaces sys.modules['company_audit'] at import time, leaking the stub into other tests in the same process.",
      "fix": "Scope the stub with mock.patch.dict(sys.modules, ...) in setUpModule/tearDownModule."
    },
    {
      "severity": "P3",
      "evidence_level": "unverified (full repo not provided)",
      "location": "orders.py:5",
      "scenario": "actor is a new required positional argument. Any caller other than handlers.cancel that was not shown would raise TypeError.",
      "fix": "Search the repo for cancel_order( callers and confirm each passes actor."
    }
  ]
}
```