**Review report**

**REVIEWED:** PR #131, head `8a41c7e`, merge base `2d90b53`.
- Both SHAs are taken from PR.md, the author's own statement. I had no repository and could not confirm them or check out a worktree. This review covers exactly the text of `work/change.patch` against `work/base/`.
- I had no tools, so I did not run the tests. "Tests pass" remains the author's claim.

**TIER:** Standard.
- The change adds an audit write to an ordinary code path.
- It does not touch authentication, permissions, secrets, network exposure, migrations or money movement. Cancellation is a state change, not a payment.
- The audit records do feed support and finance, which raises the weight of record-integrity findings but not the tier.
- Data: the code and the user ids it handles stayed in this session. Nothing was sent to a subagent or an external endpoint.

**REVIEWERS:**
- Reviewer: this instance (Claude Opus 5.5, `claude-opus-5-5`). It did not write or help write the change and has no memory of authoring it.
- Author: unknown. No commits or trailers were provided, so there is no `Co-Authored-By` to read.

**Scope check against the request:** The PR records who cancelled the order (`actor` = signed-in user id) and uses the shared library. It adds nothing beyond the request. One caveat: whether it uses that library *correctly* cannot be verified (finding 1).

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 | `orders.py:16`, `tests/test_orders.py:9-15` | The call `record("order.cancelled", order_id=..., actor=...)` is checked only against a hand-written stub, `_record(event, **fields)`. That stub accepts any keyword arguments. If the real `company_audit.record` has a different signature (e.g. a required `fields` dict, different kwarg names, or a required `tenant`/`source`), the call raises `TypeError` in production. The audit write happens before the status change, so **every** cancellation would then fail: an outage of the cancel endpoint that the test suite cannot catch. The real library was not provided, so I can't tell whether this happens. | A contract test that replaces the stub with `unittest.mock.create_autospec(company_audit.record)` built from the real library (or a test against the real library in a sandbox), then cancels an order. It fails today if the signature is wrong and passes once the call matches. |
| 2 | P2 | `orders.py:9-17` | Two cancel requests for the same open order arrive concurrently, e.g. a double-click or a client retry. Both read `status == "open"`, both call `record`, and both call `set_status`. The result is two `order.cancelled` audit records for one cancellation, possibly with two different actors if support and the customer both clicked. This contradicts the PR's claim "cancelling twice records once", which holds only when the calls are sequential. The read-check-write sequence is not atomic. | A FakeDb whose `get_order` returns `"open"` on both calls, simulating the interleaving. Call `cancel_order` twice and assert `len(calls) == 1`. This fails today. It passes once the status change is a conditional update (`UPDATE … WHERE status='open'`, checking the affected row count) and the record is written only for the winner, ideally in the same transaction or through an outbox. |
| 3 | P2 | `orders.py:16-17` | `record` succeeds, then `db.set_status` raises (DB timeout, constraint error, connection drop). The order stays open, but the audit trail says it was cancelled, by whom and when. Support and finance would read a cancellation that never happened. The PR covers only the opposite failure (audit fails, so the order stays open). | A FakeDb whose `set_status` raises. Call `cancel_order`, expect the exception, and assert `calls == []`, or that a compensating/failed event was recorded, depending on the chosen design. This fails today. |
| 4 | P3 | `tests/test_orders.py:15-17` | The stub is installed in `sys.modules` at import time, and `orders` binds `record` with `from company_audit import record`. Suppose another test module imports `orders` (with the real library) before this one runs, for example under pytest collection order. Then this module's stub is never used, and the tests call the real audit library. The stub is also never removed, so it leaks into every later test in the same process. | Import `orders` with a sentinel `company_audit` first, then import this test module, and assert that `orders.record is _record`. This fails under that ordering. The fix is `mock.patch("orders.record")` per test. |

**FILES NEEDED BUT NOT PROVIDED:**
- `company_audit`: the source or API documentation for `record`, needed to settle finding 1.
- The `db` implementation: to see whether `get_order`/`set_status` run inside a transaction or support a conditional update (findings 2 and 3).
- The login middleware: to confirm `request["user"]` is always set on this route.
- The commit log with trailers, for authorship.

No text in the PR, diff or files addressed the reviewer, so there is no prompt-injection finding.

---

**Close-out**

Not written. Per the skill, the author adjudicates these findings and whoever closes the PR writes the close-out. A reviewer does not adjudicate its own findings.

**ADJUDICATION:** pending for findings 1–4.

**VERIFIED AFTER FIXES:** none yet.

**MERGE RECOMMENDATION (provisional, from the reviewer):** do not merge yet.
- Finding 1 is P1, so it cannot be deferred. It must be fixed (a contract test against the real `record` signature) or rejected with evidence from `company_audit`.
- Findings 2 and 3 are P2. They need a fix or a tracked issue each.
- No CI check results were provided. A missing check is not green.

```json
{
  "verdict": "do_not_merge_yet",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "inferred (company_audit not provided; test stub accepts any kwargs)",
      "location": "orders.py:16, tests/test_orders.py:9-15",
      "scenario": "If the real company_audit.record signature differs from record(event, order_id=, actor=), every cancel raises TypeError before set_status, so all cancellations fail; the permissive stub cannot detect this.",
      "fix": "Verify the call against the real library and add a contract test using create_autospec(company_audit.record)."
    },
    {
      "severity": "P2",
      "evidence_level": "read from code",
      "location": "orders.py:9-17",
      "scenario": "Two concurrent cancels both read status 'open' and each writes an order.cancelled record, giving duplicate (possibly conflicting-actor) audit entries.",
      "fix": "Use a conditional status update (WHERE status='open') and record only when it changed a row, in the same transaction or via an outbox."
    },
    {
      "severity": "P2",
      "evidence_level": "read from code",
      "location": "orders.py:16-17",
      "scenario": "record succeeds, then db.set_status raises; the order stays open but the audit trail says it was cancelled.",
      "fix": "Write the record and status change atomically (transaction/outbox) or record a compensating failure event; add a test with a failing set_status."
    },
    {
      "severity": "P3",
      "evidence_level": "read from code",
      "location": "tests/test_orders.py:15-17",
      "scenario": "If orders is imported before this test module, the sys.modules stub is bypassed and the real audit library is called; the stub also leaks to later tests.",
      "fix": "Patch orders.record per test with unittest.mock.patch instead of a module-level sys.modules assignment."
    }
  ]
}
```