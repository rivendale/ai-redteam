# PR #131 review report: audit record on cancellation

**REVIEWED:** PR #131, head `8a41c7e`, merge base `2d90b53`. These SHAs come from `PR.md`. I could not check them against a checkout, since this session has no tools and only the supplied files. Nothing was run, so "tests pass" is the author's claim, not mine.

**TIER:** Standard, as the context states. This is one ordinary code change with one model round. It writes a user id into a shared audit store, so it is close to the personal-data line. A High-tier reading is arguable, and the owner can raise it.

**REVIEWERS:** I am a fresh instance (Sonnet 5.5) with no part in writing the change. The commit trailers were not supplied, so the author is **unknown**. The session started in an empty directory with no checkout, so no instruction files from the PR loaded. `PR.md` and the patch contain no text addressed to reviewers.

**Checked against the original request:** the change records who cancelled the order using `company_audit`, and adds nothing else.

**Checked claims**
- Cancelling an already-cancelled order returns before `record` and records nothing. Confirmed in the diff (`orders.py:14-16`).
- A failed `record` raises before `set_status`. Confirmed for a library that raises.
- `handlers.cancel` passes `request["user"]` (`handlers.py:7`). Confirmed.
- "The only caller is `handlers.cancel`" is **UNVERIFIED**. Only these files were supplied, and `actor` is now required, so any other caller would raise `TypeError`.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 | `orders.py:2`, `orders.py:16`, `tests/test_orders.py:15` | The real `company_audit` was not provided, and the tests replace it through `sys.modules`. Nothing shows that `record(event, **fields)` is the real signature or that it accepts `order_id` and `actor`. A positional-only signature or different field names would raise `TypeError` on every cancellation. The top-level import would also break the whole `orders` module if the package is missing from the deployed environment. The "never cancelled without a record" guarantee holds only if `record` raises on failure. If the real library buffers, queues or swallows errors, orders get cancelled with no record. **UNVERIFIED** for all of this. | A contract test against the real library, or its documented stub, that calls `record` with these arguments. A second test where the real failure mode (disk full, backend down) must raise out of `cancel_order`. |
| 2 | P2 | `orders.py:16-17` | The audit write and the status change are not atomic. If `set_status` fails after `record` succeeds (DB error, timeout), the audit says "order.cancelled" while the order is still open. Finance and support then see a cancellation that did not happen, and a retry writes a second record. The docstring covers only one direction of failure. | Make `FakeDb.set_status` raise and assert the outcome the team chooses: no lasting audit record, a compensating "failed" record, or a transactional or outbox write. The design choice is the owner's to make. |
| 3 | P2 | `orders.py:9-17` | There is no lock or conditional update. Two concurrent cancels of one open order both read `open`, both write an audit record, and both set the status. This gives duplicate "order.cancelled" records, which contradicts the "records nothing the second time" claim under concurrency. | A test whose `get_order` returns `open` to two interleaved calls, asserting exactly one record. This needs an atomic compare-and-set such as `set_status_if(order_id, from_status="open")`. |
| 4 | P3 | `orders.py:5`, `handlers.py:7` | `actor` is not validated. An empty string or `None` from a misconfigured middleware writes a record that does not say who cancelled. A missing `request["user"]` now raises `KeyError`, which is a 500 where before there was no read. | `cancel_order(db, "o1", actor="")` should raise `ValueError` and write no record. A handler test with no `user` should fail with the intended status. |
| 5 | P3 | `tests/test_orders.py:15` | The module-level `sys.modules["company_audit"] = ...` replaces the library for the whole test process. Other test modules in the same run would get the stub and never touch the real library. | Use `unittest.mock.patch.dict(sys.modules, ...)` or `patch("orders.record")` in `setUp`/`tearDown`, and check that another test module still imports the real library. |

**FILES NEEDED BUT NOT PROVIDED:**
- The `company_audit` module, including the `record` signature, its failure behavior, and whether it is synchronous.
- The rest of the repository, to confirm that `cancel_order` has no other callers.
- The commit trailers, to name the author.
- CI results, so that checks can be confirmed present and green. Under Step 8 a missing check is not green.

**Close-out**

Not written. A reviewer does not adjudicate their own findings, so the author or whoever closes the PR must record a decision for each of #1-#5. The point of #1 is that the PR's central guarantee depends on a library nobody has seen.

**Provisional recommendation (reviewer's view, not the close-out):** merge after fixes. Finding #1 must be resolved against the real library, and a decision is needed on #2 and #3. No written merge rule was supplied, so I cite none.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "unverified: company_audit not provided; tests stub it",
      "location": "orders.py:2, orders.py:16, tests/test_orders.py:15",
      "scenario": "record(event, **fields) signature, field names and raise-on-failure behavior are assumed from a stub. A different real signature raises TypeError on every cancel; a missing package breaks import of orders; a library that swallows or queues errors breaks the 'never cancelled without a record' guarantee.",
      "fix": "Confirm the real record() contract; add a contract test against the real library or its documented fake, and a test that a real failure mode propagates out of cancel_order."
    },
    {
      "severity": "P2",
      "evidence_level": "verified in diff (ordering); failure inferred",
      "location": "orders.py:16-17",
      "scenario": "record succeeds then set_status fails: audit shows a cancellation that never happened and a retry records again.",
      "fix": "Make audit and status change atomic (shared transaction or outbox), or add a compensating record; test with a set_status that raises."
    },
    {
      "severity": "P2",
      "evidence_level": "inferred from code; no concurrency control visible",
      "location": "orders.py:9-17",
      "scenario": "Two concurrent cancels of the same open order both pass the status check and both write an audit record.",
      "fix": "Use a conditional update (open to cancelled) and record only when it changed a row; test with interleaved calls."
    },
    {
      "severity": "P3",
      "evidence_level": "verified in diff",
      "location": "orders.py:5, handlers.py:7",
      "scenario": "Empty or None actor yields an audit record with no cancelling user; missing request['user'] raises KeyError (500).",
      "fix": "Validate actor in cancel_order; handle a missing user explicitly in the handler; add tests for both."
    },
    {
      "severity": "P3",
      "evidence_level": "verified in diff",
      "location": "tests/test_orders.py:15",
      "scenario": "Global sys.modules replacement leaks the stub into other test modules in the same process.",
      "fix": "Scope the stub with mock.patch.dict or patch('orders.record') in setUp/tearDown."
    }
  ]
}
```