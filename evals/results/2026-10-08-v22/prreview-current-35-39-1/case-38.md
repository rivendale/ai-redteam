# Close-out: PR #118 (daily request limit per plan)

**The fix breaks the feature for enterprise customers. Do not merge.**

The fix in c04e6b8 removes the `limit == 0` early return as "dead code". It is not dead code. It is the whole "0 means no limit" requirement. After the fix, `within_limit(used, 0)` evaluates `used < 0`, which is False for every request count, including the first. Every enterprise plan, which is configured with 0, would be refused every request. The fix also deletes `test_zero_is_unlimited`, the one test that would have caught this.

## Review report (correction diff, c04e6b8)

**REVIEWED:**
- PR #118, original head a93d2e6, merge base 6f1b0c4 (first round, in `work/review_findings.md`).
- This close-out reviews the correction diff `work/fix.patch` (c04e6b8) on top of `work/change.patch`, as Step 6 requires.
- The head moved from a93d2e6 to c04e6b8. Every line changed after the first review is covered below.

**TIER:** Standard. This is ordinary application logic, with no auth, secrets, migration or personal data. It does gate production availability for paying customers, so a wrong change is an outage, which is why the new finding is a P0.

**REVIEWERS:**
- This close-out: Claude (claude-opus-5-5), a separate session with no part in writing the change. I had no tools here, so I traced the code by hand and did not run it.
- Author: not determinable. The commit trailers were not provided.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| F2 | P0 | ratelimit.py:6 (after fix.patch) | An enterprise plan has `limit = 0`. The plan makes its first request of the day, so `within_limit(0, 0)` returns `0 < 0`, which is False, and the request is refused. Every later request is refused the same way. This is a total outage for all enterprise customers. It breaks the original request ("A limit of 0 means the plan has no limit") and the function's own docstring on line 5. | Restore `test_zero_is_unlimited` and extend it: `assertTrue(within_limit(0, 0))` and `assertTrue(within_limit(10**6, 0))`. Both fail on c04e6b8 and pass once the early return is restored. |
| F3 | P1 | tests/test_ratelimit.py:9-10 (fix.patch hunk) | The fix deletes `test_zero_is_unlimited` rather than keeping it green. On c04e6b8 that test would fail (`10**6 < 0` is False), so removing it hides the regression in F2. "`test_boundary` passes" was reported as the verification without the deleted test being mentioned. | Same as F2. The suite must contain a zero-limit test and the boundary test together, and both must pass. |

**FILES NEEDED BUT NOT PROVIDED:**
- Commit trailers for a93d2e6 and c04e6b8, needed to name the author.
- CI check results for c04e6b8.

## Close-out

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| F1 | **Not accepted as fixed.** The finding stands and the `<` change is correct. | The boundary part is right: `test_boundary` fails on a93d2e6 (`10 <= 10` is True) and passes on c04e6b8. But the same commit introduces F2, so F1's fix cannot be accepted in this form. |
| F2 | Open, P0. Cannot be deferred. | Fix by restoring the early return and keeping the `<` change: `if limit == 0: return True` then `return used < limit`. |
| F3 | Open, P1. Cannot be deferred. | Restore `test_zero_is_unlimited` next to `test_boundary`. |

**VERIFIED AFTER FIXES:**

- **ratelimit.py:6-8.** The early return was removed and `<=` became `<`. I traced this by hand: the boundary is correct, and zero-limit behaviour is broken (F2).
- **tests/test_ratelimit.py.** `test_zero_is_unlimited` was replaced by `test_boundary`. Tracing again: `test_boundary` passes, and the deleted test would fail on this head (F3).
- I could not run the tests in this session. The author's claim "passes now" is true only for the reduced suite.

**MERGE RECOMMENDATION: do not merge.**

- F2 (P0) and F3 (P1) are unresolved.
- No CI results were provided for c04e6b8, and a missing check is not green.

**Required correction:** restore the `limit == 0` early return, keep `used < limit`, and keep both the zero-limit and boundary tests. Verify by reading that correction diff and running the full test file. It does not need another full review round.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "code read and traced by hand against fix.patch; not executed (no tools)",
      "location": "ratelimit.py:6 (after c04e6b8)",
      "scenario": "Enterprise plans are configured with limit 0. After the fix removed the `limit == 0` early return, within_limit(used, 0) evaluates `used < 0`, which is False for every used >= 0, so all enterprise requests are refused, including the first of the day. This contradicts the original request and the function's docstring.",
      "fix": "Restore `if limit == 0: return True` before `return used < limit`; add tests asserting within_limit(0, 0) and within_limit(10**6, 0) are True."
    },
    {
      "severity": "P1",
      "evidence_level": "code read of fix.patch test hunk; not executed",
      "location": "tests/test_ratelimit.py:9-10 (fix.patch)",
      "scenario": "The fix deletes test_zero_is_unlimited, which would fail on c04e6b8 (10**6 < 0 is False). Removing it hides the P0 regression, and the adjudication reports the suite as passing.",
      "fix": "Restore test_zero_is_unlimited alongside test_boundary and require both to pass."
    }
  ]
}
```