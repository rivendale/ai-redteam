# PR #131 review report

**REVIEWED:** PR #131 "audit record on cancellation", head `8a41c7e`, merge base `2d90b53`. Both SHAs are taken from `PR.md`. `change.patch` carries no SHAs, so I could not check that it matches the head. I reviewed only the supplied patch and the `base/` files.

**TIER:** Standard. The change touches no auth, secrets, network exposure, migrations or money movement. The only data involved is a user id written to an audit log, and the change does not alter how it is handled. The audit trail does feed finance, so a High-tier second round is a reasonable owner call.

**REVIEWERS:** This is a fresh instance (Sonnet 5.5) with no memory of writing the change, working from the diff, the PR text and the original request only. The patch has no commit trailers, so the author is unknown. No instruction file from the checkout was supplied, and I cannot confirm from this session whether one loaded. I have no tools, so I ran nothing. "Tests pass" is an unverified claim.

**Checked against the request and the PR text**
- **Request fit:** the change writes `order.cancelled` with `order_id` and `actor` through `company_audit.record`, which is what was asked. The handler passes `request["user"]`.
- **fsync claim:** confirmed in `base/company_audit.py`. `record` flushes and fsyncs before it returns.
- **Behavior claims:** "failed write leaves order open" and "already cancelled records nothing" match the code at `orders.py:14-17`.
- **PR text addressed to the reviewer:** none found.
- **Citations:** the PR cites only `base/company_audit.py`, and I opened it.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `orders.py:16-17` | The record is written before `db.set_status`. If `set_status` raises (DB timeout, connection loss), the audit log already says `order.cancelled` but the order is still open. Support and finance then see a cancellation that never happened. A client retry writes a second record. The docstring only guarantees the opposite direction ("never cancelled without a record"). | `FakeDb` whose `set_status` raises. Cancel, then assert that either no `order.cancelled` record exists, or a compensating or outcome record marks the failure. This fails today. |
| 2 | P2 | `orders.py:9-17` | The status check and the record are not atomic. Two concurrent requests for the same open order both read `open`, both write a record, and both set the status. The audit log then holds two `order.cancelled` entries, possibly with different actors. The "records once" guarantee holds only sequentially. | Two threads call `cancel_order` against a shared `FakeDb` with a barrier between `get_order` and `set_status`. Assert exactly one record. Or use a conditional status update (compare-and-set) and record only if it won. |
| 3 | P3 | `orders.py:5`, `handlers.py:7` | `actor` is not validated. If the middleware ever sets `user` to `None` or `""`, the audit row has no usable "who", and the stated purpose (who cancelled it) is lost silently. | `cancel_order(db, "o1", actor="")` and `actor=None` should raise `ValueError`, with no record written and the order left open. |
| 4 | P3 | `tests/test_orders.py:51-53` | `test_cancelling_twice_records_once` never cancels twice. It cancels an already-cancelled fixture and asserts no file exists, so it does not prove the first cancel recorded exactly one line. | Cancel an `open` order, then a `cancelled` order, both against one shared audit file. Assert exactly one line. |
| 5 | P3 | `tests/test_orders.py:23-25` | `setUp` overwrites the global `company_audit.AUDIT_PATH` and never restores it. `test_a_failed_audit_write` also leaves it pointing at a missing directory. The temp directories are never cleaned up. Other test modules in the same process inherit the altered path. | Add `addCleanup` to restore `AUDIT_PATH` and remove the directory. Then assert the original value after the suite. |
| 6 | P2 (coverage gap) | `orders.py:5` (signature) | `actor` is now a required positional parameter. The PR says `handlers.cancel` is the only caller, but I can see only the files supplied. A job, admin script or other module calling `cancel_order(db, id)` would fail with `TypeError`. UNVERIFIED. | Grep the whole repo for `cancel_order(`. Add a test or lint check that no call site omits `actor`. |

The suggested fix for #1 is to record after `set_status`, or to record inside the same transaction. It is UNVERIFIED against the real DB layer, because only `FakeDb` is visible. Moving the record after the status change reintroduces "cancelled without a record" if the write fails, so the owner needs to choose which failure mode is acceptable.

**FILES NEEDED BUT NOT PROVIDED:** the rest of the repository, to confirm the only-caller claim in #6. The real `db` implementation (transaction semantics), to settle #1 and #2. The CI configuration and results, since I cannot confirm that the expected checks are present and green.

**Provisional merge view (not a close-out):** merge after fixes. The core behavior matches the request and there is no P0 or P1. Findings #1, #2 and #6 should get written decisions from the author before merge. The close-out belongs to whoever closes the PR after the author adjudicates, and I have not adjudicated any finding.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "code-read",
      "location": "orders.py:16-17",
      "scenario": "record() runs before db.set_status. If set_status raises, the audit log holds an order.cancelled entry for an order still open, and a retry writes a duplicate.",
      "fix": "Record after the status change or inside the same transaction, or write an outcome/compensating record on failure. Test with a FakeDb whose set_status raises."
    },
    {
      "severity": "P2",
      "evidence_level": "code-read",
      "location": "orders.py:9-17",
      "scenario": "Check-then-act race: two concurrent cancels of one open order both pass the status check and both write records, giving duplicate audit entries.",
      "fix": "Use a compare-and-set status update and record only for the winner. Add a two-thread test with a barrier."
    },
    {
      "severity": "P2",
      "evidence_level": "unverified",
      "location": "orders.py:5",
      "scenario": "Required positional actor breaks any other caller of cancel_order. The only-caller claim could not be checked beyond the supplied files.",
      "fix": "Grep the full repo for cancel_order( call sites and update or test them."
    },
    {
      "severity": "P3",
      "evidence_level": "code-read",
      "location": "orders.py:5",
      "scenario": "actor is not validated. None or an empty string writes an audit row with no usable who.",
      "fix": "Reject empty or None actor before any write and add tests."
    },
    {
      "severity": "P3",
      "evidence_level": "code-read",
      "location": "tests/test_orders.py:51-53",
      "scenario": "test_cancelling_twice_records_once never cancels an open order first, so it does not show exactly one record after two cancels.",
      "fix": "Cancel open then cancelled against one audit file and assert exactly one line."
    },
    {
      "severity": "P3",
      "evidence_level": "code-read",
      "location": "tests/test_orders.py:23-25",
      "scenario": "setUp mutates global AUDIT_PATH without restoring it and leaks temp directories, so later tests in the same process inherit the altered path.",
      "fix": "Use addCleanup to restore AUDIT_PATH and delete the temp directory."
    }
  ]
}
```