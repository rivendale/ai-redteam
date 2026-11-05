# PR #131 review report

**REVIEWED:** PR #131 (audit record on cancellation), head `8a41c7e`, merge base `2d90b53`. The review is static and covers only the supplied `PR.md`, `change.patch` and `base/` files. I ran no code, so "tests pass" is the author's claim and is unverified.

**TIER:** Standard. The change adds an audit write to an ordinary code path and does not touch auth, secrets, migrations or money movement. The stated stakes are standard. If the owner treats finance audit integrity as High, a second round is required. The `actor` field is a user id, which is a minor data-handling point. Nothing was sent outside this session.

**REVIEWERS:** This instance (Claude Sonnet 5.5) with no memory of writing the change. Commit trailers were not supplied, so the author is not recorded and independence from the author cannot be confirmed.

**Checks against the original request:** the change records who cancelled an order, using `company_audit`. There is no extra scope. The handler passes `request["user"]`, which matches the base docstring. I checked each claim in `PR.md`:
- "Required `actor`": confirmed in the patch.
- "Audit before the status change": confirmed at `orders.py:16`.
- "Already cancelled records nothing": confirmed, because the early return precedes `record`.
- "Only caller is `handlers.cancel`": unverified, since only `handlers.py` and `orders.py` were provided.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 (UNVERIFIED, library not provided) | `orders.py:2`, `orders.py:16` | The code assumes `company_audit.record(event, **fields)` accepts `order_id` and `actor` keywords and returns normally. The tests replace the module with a stub, so the real signature, required fields, event naming and failure modes are never exercised. If the signature differs, or the import fails in a deployed environment, every cancellation raises `TypeError` or `ImportError`. Because audit is fail-closed, no order can be cancelled. | A contract test against the real `company_audit` (or its published interface) that calls `record("order.cancelled", order_id=..., actor=...)` and checks the accepted fields. |
| 2 | P2 | `orders.py:16-17` | The audit write and `db.set_status` are not atomic. If `set_status` raises (DB error, connection lost) after `record` succeeds, finance sees an `order.cancelled` record for an order that is still open. A retry then writes a second record. The docstring says a cancellation never lacks a record, but the reverse is not guaranteed. | `FakeDb.set_status` raises. Assert either that no committed audit record exists, or that a retry yields exactly one record for the order. |
| 3 | P2 | `orders.py:9-17` | The read-check-write sequence has no lock. Two concurrent requests for the same open order both read `open`, both call `record`, and both set the status. Two audit records exist for one cancellation. The claim that cancelling twice records once holds only sequentially. | A test with a `db` whose `get_order` returns `open` for both calls, then two `cancel_order` calls. Assert one record, which needs a conditional update or a lock. |
| 4 | P2 (UNVERIFIED) | `orders.py:4` (signature) | `actor` is now required, which breaks any caller other than `handlers.cancel` (admin scripts, jobs, other services) with a `TypeError`. The files that would show other callers were not provided. | Search the full repository for `cancel_order(` and add a test for each non-handler caller. |
| 5 | P3 | `handlers.py:9` | `request["user"]` raises `KeyError` if the middleware did not set it. Before the change the handler did not read it, so a missing user now becomes a 500 on a route that used to work. There is also no check that `actor` is a non-empty string, so an audit record could carry `None` or an empty actor. | A handler test with no `user` key that expects a 401/403 rather than a `KeyError`, plus a test that `cancel_order` rejects an empty `actor`. |
| 6 | P3 | `tests/test_orders.py:12-16` | Assigning `sys.modules["company_audit"]` at import time leaks the stub into any other test in the same process, hiding the real library. There is also no test that a missing order (`KeyError`) records nothing. | Use `unittest.mock.patch.dict(sys.modules, ...)` in `setUp`/`tearDown`. Add a missing-order test that asserts `calls == []`. |

Fail-closed behavior, where an audit outage blocks cancellations, is a deliberate design choice that the PR states. Whether support can accept that during an audit outage is an owner decision, not a defect.

**FILES NEEDED BUT NOT PROVIDED:**
- `company_audit` (interface and failure behavior).
- The rest of the repository, to find other callers of `cancel_order`.
- The commit trailers for `8a41c7e`.
- The CI check results.

**Close-out:** Not written. The author must adjudicate the findings first, and a reviewer does not adjudicate its own findings.

**Provisional merge view:** Merge after fixes. Finding 1 must be resolved against the real library, and findings 2–4 need a written decision, before the merge gates in Step 8 can be met. CI status is unknown, and a missing check is not green.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "unverified",
      "location": "orders.py:2,16",
      "scenario": "company_audit was not provided and tests stub it. If record() has a different signature or the import fails, every cancellation raises and orders cannot be cancelled.",
      "fix": "Add a contract test against the real company_audit interface and confirm the field names and failure modes."
    },
    {
      "severity": "P2",
      "evidence_level": "static-read",
      "location": "orders.py:16-17",
      "scenario": "record() succeeds, then db.set_status raises. The audit trail shows a cancellation for an order that is still open, and a retry writes a duplicate record.",
      "fix": "Make the audit write and status change atomic (same transaction or outbox), or make records idempotent per order, and test with a failing set_status."
    },
    {
      "severity": "P2",
      "evidence_level": "static-read",
      "location": "orders.py:9-17",
      "scenario": "Two concurrent cancels of the same open order both pass the status check and both write an audit record, so the 'records once' guarantee fails under concurrency.",
      "fix": "Use a conditional update or row lock so only one request records, and add a concurrent-cancel test."
    },
    {
      "severity": "P2",
      "evidence_level": "unverified",
      "location": "orders.py:4",
      "scenario": "The required actor argument breaks any caller other than handlers.cancel. Other callers were not provided, so the claim of a single caller is unconfirmed.",
      "fix": "Grep the full repo for cancel_order callers and update or test each one."
    },
    {
      "severity": "P3",
      "evidence_level": "static-read",
      "location": "handlers.py:9",
      "scenario": "A missing request['user'] raises KeyError (500) instead of an auth error, and an empty or None actor can be written to the audit record.",
      "fix": "Validate the user and reject with 401/403, and validate that actor is a non-empty string in cancel_order."
    },
    {
      "severity": "P3",
      "evidence_level": "static-read",
      "location": "tests/test_orders.py:12-16",
      "scenario": "The global sys.modules stub leaks into other tests in the same process, and there is no test that a missing order records nothing.",
      "fix": "Scope the stub with patch.dict in setUp/tearDown and add a missing-order test."
    }
  ]
}
```