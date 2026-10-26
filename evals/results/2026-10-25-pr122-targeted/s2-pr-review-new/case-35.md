# PR #131 review report

**REVIEWED:** PR #131, head `8a41c7e`, merge base `2d90b53`. Both SHAs are taken from PR.md. I had no tools, so I could not confirm them against a checkout or review in a throwaway worktree. I read the patch and the base files only.

**TIER:** Standard. The change adds a write to the audit trail on an existing path. It does not touch auth, permissions, secrets, network exposure, migrations or money movement. The context says the stakes are standard. One model round is the budget, and this is it.

**REVIEWERS:** This is a fresh instance (Claude Sonnet 5.5) with no memory of writing the change. Commit trailers were not provided, so the author is unknown. The PR text is treated as data. It contains no instructions addressed to the reviewer.

**Not run:** the tests (no execution available). The "tests pass" claim in PR.md is unverified. The tests stub `company_audit`, so a pass would say nothing about the real library either way.

**Request check:** "Record who cancelled, via the shared library" is implemented in `orders.py:16` and `handlers.py:7`. I found nothing extra beyond the required `actor` parameter and the tests.

## FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `orders.py:16-17` | `record(...)` succeeds, then `db.set_status` raises (DB error, lock timeout). The audit trail now says "order.cancelled by alice" but the order is still open. A retry writes a second record. Support and finance would read a cancellation that never happened. The docstring only guarantees the opposite direction (no cancellation without a record). | A `FakeDb` whose `set_status` raises. Assert there is no net "cancelled" record (transaction or compensating event), or that a retry yields one record. It fails today because `calls` holds one record with the order open. |
| 2 | P2 | `orders.py:9-17` | Two concurrent cancels of the same open order both read `status == "open"`, both pass the `cancelled` check, both write a record, and both set the status. This gives two audit records, possibly with different actors. "Cancelling twice records once" is only true sequentially (`tests/test_orders.py:61-64`). | A `FakeDb` that returns a stale "open" to two calls. Assert one record, with `set_status` being a conditional open→cancelled transition whose result gates `record`. |
| 3 | P3 | `tests/test_orders.py:15` | `sys.modules["company_audit"] = ...` replaces the module for the whole test process and is never restored. In a shared runner, other tests that import the real library get the stub, or the order of imports changes results. | Run this file alongside a test that imports the real `company_audit`. Assert the real module is still importable afterwards. Use `unittest.mock.patch.dict` or `patch("orders.record")` instead. |

No finding is made on the "fails closed" claim itself. It depends on `company_audit.record` raising on failure, and I cannot see that library. This is a coverage gap, listed below, not a supported defect.

## FILES NEEDED BUT NOT PROVIDED

- **`company_audit`**: needed to confirm these four points.
  - That `record(event, **fields)` accepts `order_id` and `actor`.
  - That it is synchronous and raises on failure. A buffered or queued implementation that swallows errors would make the "failed write leaves the order open" guarantee false.
  - That it is idempotent or deduplicates (relevant to findings 1 and 2).
  - That it is declared as a dependency of this service. No manifest is in the diff.
- **The rest of the repository**: PR.md says `handlers.cancel` is the only caller. Only `handlers.py`, `orders.py` and the README were provided. Any other caller of `cancel_order(db, order_id)` would raise `TypeError` now that `actor` is required. This is UNVERIFIED.
- **CI results**: no check status was provided, so I cannot call checks green.

## Merge recommendation (reviewer's view)

**Merge after fixes.** This is not a close-out, because the author must adjudicate first.

- The `company_audit` contract and the other-callers claim must be confirmed against the real library and repo.
- Findings 1 and 2 need a decision. Fix them, or defer them as P2 with a tracking issue.
- Finding 3 is a small fix.
- Per Step 8, all checks must be present and green, and I have no evidence of that yet.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "read from diff; not executed",
      "location": "orders.py:16-17",
      "scenario": "record() succeeds and db.set_status then raises, leaving an audit record for a cancellation that did not happen; a retry writes a second record.",
      "fix": "Do both writes in one transaction if the db supports it, or add a compensating/pending-state record, and make the event idempotent per order. Add a test with a set_status that raises."
    },
    {
      "severity": "P2",
      "evidence_level": "read from diff; not executed",
      "location": "orders.py:9-17",
      "scenario": "Two concurrent cancels both read status 'open', both pass the cancelled check, and both write an audit record (possibly with different actors).",
      "fix": "Make the status change a conditional open->cancelled update and write the record only when that transition succeeds, or deduplicate in the audit event. Test with a stale-read FakeDb."
    },
    {
      "severity": "P3",
      "evidence_level": "read from diff; not executed",
      "location": "tests/test_orders.py:15",
      "scenario": "The test replaces sys.modules['company_audit'] globally and never restores it, which can leak the stub into other tests in the same process.",
      "fix": "Use unittest.mock.patch.dict(sys.modules, ...) or patch('orders.record') scoped to the tests."
    },
    {
      "severity": "P3",
      "evidence_level": "UNVERIFIED (library and repo not provided)",
      "location": "orders.py:2,16; handlers.py:7",
      "scenario": "The fail-closed guarantee, the record() signature, the dependency declaration and the 'only caller' claim all rest on files not provided. If record() swallows errors or other callers exist, the PR's stated behavior does not hold.",
      "fix": "Supply company_audit and a repo-wide search for cancel_order callers, then confirm record() raises on write failure."
    }
  ]
}
```