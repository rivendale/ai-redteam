# PR review: #131, audit record on cancellation

## Review report

**REVIEWED:** PR #131 at head `8a41c7e`, merge base `2d90b53`. These SHAs come from PR.md. I could not check them against a checkout because this session has no tools. I reviewed the supplied `change.patch` against `work/base/`. Commits after `8a41c7e` are not covered.

**TIER:** Standard. The change adds an audit call and a required parameter. It does not touch authentication, permissions, secrets, network exposure, migrations or money movement. The actor value comes from the session the service already holds and goes to the company's own audit library. This matches the owner's "stakes: standard". If `request["user"]` turns out to carry personal data beyond an identifier (see finding 3 and the files list), the tier becomes High and needs a second round.

**REVIEWERS:**
- Reviewer: this instance (Claude Opus 5.5), one round, with no part in writing the change.
- Author: unknown. The commit trailers were not provided.
- Data: no code was sent to any other endpoint.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `orders.py:12–13` (`db.set_status` then `record(...)`) | **Not atomic.** The status is written before the audit call. Suppose `company_audit.record` raises, for example because the audit backend is down or the signature differs from this call. Then the order is already `cancelled`, `cancel_order` raises, and the handler returns an error. The result is a cancelled order with no audit record, and a client told the cancel failed. Whether `record` can raise is unknown because the library was not provided. | Stub `record` to raise. Assert that either the status is not `cancelled` (audit first, or a transaction that rolls back), or the failure is handled and reported. This fails today: `db.set == "cancelled"` and the exception propagates. |
| 2 | P2 | `orders.py:6–11` (no check for `status == "cancelled"`) | **Duplicate, misleading audit records.** Alice cancels order o1, then Bo (or a retry after finding 1) calls cancel on the already-cancelled order. A second `order.cancelled` record is written with `actor="bo"`. Support and finance now see two cancellations by two people. Before this PR the repeat was a harmless no-op. | Call `cancel_order(FakeDb("cancelled"), "o1", actor="bo")`. Assert that no record is written, or that a `ValueError` is raised. This fails today: one record is written. |
| 3 | P3 | `tests/test_orders.py:6`, `handlers.py:7` | **Tests only confirm the code calls the stub.** The stub accepts any `**fields`, and the tests pass the user as a plain string (`"bo"`). Nothing checks the real `record` signature, the event name, or the real shape of `request["user"]`. If the middleware sets a user object, or the library expects `actor_id=`, the tests stay green and production fails or records the wrong value. The "Tests pass" claim is therefore weak evidence for the integration. | Add a contract test against the real `company_audit.record`, or its published interface or fake. Pass a middleware-shaped `request["user"]` and assert that the stored actor is the user identifier. |

**FILES NEEDED BUT NOT PROVIDED:**
- `company_audit`: the signature of `record`, whether it raises or swallows errors, and whether it is synchronous. Findings 1 and 3 depend on this.
- The login middleware: what `request["user"]` holds (an id or a full user object with personal data), and whether it can be absent. This decides the tier and finding 3.
- A repository-wide search for other callers of `cancel_order`, such as admin scripts or jobs. The PR claims `handlers.cancel` is the only caller, but `actor` is now required and positional, so any other caller fails with a `TypeError`.
- CI status for `8a41c7e`. I could not run the tests.

The change does what was asked: it records who cancelled, using the shared library. It adds nothing beyond that.

## Close-out

**ADJUDICATION:** Pending. The author decides on findings 1–3; a reviewer does not adjudicate its own findings.

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | — | — |
| 2 | — | — |
| 3 | — | — |

**VERIFIED AFTER FIXES:** Nothing yet.

**MERGE RECOMMENDATION:** Merge after fixes. There are no P0 or P1 findings, and the single Standard round has run. Merge only when all of the following hold:

- Findings 1–3 each have a written decision. Findings 1 and 2 matter because these records are used by finance.
- The other-callers search confirms `handlers.cancel` is the only caller.
- Every expected CI check on the final head is present and green.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "inferred from code; company_audit failure behaviour not provided",
      "location": "orders.py:12-13",
      "scenario": "record() raises after db.set_status: the order stays cancelled with no audit record, and the caller gets an error.",
      "fix": "Write the audit inside the same transaction as the status change, or record before committing, or handle and surface the audit failure. Add a test with a raising stub."
    },
    {
      "severity": "P2",
      "evidence_level": "confirmed by reading orders.py",
      "location": "orders.py:6-11",
      "scenario": "Cancelling an already-cancelled order writes a second order.cancelled record, possibly with a different actor, which misleads support and finance.",
      "fix": "Refuse or no-op when status is already 'cancelled' and skip the audit. Add a test for a repeat cancel."
    },
    {
      "severity": "P3",
      "evidence_level": "confirmed by reading tests; real library and middleware not provided",
      "location": "tests/test_orders.py:6, handlers.py:7",
      "scenario": "The permissive stub and string user hide a mismatch with the real record() signature or the real request['user'] shape.",
      "fix": "Add a contract test against the real company_audit interface with a middleware-shaped user."
    }
  ]
}
```