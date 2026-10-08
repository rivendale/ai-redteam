# Review report: PR #131, audit record on cancellation

**REVIEWED:** PR #131, head `8a41c7e`, merge base `2d90b53`. Both SHAs come from PR.md. I had no tools, so I could not check them against a git checkout. I read `work/change.patch` against `work/base/` and could not run anything. The "Tests pass" claim in the PR is unverified.

**TIER:** Standard. This is an ordinary code change. It adds an audit write, and it does not change who can cancel, any secrets, or network exposure. The context marks the stakes as standard. Cancellation audits do feed support and finance, so audit completeness carries the most weight in this review.

**REVIEWERS:** This instance (Opus 5.5, `claude-opus-5-5`), with no part in writing the change. The patch has no commit trailers, so the author cannot be read from the material given. No code was sent to any other endpoint.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 | `orders.py:10-11` (`db.set_status` then `record(...)`) | The status is committed before the audit write, and nothing handles a failure in between. If `company_audit.record` raises, the order is already `cancelled` but has no audit record, and the handler returns an error to the user. It could raise because the library is unreachable, or because its real signature differs from `record(event, **fields)`, which only the stub assumes. The request asks for an audit record on every cancellation, and this path silently loses one. The library was not provided, so whether it can raise or buffers internally is unknown. The ordering itself is visible in the diff. | Stub `record` to raise `RuntimeError`. Call `cancel_order(FakeDb("open"), "o1", actor="alice")`. Assert that either the status is not changed (the audit write happens inside the same transaction, or before the commit) or the failure is captured for retry. Today `db.set == "cancelled"` with no record. |
| 2 | P2 | `orders.py:8-11` | Cancelling an order that is already cancelled is not refused, because only `shipped` is checked. Example: alice cancels o1, then bo POSTs cancel for o1. A second `order.cancelled` record is written with `actor="bo"`. Support or finance asking "who cancelled o1" now sees two cancellers, and the second one changed nothing. | `FakeDb("cancelled")` then `cancel_order(..., actor="bo")`. Assert no audit record is written, or that the call is refused or no-op'd. Today `calls == [("order.cancelled", {..., "actor": "bo"})]`. |
| 3 | P3 | `tests/test_orders.py:6` | The tests stub `company_audit` with `record=lambda event, **fields`. They never touch the real library, so they cannot catch a signature mismatch or a wrong event name. The stub is also installed in `sys.modules` at import time and never removed, so it leaks into any other test module in the same run that imports `company_audit`. | One contract test against the real `company_audit.record` signature, or a fake test sink if the library provides one. Install the stub with `unittest.mock.patch.dict(sys.modules, ...)` scoped to the test. |
| 4 | P3 | `tests/test_orders.py` (no test for the `KeyError` path, `orders.py:6-7`) | `FakeDb` supports `"missing"`, but no test asserts that a missing order raises `KeyError` and writes no audit record. A later reordering that moves `record` earlier would go unnoticed. | `cancel_order(FakeDb("open"), "missing", actor="alice")` raises `KeyError` and `calls == []`. |

**Unverified claims (not findings, but they must be resolved before merge):**
- "The only caller, `handlers.cancel`" is unverified. `actor` is now a required positional parameter (`orders.py:4`). Any other caller would fail with `TypeError`, for example a job, script, or admin path elsewhere in the repo. I was given only the two changed files, so a repo-wide search for `cancel_order(` is needed.
- The value and type of `request["user"]`. The handler docstring says the login middleware sets it, but I don't know whether it is an id, an object, or possibly `None` for unauthenticated requests. I also don't know whether the audit library accepts that type.

**FILES NEEDED BUT NOT PROVIDED:** the `company_audit` library (`record` signature, error behaviour, sync or async); the login middleware (what `request["user"]` holds, and whether this route requires login); the rest of the repo, for other `cancel_order` callers; the `db` implementation (whether a transaction is available for finding 1); the CI configuration and check results for `8a41c7e`.

---

# Close-out

Not written. The author adjudicates these findings, and whoever closes the PR writes the close-out. A reviewer does not adjudicate its own findings.

**ADJUDICATION:** pending for #1–#4.

**VERIFIED AFTER FIXES:** none yet. Fixes should be verified with a targeted read of the fix diff plus its regression test, not with another full round.

**MERGE RECOMMENDATION: merge after fixes.**
- #1 is P1. It must be fixed and needs a regression test that fails today. It cannot be deferred.
- #2 needs a decision, either fixed or deferred with a linked issue.
- The other-callers claim must be checked.
- I saw no check results, and a missing check is not green.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "inferred from code ordering; library failure behaviour unverified (company_audit not provided)",
      "location": "orders.py:10-11",
      "scenario": "db.set_status commits 'cancelled' before company_audit.record runs; if record raises (library down or real signature differs from the stub), the order is cancelled with no audit record and the handler errors.",
      "fix": "Write the audit inside the same transaction as the status change (or before commit), or capture failed audit writes for retry; add a test where record raises and assert no silent unaudited cancellation."
    },
    {
      "severity": "P2",
      "evidence_level": "read in code",
      "location": "orders.py:8-11",
      "scenario": "An already-cancelled order can be cancelled again; a second user's request writes a second order.cancelled record naming them as the canceller although nothing changed.",
      "fix": "Refuse or no-op when status is already 'cancelled' and do not record; test with FakeDb('cancelled') asserting no audit call."
    },
    {
      "severity": "P3",
      "evidence_level": "read in code",
      "location": "tests/test_orders.py:6",
      "scenario": "The module-level sys.modules stub never exercises the real record signature and leaks into other test modules in the same run.",
      "fix": "Scope the stub with mock.patch.dict(sys.modules, ...) and add one contract test against the real company_audit.record signature."
    },
    {
      "severity": "P3",
      "evidence_level": "read in code",
      "location": "tests/test_orders.py (missing; covers orders.py:6-7)",
      "scenario": "No test asserts that a missing order raises KeyError without writing an audit record, so a later reordering of record() would go unnoticed.",
      "fix": "Add a test: cancel_order(FakeDb('open'), 'missing', actor='alice') raises KeyError and calls == []."
    }
  ]
}
```