# PR #131 review: audit record on order cancellation

**Review report**

**REVIEWED:** PR #131, head `8a41c7e`, merge base `2d90b53`. These SHAs come from PR.md; I had no repository access and could not check them. I reviewed `change.patch` against `base/handlers.py` and `base/orders.py`. I had no tools, so I did not run the tests or the code. The test outcomes below come from reading the code.

**TIER:** Standard. The change is ordinary application code. It adds an audit write to an existing state change and touches no auth, permissions, secrets, network exposure, migrations or money movement in the given files. Finance reads these audit records, which puts it near High. Nothing in the diff moves money, so I kept Standard, as the context also states. If cancellation triggers refunds somewhere downstream, the owner should raise it to High.

**REVIEWERS:** One read by this session (Claude, `claude-opus-5-5`). This session did not write the change. No code left this session. The patch has no commit trailers, so the author is unknown from the evidence given.

**Request coverage:** The request is met on a code read. The patch writes a record via `company_audit.record` with `actor` set to the signed-in user's id, and adds nothing beyond the request. The PR also says it "only caller" `handlers.cancel` uses this function. That holds for the files provided, but other callers (scripts, admin tools, jobs) were not given. Any of them would now fail with a `TypeError`.

**Tests (read, not run):** The five tests look like they would pass.
- The `sys.modules` stub works with `from company_audit import record`, because `from … import` only does `getattr` on the module object.
- The stub accepts any `**fields`. So the tests cannot show that the real library accepts `order_id=` / `actor=`, or that it raises on failure.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `orders.py:16-17` | The order is open. `record(...)` succeeds, then `db.set_status` raises (DB timeout, lost connection). The audit log now says "order.cancelled by alice" while the order is still open. If the user retries, a second `order.cancelled` record is written. Support and finance then see a cancellation that never happened, or two of them. The docstring guards only one direction ("never cancelled without its record"), not "never recorded without a cancellation". Nothing marks, compensates or reconciles the orphan record. | `FakeDb` whose `set_status` raises `RuntimeError`. Assert that either no `order.cancelled` record remains, or a compensating/failure record is written (whichever behaviour the owner chooses). It fails today because `calls` holds one `order.cancelled` entry. |
| 2 | P3 | `orders.py:9-17` | Two concurrent cancel requests for the same open order both read `status == "open"`. Both pass the check at line 14, both call `record`, and both call `set_status`. That produces two `order.cancelled` audit records, possibly with different actors. The PR claims "cancelling an order that is already cancelled … records nothing", but that only holds for sequential calls. | A `FakeDb` where `get_order` returns `"open"` to two interleaved calls (or run two threads against a barrier). Assert that exactly one record is written. It fails today with two. |
| 3 | P3 | `tests/test_orders.py:61-64` | `test_cancelling_twice_records_once` never cancels twice. It starts from a DB already in `"cancelled"` state. A regression that recorded on the second of two real calls (say, the record moved above the status check) would pass this test only if the fake were also wrong. The name promises coverage the test does not give. | Cancel once on an open `FakeDb` that updates its own `status` in `set_status`, then cancel again. Assert `len(calls) == 1` and the second call returns `False`. |

**FILES NEEDED BUT NOT PROVIDED:**
- **The `company_audit` library**, at least the `record` signature and how it fails. The PR's central guarantee ("a failed audit write leaves the order open") holds only if `record` writes synchronously and raises on failure. If it buffers or enqueues and fails later, or swallows errors, orders get cancelled without a record. The stub also cannot show that `order_id=` and `actor=` are accepted field names. This is a coverage gap, not a confirmed defect.
- **A repo-wide list of callers of `cancel_order`**, to confirm the "only caller" claim.
- **Login middleware and routing for `/orders/<id>/cancel`.** These would confirm that `request["user"]` is always set on this route. If it is missing, `handlers.py:7` now raises `KeyError` (a 500) where it previously cancelled.
- **CI results for head `8a41c7e`.** "Tests pass" is a claim; I saw no check run.

---

**Close-out:** Pending. The author adjudicates the findings above; the reviewer does not.

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | pending author | |
| 2 | pending author | |
| 3 | pending author | |

**VERIFIED AFTER FIXES:** Nothing yet.

**MERGE RECOMMENDATION:** Not yet mergeable. Merge after these are done:
- Each finding gets a written decision. All are P2/P3, so deferral with a tracking issue is allowed.
- The `company_audit.record` failure semantics and field names are confirmed against the real library.
- The `cancel_order` caller list is confirmed.
- The expected CI checks are present and green on `8a41c7e`.

No P0 or P1 blocker was found.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "code-read",
      "location": "orders.py:16-17",
      "scenario": "record() succeeds, then db.set_status raises; the audit log shows a cancellation that did not happen, and a retry writes a second order.cancelled record.",
      "fix": "Write and reconcile in one transaction or outbox. Otherwise, on set_status failure write a compensating/failed record, or record after the status change with an outbox that guarantees delivery. Add a test where set_status raises."
    },
    {
      "severity": "P3",
      "evidence_level": "code-read",
      "location": "orders.py:9-17",
      "scenario": "Two concurrent cancels both read status 'open' and both write order.cancelled audit records, contradicting the 'records once' claim.",
      "fix": "Use a conditional update (set status to cancelled where status is open) and record only when it affected a row, or lock the row; add an interleaved-call test."
    },
    {
      "severity": "P3",
      "evidence_level": "code-read",
      "location": "tests/test_orders.py:61-64",
      "scenario": "test_cancelling_twice_records_once starts from an already-cancelled order, so it never exercises two real cancellations.",
      "fix": "Have FakeDb.set_status update its status, cancel twice, and assert exactly one record and that the second call returns False."
    }
  ]
}
```