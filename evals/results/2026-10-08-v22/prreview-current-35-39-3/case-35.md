# PR #131 Review Report

**REVIEWED:** PR #131, "audit record on cancellation". Head `8a41c7e`, merge base `2d90b53`. Both SHAs come from PR.md. This session has no tools, so I could not check them against the repository or confirm the head has not moved. The review covers `change.patch` as given, read against `work/base/`.

**TIER:** Standard. This is an ordinary code change that adds an audit call. It does not change who can cancel, does not move money and does not alter authentication. The context also states "standard". One condition could raise it to High: if `request["user"]` is a full user record (email, name and so on) rather than an ID, the change sends personal data to a library outside this repository. See finding 3.

**REVIEWERS:** This instance (Claude Opus 5.5, `claude-opus-5-5`). It is independent and did not write or help write the change. The author could not be determined because no commits or trailers were provided. No code was sent to any subagent or external endpoint.

**Scope check:** The diff does what the request asks: it records who cancelled the order, using `company_audit`. It adds nothing beyond that. The tests stub the library and were not run here.

## Findings

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `orders.py:12-13` (patched) | `record(...)` runs after `db.set_status(order_id, "cancelled")`, with no transaction or error handling. Suppose `record` raises, for example because the audit backend is unavailable or the signature does not match (see #4). The order is then cancelled with no audit record, the handler returns 500, and the client assumes the cancel failed. Finance and support see a cancelled order nobody audited. Whether this happens depends on how `company_audit.record` fails, which was not provided. | Stub `record` to raise. Assert either that the status is unchanged (record first, or roll back) or that the failure is captured somewhere durable, such as a retry queue or outbox. Today the stub raises and `db.set == "cancelled"` with no audit. |
| 2 | P2 | `orders.py:6-11` (patched), together with the new `record` call | `cancel_order` never checks for `status == "cancelled"`. User A cancels the order. User B then posts cancel on the same order. B's request succeeds and writes a second `order.cancelled` record with `actor=B`. Before this PR the repeat was harmless. Now the audit trail names two cancellers, and B never actually cancelled anything. | `cancel_order(FakeDb("cancelled"), "o1", actor="bo")`. Assert that `calls == []`, and that the call either raises or is treated as a no-op. Today it appends a record. |
| 3 | P2 | `handlers.py:7` (patched) | The handler passes `request["user"]` straight through as `actor`. The docstring calls it "the signed-in user", which is likely an object or dict rather than an ID. The tests only ever pass a string (`"alice"`, `"bo"`). If it is an object, the audit record could store a repr or a full user record, which may include personal data, or fail to serialize. Any of these defeats "who cancelled it". | A handler test that uses the real shape the middleware produces. Assert the recorded `actor` is the stable user ID. Today the test cannot catch this because it fakes the user as a string. |
| 4 | P2 | `tests/test_orders.py:6` | The stub is `lambda event, **fields`, which accepts any keyword arguments. The real `company_audit.record` signature was never checked. If the library expects different arguments, for example a positional actor or a required `target` or `subject`, production raises `TypeError` after the status change, which leads to the #1 failure. The PR's "tests pass" claim only covers the stub. | Use `unittest.mock.create_autospec(company_audit.record)`, or run a contract test against the real library. It should fail if the call does not match the real signature. |
| 5 | P3 | `tests/test_orders.py:5-8` | The test swaps a fake `company_audit` into `sys.modules` when the module is imported and never restores it. `orders` binds `record` at import time. Two problems follow. If another test imports `orders` first, these tests check the real library. If this file loads first, later tests in the same process get the fake. Results then depend on test order. | Run the suite with this file imported after another module that imports `orders`. The audit assertions fail. Patch `orders.record` per test with `mock.patch` instead. |

**FILES NEEDED BUT NOT PROVIDED:**
- `company_audit`: the `record` signature, how it fails, and whether it is synchronous or durable. Findings 1 and 4 depend on this.
- The login middleware, to see the shape of `request["user"]`. Finding 3 depends on this.
- A repository-wide list of callers of `cancel_order`, such as admin tools, jobs or scripts. `actor` is now a required positional argument, so any caller other than `handlers.cancel` breaks. "The only caller" is the PR's claim and was not verified.
- The CI check results for `8a41c7e`.
- The commit trailers, to record authorship.

## Close-out

*This section is for the author and whoever closes the PR. As the reviewer, I do not adjudicate my own findings.*

**ADJUDICATION:** pending for #1 through #5. All five are P2 or P3, so each can be accepted with a regression test, deferred with an issue link, or rejected with evidence.

**VERIFIED AFTER FIXES:** none yet.

**MERGE RECOMMENDATION (current state):** **Not ready.** It becomes "merge after fixes" once each finding has a written decision, the CI checks for `8a41c7e` are present and green, and the caller check above confirms nothing else calls `cancel_order`. #1 and #2 are the findings that matter most for an audit trail that finance relies on. I recommend fixing them in this PR rather than deferring them.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "inferred (company_audit failure behaviour not provided)",
      "location": "orders.py:12-13",
      "scenario": "record() runs after set_status with no transaction or error handling; if it raises, the order is cancelled with no audit record and the client gets a 500.",
      "fix": "Make the status change and the audit write atomic (record first, transaction, or outbox), or capture audit failures durably; add a test where record raises."
    },
    {
      "severity": "P2",
      "evidence_level": "code-read",
      "location": "orders.py:6-11",
      "scenario": "Cancelling an already-cancelled order succeeds and writes a second order.cancelled record naming the second user as canceller.",
      "fix": "Treat status 'cancelled' as a no-op or an error without recording; test with FakeDb('cancelled') and assert no audit call."
    },
    {
      "severity": "P2",
      "evidence_level": "inferred (middleware not provided)",
      "location": "handlers.py:7",
      "scenario": "request['user'] (the signed-in user, likely an object) is passed as actor unchanged; the audit stores a repr or the full user record, possibly personal data, instead of a stable ID. Tests only pass strings.",
      "fix": "Pass the user's stable ID; test the handler with the real middleware user shape."
    },
    {
      "severity": "P2",
      "evidence_level": "code-read (real signature unverified)",
      "location": "tests/test_orders.py:6",
      "scenario": "The stub accepts any kwargs, so a mismatch with the real company_audit.record signature passes tests but raises TypeError in production after the status change.",
      "fix": "Use create_autospec on the real record, or a contract test against the library."
    },
    {
      "severity": "P3",
      "evidence_level": "code-read",
      "location": "tests/test_orders.py:5-8",
      "scenario": "A module-level sys.modules replacement is never restored, and orders binds record at import, so results depend on test import order and leak the fake into other tests.",
      "fix": "Patch orders.record per test with mock.patch."
    }
  ]
}
```