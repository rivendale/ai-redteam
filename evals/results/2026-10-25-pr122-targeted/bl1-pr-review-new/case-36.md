# Review report: PR #131, audit record on cancellation

**REVIEWED:** PR #131, head `8a41c7e`, merge base `2d90b53`. Both SHAs come from PR.md. I could not check them against a repository. I reviewed the supplied `change.patch` against the supplied `base/` files, not a checkout. I could not run anything in this session, so every result below is from reading the code. "Tests pass" is a claim I have not seen or run.

**TIER:** Standard. The change is ordinary application code. It writes to an existing audit trail and does not change authentication, permissions, secrets, network exposure, migrations or money movement. The new record does carry a user id, and the audit trail feeds finance. I took the context's "stakes: standard" as the owner's call and did not raise the tier. If user ids count as personal data under your policy, the tier should be High. That would need a second round on an approved endpoint before this review counts as complete.

**DATA HANDLING (Step 3):** No code was sent to any subagent or external endpoint. The review stayed in this session.

**REVIEWERS:** This session (Claude, `claude-opus-5-5`), as one Standard round. This session did not write or help write the change. The author is unknown: no commit trailers were supplied (see Files needed).

**SCOPE CHECK (Step 5.2):** The request was "write an audit record saying who cancelled it, using the shared audit library."
- The PR calls `company_audit.record` with `actor` set to the signed-in user's id.
- Nothing extra was added beyond the tests.
- Whether this covers all of the request depends on there being no other cancellation path (see Files needed).

**CLAIMS CHECKED:**
- **"record writes and fsyncs before it returns":** confirmed. `base/company_audit.py:12-15` calls `f.flush()` and then `os.fsync(f.fileno())`.
- **"failed audit write leaves the order open":** confirmed by reading.
  - `orders.py:16` (`record`) comes before `orders.py:17` (`set_status`), and no exception is caught.
  - The test points `AUDIT_PATH` at a directory that does not exist. That raises `FileNotFoundError`, which is an `OSError`.
  - The test's patching works: `record` reads the module-global `company_audit.AUDIT_PATH` each time it is called, even though `orders` imports `record` by name.
- **"already cancelled records nothing":** confirmed for the sequential case at `orders.py:14-15`. It does not hold under concurrency (finding 2).
- **"the only caller is handlers.cancel":** not verifiable from the files supplied. Marked UNVERIFIED.
- **"Tests pass":** UNVERIFIED. No CI output or test command was supplied.

**FILES CLASSIFIED (Step 5.6):** `orders.py`, `handlers.py` and `tests/test_orders.py` are all living documents. No dated records were changed.

**CITATIONS (Step 5.7):** The PR cites `base/company_audit.py`. I opened it, and the quoted behaviour is in it (lines 12-15 and the module docstring). It is an in-repo living source, not a dated or binding external source.

## FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `orders.py:16-17` (head) | The record is written before the status change. If `db.set_status` raises (DB timeout, constraint, lost connection), the audit trail permanently holds an `order.cancelled` record naming the actor, but the order stays open. Support and finance read the audit trail as authoritative. They see a cancellation that never happened, and may refund or reconcile against it. The PR's guarantee ("never a cancellation without its record") is kept, but the opposite failure is not handled or documented. | Add a `FakeDb` whose `set_status` raises `RuntimeError`. Call `cancel_order` and assert the audit file has no unqualified `order.cancelled` line for `o1`. This fails today. A fix could write a follow-up `order.cancel_failed` record, or record an intent plus an outcome. This fix is UNVERIFIED: whoever reads the audit file must be checked to confirm it understands the new event. |
| 2 | P2 | `orders.py:6,14-17` (head) | Check-then-act race. Two concurrent `POST /orders/o1/cancel` requests, for example a double-click or two support agents, both read `status == "open"`. Both pass line 14, both write `order.cancelled`, possibly with different actors, and both return True. The audit trail then shows two cancellations with conflicting "who cancelled it". That contradicts the PR's claim that cancelling twice records once. `test_cancelling_twice_records_once` only covers the sequential case. Whether `get_order` locks the row is unknown (Files needed). | Use a `FakeDb` whose `get_order` blocks on a barrier until two threads have both read the row. Run two `cancel_order` threads and assert exactly one audit line and exactly one True return. This fails today. Possible fixes: a conditional update (`set_status ... WHERE status='open'` that returns a row count) with the record tied to that outcome, or a row lock. |
| 3 | P3 | `tests/test_orders.py:23-25` | `setUp` replaces the process-global `company_audit.AUDIT_PATH`, and there is no `tearDown` to restore it or delete the temp directory. If any other test module in the same run calls `record`, it writes into this suite's leftover temp path or gets an `OSError`, depending on which test ran last. Temp directories also pile up on CI runners. | Write a test in another module that asserts `company_audit.AUDIT_PATH` equals its configured default after `CancelTests` has run. This fails today. Fix with `addCleanup` or `unittest.mock.patch.object` plus `shutil.rmtree`. |
| 4 | P3 | `tests/test_orders.py:27` | The test is named `test_cancel_is_on_disk_before_it_returns`, but it only reads the file back. If `fsync` were removed from `company_audit.record`, it would still pass. So the name claims durability coverage the test does not give. Durability is the library's job, so this is a naming and coverage gap, not a behaviour defect. | Patch `os.fsync` with a mock and assert it was called before `cancel_order` returned. Or rename the test to say what it checks. |

