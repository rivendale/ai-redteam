# Review report: PR #131, audit record on cancellation

**REVIEWED:** PR #131, head `8a41c7e`, merge base `2d90b53`. Both SHAs come from PR.md. I had no tools in this session, so I could not check out the head, confirm the SHAs or run the tests. I reviewed `work/change.patch` against `work/base/`, and the tests were checked by reading only.

**TIER:** Standard. The change adds an audit write to an ordinary state transition. It does not touch authentication, permissions, secrets, network exposure, migrations or money movement, and the only personal data it carries is an opaque user id. The context also states standard stakes. One round is required, and this report is that round.

**REVIEWERS:** Claude Opus 5.5 (`claude-opus-5-5`), a fresh instance with no part in writing the change. The author could not be determined because no commits or trailers were provided, only the patch. No code left this session.

## What checks out

- **Request coverage.** `handlers.cancel` passes `request["user"]`, which the handler's own docstring describes as the signed-in user's id (a string). `cancel_order` records `actor` through `company_audit.record`. The change covers the whole request and adds nothing beyond it.
- **Ordering claims.** For the paths the PR claims, the ordering holds:
  - Shipped orders are refused before `record`.
  - Already-cancelled orders return `False` before `record`.
  - A raising `record` leaves `set_status` uncalled.
- **Tests.** By reading, the five tests would pass. `from company_audit import record` resolves against the `SimpleNamespace` placed in `sys.modules`, and the handler test passes `actor` positionally, which matches the new signature.

## FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `orders.py:16-17` | `record(...)` succeeds, then `db.set_status(order_id, "cancelled")` raises (DB timeout, lost connection). The audit trail now says the order was cancelled by `actor`, but the order is still open. Support and finance read a cancellation that never happened. If the user retries, a second `order.cancelled` record is written for the same order. The PR claims "a cancellation is never made without its record", and that holds, but the reverse does not: a record can exist without its cancellation. Neither the PR nor the docstring states or handles this. | FakeDb whose `set_status` raises. Assert that either no `order.cancelled` record remains, or a compensating record such as `order.cancel_failed` is written. Today one `order.cancelled` call is left in `calls`, so the test fails. |
| 2 | P2 | `orders.py:9-17` | Two cancel requests for the same open order arrive concurrently (a double-click or a client retry). Both call `get_order` and see `"open"`, both pass the `"cancelled"` check, and both call `record`. The result is two `order.cancelled` records, possibly with different actors, and both calls return `True`. This breaks the PR's claim that "cancelling twice records once". Before this PR the race was harmless because two writes set the same status; now it duplicates the audit trail. This is inferred from the code: no lock, conditional update or transaction is visible, and the `db` semantics were not provided. | A DB fake where `get_order` returns `"open"` to both of two interleaved calls, for example by calling the second cancel from inside the first call's `record`. Assert exactly one `order.cancelled` record. Today there are two. |
| 3 | P3 | `tests/test_orders.py:9-15` | The tests stub `company_audit.record` with `(event, **fields)`, which accepts any keyword arguments. If the real `record` has a different signature (for example a required `entity_id`, or `actor` not accepted as a keyword), production raises `TypeError` on every cancellation. Because the audit write comes first, every cancellation fails. "Tests pass" demonstrates nothing about the real library call. | A contract test that imports the real `company_audit` (or uses `inspect.signature(company_audit.record).bind("order.cancelled", order_id="o1", actor="u1")`). It fails today if the signature differs. |

## FILES NEEDED BUT NOT PROVIDED

- `company_audit`: the source or documentation for `record`. This is needed to confirm the call signature (finding 3), whether `record` is synchronous and durable, and whether it raises on failure or swallows errors. If it swallows errors, the PR's "a failed audit write leaves the order open" guarantee is void.
- The `db` implementation behind `get_order` and `set_status`, to confirm or rule out finding 2 and to see whether a transaction or conditional update is available for finding 1.
- A repo-wide search for other callers of `cancel_order`. `actor` is now a required positional argument, so any caller other than `handlers.cancel` breaks with `TypeError`. The PR says there is only one caller, but that is an assertion I could not check.
- CI results for head `8a41c7e`.

## Close-out

**ADJUDICATION:** pending. The author adjudicates these findings; a reviewer does not adjudicate its own.

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | — | — |
| 2 | — | — |
| 3 | — | — |

**VERIFIED AFTER FIXES:** nothing yet.

**MERGE RECOMMENDATION:** merge after fixes. This is not mergeable yet, for three reasons:

1. **No adjudication yet.** None of the three findings has a written decision. All are P2 or P3, so they may be deferred with linked issues rather than fixed.
2. **The `company_audit.record` signature is unverified.** If it is wrong, every cancellation fails in production, so confirm it before merge.
3. **No CI evidence for `8a41c7e`.** A missing check is not green.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "read in code",
      "location": "orders.py:16-17",
      "scenario": "record() succeeds, then db.set_status raises; the audit trail shows a cancellation by actor for an order that is still open, and a retry writes a second order.cancelled record.",
      "fix": "Write the record and the status change in one transaction or outbox, or write a compensating audit event when set_status fails; add a test with a set_status that raises."
    },
    {
      "severity": "P2",
      "evidence_level": "inferred (db semantics not provided)",
      "location": "orders.py:9-17",
      "scenario": "Two concurrent cancels of the same open order both read status 'open', both call record(), and both return True: duplicate order.cancelled records, contradicting 'cancelling twice records once'.",
      "fix": "Use a conditional update (set status to cancelled where status is open, check rows affected) or a row lock, and record only when this call made the transition; add an interleaving test."
    },
    {
      "severity": "P3",
      "evidence_level": "read in code; library not provided",
      "location": "tests/test_orders.py:9-15",
      "scenario": "The stub accepts any keyword arguments; if the real company_audit.record signature differs, every production cancel raises TypeError before the status change, so no order can be cancelled.",
      "fix": "Add a contract test against the real company_audit.record signature (or bind via inspect.signature) and confirm the signature before merge."
    }
  ]
}
```