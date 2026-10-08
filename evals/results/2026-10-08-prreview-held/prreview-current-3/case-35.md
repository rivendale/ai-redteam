**Review report**

REVIEWED: PR #131, head `8a41c7e`, merge base `2d90b53`. I reviewed the supplied `change.patch` against `work/base/`. No tools were available, so I could not confirm that the patch matches `8a41c7e`, and I could not run anything.

TIER: Standard. The change adds an audit write to an ordinary state change. It does not touch authentication, permissions, secrets, network exposure or money movement, and the context sets the stakes as standard. The audit trail feeds finance, so if the owner treats finance audit records as regulated, raise this to High.

REVIEWERS: Claude Opus 5.5 (`claude-opus-5-5`), a fresh instance with no part in writing the change. The author could not be determined because the commit trailers were not supplied. Nothing was sent outside this session.

FINDINGS:

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `orders.py:16-17` | The audit record is written, then `db.set_status` raises (DB timeout, lost connection, constraint error). The order stays open, but the audit trail permanently says it was cancelled by `actor`. If the user retries and it succeeds, there are two `order.cancelled` records for one cancellation. The PR only guarantees one direction ("never cancelled without a record"). The reverse, a record without a cancellation, is unhandled and undocumented, and finance reads these records. | Use a `FakeDb` whose `set_status` raises. Call `cancel_order` and assert that either no `order.cancelled` record remains or a compensating record (e.g. `order.cancel_failed`) is written. This fails today: `calls` holds one `order.cancelled` and the order is open. |
| 2 | P3 | `orders.py:9,14-17` | Two concurrent cancels of the same open order (a double-click, or user and support at once) can both read `status == "open"` before either write. Both write `order.cancelled`, possibly with different actors, and both return True. The PR's claim "cancelling an already-cancelled order records nothing" holds only for sequential calls. This assumes `db.get_order` takes no row lock; the db layer was not provided. | Use a `FakeDb` whose `get_order` returns `"open"` to two interleaved calls (or a threaded test against the real db). Assert exactly one `order.cancelled` record. This fails today with two. |
| 3 | P3 | `tests/test_orders.py:15` | The test replaces `sys.modules["company_audit"]` at import time and never restores it. In a full suite run, any test module imported later that uses `company_audit` silently gets the stub. If another module has already imported `orders` with the real library, this file's assertions on `calls` see nothing. | Run the suite with a second test file that imports `company_audit` and checks a real attribute, ordered after this one. It fails today. Fix by patching `orders.record` with `unittest.mock.patch` per test. |

Other notes, not findings:
- The PR's central guarantee is that a failed audit write raises and leaves the order open. That depends on the real `company_audit.record` raising synchronously on failure, and on it accepting `(event, order_id=..., actor=...)`. Neither is verified: the tests stub the library with exactly the behaviour the PR assumes. If `record` buffers or sends asynchronously, or reports failure by return value, the guarantee is false. I couldn't write a concrete scenario without the library, so this is listed below rather than as a finding.
- Scope matches the request: an audit record of who cancelled, using the shared library, and nothing extra. On reading, the tests appear consistent with the code. "Tests pass" is still unverified because I could not run them.

FILES NEEDED BUT NOT PROVIDED: the `company_audit` source or docs for the `record` signature, failure behaviour and sync vs. async; the db layer for `get_order`/`set_status` transaction and locking semantics; commit trailers for authorship; CI check results for `8a41c7e`.

**Close-out**

ADJUDICATION: Pending. The author adjudicates findings 1–3, and the reviewer does not adjudicate its own findings. All three are P2/P3, so each may be fixed or deferred with a linked issue.

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | pending | — |
| 2 | pending | — |
| 3 | pending | — |

VERIFIED AFTER FIXES: Nothing yet. No fixes have been made.

MERGE RECOMMENDATION: **Merge after fixes.** There are no P0/P1 blockers. Before merge:
- every finding needs a written decision;
- the `company_audit.record` contract must be confirmed (it raises synchronously on failure, and the keyword fields are accepted), since the PR's main guarantee rests on it;
- the expected CI checks for `8a41c7e` must be present and green, which I have not seen;
- the patch reviewed here must be confirmed to match head `8a41c7e`.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "code-read",
      "location": "orders.py:16-17",
      "scenario": "record() succeeds, then db.set_status raises; the order stays open but an order.cancelled audit record exists, and a retry writes a second one.",
      "fix": "Write the record and the status change atomically (same transaction or outbox), or write a compensating audit event when set_status fails; add a test with a set_status that raises."
    },
    {
      "severity": "P3",
      "evidence_level": "inferred (db locking semantics not provided)",
      "location": "orders.py:9,14-17",
      "scenario": "Two concurrent cancels both read status 'open' and both write order.cancelled (possibly with different actors) and both return True.",
      "fix": "Use a conditional update (set status to cancelled where status is open) and record only if a row changed, or lock the row on read."
    },
    {
      "severity": "P3",
      "evidence_level": "code-read",
      "location": "tests/test_orders.py:15",
      "scenario": "The global sys.modules['company_audit'] stub is never restored, so later test modules get the stub, and an earlier real import of orders makes this file's assertions miss calls.",
      "fix": "Patch orders.record per test with unittest.mock.patch instead of replacing sys.modules at import time."
    }
  ]
}
```