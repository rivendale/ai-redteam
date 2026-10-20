# PR #131 review: audit record on cancellation

**Review report**

**REVIEWED:** PR #131, head `8a41c7e`, merge base `2d90b53`. These short SHAs come from PR.md. I had no tools, so I could not check out the head, confirm the full SHAs or check that `change.patch` matches `8a41c7e`. This review covers the patch text as given against `work/base/`. Nothing was run. The "Tests pass" claim is unverified; reading the tests, I expect them to pass.

**TIER:** Standard. The change adds an audit write to an ordinary order operation. It does not touch authentication, permissions, secrets, network exposure, migrations or money movement. The context also rates the stakes as standard. One caveat: the user id now goes to `company_audit`. If that sink is held to personal-data rules, the tier should be High, and the owner should confirm it is not.

**REVIEWERS:**
- Reviewer: this session (Claude Opus 5.5, `claude-opus-5-5`). It did not write or help write the change, and the review stayed in this session.
- Author: unknown. No commits or trailers were provided.

**Scope against the request:** The request was "write an audit record saying who cancelled it, using the shared audit library". The patch does this:
- `orders.py` records the event with `order_id` and `actor`.
- `handlers.py` passes `request["user"]` as the actor.
- Nothing beyond the request was added.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `orders.py:16-17` (patched) | The audit record is written before the status change, and the two writes are not atomic. Sequence: the order is open, `record(...)` succeeds, then `db.set_status` raises (DB timeout, connection drop, constraint error). The audit log now says user X cancelled the order, but the order is still open. Finance and support see a cancellation that never happened. If the user retries, a second `order.cancelled` record is written for the same order. The PR's ordering avoids the opposite failure (a cancellation with no record), but replaces it with a false record. The fix options are a transaction or outbox shared with the status write, or a compensating or "failed" record. | Give `FakeDb.set_status` a failure mode that raises. Assert that `calls` holds no committed `order.cancelled` record for `o1` (or holds a compensating record). This fails today. |
| 2 | P2 | `orders.py:14-17` (patched) | The read, check and write are not atomic. Two concurrent cancel requests for one open order, from the same user (double-click) or two users, both read `status == "open"`. Both call `record(...)` and both set the status. Result: two `order.cancelled` records, possibly with different actors, and "who cancelled it" becomes ambiguous. The base code had the same race, but it was harmless there because setting `cancelled` twice changes nothing. Whether `db.get_order` locks is not shown. | Use a FakeDb whose `get_order` returns `open` for both callers (simulating interleaving), then call `cancel_order` twice before either `set_status` takes effect. Assert exactly one `order.cancelled` record. This fails today. A conditional update such as `UPDATE ... WHERE status='open'` would make it pass. |
| 3 | P3 | `tests/test_orders.py:15` | The test assigns `sys.modules["company_audit"]` at module import time and never restores it. In a test run that collects this file alongside any other test that imports the real `company_audit` (or patches it), those tests silently get the stub. Order-dependent passes or failures follow. | Run the suite with a second test module that does `import company_audit` and asserts it is the real module. Collected after this file, it fails today. Using `unittest.mock.patch.dict(sys.modules, ...)` in `setUpModule`/`tearDownModule` makes it pass. |

**Coverage gaps (unresolved, not findings):**

- **`company_audit.record` contract.** This is the largest open question. Every test stubs `record(event, **fields)`, so none of them shows that the real library accepts this call. Three things are unverified:
  - **Signature.** If the real signature differs (positional fields, a different event naming scheme, required fields such as `target` or `timestamp`), every cancellation raises `TypeError`. That fails closed: cancellation stops working entirely.
  - **Failure behaviour.** The PR claims "a failed audit write leaves the order open". That holds only if `record` raises synchronously on failure. If the library buffers, queues asynchronously or swallows errors, the guarantee in the new docstring is false.
  - **Actor type.** The library may expect something other than a string user id for the actor field.
- **Other callers of `cancel_order`.** The PR says `handlers.cancel` is the only caller. `actor` is now a required positional parameter, so any other caller (jobs, admin scripts, other services) now raises `TypeError`. I only had the two changed files and could not confirm there are no other callers.

**FILES NEEDED BUT NOT PROVIDED:**
- `company_audit` source or API docs, covering the `record` signature, its error and failure semantics, and its data-handling and retention class.
- A repo-wide search for callers of `orders.cancel_order`.
- The `db` implementation behind `get_order` / `set_status`, to see whether it locks or runs in a transaction.
- The CI check results for `8a41c7e`.

---

**Close-out**

The reviewer does not adjudicate its own findings. This section is for the author and whoever closes the PR.

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | Pending (author) | — |
| 2 | Pending (author) | — |
| 3 | Pending (author) | — |

**VERIFIED AFTER FIXES:** None yet. Any fix should be verified by a targeted read of the fix diff and its regression test, not by another full review round.

**MERGE RECOMMENDATION: not yet.** The findings are P2/P3 and could be deferred with tracking issues, but merge criteria are not met:
- The findings have no written decisions.
- CI check status for `8a41c7e` is unknown, and a missing check is not green.
- The `company_audit.record` contract is unverified. The PR's central guarantee depends on it.

Once the library contract is confirmed (signature, and that it raises synchronously on failure), the other callers are ruled out, the three findings are adjudicated and checks are green, this can merge.

```json
{
  "verdict": "not_ready_pending_adjudication",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "code_read",
      "location": "orders.py:16-17",
      "scenario": "record() succeeds, then db.set_status raises: the audit log says the order was cancelled by the actor, but the order stays open; a retry writes a second cancellation record.",
      "fix": "Make the audit write and status change atomic (shared transaction or outbox), or write a compensating/failed record when set_status fails; add a test where set_status raises."
    },
    {
      "severity": "P2",
      "evidence_level": "inferred_db_locking_not_shown",
      "location": "orders.py:14-17",
      "scenario": "Two concurrent cancels both read status 'open', and both write order.cancelled records, possibly with different actors, so who cancelled the order is ambiguous.",
      "fix": "Use a conditional status update (WHERE status='open') or a row lock, and record only when the transition actually happened; add an interleaving test asserting one record."
    },
    {
      "severity": "P3",
      "evidence_level": "code_read",
      "location": "tests/test_orders.py:15",
      "scenario": "The module-level sys.modules['company_audit'] stub is never restored, so other tests in the same run silently import the stub instead of the real library.",
      "fix": "Install the stub with mock.patch.dict(sys.modules, ...) in setUpModule and remove it in tearDownModule."
    }
  ]
}
```