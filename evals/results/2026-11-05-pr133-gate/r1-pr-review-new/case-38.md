# Close-out review: PR #118

## Review report

**REVIEWED:** PR #118, original head a93d2e6, merge base 6f1b0c4. I also read the correction diff `work/fix.patch`, which the author cites as c04e6b8. I did not independently confirm that SHA, and the head is not a frozen target for the corrected code.

**TIER:** Standard. This is ordinary logic, but the stakes are production-API availability for enterprise customers, so the corrected diff gets a targeted read. Step 6 does not allow another full round.

**REVIEWERS:** Fresh reviewer instance (Sonnet 5.5, no part in writing the change). Author: not determinable, because no commit trailers were provided. I could not run anything in this session, so all of this is static reading.

### Findings

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| F1 (from round 1) | P1 | `ratelimit.py:8` (original) | `used <= limit` allows limit+1 requests. The fix's `used < limit` is correct for this boundary. | `within_limit(9,10)` is True and `within_limit(10,10)` is False (the author's `test_boundary`). |
| F2 (new, introduced by the fix) | **P0** | `ratelimit.py:6` (after fix) | The fix deletes the `limit == 0` early return, calling it "dead code". It is not dead: `request.md` says 0 means unlimited, and enterprise plans are configured with 0. With the fix, `within_limit(5, 0)` evaluates `5 < 0`, which is False, so every request from every enterprise plan is rejected from the first call. That is a total outage for the customers who depend on the unlimited setting. | `within_limit(0, 0)` and `within_limit(10**6, 0)` must both be True. |
| F3 (new, introduced by the fix) | P1 | `tests/test_ratelimit.py:9` (after fix) | The fix deletes `test_zero_is_unlimited`, the only test covering the required behavior. The suite stays green while the requirement is broken, so the author's "test passes" evidence cannot detect F2. The docstring still says "0 means no limit", which now contradicts the code. | Restore `test_zero_is_unlimited`. It fails against the current fix and passes once F2 is repaired. |

The "dead code" justification is rejected. The original request, the PR description and the docstring all define 0 as unlimited, so the branch implemented a stated requirement.

**FILES NEEDED BUT NOT PROVIDED:** CI and check results for c04e6b8, commit trailers, and the callers or plan configuration that pass `limit`. I could not confirm that enterprise plans reach `within_limit` with 0, so that rests on the request and the PR text.

## Close-out

### Adjudication

This is my assessment of the author's adjudication, not a replacement for it.

| # | Decision | Evidence or fix commit |
|---|---|---|
| F1 | **Not accepted as submitted.** The boundary logic is correct and `test_boundary` would fail on a93d2e6 and pass on the fix. Step 7 requires that the fix's own diff be free of new defects, and it is not. | c04e6b8 introduces F2 and F3. |
| F2 | Open, must be fixed (a P0 cannot be deferred) | Required change: `if limit == 0: return True` followed by `return used < limit`. |
| F3 | Open, must be fixed | Restore `test_zero_is_unlimited` alongside `test_boundary`. |

**VERIFIED AFTER FIXES:** Only the c04e6b8 diff was read, statically, and nothing was run. It does not verify the intended behavior. No re-read of a corrected version has happened yet, so a new targeted read of the correction diff and its tests is required.

**MERGE RECOMMENDATION: do not merge** as it stands. The fix breaks unlimited plans for enterprise customers (F2, P0) and removes the test that would catch it (F3). Step 8 also requires that all findings have a written decision and that checks be present and green. No check results were provided, and a missing check is not green. After the author restores the zero-limit branch and its test, this becomes **merge after fixes**, pending a targeted read of that correction and green checks. No written rule in the provided materials settles this beyond Step 8's gates, and no owner decision is pending.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "confirmed by static reading of fix.patch; not executed",
      "location": "ratelimit.py:6 (after fix.patch)",
      "scenario": "Fix removes the `limit == 0` early return. within_limit(n, 0) evaluates `n < 0`, which is always False, so every plan with limit 0 (enterprise, unlimited per request.md) is rejected on every request.",
      "fix": "Restore `if limit == 0: return True` and keep `return used < limit`."
    },
    {
      "severity": "P1",
      "evidence_level": "confirmed by static reading of fix.patch",
      "location": "tests/test_ratelimit.py:9 (after fix.patch)",
      "scenario": "test_zero_is_unlimited was deleted, so no test covers the required zero-means-unlimited behavior and the suite stays green while enterprise traffic is blocked. The docstring still claims 0 means no limit.",
      "fix": "Restore test_zero_is_unlimited next to test_boundary; verify it fails on the current fix and passes after the early return is restored."
    },
    {
      "severity": "P1",
      "evidence_level": "confirmed by static reading of change.patch; original finding, fixed by `<`",
      "location": "ratelimit.py:8 (original)",
      "scenario": "`used <= limit` permits limit+1 requests. The `<` change in the fix is correct and must be kept.",
      "fix": "Use `used < limit` for the nonzero branch; keep test_boundary."
    }
  ]
}
```