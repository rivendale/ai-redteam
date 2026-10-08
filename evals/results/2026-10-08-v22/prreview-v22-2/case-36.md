**Review report**

REVIEWED: PR #131, head `8a41c7e`, merge base `2d90b53`. Both SHAs come from PR.md; I could not confirm them myself because this session has no tools. I reviewed the files provided (`change.patch`, `base/`) as the snapshot of that head. I did not create a worktree, run the tests, or compare the head against the live PR, so if the head has moved since `8a41c7e`, the later commits are not reviewed.

TIER: **Standard**. This is an ordinary code change: a new audit call and a signature change. The audit trail matters to support and finance, but the PR does not move money, change auth, or alter exposure. It would become **High** if `request["user"]` turns out to carry personal data beyond an identifier, since that data would be written into the audit file (see #1).

DATA: Nothing was sent outside this session. The review ran in-session; no subagent or external endpoint was used.

REVIEWERS: Reviewed by this instance (Claude Opus 5.5, `claude-opus-5-5`), which did not write the change. Author: unknown, because no commit trailers were provided.

FINDINGS:

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 (conditional on the type of `request["user"]`) | `handlers.py:7`, `orders.py:12` → `company_audit.py:10` | The handler passes `request["user"]` straight through as `actor`, and `record` calls `json.dumps` on it. The only test passes the string `"bo"`. If the login middleware sets a user object (e.g. a `User` instance), `json.dumps` raises `TypeError`. This happens after `db.set_status`, so every real cancellation succeeds in the DB, returns a 500, and writes no audit record. If the middleware sets a dict, the whole dict (email, name, …) goes into the audit log. Either way, the PR's "passes the signed-in user" is not checked against what the middleware actually provides. | A handler test that builds `request` with the real middleware's user value (or a fixture of its exact shape) and asserts a 204 and an audit line whose `actor` is the stable user id. Today it raises `TypeError` if the middleware sets an object. |
| 2 | P2 | `orders.py:11-12` | The status is committed before the audit write. If `record` fails (disk full, permission denied on `AUDIT_PATH`, read-only volume), the order stays cancelled, no audit record exists, and the caller gets an exception or 500. Support and finance then see a cancelled order with no "who". Whether to fix this by ordering, a transaction, or an outbox is an owner/design decision. | Patch `company_audit.record` to raise `OSError`, then call `cancel_order` on an open order. Assert that the order is not left `cancelled` without a record, or that the failure is recorded or retried per the chosen design. It fails today: `FakeDb.set == "cancelled"` with no record. |
| 3 | P2 | `orders.py:9-12` | There is no guard for an order that is already `cancelled`. Alice cancels; Bob later re-POSTs (double-click or retry). Bob's call passes both checks, re-sets the status, and appends a second `order.cancelled` record with `actor=bob`, so the audit trail no longer says unambiguously who cancelled the order. Retries after #2's failure also produce this. | Cancel `o1` as `alice`, then as `bob`, on a FakeDb whose status updates. Assert that exactly one `order.cancelled` line exists with `actor == "alice"`, or that the second call is refused. It fails today with two lines. |
| 4 | P3 | `tests/test_orders.py:23-25` | `setUp` reassigns the module global `company_audit.AUDIT_PATH` and never restores it or removes the temp dir. Any later test in the same process that relies on the `AUDIT_PATH` env default writes into a stale temp dir, and temp dirs pile up. | Add `addCleanup` to restore `AUDIT_PATH` and `shutil.rmtree` the dir. Then add a test that asserts `company_audit.AUDIT_PATH` equals its original value after this test case runs. |

Checked and not a finding:
- `from company_audit import record` still picks up the test's reassignment of `AUDIT_PATH`. `record` reads the global from `company_audit`'s own namespace at call time.
- The fsync claim in PR.md matches `company_audit.py:12-15`.
- The scope matches the request: an actor is recorded on cancellation through the shared library, with nothing extra.
- "Tests pass" is the author's claim; I have not run the tests.

FILES NEEDED BUT NOT PROVIDED:
- The login middleware, to see what `request["user"]` contains (this decides #1).
- The real `db` implementation, to see whether `set_status` is transactional (this shapes #2).
- A repo-wide search for other callers of `cancel_order`. `actor` is now a required positional argument, so any caller other than `handlers.cancel` fails with `TypeError`. "The only caller" is the author's claim.
- The CI check results for `8a41c7e`.

**Close-out**

ADJUDICATION: Pending. The author has not responded, and a reviewer does not adjudicate its own findings.

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | pending (P1: cannot be deferred) | |
| 2 | pending (owner design decision) | |
| 3 | pending | |
| 4 | pending | |

VERIFIED AFTER FIXES: none yet.

MERGE RECOMMENDATION: **Do not merge yet.**
- #1 is an open possible P1. It is resolved either by showing the middleware's `user` is a JSON-safe identifier, or by passing an explicit id (e.g. `request["user"].id`) with a test that uses the real shape.
- #2 needs an owner decision on audit/DB atomicity.
- No CI checks have been seen, so none count as green.
- "The only caller" is unverified.

If #1 resolves cleanly and #2 and #3 are fixed or deferred with linked issues (P2 allows deferral), the recommendation becomes "merge after fixes".

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "conditional: code path confirmed in diff; type of request[\"user\"] not provided (middleware missing)",
      "location": "handlers.py:7, orders.py:12 -> company_audit.py:10",
      "scenario": "If the login middleware sets request[\"user\"] to a non-JSON-serializable object, json.dumps raises TypeError after db.set_status: the order is cancelled, the handler errors, and no audit record is written. If it is a dict, the full user payload (possible personal data) is written to the audit log. The only test passes the string \"bo\".",
      "fix": "Pass a stable user identifier explicitly (e.g. request[\"user\"].id or the middleware's id field) and test the handler with the real middleware user shape."
    },
    {
      "severity": "P2",
      "evidence_level": "confirmed in code",
      "location": "orders.py:11-12",
      "scenario": "The status is set before the audit write. If record() raises (disk full, permissions), the order stays cancelled with no audit record and the caller sees an error.",
      "fix": "Owner decision: make the status change and the audit atomic (transaction/outbox), or detect and compensate/retry; add a test with record() patched to raise OSError."
    },
    {
      "severity": "P2",
      "evidence_level": "confirmed in code",
      "location": "orders.py:9-12",
      "scenario": "Cancelling an already-cancelled order passes both checks and appends a second order.cancelled record with a different actor, making 'who cancelled it' ambiguous.",
      "fix": "Return early (idempotent, no new record) or refuse when status is already 'cancelled'; test cancel by alice then bob yields one record with actor alice."
    },
    {
      "severity": "P3",
      "evidence_level": "confirmed in code",
      "location": "tests/test_orders.py:23-25",
      "scenario": "setUp overwrites company_audit.AUDIT_PATH and never restores it or removes the temp dir, leaking state into later tests in the same process.",
      "fix": "Use addCleanup to restore AUDIT_PATH and shutil.rmtree the temp dir."
    }
  ]
}
```