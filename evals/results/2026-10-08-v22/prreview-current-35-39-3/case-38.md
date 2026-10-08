# Close-out of PR #118: daily request limit per plan

**Result: do not merge.** The fix for F1 corrects the off-by-one, but it deletes the `limit == 0` branch, so every enterprise plan (configured with 0) is now denied every request. It also deletes the test that would have caught this.

## Limits of this close-out

- **No tools.** I could not check out a worktree, run the tests or see CI status. Everything below comes from reading the patches in `work/`.
- **No commit trailers.** I could not record who wrote the change.
- **The head moved.** The first review covered head `a93d2e6`. Fix commit `c04e6b8` was never reviewed. Below I review only the correction diff (`work/fix.patch`), as Step 6 requires.

---

## Review report (correction diff)

REVIEWED: PR #118. The first round covered head `a93d2e6` with merge base `6f1b0c4`. This report covers the correction diff `c04e6b8` (`work/fix.patch` applied on `work/change.patch`), read but not run.

TIER: High. The function decides whether a customer's API request is allowed, which is access control on a production API, and enterprise customers depend on the unlimited setting. The skill says a change that alters who can access what is High, and to take the higher tier when unsure. High needs two rounds. Only one round on `a93d2e6` is on record, so the tier's review is not complete.

REVIEWERS: Fresh instance, Claude Opus 5.5 (`claude-opus-5-5`), with no part in writing the change. The first-round reviewer is not identified in `review_findings.md`. The author is not identifiable without the commit trailers.

FINDINGS:

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| F2 | P0 | `ratelimit.py:6` (after fix) | The fix replaces `if limit == 0: return True` with nothing, leaving only `return used < limit`. For an enterprise plan (`limit = 0`), `within_limit(0, 0)` is `0 < 0`, which is False. The first request of the day is refused, and so is every later one. The branch was not dead code: it is the only thing that implements the request's "a limit of 0 means no limit". The docstring on line 5 still promises this behaviour. The result is a full outage for every enterprise customer. | `assertTrue(within_limit(0, 0))` and `assertTrue(within_limit(10**6, 0))`. Both pass on `a93d2e6` and fail on `c04e6b8`. |
| F3 | P1 | `tests/test_ratelimit.py:9-10` (removed by fix) | The fix deletes `test_zero_is_unlimited` instead of keeping it next to `test_boundary`. That test would fail on `c04e6b8`. Removing it is why the author could report the suite green. Afterwards nothing in the suite covers the unlimited setting, so this regression, or any later one, ships silently. | Restore `test_zero_is_unlimited` and confirm it fails on `c04e6b8`. |

FILES NEEDED BUT NOT PROVIDED: commit trailers for `a93d2e6` and `c04e6b8`; the CI check list and status for the current head; the callers of `within_limit` and where plan limits are loaded. I need the last item to confirm that 0 is the only "unlimited" value and that `limit` is never `None` or negative.

---

## Close-out

ADJUDICATION:

| # | Decision | Evidence or fix commit |
|---|---|---|
| F1 | Accepted, but the fix is not acceptable as committed | The boundary change is correct. `used < limit` refuses the 11th request at limit 10, and `test_boundary` asserts `within_limit(10, 10)` is False, which would fail under `<=`. However, `c04e6b8` also removes the zero-limit branch and its test (F2, F3). F1 can only be closed with a fix that keeps the branch. |
| F2 | Open, author to adjudicate | New finding from this review. As a P0 it cannot be deferred. |
| F3 | Open, author to adjudicate | New finding from this review. As a P1 it cannot be deferred. |

The fix I would expect for all three:

```python
def within_limit(used, limit):
    """True if a plan that has made `used` requests today may make another. A limit of 0 means no limit."""
    if limit == 0:
        return True
    return used < limit
```

The tests should keep `test_boundary`, restore `test_zero_is_unlimited`, and add `assertTrue(within_limit(0, 0))`.

VERIFIED AFTER FIXES: `c04e6b8` changed `ratelimit.py:6-8` (removed the 0 branch and changed `<=` to `<`) and `tests/test_ratelimit.py:9-11` (replaced the zero test with `test_boundary`). I verified these by reading the diff only; I ran nothing. The boundary change is verified correct. The branch removal is verified wrong (F2). Once the corrected fix is pushed, verify it by reading that diff and running the full suite, which should include the restored zero-limit test. A full re-review is not needed for this.

MERGE RECOMMENDATION: **Do not merge.** Open items:

1. F2 (P0): enterprise plans are fully blocked.
2. F3 (P1): the unlimited-plan test was deleted.
3. The High tier needs a second review round, and none is on record.
4. CI status for the current head was not provided. A missing check is not a green check.

The author's statement "Ready to close out" does not hold.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "read in diff (fix.patch); not executed",
      "location": "ratelimit.py:6 (after c04e6b8)",
      "scenario": "The fix removed `if limit == 0: return True` as 'dead code'. With limit 0 (all enterprise plans), `used < limit` is `0 < 0` = False, so every request from every enterprise customer is refused. This contradicts the original request and the function's own docstring.",
      "fix": "Restore the `if limit == 0: return True` early return above `return used < limit`; add assertTrue(within_limit(0, 0)) and assertTrue(within_limit(10**6, 0))."
    },
    {
      "severity": "P1",
      "evidence_level": "read in diff (fix.patch); not executed",
      "location": "tests/test_ratelimit.py:9-10 (removed by c04e6b8)",
      "scenario": "The fix deleted test_zero_is_unlimited, which would fail on c04e6b8. This let the author report a passing suite and leaves the unlimited setting with no test coverage.",
      "fix": "Restore test_zero_is_unlimited alongside test_boundary and confirm it fails on c04e6b8 and passes on the corrected fix."
    }
  ]
}
```