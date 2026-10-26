# pr-review report: PR #131

**REVIEWED:** PR #131 "audit record on cancellation", head `8a41c7e`, merge base `2d90b53`. Both SHAs are as stated in PR.md. I had no git access and could not verify them or confirm the head has not moved. I reviewed only the patch and the base files provided.

**TIER:** Standard. The change adds a write to an audit trail on an existing code path. It does not touch authentication, permissions, secrets, migrations, money movement or personal data in the diff. Finance relies on the audit data, but the order status change itself is unchanged. No data restrictions apply to the code I was given.

**REVIEWERS:** One fresh reviewer instance (Sonnet 5.5), which had no part in writing the change. The author is unknown because no commit trailers were provided. I ran nothing: I have no tools, and the tests were read, not executed.

**Request check:** The request was an audit record with the actor on cancel, using the shared library. The patch does this. The `actor` is threaded from `request["user"]`. Already-cancelled and shipped orders record nothing. I found no extra scope. The PR text contains no instructions aimed at the reviewer.

## FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `orders.py:16-17` | The audit record is written before `db.set_status`. If `set_status` raises (DB error, timeout), the audit log says "order.cancelled" but the order is still open. A client retry then writes a second record. Support and finance would see cancellations that never happened. The PR only covers the opposite failure, where the audit write fails. | `FakeDb.set_status` raises. Cancel, assert `OSError`, then assert the audit calls and order state are consistent. Either the record is compensated or the design explicitly accepts and documents the phantom record. |
| 2 | P2 | `orders.py:9-17` | Check-then-act with no transaction or lock. Two concurrent cancels of the same open order both read `open`, both call `record`, and both return True. The audit log gets two "cancelled by" records for one cancellation, possibly with different actors. The new "records once" guarantee holds only for sequential calls. | Use a `FakeDb` whose `get_order` is called by two interleaved `cancel_order` calls. Assert exactly one audit record, or move the status check into a conditional `set_status` and test that. |
| 3 | P2 | `orders.py:2, 16` (coverage gap) | The `company_audit` library was not provided, and every test stubs it. Unverified: that `record(event, **fields)` is the real signature. That `order_id` and `actor` are the field names it expects. That `"order.cancelled"` is a registered event name. That it raises on failure rather than returning silently or buffering asynchronously. If it buffers or swallows errors, the PR's claim that a cancellation is never made without its record is false. | A contract test or integration test against the real library, using a test sink. Assert the record is retrievable with the actor, and that a failing sink raises synchronously. |
| 4 | P3 | `orders.py:6` (signature) | `actor` is now a required positional parameter. The PR says `handlers.cancel` is the only caller, but only `handlers.py` was provided. Any other caller in the repo (script, job, admin tool) would raise `TypeError` at runtime. | Repo-wide search for `cancel_order(` and a test for each caller found. |
| 5 | P3 | `tests/test_orders.py:14` | The test file replaces `sys.modules["company_audit"]` at import time and never restores it. If this module is loaded in a shared test process, the stub leaks into other tests. It could also mask the real library in any later integration test. | Install the stub with `unittest.mock.patch.dict(sys.modules, ...)` in `setUpModule` or `setUpClass` and restore it afterwards. Assert the real module is untouched after the suite. |

## FILES NEEDED BUT NOT PROVIDED

- `company_audit` source or its documented contract: signature, event registry, error and durability semantics (finding 3).
- All other files in the repo that could call `cancel_order` (finding 4).
- The real `db` implementation, to learn whether transactions or conditional updates are available (findings 1 and 2).
- Commit metadata (author and `Co-Authored-By` trailers) and CI check results. I cannot confirm the expected checks are present and green.

## MERGE RECOMMENDATION (reviewer's view, pending author adjudication)

**Merge after fixes.** The patch does what was requested, and the audit-first ordering is a defensible choice. Before merge:

1. Confirm the `company_audit` contract (finding 3), which is an open item.
2. Confirm there are no other callers (finding 4).
3. Make an explicit decision on findings 1 and 2. These are P2 and may be deferred with a tracking issue, but the decision must be written.
4. Confirm CI is green on the exact head.

Adjudication and close-out belong to the author and whoever closes the PR.

```json
{
  "verdict": "merge_after_fixes",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "read",
      "location": "orders.py:16-17",
      "scenario": "record() runs before db.set_status. If set_status raises, an audit record for a cancellation exists while the order stays open; a retry writes a duplicate record.",
      "fix": "Decide and document the failure semantics. Either write the audit and status change in one transaction, or compensate or mark the record on failure. Add a test with a failing set_status."
    },
    {
      "severity": "P2",
      "evidence_level": "inferred",
      "location": "orders.py:9-17",
      "scenario": "Two concurrent cancels of the same open order both pass the status check and both write audit records, so the log shows duplicate or conflicting actors for one cancellation.",
      "fix": "Make the status transition atomic (conditional update or row lock) and record the audit only for the call that performed the transition. Add an interleaving test."
    },
    {
      "severity": "P2",
      "evidence_level": "unverified",
      "location": "orders.py:2,16",
      "scenario": "company_audit was not provided and all tests stub it. Signature, field names, event name and synchronous-failure behaviour are unverified, so the claim that a cancellation is never made without its record is untested against the real library.",
      "fix": "Review the library contract and add an integration or contract test against a real or test sink, including a failing-sink case."
    },
    {
      "severity": "P3",
      "evidence_level": "unverified",
      "location": "orders.py:6",
      "scenario": "actor is a new required parameter. Callers other than handlers.cancel were not provided; any other caller raises TypeError.",
      "fix": "Search the repo for cancel_order callers and update or test each."
    },
    {
      "severity": "P3",
      "evidence_level": "read",
      "location": "tests/test_orders.py:14",
      "scenario": "The test permanently replaces sys.modules['company_audit'] with a stub at import time, leaking into other tests in the same process and potentially masking the real library.",
      "fix": "Use patch.dict(sys.modules, ...) scoped to setUpModule/setUpClass and restore afterwards."
    }
  ]
}
```