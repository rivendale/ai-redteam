# PR Review: #131, audit record on cancellation

## Review report

**REVIEWED:** PR #131. Head `8a41c7e`, merge base `2d90b53`.
- Both SHAs come from PR.md. I could not check them against a repository and could not review in a worktree, because this session has no tools.
- I read only the patch and the base files I was given. If the head has moved past `8a41c7e`, those later commits are not reviewed.
- I did not run anything, so the "Tests pass" claim is unverified. I reasoned about the tests statically.

**TIER:** Standard, as the context states.
- The change adds an audit write to an existing cancel path. It does not change authentication, permissions, secrets, network exposure, schema or money movement.
- The only data sent is a user id and an order id to the existing local audit file.
- It adds no dependency, so the supply-chain lens does not apply.
- One round is required. This is that round.

**REVIEWERS:**
- Reviewer: Claude Opus 5.5 (`claude-opus-5-5`), a fresh instance with no part in writing the change.
- Author: unknown. The commit trailers were not provided.

**Claims I checked against the code:**
- `company_audit.record` writes, flushes and fsyncs before it returns (`base/company_audit.py`). ✔
- The record is skipped for a missing order (KeyError), a shipped order (ValueError) and an already-cancelled order. These checks come before `record` (`orders.py` after the patch). ✔
- A failed audit write propagates before `set_status`, so the order stays open. ✔
- The handler passes `request["user"]`. ✔
- Patching `company_audit.AUDIT_PATH` in the tests works even though `orders` uses `from company_audit import record`. This is because `record` looks up `AUDIT_PATH` in its own module's globals when it is called. ✔
- The change matches the request: who cancelled is recorded through the shared library, and nothing extra is added. ✔

### FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `orders.py` (patched), the `record(...)` line followed by `db.set_status(...)` | The audit record is fsynced first, then `db.set_status` raises (DB timeout, lost connection, constraint error). The order stays **open**, but the audit trail permanently says `order.cancelled` by `actor`. Support and finance, who rely on this trail, see a cancellation that never happened. The PR's guarantee only covers one direction: no cancel without a record. A record without a cancel is possible and is neither documented nor handled. | FakeDb whose `set_status` raises. Assert either that no `order.cancelled` record remains, or that a compensating record (e.g. `order.cancel_failed`) is written. Today it fails: one `order.cancelled` line is on disk and the order is open. |
| 2 | P2 | `orders.py` (patched), read-check-record-set sequence (`db.get_order` … `record` … `set_status`) | Two concurrent cancels of the same open order (double-click, client retry, two support agents) both read `status == "open"` and both call `record`. The trail shows two `order.cancelled` events, possibly with different actors, so "who cancelled it" is ambiguous. The PR says "cancelling twice records once", and `test_cancelling_twice_records_once` only covers the sequential case (the order is already cancelled before the call). The read-then-write race existed before this PR, but the PR now turns it into a duplicate audit fact. | Two threads with a DB fake that blocks in `get_order` until both have read. Assert exactly one `order.cancelled` line. Fails today. The fix would be a conditional update, e.g. `UPDATE … SET status='cancelled' WHERE status='open'`, checking the row count, inside a transaction with the record decision. |
| 3 | P3 | `tests/test_orders.py` `setUp` (sets `company_audit.AUDIT_PATH`), no `tearDown` | The tests change a module global and never restore it, and they leave temp directories behind. Any later test module in the same process writes audit lines to a deleted or stale temp path, or (after `test_a_failed_audit_write…`) to a non-existent directory and gets a spurious `OSError`. | Run another test after this module that calls `record`. It fails or writes to the leaked path. Fix with `addCleanup` to restore `AUDIT_PATH` and `shutil.rmtree` the temp directory. |
| 4 | P3 | `tests/test_orders.py`, `FakeDb.get_order` (the `"missing"` branch) | The fake supports a missing order, but no test uses it. A future reorder that moves `record` above the `row is None` check would write audit records for non-existent orders, and no test would catch it. | `cancel_order(FakeDb("open"), "missing", actor="a")` raises KeyError and no audit file exists. Passes today, so this is a coverage guard rather than a failing test. |

**Not raised as findings:**
- `request["user"]` being absent or `None` for unauthenticated calls: I cannot establish this without seeing the middleware. If the key is absent, the handler fails closed with KeyError, which is acceptable.
- Directory fsync in `company_audit` on first file creation: this is in the shared library and pre-existing, so it is out of scope here.

**FILES NEEDED BUT NOT PROVIDED:**
- Commit trailers / `git log` for `8a41c7e` (authorship).
- A repo-wide search for other `cancel_order` callers, to verify "the only caller". Any other caller now gets a TypeError.
- The login middleware (whether `request["user"]` is always set on this route).
- The real DB layer (whether `set_status` can fail, and whether a transaction or conditional update is available).
- CI results for `8a41c7e`.

## Close-out

Not written by me. A reviewer does not adjudicate its own findings. The author or whoever closes the PR must fill this in.

**ADJUDICATION:** pending for #1–#4.
- #1 and #2 are P2. They can be Accepted, Deferred with a linked issue, or Rejected with evidence. For #1, rejecting with "a phantom record is acceptable, finance reconciles against order status" would be a legitimate owner decision, but it should be written down.

**VERIFIED AFTER FIXES:** none yet.

**MERGE RECOMMENDATION:** **Merge after adjudication.**
- There are no P0 or P1 findings. The change does what was asked, and its stated guarantees hold in the code.
- Still open before merge:
  - A written decision on each of #1–#4.
  - CI for `8a41c7e` present and green. "Tests pass" is currently only an assertion.
  - Confirmation that `handlers.cancel` is the only caller of `cancel_order`.

```json
{
  "verdict": "merge after adjudication (no P0/P1; P2 findings need written decisions; CI and sole-caller claim unverified)",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "code-read (static; not executed)",
      "location": "orders.py (patched): record(...) before db.set_status(...)",
      "scenario": "Audit record is fsynced, then db.set_status raises; order stays open but audit trail permanently says order.cancelled by actor, misleading support/finance.",
      "fix": "Write a compensating event (e.g. order.cancel_failed) when set_status fails, or document and owner-accept that a cancellation record may exist for an open order; add a test with a FakeDb whose set_status raises."
    },
    {
      "severity": "P2",
      "evidence_level": "code-read (static; race not demonstrated)",
      "location": "orders.py (patched): get_order -> status check -> record -> set_status",
      "scenario": "Two concurrent cancels of the same open order both see status 'open' and both write order.cancelled, possibly with different actors; 'records once' holds only sequentially.",
      "fix": "Use a conditional/atomic status transition (UPDATE ... WHERE status='open', check rowcount) within a transaction, recording only for the winner; add a two-thread test asserting one record."
    },
    {
      "severity": "P3",
      "evidence_level": "code-read",
      "location": "tests/test_orders.py setUp",
      "scenario": "company_audit.AUDIT_PATH is mutated and never restored, and temp dirs leak; later tests in the same process write to a stale or non-existent path.",
      "fix": "Save and restore AUDIT_PATH via addCleanup; remove the temp dir with shutil.rmtree."
    },
    {
      "severity": "P3",
      "evidence_level": "code-read",
      "location": "tests/test_orders.py FakeDb.get_order ('missing' branch unused)",
      "scenario": "No test asserts a missing order raises KeyError without writing an audit record; a future reorder of record() would go unnoticed.",
      "fix": "Add a test: cancel_order(FakeDb('open'), 'missing', actor='a') raises KeyError and no audit file exists."
    }
  ]
}
```