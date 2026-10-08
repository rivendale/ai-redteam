# PR #131 Review Report: Audit Record on Cancellation

**REVIEWED:** PR #131 at head `8a41c7e`, merge base `2d90b53`. Both SHAs come from PR.md. I had no tools in this session, so I could not check out the head or confirm that `change.patch` matches `8a41c7e`. This review covers `work/change.patch` against `work/base/` as provided. If the patch differs from the head, or the head has moved, the extra commits were not reviewed.

**TIER:** Standard. The change adds an audit write to an ordinary state change. It does not touch authentication, permissions, secrets, network exposure, migrations or money movement. The context also sets the stakes as standard. One consideration pointed higher: the record stores a user id, and finance relies on the record. Neither changes who can do what or how personal data flows beyond an id the service already holds, so I kept it at Standard. One model round is required, and this is that round.

**REVIEWERS:**
- Reviewer: Claude Opus 5.5 (`claude-opus-5-5`), a separate instance with no part in writing the change. No code left this session.
- Author: unknown. No commits or trailers were provided, only PR.md and the patch. The closer should record it from the `Co-Authored-By` and author fields on `8a41c7e`.

**Claims checked against the code:**

| Claim in PR.md | Verified? | Basis |
|---|---|---|
| Audit is written before the status change | Yes | `orders.py:16` is before `:17` |
| A failed audit write leaves the order open | Yes | `record` raises before `set_status`. Test `test_a_failed_audit_write_leaves_the_order_open` covers it. |
| Cancelling an already-cancelled order records nothing | Yes for sequential calls | See finding 2 for concurrent calls |
| `record` fsyncs before returning | Yes | `company_audit.py:13-15` |
| Signed-in user id is passed | Yes | `handlers.py:7` |
| `handlers.cancel` is the only caller | Not verified | Only these three files were provided |
| "Tests pass" | Not verified | I could not run them. By reading, they look correct. |

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `orders.py:16-17` | `record(...)` succeeds and fsyncs. Then `db.set_status` raises (connection drop, lock timeout, deadlock). The durable audit log now says "order.cancelled by alice" while the order stays open. Support and finance read a cancellation that never happened. If the user retries and succeeds, the log holds two cancellation records for one cancellation. The PR guarantees "no cancellation without a record" but not the reverse, and nothing in the log tells a reader which records took effect. | Make `FakeDb.set_status` raise `RuntimeError`. Call `cancel_order(db, "o1", actor="alice")`, expect the error, then assert the audit log does not show an unqualified `order.cancelled` for `o1`: either no line, or a following `order.cancel_failed` line. This fails today because one bare `order.cancelled` line is written. |
| 2 | P3 | `orders.py:11-17`; `tests/test_orders.py:52-54` | Two requests cancel the same open order at the same time (a double-click, or user and support agent together). Both read `status == "open"`, both call `record`, both call `set_status`. The log shows two cancellations, possibly by two different actors, for one order. The check-then-act race is pre-existing, but this PR makes it visible in the audit trail. The test `test_cancelling_twice_records_once` never cancels twice: it starts from `FakeDb("cancelled")`. So it does not test the claim in its name. | Use one `FakeDb("open")` whose `set_status` really changes the status `get_order` returns. Call `cancel_order` twice and assert exactly one audit line. Add a second test where `get_order` returns `"open"` to both callers before either sets the status (two interleaved calls), and assert one record. That needs an atomic conditional update such as `UPDATE ... WHERE status='open'`. |
| 3 | P3 | `tests/test_orders.py:23-25` | `setUp` assigns `company_audit.AUDIT_PATH` globally and never restores it, and the temp dirs are never removed. Any test that runs later in the same process and calls `record` writes into a stale temp dir from this test case. In the last test, the path points into a non-existent `missing/` directory, so those later writes raise `OSError`. The failure then depends on test ordering. | Run another test module that calls `company_audit.record` after `test_orders` in the same `unittest` run. Assert that `AUDIT_PATH` equals its original value. This fails today. Fix with `addCleanup` restoring the value, or with `mock.patch.object`. |

**Considered and not raised:** the module-level `AUDIT_PATH` patch does reach `record`, because `record` reads the global at call time, so the tests are not vacuous. The fsync covers the file but not the directory entry on first create. That is a pre-existing gap in the shared library, outside this PR. The handler returns 204 on an already-cancelled order, which is also pre-existing behaviour and outside the request.

**FILES NEEDED BUT NOT PROVIDED:**
- The full repository, or a grep for `cancel_order(`. This is needed to confirm `handlers.cancel` is the only caller. Any other caller would now raise `TypeError` for the missing `actor`.
- The login middleware. This is needed to confirm that `request["user"]` is always set, and is a non-empty string, on this route. If not, the handler raises `KeyError` or records `actor: null`.
- The CI configuration and check results for `8a41c7e`.

---

# Close-out

The author adjudicates these findings, and the closer writes this section. A reviewer never adjudicates its own findings, so this section is pending.

**ADJUDICATION:** pending, for findings 1–3. All three are P2 or P3, so the author may defer any of them with a linked issue. Finding 1 is partly a design choice: record-first versus outcome-recorded. If it is deferred or rejected, the owner should make and record that decision, because finance relies on the log.

**VERIFIED AFTER FIXES:** none yet.

**MERGE RECOMMENDATION:** merge after fixes, conditional on these points:

- Every finding gets a written decision.
- CI checks for `8a41c7e` are present and green. I have not seen them, and a missing check is not green.
- The sole-caller claim is confirmed.

No P0 or P1 was found. The required round has run.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "code-read (not executed)",
      "location": "orders.py:16-17",
      "scenario": "record() succeeds and fsyncs, then db.set_status raises; the audit log durably says the order was cancelled by the actor while the order stays open, and a successful retry writes a second cancellation record for one cancellation.",
      "fix": "Record the outcome, not just the intent: write a compensating 'order.cancel_failed' record if set_status raises (or record attempt + result), or make the status change and audit write transactional; add a test where set_status raises."
    },
    {
      "severity": "P3",
      "evidence_level": "code-read (not executed)",
      "location": "orders.py:11-17; tests/test_orders.py:52-54",
      "scenario": "Two concurrent cancels of the same open order both pass the status check and both write an audit record, possibly with different actors; test_cancelling_twice_records_once starts from an already-cancelled order and never cancels twice.",
      "fix": "Use an atomic conditional status update (cancel only where status='open') and record only when it took effect; rewrite the test to cancel the same open order twice and assert one record."
    },
    {
      "severity": "P3",
      "evidence_level": "code-read (not executed)",
      "location": "tests/test_orders.py:23-25",
      "scenario": "setUp overwrites company_audit.AUDIT_PATH globally without restoring it, so later tests in the same run write to a stale temp path (or a non-existent 'missing/' dir and raise OSError), giving order-dependent failures.",
      "fix": "Use mock.patch.object(company_audit, 'AUDIT_PATH', ...) or addCleanup to restore the original value and remove the temp dir."
    }
  ]
}
```