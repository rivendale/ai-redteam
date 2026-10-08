# PR #131 review: audit record on cancellation

**Review report**

**REVIEWED:** PR #131 at head `8a41c7e`, merge base `2d90b53`. The SHAs come from PR.md. I had no tools, so I could not resolve or check them out. The review covers only `change.patch` read against `work/base/`. If the head has moved since `8a41c7e`, the later commits were not reviewed.

**TIER:** Standard. The change adds an audit write to an existing state change. It does not touch authentication or permissions, secrets, network exposure, migrations or money movement. The new data is the signed-in user's id string, written to the shared audit library. That is an internal identifier going to the company's own audit sink, so I did not treat it as a new personal-data flow. The context also gives the stakes as standard. If the owner treats user ids in audit logs as personal data, this becomes High and needs a second round.

**REVIEWERS:**
- **Reviewer:** Claude Opus 5.5 (`claude-opus-5-5`), a single round in this session. I did not write or help write this change, and no code was sent anywhere outside this session.
- **Author:** unknown. No commits or trailers were provided, only the patch, so authorship should be read from the commit trailers at `8a41c7e`.

**What I checked against the code:**
- **Scope:** the request is "write an audit record saying who cancelled it, using the shared audit library." The patch does this and nothing more.
- **Ordering:** `record(...)` runs after the not-found, shipped and already-cancelled checks and before `db.set_status`. A raised audit error therefore leaves the order open, as claimed (`orders.py:16-17` in the patched file).
- **Re-cancel:** an already-cancelled order returns `False` before `record` runs, so nothing is recorded.
- **Caller:** `handlers.cancel` now passes `request["user"]`, which the handler docstring says is the user id string set by the login middleware. Only `handlers.py` was provided, so "the only caller" is unverified beyond these files.
- **Tests:** the five tests cover the PR's claims: recorded with actor, shipped refused and unrecorded, handler passes the user, failed write leaves the order open, and re-cancel records nothing. I read them but could not run them. "Tests pass" remains a claim.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P3 | `orders.py:9-17` (patched) | Two cancel requests for the same open order arrive concurrently, for example a double-click or a client retry. Both run `get_order` and see `"open"`, both pass the `"cancelled"` check, and both call `record("order.cancelled", ...)` before either `set_status` lands. Support and finance then see two cancellation records for one cancellation, possibly with different actors. Before this PR the race was harmless because `set_status` is idempotent; the audit write makes it visible. Whether `db` serialises these calls cannot be seen from the provided files, so this is inferred, not confirmed. | Use a fake db whose `get_order` blocks on a barrier until two threads have both read the order. Run `cancel_order` from both threads and assert exactly one `order.cancelled` record. This fails today. It passes once the status change is a conditional update (cancel only if still open) and the record is written only by the request whose update won, or once the record is deduplicated by order id. |

**Notes:** these were considered and not raised as findings.
- **Audit write succeeds, status write fails:** this leaves a record for a cancellation that did not happen. The PR deliberately chose this ordering and documents it in the docstring. The opposite ordering risks an unrecorded cancellation, which is worse for the stated purpose. It is a documented trade-off, not a defect. The author may want a follow-up record (for example `order.cancel_failed`) if finance reconciles strictly against these records.
- **Test stub left in `sys.modules`:** the test replaces `company_audit` in `sys.modules` at import time and never restores it. Other test modules in the same run that import the real library would get the stub. This is test hygiene only and has no production impact.

**FILES NEEDED BUT NOT PROVIDED:**
- **`company_audit` (the `record` signature and failure behaviour):** the tests stub it as `record(event, **fields)`. Nothing provided shows that the real library accepts `order_id=` and `actor=` as keyword arguments. Nothing shows that it raises on a failed write rather than swallowing the error or buffering asynchronously. If it does not raise, the "order stays open when the audit write fails" guarantee does not hold in production.
- **The rest of the repository:** needed to confirm that `handlers.cancel` is the only caller of `cancel_order`. Any other caller would now fail with a `TypeError`, because `actor` is a required argument.
- **CI results for `8a41c7e`.**

**Close-out**

The author has not adjudicated these findings yet, and a reviewer does not adjudicate its own findings.

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | Pending: author to decide | — |

**VERIFIED AFTER FIXES:** none yet.

**MERGE RECOMMENDATION:** merge after checks. No P0 or P1 was found, and the change does what the request asks. Before merging:
1. Confirm the real `company_audit.record` signature accepts `(event, order_id=..., actor=...)` and raises on a failed write.
2. Confirm there are no other callers of `cancel_order`.
3. CI must be present and green at `8a41c7e`.
4. Finding 1 needs a written decision: fix it, defer it with an issue link (allowed for a P3), or reject it with evidence that `db` serialises these calls.

```json
{
  "verdict": "merge_after_checks",
  "findings": [
    {
      "severity": "P3",
      "evidence_level": "inferred (db concurrency behaviour not provided)",
      "location": "orders.py:9-17 (patched)",
      "scenario": "Two concurrent cancels of the same open order both read status 'open' and both call record() before either set_status, producing two order.cancelled audit records (possibly with different actors) for one cancellation.",
      "fix": "Make the status change a conditional update (cancel only if still open) and write the record only from the request that won, or deduplicate the record by order id; add a two-thread barrier test asserting exactly one record."
    }
  ]
}
```