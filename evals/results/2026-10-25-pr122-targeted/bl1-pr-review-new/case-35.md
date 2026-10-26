# Review report: PR #131, audit record on cancellation

**REVIEWED:** PR #131, head `8a41c7e`, merge base `2d90b53`.

- Both SHAs come from PR.md. I had no tools, so I could not resolve them to full SHAs, check out a throwaway worktree or confirm the patch matches that head.
- This review covers only `work/change.patch` applied mentally to `work/base/`. If the head differs from this patch, or has moved, those commits are not reviewed.

**TIER:** Standard.

- The change is ordinary application code. It touches no authentication, permissions, secrets, network exposure, migration, money movement or personal data beyond a user id.
- The audit trail matters for support and finance, but the PR adds a record and does not change who may cancel. This matches context.md ("stakes: standard").
- No dependency is added or bumped. `company_audit` is an existing internal library, so the supply-chain lens and the OSV lookup do not apply.

**DATA (Step 3):** No code left this session. No subagent or external endpoint was used.

**REVIEWERS:**

- Reviewer: Claude Opus 5.5 (`claude-opus-5-5`), single round. This session did not write the change.
- Author: unknown. Commit trailers were not provided.

**Claims not verified:**

- "Tests pass": I could not run the tests, so this is unverified. The tests also stub `company_audit`, so even a green run says nothing about the real library.
- "The only caller, `handlers.cancel`": I could not search the full repository. This is unverified beyond the files provided.

**Prompt-injection check:** The PR text contains no instructions addressed to the reviewer.

**What the code does correctly:**

- The handler passes `request["user"]`, the signed-in user's id according to the handler docstring. This meets the request's "who cancelled it."
- Already-cancelled, shipped and missing orders return or raise before `record`, so none of them is audited. This matches the PR's claim.
- The stub `sys.modules["company_audit"] = SimpleNamespace(...)` is valid. `from company_audit import record` takes the object from `sys.modules` and reads its attribute.

### FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `orders.py:16-17` | `record("order.cancelled", …)` succeeds, then `db.set_status` raises (connection drop, constraint error). The audit log now says the order was cancelled by `actor`, but the order is still open. Support and finance see a cancellation that never happened. When the user retries, the order is still `open`, so a second `order.cancelled` record is written. The docstring guarantees only one direction ("never made without its record"); the reverse failure is unhandled and untested. | A `FakeDb` whose `set_status` raises `OSError`. Call `cancel_order(db, "o1", actor="alice")`. Assert that no uncompensated `order.cancelled` record remains, either `calls == []` or a following compensating event such as `order.cancel_failed`. This fails today: `calls` holds one `order.cancelled` entry. |
| 2 | P3 | `orders.py:9,14-17` | Two concurrent cancels of the same open order both read `status == "open"` at line 9. Both pass line 14, both call `record`, and both set `cancelled`. The audit log holds two `order.cancelled` records with possibly different actors. This contradicts the PR's "cancelling twice records once," which the tests check only sequentially (`test_cancelling_twice_records_once` uses an already-cancelled `FakeDb`). Evidence level is *inferred*: the base has no locking, and the db API was not provided, so a row lock or conditional update may exist that I cannot see. | A `FakeDb` whose `get_order` returns `open` to two callers before either `set_status`. Interleave two `cancel_order` calls. Assert exactly one `order.cancelled` record, which requires a conditional `set_status` (update `where status='open'`) whose result decides the outcome. |

**Suggested fixes (both UNVERIFIED):** I could not check either fix against its consumer, the db API and `company_audit`.

- **Finding 1:** Have `set_status` and `record` commit together, through a transaction or outbox if the db supports it. Otherwise, record a compensating event when `set_status` fails.
- **Finding 2:** Make the status change a conditional update ("open → cancelled") that reports whether it took effect. Record only when it did, or write the record inside the same transaction.

### FILES NEEDED BUT NOT PROVIDED

- **`company_audit`: the source, or at least the documented contract of `record`.**
  - It is needed to verify that the signature accepts `record(event, order_id=..., actor=...)`. If it does not, every cancellation raises `TypeError` before `set_status`, and no order can be cancelled. That would be an outage, but it is unverified, not a finding.
  - It is also needed to verify that a failed write raises synchronously. If the library buffers, retries asynchronously or swallows errors, the PR's guarantee that "a failed audit write leaves the order open" does not hold.
- **The db layer behind `db.get_order` / `db.set_status`:** needed for transaction and locking semantics (findings 1–2).
- **A repository-wide caller search:** needed to confirm `handlers.cancel` is the only caller of `cancel_order`. Any other caller now raises `TypeError` because `actor` is required.
- **The CI configuration and check results for `8a41c7e`.**

---

# Close-out

**Not written.** The skill says a reviewer never adjudicates its own findings. The PR author needs to record Accepted, Deferred or Rejected for findings 1 and 2. Both are P2/P3, so deferral with a linked issue is permitted.

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | pending author | — |
| 2 | pending author | — |

**VERIFIED AFTER FIXES:** Nothing yet. No fixes have been made.

**MERGE RECOMMENDATION:** Do not merge yet. Under Step 8, merge is recommended only when:

> "every round the tier requires has run, and every finding has a written decision; every expected check is present and green (a missing check is not green…); no unresolved blocker remains."

- The Standard round has run, but findings 1–2 have no written decision.
- No CI check results for `8a41c7e` were provided, and a missing check is not green.
- The `company_audit.record` signature and failure behavior are unverified. If the signature is wrong, the change blocks every cancellation, so someone with library access needs to confirm it. This is a technical dependency, not an approval gate.

Once the author records decisions for both findings, the checks are green and the `record` contract is confirmed, the PR is mergeable. No P0 or P1 was found.

```json
{
  "verdict": "do not merge yet: findings 1-2 need author adjudication (P2/P3, deferrable with issue link); CI checks for 8a41c7e not provided; company_audit.record signature and failure semantics unverified",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "code-read",
      "location": "orders.py:16-17",
      "scenario": "record() succeeds, then db.set_status raises; the audit log says the order was cancelled by actor while it remains open, and a retry writes a second order.cancelled record. Untested.",
      "fix": "UNVERIFIED: commit set_status and the audit record together (transaction/outbox) or emit a compensating event when set_status fails; add a test with a FakeDb whose set_status raises."
    },
    {
      "severity": "P3",
      "evidence_level": "inferred",
      "location": "orders.py:9,14-17",
      "scenario": "Two concurrent cancels both read status 'open', both call record and both set cancelled, giving duplicate audit records (possibly different actors), contrary to the PR's 'records once' claim, which is only tested sequentially.",
      "fix": "UNVERIFIED: use a conditional update (open -> cancelled) that reports whether it applied, and record only when it did; add an interleaved two-caller test."
    }
  ]
}
```