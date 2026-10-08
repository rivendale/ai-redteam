# Close-out of PR #118: daily request limit per plan

**Recommendation: do not merge.** The fix for F1 makes every enterprise plan fail closed. I could not run anything in this session, so all of this comes from reading the patches.

**REVIEWED:** PR #118. The first round covered head `a93d2e6` against merge base `6f1b0c4`. This close-out covers the correction `c04e6b8` (`work/fix.patch`) on top of `a93d2e6`. No full review has covered head `c04e6b8`; only its correction diff was read, which is what Step 6 asks for.

**TIER:** High. The function decides whether a request to the production API is served, so it controls access. A wrong answer either blocks paying customers or lifts their limits. The first round was one run with no named vendor, so the second round the High tier requires has not run. If the owner decides this is Standard, that is their call to record; this finding blocks merge either way.

**REVIEWERS:** This close-out is by Claude Opus 5.5, a fresh instance that did not write the change or the fix. The first-round reviewer is not named in `review_findings.md`. The author is the PR author. No commit trailers were provided, so co-authors cannot be confirmed.

## Verification of the correction diff

The change from `<=` to `<` is correct and fixes F1:

- With limit 10, `within_limit(9, 10)` is True and `within_limit(10, 10)` is False.
- `test_boundary` fails on `a93d2e6`, because `10 <= 10` is True. It passes on `c04e6b8`.

The fix also removes `if limit == 0: return True`, calling it "dead code". It was not dead code. It was the requirement: "A limit of 0 means the plan has no limit (enterprise plans are configured with 0)."

- After the fix, `within_limit(used, 0)` is `used < 0`. That is False for every `used >= 0`.
- So every enterprise plan is refused its first request of the day.
- The fix also deletes `test_zero_is_unlimited`, the only test that would have caught this. On `c04e6b8` that test would fail, since `10**6 < 0` is False.
- The docstring at `ratelimit.py:5` still says "A limit of 0 means no limit", which the code now contradicts.

## New finding on the correction

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| N1 | P0 | `ratelimit.py:6` (after `fix.patch`) | Removing the `limit == 0` branch inverts the meaning of unlimited. An enterprise plan configured with `limit=0` that has made 0 requests calls `within_limit(0, 0)`, which returns `0 < 0`, i.e. False. Every enterprise customer is blocked from the production API, which is an outage. The test protecting this case was deleted in the same commit. | Restore `test_zero_is_unlimited`: `assertTrue(within_limit(0, 0))` and `assertTrue(within_limit(10**6, 0))`. Both fail on `c04e6b8` and pass once the branch is restored. |

**Fix:** keep the early return and apply the boundary change below it:

```python
if limit == 0:
    return True
return used < limit
```

Keep both `test_boundary` and `test_zero_is_unlimited`.

**FILES NEEDED BUT NOT PROVIDED:**
- The caller(s) of `within_limit`, and how a plan's `limit` is loaded (is a missing limit ever `0` or `None`?).
- CI check results for `c04e6b8`.

## Close-out

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| F1 | Accepted, but the fix is not acceptable as written | The boundary part of `c04e6b8` is correct, and `test_boundary` fails before and passes after. The same commit introduces N1 (P0). F1 can close only once a fix keeps the boundary change without removing the `limit == 0` branch. |
| N1 | Open (P0, cannot be deferred) | Author to fix. `test_zero_is_unlimited` must be restored and must fail on `c04e6b8`. |

**VERIFIED AFTER FIXES:** Only the correction diff `a93d2e6..c04e6b8` changed after the review.

- Lines 6–8 of `ratelimit.py` were replaced by `return used < limit`. Verified by reading. The boundary is correct, but the zero-limit behaviour regressed (N1).
- In the test file, `test_zero_is_unlimited` was replaced by `test_boundary`. Verified by reading. The replacement removed coverage of the requirement.

No tests were run in this session. The expected results above come from tracing the code by hand.

**MERGE RECOMMENDATION: do not merge.** Four things are open:

1. P0 N1 is unresolved.
2. The second High-tier round has not run on the corrected head.
3. CI check status for `c04e6b8` is not provided; a missing check is not green.
4. The adjudication's "Ready to close out" should be withdrawn.

Once N1 is fixed, verify that correction diff and run both tests, then run the second-vendor round on the new head.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "read (code traced by hand; tests not run in this session)",
      "location": "ratelimit.py:6 (after fix.patch, commit c04e6b8)",
      "scenario": "The fix for F1 removed the `if limit == 0: return True` branch as 'dead code'. within_limit(used, 0) now returns used < 0, which is False for every used >= 0, so every enterprise plan (configured with limit 0 = unlimited) is refused all requests on the production API. The same commit deleted test_zero_is_unlimited, the test that would have caught it; the docstring still promises 0 means no limit.",
      "fix": "Restore the limit == 0 early return above `return used < limit`; restore test_zero_is_unlimited (assert within_limit(0, 0) and within_limit(10**6, 0) are True) alongside test_boundary."
    }
  ]
}
```