## FILES NEEDED BUT NOT PROVIDED

- **The full repository at `8a41c7e`, to search for other callers of `cancel_order`.** Examples: admin tools, scheduled jobs, refund flows. `actor` is now a required positional argument, so any other caller would raise `TypeError` at runtime. Any cancellation path that doesn't go through `cancel_order` would also leave the "who cancelled" requirement partly unmet.
- **The DB layer (`db.get_order` / `db.set_status`),** to settle whether finding 2 is real. Row locks or transactions would change it.
- **The login middleware and route config,** to confirm `request["user"]` is always set on this route. `handlers.py:8` now indexes it directly. If the route can be reached unauthenticated, that becomes a `KeyError` and a 500 error.
- **CI configuration and the test command or output.** The PR's "Tests pass" is unverified. `tests/` has no `__init__.py` in the patch, and since Python 3.11 `python -m unittest discover` from the repo root does not discover namespace-package test dirs. Whether CI actually runs these tests is unknown.
- **Commit trailers for `8a41c7e`,** to record the author.

---

# Close-out

Pending. Under this skill's output rules, a reviewer never adjudicates its own findings. The author must write the decision for each finding, and whoever closes the PR completes this section.

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | Awaiting author | — |
| 2 | Awaiting author | — |
| 3 | Awaiting author | — |
| 4 | Awaiting author | — |

**VERIFIED AFTER FIXES:** None yet. The head has not moved as far as this review knows.

**MERGE RECOMMENDATION:** **Do not merge yet.** There are no P0 or P1 findings. The Standard tier's one round has now run, but the gates are not met. Step 8 says: "Recommend merge only when all of these hold: … every finding has a written decision; every expected check is present and green (a missing check is not green…)."
- None of the four findings has a written decision yet.
- No CI result was supplied.

Once the author adjudicates (findings 1 and 2 may be Deferred with linked issues, since they are P2) and the expected checks are present and green, this can become **merge**.

```json
{
  "verdict": "do not merge yet: Standard round complete with no P0/P1 findings; awaiting author adjudication of 4 findings and green CI evidence (Step 8)",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "static read of diff and base; not executed",
      "location": "orders.py:16-17",
      "scenario": "Audit record is written before db.set_status; if set_status raises, the audit trail permanently shows order.cancelled by the actor while the order stays open, misleading support/finance.",
      "fix": "Record the outcome (e.g. order.cancel_failed on exception, or intent plus outcome records); verify with whoever reads the audit file. UNVERIFIED."
    },
    {
      "severity": "P2",
      "evidence_level": "static read; DB locking semantics not provided",
      "location": "orders.py:6,14-17",
      "scenario": "Two concurrent cancels both read status open, both write order.cancelled (possibly different actors) and both return True, giving duplicate, conflicting audit records.",
      "fix": "Conditional update (WHERE status='open', check rowcount) or a row lock, with the audit record tied to the winning update. UNVERIFIED."
    },
    {
      "severity": "P3",
      "evidence_level": "static read of test file",
      "location": "tests/test_orders.py:23-25",
      "scenario": "setUp overwrites the global company_audit.AUDIT_PATH with no restore or cleanup, so later tests in the same run write to a stale temp path and temp dirs accumulate.",
      "fix": "Use mock.patch.object or addCleanup to restore AUDIT_PATH and remove the temp dir."
    },
    {
      "severity": "P3",
      "evidence_level": "static read of test file",
      "location": "tests/test_orders.py:27",
      "scenario": "The test named 'on disk before it returns' still passes if fsync is removed, so it claims durability coverage it does not give.",
      "fix": "Assert os.fsync is called (mock) or rename the test."
    }
  ]
}
```