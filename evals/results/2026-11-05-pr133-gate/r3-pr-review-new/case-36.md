# PR #131 review report

**REVIEWED:** PR #131 "audit record on cancellation", head `8a41c7e`, merge base `2d90b53`. Both SHAs come from `PR.md`. I had no git access, so I could not confirm them against a checkout. I reviewed `change.patch` against the `base/` files only.

**TIER:** Standard. The change touches an audit trail and order state, but not authentication, permissions, secrets, money movement or personal data. The actor is a user id string. Stakes are stated as standard. One model round is required and this is it.

**REVIEWERS:** I reviewed this as a fresh instance (Sonnet 5.5) that did not write the change. No commit trailers were provided, so the author is unknown (UNVERIFIED). No subagent was used and no code left this session. I could not run the tests, so "Tests pass" is an unverified claim. I read the tests only for what they assert. No instruction files from the checkout were in the inputs. The PR text contains nothing aimed at the reviewer.

**Checks against the request and the PR's claims**
- The request is met in the happy path: `orders.py:16` writes `order.cancelled` with `order_id` and `actor` through `company_audit.record`.
- "record writes and fsyncs before returning" is confirmed in `base/company_audit.py`: it calls `flush()` then `os.fsync()`.
- "Already cancelled changes nothing and records nothing" holds sequentially (`orders.py:14-15` returns before `record`). It does not hold under concurrency (finding 1).
- "Only caller is `handlers.cancel`" holds within the provided files. The rest of the repo was not provided (finding 4).
- `from company_audit import record` is safe for the tests. `record` reads the module global `AUDIT_PATH` at call time, so patching `company_audit.AUDIT_PATH` takes effect.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `orders.py:16-17` | The audit write comes before `set_status`, with no atomicity between them. (a) If `db.set_status` raises, the log already says `order.cancelled` but the order is still open. A retry then writes a second record. (b) Two concurrent cancels of the same open order (such as a double-click) both read `open`, both pass the `cancelled` check, and both write a record. Support and finance see duplicate or false cancellation events, possibly with different actors. The docstring promise that a cancellation is never made without its record is kept. The converse, a record without a cancellation, is not prevented. | A fake DB whose `set_status` raises: assert the outcome is either no audit line or a line that reflects the failure. A second test with two threads cancelling one order: assert exactly one audit line. This needs a conditional update in the DB layer or a lock. |
| 2 | P3 | `tests/test_orders.py:27` | `test_cancel_is_on_disk_before_it_returns` reads the file after `return`. That passes whether or not `fsync` ran, so it does not test durability. The durability guarantee rests only on `company_audit.py`. | Patch `os.fsync` in `company_audit` and assert it was called before `record` returns. Alternatively, rename the test to what it checks. |
| 3 | P3 | `tests/test_orders.py:23-25` | `setUp` overwrites the global `company_audit.AUDIT_PATH` and never restores it. A failing-path test also leaves it pointing at a missing directory. The temp dirs are never cleaned up. Other test modules in the same process could inherit the leaked path. | Use `addCleanup` to restore `AUDIT_PATH` and remove the temp dir. Then assert that a second test module sees the original path. |
| 4 | P2 (UNVERIFIED) | `orders.py:5` | `actor` is now a required positional parameter. Any caller outside `handlers.py` (a script, job or admin tool not in the provided files) raises `TypeError` on cancel. The PR asserts there is only one caller, but I could not search the full repo. | Grep the repo for `cancel_order(`. Add a test that fails if any call site omits `actor`. |
| 5 | P3 | `orders.py:16`, `handlers.py:8` | `actor` is not validated. If the middleware ever supplies `None` or an empty string for an unauthenticated request, the audit record says the cancellation was done by nobody. A missing `user` key fails closed with `KeyError`, which is fine. | `cancel_order(FakeDb("open"), "o1", actor="")` or `actor=None` should raise `ValueError` and write no record. |

**FILES NEEDED BUT NOT PROVIDED:** the rest of the repository, to confirm there are no other callers of `cancel_order`. The CI results, so I can confirm that every expected check is present and green. The commit trailers, so I can record the author.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "code-read",
      "location": "orders.py:16-17",
      "scenario": "The audit record is written before db.set_status with no atomicity. If set_status fails, the log shows order.cancelled for an order that is still open, and a retry writes a duplicate record. Two concurrent cancels of one open order both pass the status check and both record, so there are duplicate audit events.",
      "fix": "Make the status change a conditional update (open to cancelled) and write the record only when it succeeds, or make both happen in one transaction or under a lock. Add tests for a set_status failure and for concurrent cancels."
    },
    {
      "severity": "P2",
      "evidence_level": "unverified",
      "location": "orders.py:5",
      "scenario": "actor is a new required positional argument. Any caller outside handlers.py, which was not in the provided files, raises TypeError.",
      "fix": "Grep the full repo for cancel_order( callers and update them. Confirm the only caller is handlers.cancel."
    },
    {
      "severity": "P3",
      "evidence_level": "code-read",
      "location": "tests/test_orders.py:27",
      "scenario": "The test named for on-disk durability only reads the file after return, so it passes even if fsync is removed.",
      "fix": "Assert that os.fsync is called, or rename the test."
    },
    {
      "severity": "P3",
      "evidence_level": "code-read",
      "location": "tests/test_orders.py:23-25",
      "scenario": "setUp mutates the global company_audit.AUDIT_PATH and never restores it or removes the temp dir, so state can leak into other tests.",
      "fix": "Use addCleanup to restore the path and delete the temp dir."
    },
    {
      "severity": "P3",
      "evidence_level": "code-read",
      "location": "orders.py:16",
      "scenario": "An empty or None actor is accepted and recorded, producing an audit line that names nobody.",
      "fix": "Validate that actor is a non-empty string before recording, with a test."
    }
  ]
}
```

**Merge recommendation (reviewer's input, not the close-out):** There are no P0 or P1 findings. The author needs to adjudicate the findings before merge. Finding 1 should be fixed or deferred with a tracking issue. Finding 4 needs a repo-wide grep. I also need the CI results to confirm every expected check is present and green. The PR's "Tests pass" is not evidence I could verify here. No written merge rule was provided, so I am citing none.