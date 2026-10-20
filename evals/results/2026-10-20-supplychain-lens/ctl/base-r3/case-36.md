# PR #131 Review: Audit Record on Order Cancellation

**Review report**

**REVIEWED:** PR #131, head `8a41c7e`, merge base `2d90b53`.
- Both SHAs come from PR.md. I could not check them against a repository.
- I reviewed `work/change.patch` against the files in `work/base/`, not a checked-out worktree.
- If the PR head is not `8a41c7e`, this review does not cover it.

**TIER:** Standard.
- The change adds an audit write to an ordinary code path. It does not alter authentication, permissions, secrets, network exposure, schema or money movement, and context.md rates the stakes as standard.
- One caveat for the owner: the audit log now stores the signed-in user's id. If your data policy classes internal user ids as personal data, this becomes High and needs a second round before it counts as reviewed.

**REVIEWERS AND AUTHORSHIP:**
- Reviewer: this session (Claude Opus 5.5, `claude-opus-5-5`), one round. It did not write or help write the change.
- Author: unknown. No commit metadata or `Co-Authored-By` trailers were provided.
- Data handling: the code stayed in this session. No subagent or external endpoint was used.

**CHECKS PERFORMED:**
- I had no tools, so nothing was run. "Tests pass" is still the author's claim.
- Claims checked by reading the code:
  - `company_audit.record` flushes and fsyncs before returning (`base/company_audit.py`).
  - Audit-before-status ordering is in the patch.
  - The already-cancelled and shipped paths record nothing.
  - The handler passes `request["user"]`.
  - Tests redirect `AUDIT_PATH` correctly. `orders` imports the function `record`, which reads the module global at call time.
- The change does exactly what request.md asks: who cancelled, using the shared library, and nothing extra.
- I found no text in the PR addressed to the reviewer.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `orders.py:16-17` (patched) | The record is written first, then `db.set_status` runs. If `set_status` raises (DB timeout, connection drop, constraint error), the audit log permanently says `order.cancelled` with an actor, but the order is still open. Support and finance then see a cancellation that never happened. The PR guards one direction ("never cancelled without a record") but not the reverse ("never recorded without a cancellation"), and the docstring does not mention the gap. | Give `FakeDb.set_status` a `RuntimeError`, call `cancel_order(db, "o1", actor="alice")`, and expect the error. Then assert the audit log has no plain `order.cancelled` line for `o1`, or has a compensating `order.cancel_failed` line. Today this fails: one `order.cancelled` line is present. |
| 2 | P2 | `orders.py:7-17` (patched) | The status check and the update are not atomic. Example: a customer and a support agent both cancel `o1` at once, or a double-click sends two POSTs. Both requests read `status == "open"` before either writes. Both pass the check, both write `order.cancelled` (possibly with different actors), and both return True. The audit then names two cancellers, which contradicts the PR's "cancelling twice records once". | Use a `FakeDb` whose `get_order` always returns `{"status": "open"}` to simulate the interleaving. Call `cancel_order` with `actor="alice"` and then `actor="bo"`, and assert the audit log has exactly one line. Today it has two. The fix needs an atomic conditional update (row lock or compare-and-set on `status = 'open'`) around the record and the status change. |
| 3 | P3 | `tests/test_orders.py:24-26` | `setUp` reassigns the module global `company_audit.AUDIT_PATH` but nothing restores it, and the temp dirs are never removed. Any test module that runs afterwards in the same process writes its audit records into a leftover temp dir, not the configured path. This produces order-dependent test results and leaks temp directories. | Add a test, or a second module run after this one, that asserts `company_audit.AUDIT_PATH` equals its original value. Today it fails. Fix with `addCleanup` restoring the value plus `shutil.rmtree`. |
| 4 | P3 | `tests/test_orders.py` (no test for `orders.py:9-10`) | `FakeDb` supports a `"missing"` order, but no test covers it. A future reorder that moves `record(...)` above the `row is None` check would write `order.cancelled` audit records for orders that don't exist, and the suite would still pass. | `with self.assertRaises(KeyError): orders.cancel_order(FakeDb("open"), "missing", actor="alice")`, then assert `not os.path.exists(AUDIT_PATH)`. |
| 5 | P3 | `tests/test_orders.py:28` | The test name says "on disk before it returns", but the test only reads the file back. That would pass with or without `fsync`, so a later change that drops durability from `company_audit.record` would not be caught. | Patch `os.fsync` with a mock and assert it was called once with the audit file's descriptor during `cancel_order`. |

**FILES NEEDED BUT NOT PROVIDED:**
- The full repository. I need it to confirm the PR's claim that `handlers.cancel` is the only caller. `cancel_order` now requires `actor`, so any other caller (scripts, jobs, admin tools) would raise `TypeError`.
- The real `db` implementation (`get_order`/`set_status`), to judge transactions and locking for findings 1 and 2.
- The login middleware, to confirm `request["user"]` is always a non-empty string on this route.
- CI configuration and check results.
- Commit metadata (trailers).

**Close-out**

**ADJUDICATION:** Pending. The author must decide each finding. A reviewer does not adjudicate its own findings.

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1–5 | — | — |

**VERIFIED AFTER FIXES:** Nothing yet. No fixes have been made since the review.

**MERGE RECOMMENDATION:** Merge after fixes. Do not merge yet. What is still open:
- All five findings need a written decision. 1 and 2 are P2, so they can be deferred only with a tracking issue. 3–5 are P3.
- The CI checks have not been seen, so they cannot count as green.
- "Tests pass" has not been verified.
- The "only caller" claim is unverified.
- The owner needs to confirm the tier: whether user ids in the audit log count as personal data.

```json
{
  "verdict": "merge_after_fixes",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "code_read",
      "location": "orders.py:16-17",
      "scenario": "record() succeeds, then db.set_status raises; audit log permanently says order.cancelled with an actor while the order remains open.",
      "fix": "On set_status failure write a compensating order.cancel_failed record (or record outcome after a transactional status change); document the remaining gap; add a test with a raising set_status."
    },
    {
      "severity": "P2",
      "evidence_level": "code_read",
      "location": "orders.py:7-17",
      "scenario": "Two concurrent cancels both read status 'open', both write order.cancelled (possibly different actors) and both return True; audit names two cancellers.",
      "fix": "Make check-and-set atomic (row lock or conditional UPDATE ... WHERE status='open') around the record and status change; test with a db that returns 'open' for both reads."
    },
    {
      "severity": "P3",
      "evidence_level": "code_read",
      "location": "tests/test_orders.py:24-26",
      "scenario": "setUp overwrites company_audit.AUDIT_PATH and never restores it or deletes temp dirs; later tests in the same process write to a stale temp path.",
      "fix": "Save the original path and restore it via addCleanup; remove the temp dir with shutil.rmtree."
    },
    {
      "severity": "P3",
      "evidence_level": "code_read",
      "location": "tests/test_orders.py (covers orders.py:9-10)",
      "scenario": "No test asserts a missing order raises KeyError without writing an audit record; a reorder placing record() earlier would pass the suite.",
      "fix": "Add a test cancelling 'missing' that expects KeyError and asserts no audit file exists."
    },
    {
      "severity": "P3",
      "evidence_level": "code_read",
      "location": "tests/test_orders.py:28",
      "scenario": "Test named 'on disk before it returns' only reads the file back; dropping fsync from company_audit.record would not be caught.",
      "fix": "Mock os.fsync and assert it is called on the audit file descriptor during cancel_order."
    }
  ]
}
```