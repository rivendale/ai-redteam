# Review report: PR #131

**REVIEWED:** PR #131, "audit record on cancellation". Head `8a41c7e`, merge base `2d90b53`, both as stated in PR.md. I reviewed the patch and base files as supplied. I had no tools, so I could not open a worktree, confirm the SHAs or run the tests.

**TIER:** Standard. This is an ordinary code change: it adds a call to an existing shared library and threads one argument through the only caller. It does not change authentication, permissions, secrets, network exposure, migrations or money movement. Cancellations matter to support and finance, and the context sets the stakes at standard. If the owner treats user ids in the audit file as personal data, this becomes High and needs a second round.

**DATA:** Nothing was sent out of this session. The review ran in-session only.

**REVIEWERS:** This instance (Claude, `claude-opus-5-5`) reviewed the change. It did not write the change and has no authoring context. The commit trailers were not supplied, so authorship is not recorded.

## What I checked

- **Request coverage.** An audit record of who cancelled is written through `company_audit.record` (`orders.py:16`). The actor is `request["user"]`, which `handlers.py` documents as the signed-in user's id, a string set by the login middleware. Nothing beyond the request was added.
- **Ordering.** `record(...)` runs before `db.set_status` and after the shipped and already-cancelled guards. So:
  - a refused cancel writes nothing;
  - a re-cancel returns `False` and writes nothing;
  - a failed audit write raises before the status changes.

  This matches the docstring and the PR description.
- **Durability claim.** `company_audit.record` opens in append mode, writes, flushes and calls `os.fsync` before returning. The claim holds.
- **Tests (read, not run).**
  - `record` reads the module global `AUDIT_PATH` at call time, so rebinding `company_audit.AUDIT_PATH` in `setUp` does redirect writes, including through `orders`' `from company_audit import record`.
  - The failure test points at a missing directory. Opening it in `"a"` mode raises `FileNotFoundError`, which is an `OSError`, and the test asserts `db.set is None`.
  - Shipped, re-cancel, handler-actor and happy-path cases are each covered by a test.
- **Signature change.** `actor` is now required. The PR says `handlers.cancel` is the only caller, and it is updated.

## Non-findings, recorded so they are not re-raised

- **Audit written first.** If `db.set_status` then fails, a record exists for an order that is still open. This is the deliberate trade-off of write-ahead ordering, and the docstring states the invariant chosen: never a cancellation without its record. Without a transaction spanning the file and the DB, one direction has to be chosen, and this is the safer one for audit.
- **Concurrent cancels.** Two concurrent cancels of the same order can both pass the status check, which is a pre-existing race in `cancel_order`. Each would write a record. The change neither creates nor widens this race.

## FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| none | | | | |

**FILES NEEDED BUT NOT PROVIDED:**
- The rest of the repository, to confirm `handlers.cancel` is the only caller of `cancel_order` (any other caller would now raise `TypeError`).
- The login middleware, to confirm `request["user"]` is always set.
- CI results for head `8a41c7e`.
- The commit trailers.

# Close-out

**ADJUDICATION:** No findings, so there is nothing to adjudicate.

**VERIFIED AFTER FIXES:** There were no fixes. The head reviewed is `8a41c7e`.

**MERGE RECOMMENDATION:** Merge, once two things are confirmed:
1. CI on `8a41c7e` is present and green. I could not run the tests, and "Tests pass" is still an unverified claim.
2. A repo-wide search confirms no other callers of `cancel_order`.

No blocker and no owner decision is pending, unless the owner classes user ids as personal data, which would raise the tier to High.

```json
{
  "verdict": "merge",
  "findings": []
}
```