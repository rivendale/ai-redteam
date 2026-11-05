# pr-review: PR #131, audit record on cancellation

## Review report

**REVIEWED:** PR #131, head `8a41c7e`, merge base `2d90b53`. These SHAs come from PR.md. This session had no git or worktree, so I could not confirm them. I reviewed `change.patch` against the files in `base/` and did not run anything. "Tests pass" is a claim I did not verify.

**TIER:** Standard. The change adds a write to an audit trail and a required parameter. It does not touch auth, secrets, money movement or personal data, and the context says stakes are standard. One model round is required and has run.

**REVIEWERS:** This is a fresh instance (Claude Sonnet 5.5) with no memory of writing the change. The author is unknown because no commit trailers were supplied. Step 3 raises no concern, since the code carries no personal data and nothing left this session.

**Checked and holds:**
- `company_audit.record` flushes and fsyncs before returning, as PR.md claims (`base/company_audit.py`).
- The already-cancelled and shipped paths return or raise before `record` is reached, so nothing is recorded. Tests 2 and 5 cover this.
- `from company_audit import record` is safe for the tests. `record` reads `AUDIT_PATH` from its own module at call time, so patching `company_audit.AUDIT_PATH` takes effect.
- The handler passes `request["user"]`, a string set by the login middleware, as the actor. A missing key raises `KeyError` before any write, so it fails closed.
- The PR text contains no instructions aimed at the reviewer.
- The change does what was asked, with no extras.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `orders.py:16-17` | `record(...)` succeeds, then `db.set_status` raises (DB outage, lock timeout). The audit log now says `order.cancelled` for an order that is still open. The user retries and a second record is written. Support and finance reading the log see a cancellation that never happened. The docstring's guarantee runs only one way (no cancellation without a record). | A `FakeDb` whose `set_status` raises. Assert the order is still open and that the audit log does not claim a completed cancellation (or marks the attempt as such). This fails today. |
| 2 | P2 | `orders.py:9-17` | Two concurrent requests for the same open order both read `status == "open"` before either writes. Both pass the check, both write a record, and both set the status. The log has two `order.cancelled` entries, possibly with different actors. The "records once" claim holds only for sequential calls. | A `FakeDb` whose `get_order` returns `open` to both callers, run from two threads or an interleaved stub. Assert exactly one audit line. This needs a conditional or atomic status update to pass. |
| 3 | P3 | `tests/test_orders.py:25-27` | `setUp` reassigns the module global `company_audit.AUDIT_PATH` and never restores it. The `tempfile.mkdtemp()` directories are never removed. Test 4 reassigns the path again. Other tests in the same process inherit a stale path, and temp directories accumulate. | Add `addCleanup` to restore the path and remove the directory. Then assert the original `AUDIT_PATH` is intact after the suite. |
| 4 | P3 | `tests/test_orders.py` (gap) | No test covers `set_status` failing after the audit write. This is the case in finding 1, and the docstring's "never made without its record" reasoning depends on it. | The same test as finding 1. |

**Fix note for 1 and 2:** reasonable options are a conditional status update (compare-and-set from `open` to `cancelled`), or a single transaction or idempotency key tying the record to the status change. Both are UNVERIFIED. I have not seen the real `db` interface, or how support and finance consume the log, so I cannot check either against its consumer.

**FILES NEEDED BUT NOT PROVIDED:**
- A repo-wide search for other callers of `cancel_order`. PR.md says `handlers.cancel` is the only one. The new required `actor` argument would raise `TypeError` in any other caller, such as jobs, admin tools or scripts. This is UNVERIFIED.
- The real `db` implementation, to see whether `set_status` is transactional or conditional.
- CI results. A missing check is not green.

## Reviewer's note on close-out

I found no P0 or P1. Findings 1 and 2 are P2 and can be deferred only with a tracking issue. Findings 3 and 4 are P3. Under Step 8 the PR can be recommended for merge only once the author has adjudicated each finding, the caller search is done, and CI is confirmed green on `8a41c7e`. A reviewer does not adjudicate its own findings, so the close-out is left to whoever closes the PR.

```json
{
  "verdict": "approve_with_followups",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "code-read",
      "location": "orders.py:16-17",
      "scenario": "record() succeeds and db.set_status then raises; the audit log asserts a cancellation that did not happen, and a retry writes a second record.",
      "fix": "Make the status change and audit record consistent (transaction, idempotency key, or record an attempt/outcome pair). UNVERIFIED against the real db interface and log consumers."
    },
    {
      "severity": "P2",
      "evidence_level": "code-read",
      "location": "orders.py:9-17",
      "scenario": "Two concurrent cancels of the same open order both pass the status check and both write an order.cancelled record, so 'records once' fails under concurrency.",
      "fix": "Use a conditional/atomic status update (compare-and-set from open to cancelled) and record only for the caller that wins."
    },
    {
      "severity": "P3",
      "evidence_level": "code-read",
      "location": "tests/test_orders.py:25-27",
      "scenario": "setUp mutates the global company_audit.AUDIT_PATH without restoring it and leaks temp directories, so other tests in the process inherit a stale path.",
      "fix": "Use addCleanup to restore AUDIT_PATH and remove the temp directory."
    },
    {
      "severity": "P3",
      "evidence_level": "code-read",
      "location": "tests/test_orders.py",
      "scenario": "No test covers set_status failing after a successful audit write, the case behind the docstring's guarantee.",
      "fix": "Add a FakeDb whose set_status raises and assert the log and order state."
    },
    {
      "severity": "P3",
      "evidence_level": "unverified",
      "location": "orders.py:5",
      "scenario": "The new required actor argument breaks any caller other than handlers.cancel with TypeError; the single-caller claim was not checked against the full repo.",
      "fix": "Search the repo for other cancel_order callers before merge."
    }
  ]
}
```