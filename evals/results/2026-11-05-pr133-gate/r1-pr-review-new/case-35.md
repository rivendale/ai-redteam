# PR Review: PR #131, audit record on cancellation

**REVIEWED:** PR #131, head `8a41c7e`, merge base `2d90b53`. Both SHAs come from PR.md. I could not check them against a repository, so they are the author's assertion. I reviewed only `change.patch` and `work/base/`, and no later commits.

**TIER:** Standard. The change touches an audit trail used by support and finance, and the actor id is a user identifier. It does not touch auth, permissions, secrets, migrations or money movement. The context also states standard stakes. I'm taking one model round. If the unseen `company_audit` library turns out to handle personal data under a retention rule, re-tier to High.

**REVIEWERS:** One review round, by Claude Sonnet 5.5 in a separate session with no memory of writing the change. The author is not identifiable: no commit trailers (`Co-Authored-By`) were provided. Step 3 (approved endpoint) was met by reviewing only the code supplied in-session, and nothing was sent elsewhere. No instruction files (`AGENTS.md`, `CLAUDE.md`, skill files) appear in the supplied material, and nothing in the PR text addresses the reviewer. I could not run anything, so "tests pass" is unverified. By reading, the five tests should pass against their stub.

## FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `orders.py:16-17` | The audit record is written before `db.set_status`. If `set_status` raises (DB error, timeout), the audit log says "order.cancelled" for an order that is still open. Support and finance would then see a cancellation that never happened. The docstring only guarantees the opposite direction. | A fake db whose `set_status` raises. Assert the caller sees the error and decide the intended behavior: either a compensating or "failed" audit event, or a shared transaction with the audit write. Today nothing covers this path. |
| 2 | P2 | `orders.py:14-17` | Two concurrent cancels of the same open order both read `status == "open"`, both pass the check, and both call `record`. Two audit records are written for one cancellation. "Cancelling twice records once" is tested only sequentially. | Two interleaved calls against a fake db that returns "open" to both. Expect one audit record, or a conditional update (`UPDATE … WHERE status='open'`) whose result gates the record. |
| 3 | P2 (UNVERIFIED) | `orders.py:2`, `orders.py:16` | The central claim, "a failed audit write leaves the order open", rests on `record` raising on failure. The tests stub `company_audit` with a function that raises. The real library was not provided. If it buffers, swallows errors, returns a status flag, or has a different signature (positional arguments, required fields, a different keyword name than `order_id`/`actor`), the guarantee fails or the call raises `TypeError` in production. | A contract test against the real `company_audit` in a sandbox. Assert the accepted signature and that a failed write raises. |
| 4 | P3 | `handlers.py:7` | Nothing validates that `request["user"]` is a non-empty string. If the middleware is bypassed or sets `None` or `""`, the order is cancelled and an audit record is written with an empty actor, which defeats the purpose of "who cancelled it". A missing key raises `KeyError` before any change, which is safe. | Call `handlers.cancel` with `user=None` and `user=""`. Expect a refusal and no cancellation. |
| 5 | P3 | `orders.py:6` | `actor` is now required. The PR says `handlers.cancel` is the only caller, but only `handlers.py` and `orders.py` were supplied. Any other caller (a job, admin script or other service) would raise `TypeError`. | Repo-wide search for `cancel_order(`, plus an import-time test of every caller. |
| 6 | P3 | `orders.py:2`, `tests/test_orders.py:13` | The new import-time dependency on `company_audit` has no visible declaration, version pin or manifest change in the diff. An environment without it fails with `ImportError` when `orders` is imported, which breaks the whole service. The tests also overwrite `sys.modules["company_audit"]` globally at import, which can mask the real module in a combined test run. | A smoke test importing `orders` in a clean environment without the stub. Make the stub scoped, for example with `unittest.mock.patch.dict`. |

**Checked and not findings:**
- The change matches the request: an audit record with the actor, using the shared library, and nothing extra.
- Sentence-by-sentence, the docstring and PR text match the code: the order stays open if the audit write raises, and nothing is recorded for an already-cancelled or shipped order.
- The handler passes `request["user"]` as documented.

**FILES NEEDED BUT NOT PROVIDED:**
- The `company_audit` source or its documented contract (finding 3).
- The dependency manifest or lockfile (finding 6).
- The rest of the repository, to confirm the only-caller claim (finding 5).
- The `db` implementation, to establish transactional behavior (findings 1 and 2).
- CI check results. Step 8's requirement that every expected check is present and green cannot be confirmed.
- Commit trailers.

## Close-out (pending)

The author adjudicates findings 1-6, and whoever closes the PR writes the adjudication table. I do not adjudicate my own findings.

**MERGE RECOMMENDATION: merge after fixes.** Finding 3 must be resolved first by confirming the real `record` contract. Findings 1 and 2 need either a fix or a deferral with a tracking issue (P2 only). Findings 4-6 can be fixed or deferred. Any fix is verified by a targeted read of the correction diff and its tests, not another full review. No written rule beyond the skill's Step 8 gates covers this. Those gates are not yet met: CI status is unknown, and the library contract is unverified.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "code-read",
      "location": "orders.py:16-17",
      "scenario": "record() runs before db.set_status; if set_status raises, an 'order.cancelled' audit record exists for an order that is still open.",
      "fix": "Write the audit record and status change in one transaction, or emit a compensating audit event; add a test where set_status raises."
    },
    {
      "severity": "P2",
      "evidence_level": "code-read",
      "location": "orders.py:14-17",
      "scenario": "Two concurrent cancels both read status 'open' and both call record(), producing duplicate audit records for one cancellation.",
      "fix": "Use a conditional update (WHERE status='open') and record only when it changed a row; add a concurrency test."
    },
    {
      "severity": "P2",
      "evidence_level": "unverified",
      "location": "orders.py:2, orders.py:16",
      "scenario": "company_audit was not provided and tests stub it. If the real record() swallows errors, buffers, or has a different signature, the 'failed audit leaves order open' guarantee or the call itself fails in production.",
      "fix": "Confirm the real record() signature and failure behavior from its source or docs; add a contract test against the real library."
    },
    {
      "severity": "P3",
      "evidence_level": "code-read",
      "location": "handlers.py:7",
      "scenario": "A None or empty request['user'] cancels the order and writes an audit record with no real actor.",
      "fix": "Validate actor is a non-empty string before cancelling; add tests for None and ''."
    },
    {
      "severity": "P3",
      "evidence_level": "unverified",
      "location": "orders.py:6",
      "scenario": "actor is now required; any caller other than handlers.cancel (not shown) raises TypeError.",
      "fix": "Search the whole repo for cancel_order callers and update or test them."
    },
    {
      "severity": "P3",
      "evidence_level": "code-read",
      "location": "orders.py:2, tests/test_orders.py:13",
      "scenario": "The new company_audit dependency has no visible declaration or pin, so a clean environment hits ImportError on import orders; the test also replaces sys.modules globally.",
      "fix": "Declare and pin the dependency; scope the stub with unittest.mock.patch.dict and add an import smoke test."
    }
  ]
}
```