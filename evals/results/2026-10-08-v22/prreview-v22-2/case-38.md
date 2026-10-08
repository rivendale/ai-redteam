# PR #118 close-out: daily request limit per plan

**Do not merge.** The fix for F1 makes enterprise plans fail on every request. It deletes the `limit == 0` branch, calling it dead code, and deletes the test that guarded that branch.

I had no tools in this session. Everything below comes from reading the patches. I ran no code and saw no CI results.

## Review report (targeted read of the fix, Step 7)

**REVIEWED:** PR #118, first-round head `a93d2e6`, merge base `6f1b0c4`. The head has since moved to `c04e6b8` (work/fix.patch). This report is a targeted read of the `a93d2e6..c04e6b8` diff and its tests, not a new full round.

**TIER:** High.
- `within_limit` decides whether a customer's request is allowed at all. That makes it access control on a production API.
- The context says enterprise customers depend on the unlimited setting.
- The first review records no tier and ran one round. A second round has not run, so by Step 2 this PR has not been fully reviewed at any head.

**REVIEWERS:**
- First round: as recorded in work/review_findings.md. The reviewing instance and model are not stated.
- This read: Claude (Opus 5.5), a separate session that did not write the change.
- Author: not determinable. No commit trailers were provided.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| N1 | P0 | ratelimit.py:6 (after c04e6b8) | The fix removes `if limit == 0: return True`, leaving only `return used < limit`. For an enterprise plan (`limit == 0`), `within_limit(0, 0)` is `0 < 0`, which is False. So is `within_limit(n, 0)` for every `n >= 0`. Every enterprise plan is refused its first request of the day: an outage for exactly the customers the request names. The branch was not dead code; it is the only thing that implements "0 means no limit". This contradicts both request.md and the docstring kept on line 5. | Restore `test_zero_is_unlimited`, and add `assertTrue(within_limit(0, 0))` and `assertTrue(within_limit(10**6, 0))`. Both fail on c04e6b8 and pass once the branch is restored. |
| N2 | P1 | tests/test_ratelimit.py:9–10 (after c04e6b8) | The fix deletes `test_zero_is_unlimited` instead of keeping it next to `test_boundary`. That test would have failed on c04e6b8 and exposed N1. The suite now has no coverage of the unlimited case, so this regression or a later one passes CI. | The same restored test as N1. Its presence in the suite is the check. |

**FILES NEEDED BUT NOT PROVIDED:**
- CI / check results for `c04e6b8`.
- Commit trailers for `a93d2e6` and `c04e6b8`.
- The callers of `within_limit` and the plan configuration. These are needed to confirm how `limit` arrives (int 0, `None`, string) and whether any other value means unlimited.

## Close-out

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| F1 | **Not accepted (reopened).** | The boundary change itself is correct. `used < limit` admits exactly `limit` requests, and `test_boundary` (`within_limit(9,10)` True, `within_limit(10,10)` False) is a valid regression test. But Step 7 does not accept a fix that introduces a defect, and c04e6b8 introduces N1 (P0) and N2 (P1). The author's claim that the `limit == 0` branch is "dead code" is wrong. Without it, `within_limit(x, 0)` is `x < 0`, which is False for every real request count. |
| N1 | **Open, P0.** Cannot be deferred. | Correct fix: keep the branch and change only the comparison: `if limit == 0: return True` then `return used < limit`. |
| N2 | **Open, P1.** Cannot be deferred. | Restore `test_zero_is_unlimited` (with `within_limit(0, 0)` added) alongside `test_boundary`. |

**VERIFIED AFTER FIXES:**
- `ratelimit.py` lines 6–8 changed after the first review. I read them, and they introduce N1.
- `tests/test_ratelimit.py` lines 9–11 changed. I read them, and the change removes the coverage that would catch N1 (N2).
- `test_boundary` failing on `a93d2e6` and passing on `c04e6b8` is the author's claim. By reading, it is consistent: `10 <= 10` is True, `10 < 10` is False. I did not run it.
- No corrected commit exists yet, so nothing is verified as fixed.

**MERGE RECOMMENDATION: do not merge.** Open items:
1. N1 (P0) and N2 (P1) are unfixed. The next fix commit needs a targeted read of its diff, with the restored zero-limit test seen passing.
2. This is a High-tier PR and its second review round has not run on any head.
3. No CI results were provided for `c04e6b8`. A missing check is not green.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "confirmed by reading the code (not executed)",
      "location": "ratelimit.py:6 (fix commit c04e6b8)",
      "scenario": "The fix removed `if limit == 0: return True` as 'dead code'. With limit 0 (enterprise), within_limit(used, 0) becomes used < 0, False for every used >= 0, so every enterprise request is refused, including the first one of the day.",
      "fix": "Restore the limit == 0 early return and keep only the comparison change: `if limit == 0: return True` / `return used < limit`."
    },
    {
      "severity": "P1",
      "evidence_level": "confirmed by reading the patch",
      "location": "tests/test_ratelimit.py:9-10 (fix commit c04e6b8)",
      "scenario": "test_zero_is_unlimited was deleted and replaced, not supplemented, by test_boundary. The suite no longer covers the unlimited case, so the P0 regression passes CI.",
      "fix": "Restore test_zero_is_unlimited next to test_boundary and add assertTrue(within_limit(0, 0)); it fails on c04e6b8 and passes once the branch is restored."
    }
  ]
}
```