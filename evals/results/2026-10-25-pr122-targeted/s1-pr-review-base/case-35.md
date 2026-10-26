# Review report: PR #131, audit record on cancellation

**REVIEWED:** PR #131, head `8a41c7e`, merge base `2d90b53`. Both SHAs are taken from `PR.md`. I could not verify them or make a throwaway checkout, because I have no tools or repository here. I reviewed `change.patch` against `work/base/` only.

**TIER:** Standard. The change adds an audit write to ordinary application code, and `context.md` rates the stakes as standard. It does not touch auth, secrets, migrations, money movement or personal data beyond a user id. The tier requires one model round, and this is it.

**REVIEWERS:**
- **Reviewer:** a fresh Claude Sonnet 5.5 instance with no tools. It did not write the change and has no memory of it.
- **Author:** unknown. No commit trailers were provided.
- **Data handling:** only the supplied diff and base files were used, and nothing was sent elsewhere.

**Not run:** the claim "Tests pass" is unverified. I read the tests but did not run them. They stub `company_audit`, so they cannot show that the real library behaves as the PR assumes.

**Request check:** the change does what was asked. It writes an audit record with the actor on cancellation, through `company_audit`. The scope is otherwise tight. There is no reviewer-directed text in the PR and nothing extra in the diff.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 (unverified) | `orders.py:16` (`record(...)`) | The "failed audit write leaves the order open" guarantee depends on `company_audit.record` raising on failure. The library was not provided. If it returns an error value, logs and swallows, or queues asynchronously, `cancel_order` proceeds to `set_status` and the order is cancelled with no record. The test stubs `record` to raise `OSError`, so it cannot catch this. | Contract test against the real library, or its documented failure mode: force a write failure and assert `cancel_order` does not cancel. Also assert the call signature `record("order.cancelled", order_id=..., actor=...)` is accepted. |
| 2 | P2 | `orders.py:16-17` | The audit write and the status change are not atomic. If `db.set_status` raises (DB error, timeout) after `record` succeeded, the audit log says "order.cancelled" for an order that is still open. A retry then writes a second record. Support and finance would see a cancellation that did not happen, or a duplicate. | A fake `db.set_status` that raises: assert the audit has no committed "order.cancelled" entry (or a compensating entry), and that a retry yields exactly one. |
| 3 | P2 | `orders.py:11-17` | Check-then-act race. Two concurrent cancels of the same open order both read `status == "open"`, both call `record`, and both call `set_status`. The result is two audit records, and possibly two different actors, for one cancellation. This contradicts "cancelling an already-cancelled order records nothing". `set_status` is unconditional. | A concurrency test with two threads and a barrier inside `FakeDb.get_order`: assert exactly one audit record. A real fix needs a conditional update (`UPDATE ... WHERE status='open'`) or a row lock. |
| 4 | P3 | `tests/test_orders.py:56` | `test_cancelling_twice_records_once` makes one call on an already-cancelled order. It does not cancel twice, so it only covers the idempotent path, not the double-cancel flow its name suggests. The tests also install the stub in `sys.modules` globally and never remove it, which can mask a missing or incompatible real dependency in the same test process. | Rename it, or make it cancel an open order and then cancel it again. Add a case where `set_status` raises. |

**FILES NEEDED BUT NOT PROVIDED:**
- `company_audit` source or documentation: signature, failure semantics, sync or async behavior, and whether it can join the DB transaction.
- The dependency manifest or lockfile. I cannot confirm `company_audit` is declared, and it is imported at module load (`orders.py:2`). If it is missing in an environment, `orders` and `handlers` fail to import.
- Other callers of `cancel_order`. The PR says `handlers.cancel` is the only one, but only the base files were supplied, so I could not confirm it. Making `actor` required would break any other caller.
- Real `db` implementation (transaction support) and CI check results.

**Close-out (for the author or closer to complete):** no adjudication exists yet.

**MERGE RECOMMENDATION:** merge after fixes. Before merge:
1. Confirm the `company_audit.record` contract and that it raises on failure (finding 1).
2. Decide how to handle ordering and atomicity (findings 2 and 3), or defer 2 and 3 with tracking issues, since both are P2.
3. Confirm the dependency is declared and that CI checks are green.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "unverified",
      "location": "orders.py:16",
      "scenario": "The guarantee that a failed audit write leaves the order open depends on company_audit.record raising on failure. The library was not provided and tests stub it. If it returns an error value, swallows errors or writes asynchronously, the order is cancelled without a record.",
      "fix": "Confirm the real record() signature and failure semantics. Add a contract test against the real library or its documented failure mode."
    },
    {
      "severity": "P2",
      "evidence_level": "confirmed_by_reading",
      "location": "orders.py:16-17",
      "scenario": "record() runs before db.set_status() with no shared transaction. If set_status raises, the audit log shows order.cancelled for an order that is still open, and a retry writes a duplicate record.",
      "fix": "Write the audit record and the status change in one transaction, or add a compensating entry on failure. Test with a set_status that raises."
    },
    {
      "severity": "P2",
      "evidence_level": "confirmed_by_reading",
      "location": "orders.py:11-17",
      "scenario": "Check-then-act race: two concurrent cancels of the same open order both see status open and both write an audit record, possibly with different actors. set_status is unconditional.",
      "fix": "Use a conditional update (WHERE status = 'open') or a row lock, and record only if the update changed a row. Add a two-thread test."
    },
    {
      "severity": "P3",
      "evidence_level": "confirmed_by_reading",
      "location": "tests/test_orders.py:56",
      "scenario": "test_cancelling_twice_records_once only cancels an already-cancelled order once, and the global sys.modules stub is never removed.",
      "fix": "Cancel an open order twice, add a set_status failure case, and scope the stub to the test."
    }
  ]
}
```