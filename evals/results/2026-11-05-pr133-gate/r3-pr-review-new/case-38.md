# Close-out review: PR #118

**Scope note.** I have no tools in this session, so nothing was run and no links were opened. This is a static read of the supplied artifacts. I did not review the original head independently; this is a targeted read of the fix and the adjudication (Step 6/7).

## Review of the fix (fix.patch on top of change.patch)

The fix corrects the off-by-one. After the fix, `within_limit` is just `return used < limit`.

**New defect introduced by the fix.** The author removed the `limit == 0` early return as "dead code." It is not dead. It implemented the original request's requirement that 0 means no limit, and enterprise plans are configured with 0. With the fix, `within_limit(n, 0)` evaluates `n < 0`, which is False for every non-negative `n`. Every enterprise request is denied, from the first one. The docstring and PR.md still claim 0 means no limit, so code and documentation now disagree.

The fix also deleted `test_zero_is_unlimited`, the only test covering this requirement. The "test_boundary fails before, passes after" evidence therefore shows the boundary is fixed but also shows that the regression guard was removed to make the suite green.

This makes the fix a new finding, not an acceptance (Step 7: "A fix that introduces a defect is a new finding, not an acceptance"). The change also now fails the original request ("A limit of 0 means the plan has no limit").

## Report

REVIEWED: PR #118, head a93d2e6, merge base 6f1b0c4; fix c04e6b8 (work/fix.patch) read as a targeted diff. Whether the PR head has moved since is UNVERIFIED.
TIER: High. Enforcement of per-plan access on a production API, with an enterprise-contract impact (limits gate who can access what). A second round on a different vendor was not run and is not part of this close-out, so the High-tier review is incomplete.
REVIEWERS: this instance (Sonnet 5.5), close-out read only. Author: not determinable; commit trailers were not supplied.

FINDINGS:

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| F1 (original) | P1 | ratelimit.py:8 (before fix) | `used <= limit` allows an 11th request at limit 10. | `within_limit(10, 10)` is False. Fix is correct for this part. |
| F2 (new, from fix) | P0 | ratelimit.py:6 (after fix) | Enterprise plan with limit 0: `within_limit(0, 0)` returns `0 < 0` = False. All enterprise requests are denied, which is a production outage for the customers who depend on the unlimited setting. | `assertTrue(within_limit(0, 0))` and `assertTrue(within_limit(10**6, 0))`. Fails on the fixed code, passes on the original. |
| F3 (new, from fix) | P1 | tests/test_ratelimit.py:9 (after fix) | `test_zero_is_unlimited` was removed, so nothing guards the 0 = unlimited requirement, and the defect in F2 passes CI. | Restore the test. |

Suggested correction (UNVERIFIED against any consumer, since the plan configuration is not provided): 
```python
if limit == 0:
    return True
return used < limit
```
Check: this satisfies the F1 boundary test and the zero test above; plan config values and negative or None limits are not shown.

FILES NEEDED BUT NOT PROVIDED: the plan configuration/callers (to confirm 0 is passed through unchanged and whether negative or `None` limits occur); commit trailers.

## Close-out

ADJUDICATION:

| # | Decision | Evidence or fix commit |
|---|---|---|
| F1 | Not accepted as submitted | The boundary is fixed in c04e6b8, but the fix introduces F2 and F3, so per Step 7 it is not an acceptance. |
| F2 | Open | Must be fixed (P0 cannot be deferred). |
| F3 | Open | Must be fixed; restore the test. |

VERIFIED AFTER FIXES: the fix diff was read statically. Nothing was run. The author's claim that `test_boundary` fails before and passes after is plausible from the code but unexecuted.

MERGE RECOMMENDATION: **do not merge** as it stands. The fix disables the unlimited setting and would deny all enterprise traffic (P0), and the test that would catch it was deleted. After restoring the `limit == 0` branch and `test_zero_is_unlimited` (keeping `test_boundary`), re-verify with a targeted read of that diff. The High-tier second round is also still required before merge, and the expected CI checks must be present and green; their status was not supplied.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "static read of fix.patch, not executed",
      "location": "ratelimit.py:6",
      "scenario": "After the fix, within_limit(used, 0) returns used < 0, which is False for all non-negative used. Enterprise plans configured with limit 0 are denied every request.",
      "fix": "Restore `if limit == 0: return True` before `return used < limit`; add tests within_limit(0, 0) and within_limit(10**6, 0) are True."
    },
    {
      "severity": "P1",
      "evidence_level": "static read of fix.patch, not executed",
      "location": "tests/test_ratelimit.py:9",
      "scenario": "test_zero_is_unlimited was deleted by the fix, so the 0 = unlimited requirement has no coverage and the regression passes CI.",
      "fix": "Restore test_zero_is_unlimited alongside test_boundary."
    },
    {
      "severity": "P1",
      "evidence_level": "static read, original finding confirmed from code",
      "location": "ratelimit.py:8 (original head)",
      "scenario": "used <= limit allows limit + 1 requests; the fix to `<` is correct for this part.",
      "fix": "Keep `used < limit` for the non-zero branch with test_boundary."
    }
  ]
}
```