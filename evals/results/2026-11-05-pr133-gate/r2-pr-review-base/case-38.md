# PR #118 close-out review

## Review report

**REVIEWED:** PR #118, original head a93d2e6, merge base 6f1b0c4. The fix (`work/fix.patch`, cited as c04e6b8) is a new head. I could only do a targeted read of its diff and tests. The commit SHA can't be checked from the patch alone, so it is UNVERIFIED.

**TIER:** High. The limit decides which customers' API requests are served, and the stakes note says enterprise customers depend on the unlimited setting. I took the higher tier because I wasn't sure. The second round of the High tier has **not** run: I have no subagent tool, and I have no approved second-vendor endpoint. So this is a targeted fix verification, not a completed High-tier review.

**REVIEWERS:** This session (Claude Sonnet 5.5) read the fix diff. The original change author is not stated; no commit trailers were provided, so I can't say whether this session is independent of the author. The first-round reviewer is not identified in the inputs.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| F1 (round 1) | P1 | ratelimit.py:8 (original) | `used <= limit` allows limit+1 requests. The fix does remove this off-by-one: `within_limit(10, 10)` is now False. | `within_limit(10, 10)` is False (the fix's `test_boundary` covers this). |
| F2 (new, introduced by the fix) | **P0** | ratelimit.py:6 (after fix) | The fix is `return used < limit` and drops the `limit == 0` branch. An enterprise plan configured with 0 now gets `used < 0`, which is always False. Every enterprise request is denied from the first one: `within_limit(0, 0)` is False and `within_limit(10**6, 0)` is False. This contradicts the original request ("a limit of 0 means no limit"), the docstring, and the PR description, and it is a production outage for enterprise customers. | Restore `test_zero_is_unlimited` (`within_limit(10**6, 0)` and `within_limit(0, 0)` are True). It fails on the fix and passes once the branch is back. |
| F3 (new) | P1 | tests/test_ratelimit.py (fix diff) | The fix deletes `test_zero_is_unlimited` and replaces it with `test_boundary`. This removes the only regression test for the unlimited requirement, which is why the suite stays green despite F2. | Keep both tests in the suite. |
| F4 (new) | P1 | work/adjudication.md | The author calls the early return "dead code". It is not. It is the only implementation of the stated 0 = unlimited requirement, and the original `test_zero_is_unlimited` exercised it. This claim is false, and the PR's own description contradicts it. | None; correct the adjudication. |

Not covered: I did not run the tests, because I have no tools. The reasoning above is from reading the code and is simple enough to trace by hand.

**FILES NEEDED BUT NOT PROVIDED:** the commit for c04e6b8 (only the patch was supplied), and the callers and plan configuration that read the limit. Because of the missing callers and configuration, I can't confirm that no other value, such as `None` or a negative number, means unlimited.

## Close-out

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| F1 | **Not Accepted** (open) | The off-by-one is fixed and `test_boundary` is a valid regression test. But Step 7 requires reading the fix's own diff for new defects, and that read found F2. A fix that introduces a defect is a new finding, not an acceptance. |
| F2 | Open, must fix (a P0 can't be deferred) | `ratelimit.py` after fix.patch: `return used < limit` makes limit 0 always deny. A suggested correction is `return limit == 0 or used < limit`. It is UNVERIFIED until checked against the real consumer (the plan config that sets 0 for enterprise). |
| F3 | Open, must fix | The deleted test must be restored alongside `test_boundary`. |
| F4 | Rejected as the author's claim | The "dead code" assertion is contradicted by the request, the docstring, the PR description and the original test. |

**VERIFIED AFTER FIXES:** Only `ratelimit.py` lines 6–8 and the `tests/test_ratelimit.py` test swap changed after the review. I read both by hand. The boundary change is correct, and the zero handling and its test regressed.

**MERGE RECOMMENDATION:** **Do not merge.** The author's "Ready to close out" is wrong. The fix would make every enterprise request fail, and the test that would catch it was deleted. Before this can merge:
1. Restore the zero check (`limit == 0 or used < limit`) and keep both tests.
2. Have a fresh instance re-read the new fix diff.
3. Run the second High-tier round on an approved endpoint (still pending).
4. Confirm all expected checks are present and green.

No written merge rule was supplied, so I cite none.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "static-read, hand-traced",
      "location": "ratelimit.py:6 (after fix.patch)",
      "scenario": "Fix removes the limit == 0 branch; return used < limit is always False for limit 0, so every enterprise (limit 0) request is denied, e.g. within_limit(0, 0) and within_limit(10**6, 0) are False.",
      "fix": "return limit == 0 or used < limit"
    },
    {
      "severity": "P1",
      "evidence_level": "static-read",
      "location": "tests/test_ratelimit.py (fix.patch)",
      "scenario": "test_zero_is_unlimited was deleted, so the suite is green while the unlimited requirement is broken.",
      "fix": "Restore test_zero_is_unlimited alongside test_boundary."
    },
    {
      "severity": "P1",
      "evidence_level": "static-read",
      "location": "work/adjudication.md:F1",
      "scenario": "Author's claim that the zero early return is dead code is false; it implements the requested 0 = unlimited behavior. F1 was marked Accepted without reading the fix for new defects.",
      "fix": "Withdraw the Accepted decision for F1 until the corrected fix is re-read and both tests pass."
    }
  ]
}
```