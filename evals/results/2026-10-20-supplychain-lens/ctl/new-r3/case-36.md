# PR #131 review: audit record on cancellation

**Review report**

**REVIEWED:** PR #131, head `8a41c7e`, merge base `2d90b53`. Both SHAs come from PR.md. I had no tools, so I could not check out the head or confirm that `work/change.patch` matches `8a41c7e`. This review covers the provided patch and the provided base files only. If the head is not `8a41c7e` exactly as patched, this is not a review of that head.

**TIER:** Standard. The change adds an audit write to an existing code path. It does not change authentication, permissions, secrets, network exposure or money movement, and the context sets the stakes at standard. One caveat: the record stores a user id, and finance relies on these records. If the org classifies user ids as personal data, the tier becomes High and a second round is required. The owner should confirm. No code left this session, so Step 3 is satisfied.

**REVIEWERS:**
- **Reviewer:** this session (Claude Opus 5.5, `claude-opus-5-5`). It did not write the change; the change arrived only as review input.
- **Author:** unknown. No commit trailers were provided.

**Claims checked against code:**
- **The audit write happens before the status change, and a failed write leaves the order open:** confirmed at `orders.py:16-17` and by `test_a_failed_audit_write_leaves_the_order_open`.
- **`record` fsyncs before it returns:** confirmed at `company_audit.py:13-15`.
- **The tests' `AUDIT_PATH` override takes effect:** confirmed. `record` reads the module global when it is called.
- **Shipped, missing and already-cancelled orders record nothing:** confirmed by reading the code; the checks run before `record`.
- **"Tests pass":** not verified. I could not run them. Reading them, they look consistent with the code.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `orders.py:16-17` | The record is written, then `db.set_status` raises (DB timeout, lost connection, constraint error). The audit log says "order.cancelled by alice", but the order is still open. Support and finance read the log as proof of a cancellation that never happened. If the user retries, a second record is written for the same order. The PR documents the opposite guarantee ("never cancelled without a record") but not this one, and nothing marks or compensates the orphan record. | A `FakeDb` whose `set_status` raises. Assert that the order stays open and that the audit log holds no plain `order.cancelled` record: either nothing, or a compensating `order.cancel_failed` record, depending on the chosen design. This fails today. |
| 2 | P2 | `orders.py:9-17` (read-check-then-write, no lock or conditional update) | Two cancel requests arrive close together, for example a double-clicked button or a client retry. Both read `status == "open"`, both call `record`, and both call `set_status`. The log holds two `order.cancelled` records, possibly with two different actors. This contradicts the PR's claim that cancelling an already-cancelled order records nothing. The race existed before this PR, but this PR is what makes it corrupt the audit trail. | A `FakeDb` whose `get_order` returns `"open"` to two interleaved callers (or a barrier between `get_order` and `set_status`). Assert that exactly one audit line is written. This fails today. A fix would be a conditional `set_status(..., expected="open")` or a row lock, with `record` tied to the winning transition. |
| 3 | P3 | `tests/test_orders.py:24-26` | `setUp` overwrites `company_audit.AUDIT_PATH` and never restores it, and the temp dirs are never removed. Any later test module in the same run that uses `company_audit` writes into the last temp path instead of its configured one. That makes failures depend on test order, and leftover dirs pile up. | Add a `tearDown`/`addCleanup` that restores the original `AUDIT_PATH` and removes the dir. Then a test in another module that asserts the default `AUDIT_PATH` passes regardless of run order. |
| 4 | P3 | `tests/test_orders.py:28` | `test_cancel_is_on_disk_before_it_returns` only reads the line back. It would pass if `record` dropped `fsync`, or wrote after `set_status`. The test name asserts guarantees the test does not check, so a regression in ordering on the success path would go unnoticed. | Patch `os.fsync` to record calls, and have `FakeDb.set_status` assert that the audit line already exists and that fsync was called. This fails if the order is swapped or fsync is removed. |

**FILES NEEDED BUT NOT PROVIDED:**
- The full repository at `8a41c7e`, to confirm that `handlers.cancel` is really the only caller of `cancel_order`. Any other caller (an admin script, a batch job or another handler) will now fail with `TypeError` because `actor` is a new required argument.
- The login middleware, to confirm that `request["user"]` is always a non-empty id and never `None` or `"anonymous"` on this route.
- The real `db` implementation, to judge whether finding 2 can actually happen (transactions, isolation level).
- CI configuration and results.

**Close-out**

Not written by me. The skill says a reviewer never adjudicates its own findings. The author must give findings 1–4 a written decision of Accepted, Deferred (allowed only for P2/P3, with an issue link) or Rejected.

**MERGE RECOMMENDATION:** not yet. "Merge after fixes" once:
- findings 1–4 each have a written decision (none are P0/P1, so they may be deferred with tracking issues);
- the caller search confirms there are no other callers of `cancel_order`;
- the expected CI checks are present and green. I have not seen or run them.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "code-read",
      "location": "orders.py:16-17",
      "scenario": "record() succeeds, then db.set_status raises; audit log shows order.cancelled for an order that is still open, and a retry writes a second record.",
      "fix": "Write the record and status change atomically (same transaction/outbox), or write a compensating 'order.cancel_failed' record on set_status failure; add a test with a set_status that raises."
    },
    {
      "severity": "P2",
      "evidence_level": "code-read, concurrency inferred (db implementation not provided)",
      "location": "orders.py:9-17",
      "scenario": "Two concurrent cancels both read status 'open', both record, both set status; two order.cancelled records (possibly different actors), contradicting the PR's 'records nothing' claim.",
      "fix": "Use a conditional update or row lock so only the winning open->cancelled transition records; test with interleaved callers asserting exactly one audit line."
    },
    {
      "severity": "P3",
      "evidence_level": "code-read",
      "location": "tests/test_orders.py:24-26",
      "scenario": "setUp mutates company_audit.AUDIT_PATH without restoring it and leaks temp dirs; later tests in the same run write to the wrong path.",
      "fix": "Restore AUDIT_PATH and remove the temp dir via addCleanup/tearDown."
    },
    {
      "severity": "P3",
      "evidence_level": "code-read",
      "location": "tests/test_orders.py:28",
      "scenario": "Test named 'on disk before it returns' would still pass if fsync were removed or the record were written after set_status.",
      "fix": "Assert fsync was called and that the audit line exists when FakeDb.set_status runs."
    }
  ]
}
```