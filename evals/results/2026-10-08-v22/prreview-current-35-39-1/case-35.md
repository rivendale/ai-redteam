# Review report: PR #131 (audit record on cancellation)

**REVIEWED:** PR #131, head `8a41c7e`, merge base `2d90b53`. I had no tools in this session, so I could not use a worktree. I read `change.patch` against the base files provided (`base/handlers.py`, `base/orders.py`). I did not run anything, so "Tests pass" is still the author's claim.

**TIER:** Standard. The change adds an audit write to an existing order flow and touches no auth, secrets, migrations, money movement or personal data beyond a user identifier. This matches the stakes in `context.md`.

**REVIEWERS:** This session (Claude Opus 5.5, `claude-opus-5-5`) did one round. It did not write the change. The commit trailers were not provided, so the author is not recorded here. No code was sent outside this session.

**Scope check against the request:** The change does all of what was asked (an audit record with the actor, written through `company_audit`) and nothing extra.

## FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `orders.py:11-12` | `db.set_status(...)` runs before `record(...)`, and nothing ties the two together. Suppose `record` raises (audit service unreachable, serialization error, contract mismatch; see #3). If `set_status` has already committed, the order is cancelled with no audit record, and the caller gets an error for a cancellation that took effect. Support and finance would then see a cancelled order with no "who". Whether `set_status` commits on its own depends on the db layer, which was not provided. | Use a stub `record` that raises. Assert that either the status is not changed, or the failure is surfaced and retried or queued so a record is eventually written. Today the test shows `db.set == "cancelled"` with `calls == []`. |
| 2 | P2 | `orders.py:9` (status check) and `orders.py:12` | Only `"shipped"` is refused, so an already-cancelled order can be cancelled again. Example: user A cancels `o1`, then user B POSTs cancel on `o1`. The second call succeeds and writes a second `order.cancelled` record with `actor=B`. The audit trail now shows two cancellations by two different people, so "who cancelled it" is ambiguous. The status behaviour existed before this PR; the misleading duplicate record is new. | Cancel `FakeDb("cancelled")` with `actor="bo"`. Assert that no audit record is written (or that the call is refused). Today one record with `actor="bo"` is written. |
| 3 | P2 | `orders.py:2`, `orders.py:12`; `tests/test_orders.py:6` | The tests replace `company_audit` in `sys.modules` with a stub, `record(event, **fields)`. Nothing checks that the real `company_audit.record` accepts this call shape, or that `actor` can be the raw `request["user"]` value (`handlers.py:7`), which could be a user object rather than an id. If the real signature or field types differ, every cancellation in production raises after `set_status`, which triggers the #1 failure on every request. The passing tests cannot detect this. | Write a contract test that calls the real `company_audit.record` (or its documented test double) with `("order.cancelled", order_id="o1", actor=<a real request["user"] value>)` and asserts it is accepted. |

**FILES NEEDED BUT NOT PROVIDED:**
- `company_audit`: the `record` signature, its failure behaviour (raises, buffers or async), and the accepted field types.
- The db layer behind `db.set_status`: whether it commits immediately and whether there is a transaction scope.
- The login middleware: the type of `request["user"]`, and whether it can be absent or `None` on this route.
- The commit trailers, to record the author.
- CI results for head `8a41c7e`.

## Close-out

Pending. The author adjudicates findings 1–3. The reviewer does not adjudicate its own findings.

**ADJUDICATION:** not yet written.

**VERIFIED AFTER FIXES:** nothing yet.

**MERGE RECOMMENDATION:** Merge after fixes, conditionally. There are no P0 or P1 findings. Before merge:
- all three findings need a written decision. Each is P2, so it can be fixed or deferred with a linked issue.
- the expected CI checks for `8a41c7e` must be present and green. I did not see them.
- #3 needs someone to read the real `company_audit` API. If the call does not match it, #3 becomes a P1 blocker, because every cancellation would fail after the status change.

```json
{
  "verdict": "merge after fixes (pending adjudication of findings, green checks on 8a41c7e, and confirmation of the company_audit.record contract)",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "inferred from code; commit semantics of db.set_status and failure behaviour of company_audit.record not provided",
      "location": "orders.py:11-12",
      "scenario": "record() runs after db.set_status() with no transaction or retry; if record raises, the order stays cancelled with no audit record and the caller gets an error for a cancellation that took effect.",
      "fix": "Write the status change and the audit record atomically (same transaction or an outbox), or record first and only then commit; add a test where record raises and assert the status is not left cancelled without a record."
    },
    {
      "severity": "P2",
      "evidence_level": "confirmed by reading orders.py (only 'shipped' is refused)",
      "location": "orders.py:9",
      "scenario": "An already-cancelled order can be cancelled again by another user; a second order.cancelled record with a different actor is written, so the audit trail no longer says who cancelled it.",
      "fix": "Refuse or no-op on status 'cancelled' without writing a record; add a test with FakeDb('cancelled') asserting no audit call."
    },
    {
      "severity": "P2",
      "evidence_level": "unverified; company_audit and the type of request['user'] were not provided, and the tests stub the library",
      "location": "orders.py:12",
      "scenario": "Tests stub company_audit.record as record(event, **fields); if the real signature or accepted actor type differs, every production cancellation raises after set_status (compounding finding 1), and the tests cannot detect it.",
      "fix": "Confirm against the real company_audit API; pass a stable user identifier as actor; add a contract test against the real library or its official test double."
    }
  ]
}
```