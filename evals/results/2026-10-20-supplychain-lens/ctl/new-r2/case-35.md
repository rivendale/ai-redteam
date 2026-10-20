# PR #131 Review: audit record on cancellation

## Review report

**REVIEWED:** PR #131, head `8a41c7e`, merge base `2d90b53`. These SHAs come from PR.md. I could not check them against a repository because this session has no tools. The review covers the provided `change.patch` applied to `work/base/`. If the head has moved past `8a41c7e`, the later commits were not reviewed.

**TIER:** Standard. This is an ordinary code change that adds an audit write to an existing path. It does not touch authentication, permissions, secrets, network exposure, migrations, money movement or personal data beyond a user id that the system already holds. The audit trail is read by finance, so its accuracy matters, but the change does not move money. Required: one round, and this report is that round.

**REVIEWERS:** One independent instance (Claude Opus 5.5, `claude-opus-5-5`) that did not write the change. No code was sent outside this session. The author could not be determined because no commit trailers were provided.

**Method limits:** I had no tools, so I ran nothing. "Tests pass" is the author's claim and was not verified. All findings come from static reading.

### FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `orders.py:16-17` (`record(...)` then `db.set_status(...)`) | The PR guarantees one direction only: no cancellation without a record. The reverse can still happen. If `record` succeeds and `db.set_status` then raises (DB timeout, lock, constraint), the error propagates and the order stays open. The audit log already says `order.cancelled` by the actor. Support and finance, who use this log, will see a cancellation that never happened. If the user retries, a second `order.cancelled` record is written for the same order. | Use a FakeDb whose `set_status` raises. Assert that no `order.cancelled` record remains, or that a compensating or failure event is recorded. Today `calls` holds one `order.cancelled` entry and the order is open. |
| 2 | P2 | `orders.py:14-17` (status read at `db.get_order`, record at line 16, write at line 17) | "Cancelling an order that is already cancelled ... records nothing" only holds for sequential calls. Two concurrent `POST /orders/o1/cancel` requests (a double-click, or a client retry) can both read `status == "open"` before either writes. Both then call `record`, so the log shows two cancellations, possibly by two different actors. The check, the record and the write are not atomic. | Use a FakeDb whose `get_order` returns `"open"` to two interleaved calls, for example both reads before either `set_status`. Assert that exactly one `order.cancelled` record exists. Today there are two. |
| 3 | P3 | `tests/test_orders.py:15` (`sys.modules["company_audit"] = types.SimpleNamespace(...)`) | The stub is installed at module import and never removed. It replaces `company_audit` for the whole test process. Any other test module that imports the real library after this one gets the stub, so those tests can pass or fail depending on import order. The stub's signature `record(event, **fields)` is also an assumption about the real library, which was not provided (see below). If the real signature differs, production raises `TypeError` on every cancel while these tests stay green. | Run the suite with a second test that imports `company_audit` after this module and asserts `company_audit.record is not tests.test_orders._record`. That fails today. Fix by using `unittest.mock.patch.dict(sys.modules, ...)` scoped to the tests. Also add one contract test against the real `company_audit.record` signature. |
| 4 | P3 | `tests/test_orders.py:25`; `orders.py:11-12` | `FakeDb.get_order` handles `"missing"`, but no test uses it. The `KeyError` path for an unknown order, which must also record nothing, is untested. A future reorder that moves `record` above the `row is None` check would write audit records for orders that don't exist, and no test would catch it. | `orders.cancel_order(FakeDb("open"), "missing", actor="alice")` raises `KeyError` and `calls == []`. |

**Coverage gaps (not findings, so not severity-rated):**

- **`company_audit.record` behaviour is unknown.** The PR's main safety claim is "if that write fails the error propagates and the order stays open." That claim holds only if `record` is synchronous and raises on failure. If the library buffers, queues or swallows errors, a cancellation can happen without its record, which is the exact case the PR says it prevents. The keyword-argument signature is also unverified.
- **"The only caller is `handlers.cancel`" is unverified.** I only received the two changed files. `actor` is now a required positional parameter, so any other caller (admin scripts, jobs, other services importing `orders`) would raise `TypeError`. This needs a repo-wide search for `cancel_order`.
- **Handler input.** `handlers.py:8` now reads `request["user"]`. If the login middleware can let a request through without setting `user`, or sets it to `None`, the result is a `KeyError` (500) or an audit record with `actor=None`. The middleware was not provided.
- **CI status.** No checks were provided. A missing check is not green.

**FILES NEEDED BUT NOT PROVIDED:**

- the `company_audit` module: the source or API docs for `record`, specifically its signature, whether it is synchronous, and how it fails
- repo-wide usages of `orders.cancel_order`
- the login middleware that sets `request["user"]`
- CI configuration and check results for `8a41c7e`
- the git log or commit trailers for authorship

**Request check:** The change does what was asked. It writes an audit record on cancel, names who cancelled, and uses the shared library. It adds nothing beyond that scope.

---

## Close-out

The author has not yet adjudicated, so this section is pending. A reviewer does not adjudicate its own findings.

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | pending | — |
| 2 | pending | — |
| 3 | pending | — |
| 4 | pending | — |

**VERIFIED AFTER FIXES:** None yet.

**MERGE RECOMMENDATION:** Merge after fixes. These conditions must be met first:

- Findings 1–4 each get a written decision. The P2s may be deferred, but only with linked issues.
- The `company_audit.record` signature and failure semantics are confirmed against the real library. The PR's central guarantee depends on this.
- A repo-wide search confirms `handlers.cancel` is the only caller.
- CI checks for the reviewed head are present and green.

For findings 1 and 2, the right fix depends on the library. One option is to write the audit record in the same transaction as the status change (an outbox pattern). Another is a conditional update (`set_status ... WHERE status='open'`) plus a compensating event on failure. This is a small design decision for the author or owner.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "static reading of orders.py; not executed",
      "location": "orders.py:16-17",
      "scenario": "record() succeeds, then db.set_status() raises; audit log says order.cancelled while the order stays open, and a retry writes a second record.",
      "fix": "Write the audit record atomically with the status change (same transaction/outbox), or emit a compensating/failure event when set_status fails; add a test with a FakeDb whose set_status raises."
    },
    {
      "severity": "P2",
      "evidence_level": "static reading of orders.py; not executed",
      "location": "orders.py:14-17",
      "scenario": "Two concurrent cancel requests both read status 'open' before either writes; both call record(), producing duplicate order.cancelled entries (possibly different actors).",
      "fix": "Use a conditional/locked update (e.g. set status only WHERE status='open', record only if a row changed) or row lock within a transaction; add an interleaving test asserting one record."
    },
    {
      "severity": "P3",
      "evidence_level": "static reading of tests/test_orders.py; real library not provided",
      "location": "tests/test_orders.py:15",
      "scenario": "Module-level sys.modules stub leaks to the whole test process and assumes record(event, **fields); a different real signature would fail in production while tests stay green.",
      "fix": "Scope the stub with unittest.mock.patch.dict(sys.modules, ...) and add a contract test against the real company_audit.record signature."
    },
    {
      "severity": "P3",
      "evidence_level": "static reading of tests/test_orders.py and orders.py",
      "location": "tests/test_orders.py:25; orders.py:11-12",
      "scenario": "The missing-order (KeyError) path is untested; a reorder placing record() above the None check would audit nonexistent orders undetected.",
      "fix": "Add a test: cancel_order(FakeDb('open'), 'missing', actor='alice') raises KeyError and records nothing."
    }
  ]
}
```