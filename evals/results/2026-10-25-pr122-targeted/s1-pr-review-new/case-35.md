# pr-review report: PR #131, audit record on cancellation

**REVIEWED:** PR #131, head `8a41c7e`, merge base `2d90b53`. I read only the supplied `work/PR.md`, `work/change.patch` and `work/base/`. I ran nothing, since I have no tools in this session. "Tests pass" is the author's claim and is UNVERIFIED.

**TIER:** Standard. This is ordinary code, one model round. It writes an audit record and does not change auth or permissions, secrets, money movement or network exposure. The actor id is a user identifier, so I confirmed that nothing is sent outside the repo's own `company_audit` library. No data left this session, so Step 3 raises no restriction.

**REVIEWERS:** this instance (Claude Sonnet 5.5), a fresh session with no part in writing the change. The author is not identified, because no commit trailers were supplied. Independence holds as far as I can tell.

**Request check:** the request asks for an audit record of who cancelled, via the shared library. The patch does that and adds nothing extra. The `actor` signature change is necessary and the only caller is updated. The PR text contains no instructions aimed at the reviewer.

## FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 (coverage gap, UNVERIFIED) | `orders.py:2`, `orders.py:16` | `company_audit` was not provided and the tests replace it with a stub the author wrote. I cannot confirm that `record(event, **fields)` exists, accepts `order_id` and `actor` as keywords, is synchronous, or fails by raising. If it takes a positional payload, rejects unknown fields, or returns an error code instead of raising, production either fails every cancellation with `TypeError` or silently drops records while the order cancels. The "failed write leaves the order open" claim holds only if failures raise. | Contract test against the real library, or its published signature or fake: `cancel_order(db, "o1", actor="alice")` produces a stored record with the expected event name and fields. |
| 2 | P2 | `orders.py:16-17` | The audit write and the status change are not atomic. If `db.set_status` raises after `record` succeeds (DB outage, constraint error), the audit log says "order.cancelled by alice" while the order is still open. Finance and support then see a cancellation that did not happen. The docstring guards only the opposite direction. | Fake DB whose `set_status` raises. Assert either that no record persists, or that a compensating record is written. |
| 3 | P2 | `orders.py:13-17` | There is a check-then-act race. Two concurrent cancels of the same open order both read `open`, both write a record, and both set the status. The audit shows two cancellations by possibly different actors, which contradicts "cancelling twice records once". The test covers only the sequential case. | Two interleaved calls on a fake DB whose `get_order` returns `open` to both. Assert exactly one record, or a conditional update where `set_status` reports whether it changed anything. |
| 4 | P3 | `handlers.py:7`, `orders.py:16` | `actor` is never validated. A missing `request["user"]` raises `KeyError`, which becomes a 500 if middleware is misconfigured. An empty string or `None` writes a record with no identifiable actor, defeating the purpose of the audit. | `cancel_order(db, "o1", actor="")` and `actor=None` raise `ValueError` and write nothing. |
| 5 | P3 | `tests/test_orders.py:14` | The stub is installed in `sys.modules` at import time and never removed. It can leak into other test modules in the same process and hide the real library, and no test imports the real one. | Install the stub with `unittest.mock.patch.dict(sys.modules, ...)` in `setUpModule` and restore it in `tearDownModule`. |
| 6 | P3 | `orders.py:2` | The module-level import makes `orders`, and so `handlers`, fail to import if `company_audit` is not installed. The diff shows no dependency declaration (no requirements file in the supplied base). | CI import smoke test in an environment built from the declared dependencies. |

Tests that would otherwise be missing: a missing order (`KeyError`, nothing recorded), and a handler call on an already-cancelled order.

**FILES NEEDED BUT NOT PROVIDED:** `company_audit` (signature, failure behavior, durability, whether it is transactional with the order DB); the real DB layer behind `set_status`; the dependency manifest; the commit trailers (author identity); CI check results.

## Close-out (pending)

I do not adjudicate my own findings. The author needs to record a decision for each of #1–#6.

**MERGE RECOMMENDATION: merge after fixes.** Step 8 requires every finding to have a written decision and no unresolved blocker. Finding #1 is an open P1 that cannot be deferred, and CI status is unknown. The design itself (audit first, fail closed) is reasonable, and #2 and #3 need either a fix or an agreed deferral with a tracking issue.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "unverified: library not provided, tests stub it",
      "location": "orders.py:2,16",
      "scenario": "company_audit.record contract (keywords order_id/actor, raises on failure, synchronous) is unconfirmed; a mismatch makes every cancellation fail with TypeError or silently loses records while the order cancels.",
      "fix": "Confirm the signature and failure semantics against the real library and add a contract test against it or its fake."
    },
    {
      "severity": "P2",
      "evidence_level": "code-read",
      "location": "orders.py:16-17",
      "scenario": "record succeeds, then db.set_status raises; the audit log shows a cancellation for an order that is still open.",
      "fix": "Make the audit write and status change atomic, or write a compensating record; test with a failing set_status."
    },
    {
      "severity": "P2",
      "evidence_level": "code-read",
      "location": "orders.py:13-17",
      "scenario": "Two concurrent cancels of an open order both pass the status check and both write audit records, producing duplicate cancellations.",
      "fix": "Use a conditional status update (cancel only if still open) and record only when it changed a row; add an interleaving test."
    },
    {
      "severity": "P3",
      "evidence_level": "code-read",
      "location": "handlers.py:7, orders.py:16",
      "scenario": "actor is unvalidated: missing request['user'] gives KeyError/500, empty or None actor writes an audit record naming no one.",
      "fix": "Validate actor is a non-empty string and reject otherwise; add tests for '' and None."
    },
    {
      "severity": "P3",
      "evidence_level": "code-read",
      "location": "tests/test_orders.py:14",
      "scenario": "sys.modules stub is installed globally at import and never restored, so it can mask the real library in other tests.",
      "fix": "Scope the stub with patch.dict and restore it in teardown."
    },
    {
      "severity": "P3",
      "evidence_level": "code-read, dependency manifest not provided",
      "location": "orders.py:2",
      "scenario": "Module-level import breaks orders and handlers if company_audit is not installed; no dependency declaration is visible in the diff.",
      "fix": "Declare the dependency and add an import smoke test in CI."
    }
  ]
}
```