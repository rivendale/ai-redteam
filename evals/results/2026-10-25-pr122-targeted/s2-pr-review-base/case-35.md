# PR #131 review report

**REVIEWED:** PR #131 "audit record on cancellation", head `8a41c7e`, merge base `2d90b53`. Both SHAs are taken from PR.md. I had no repository, so I could not verify them.

**TIER:** Standard. It is ordinary application code, and the context sets the stakes to standard. The audit trail feeds support and finance, but the change moves no money and touches no auth or personal data. I considered High and kept Standard, so one model round applies.

**REVIEWERS:**
- Reviewer: this instance (Claude Sonnet 5.5), a fresh read with no hand in writing the change. I had no tools, so I ran nothing, including the tests.
- Author: unknown. No commit trailers were provided.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 | `orders.py:16-17` (`record(...)` then `db.set_status`) | The audit record is written before the status change, and nothing makes the two atomic. If `set_status` raises (DB error, timeout), the audit log says "order.cancelled by alice" for an order that is still open. A retry then writes a second record. Support and finance would see cancellations that never happened. The docstring's guarantee "a cancellation is never made without its record" holds, but the inverse (a record without a cancellation) is unaddressed. | Fake db whose `set_status` raises. Assert either that no record is left, or that a failure is recorded and a retry yields exactly one cancelled-record. |
| 2 | P2 | `orders.py:11-17` (check then act) | Two concurrent cancels of the same open order both read `status == "open"`, both pass the guard, and both call `record(...)`. The audit log gets two "cancelled" records, and the "records nothing when already cancelled" claim fails under concurrency. The same race can attribute the cancellation to the wrong actor. | Concurrency test with a db fake whose `get_order` blocks on a barrier. Two threads cancel the same order, and the assertion is exactly one record. This probably needs a conditional update such as `set_status` only `WHERE status='open'`, or a transaction. |
| 3 | P2 | `orders.py:2`, `tests/test_orders.py:14` | `company_audit` was not provided, and the tests replace it with a stub taking `(event, **fields)`. Nothing shows that the real `record` has this signature, accepts `order_id` and `actor` as keywords, or raises on failure instead of swallowing errors or returning a status. If the real library logs and returns on failure, the "failed audit write leaves the order open" guarantee silently does not hold. The tests would still pass. | Contract test against the real library, or against its published interface. Assert that `record("order.cancelled", order_id=..., actor=...)` is accepted, and that a forced failure propagates. |
| 4 | P2 | `orders.py:2` (module-level import), patch contains no dependency change | `company_audit` is now a hard import of `orders`. If it is not declared or installed in the deployed environment, `import orders` fails and so does `handlers`, which takes down the cancel endpoint at load. The patch touches no requirements file, and the base files I was given do not show one, so I cannot tell whether it is already available. | CI import check in a clean environment built from the declared dependencies: `python -c "import handlers"`. |
| 5 | P3 | `tests/test_orders.py:14` | The test file permanently replaces `sys.modules["company_audit"]` at import time. If other test modules run in the same process, they get the stub instead of the real library. | Use `unittest.mock.patch.dict(sys.modules, ...)` in `setUpModule` and restore it in `tearDownModule`. |
| 6 | P3 | `handlers.py:7` | `request["user"]` raises `KeyError` if the middleware did not set it. This is now a mandatory-actor path where before the user was not read. The docstring says the middleware sets it, so this is low risk, but the failure would surface as a generic error after the order lookup rather than a clear 401. | Handler test with no `user` key. Assert an explicit auth error and no status change. |

The PR text claims that the handler is the only caller of `cancel_order`, and the files I was given agree. I cannot confirm it for code outside them. `actor` is now a required positional argument, so any other caller would break.

**FILES NEEDED BUT NOT PROVIDED:**
- `company_audit` source or interface (finding 3).
- The dependency and requirements manifest and the deployment config (finding 4).
- The real `db` layer (`get_order` / `set_status`), for transaction and conditional-update semantics (findings 1 and 2).
- Any other callers of `cancel_order` outside `handlers.py`.

**Coverage note:** I did not run the tests. They stub the audit library, so even a passing run would not exercise the real one.

**Status:** this is the review report only. Adjudication and the close-out belong to the author or whoever closes the PR.

**Provisional merge view:** merge after fixes. Finding 3 should be resolved first, since the PR's central guarantee rests on a library nobody has seen. Finding 1 needs an explicit decision.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "observed in diff",
      "location": "orders.py:16-17",
      "scenario": "record() is written before db.set_status with no atomicity. If set_status raises, the audit log shows an order.cancelled event for an order that is still open, and a retry writes a duplicate record.",
      "fix": "Make the audit write and the status change atomic (same transaction), or order and compensate explicitly. Add a test where set_status raises."
    },
    {
      "severity": "P2",
      "evidence_level": "inferred from code",
      "location": "orders.py:11-17",
      "scenario": "Check-then-act race: two concurrent cancels of the same open order both pass the status guard and both write an audit record, so the 'records once' claim breaks under concurrency.",
      "fix": "Use a conditional update (status='open' only) or a transaction/lock, and record only when the update changed a row. Add a concurrency test."
    },
    {
      "severity": "P2",
      "evidence_level": "unverified, library not provided",
      "location": "orders.py:2; tests/test_orders.py:14",
      "scenario": "The real company_audit.record signature and failure behavior are unknown and the tests only use a stub. If the real record() swallows errors or has a different signature, the guarantee that a failed audit write leaves the order open does not hold, or calls fail at runtime.",
      "fix": "Confirm the real interface and add a contract test against the real library or its published interface, including failure propagation."
    },
    {
      "severity": "P2",
      "evidence_level": "inferred, manifest not provided",
      "location": "orders.py:2",
      "scenario": "company_audit becomes a hard import of orders with no dependency change in the patch. If it is not installed or declared in the deployed environment, importing orders and handlers fails and the cancel endpoint is down.",
      "fix": "Declare the dependency and add a clean-environment import check in CI."
    },
    {
      "severity": "P3",
      "evidence_level": "observed in diff",
      "location": "tests/test_orders.py:14",
      "scenario": "The test file permanently replaces sys.modules['company_audit'] at import, so other test modules in the same process get the stub.",
      "fix": "Use mock.patch.dict(sys.modules, ...) scoped with setUpModule/tearDownModule."
    },
    {
      "severity": "P3",
      "evidence_level": "inferred from code",
      "location": "handlers.py:7",
      "scenario": "request['user'] raises KeyError if the middleware did not set it, giving a generic error rather than an explicit auth failure, after the order lookup.",
      "fix": "Validate the user up front and return an explicit auth error; add a handler test without a user key."
    }
  ]
}
```