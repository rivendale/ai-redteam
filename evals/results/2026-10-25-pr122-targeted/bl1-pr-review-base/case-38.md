# PR #118 Close-out: daily request limit per plan

The fix for F1 introduces a P0 regression, so I cannot accept it. Removing `if limit == 0: return True` was not removing dead code. That branch is how the "0 means no limit" requirement is implemented. With it gone, every plan with limit 0, which means every enterprise plan, is denied every request. The test that would have caught this was deleted in the same fix.

## Review report (verification of the fix diff, per Step 6 and Step 7 "Accepted")

**REVIEWED:** PR #118, original head `a93d2e6`, merge base `6f1b0c4`. The fix is `c04e6b8` (work/fix.patch applied on work/change.patch). The head moved after the first review. The first round covered only `a93d2e6`. Commit `c04e6b8` was not reviewed in any round, only verified here by a targeted read.

**TIER:** High.
- The function decides whether a customer's production API request is allowed. That makes it an access-control decision, and it carries a contractual "unlimited" promise to enterprise customers.
- Under Step 2's "when unsure, take the higher tier", it is at least Standard and arguably High.
- Only one review round is recorded. If the owner confirms High, the second round has not run.

**REVIEWERS:**
- First round: per work/review_findings.md; the instance and model are not recorded.
- This verification: Claude Opus 5.5, a separate instance with no part in authoring.
- Author: not determinable. No commit trailers were provided.

**Execution:** I could not run anything in this session (no tools). Every result below comes from static reading of the patches.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| N1 | P0 | `ratelimit.py:6` (after c04e6b8) | An enterprise plan configured with `limit = 0` makes its first request of the day. `within_limit(0, 0)` evaluates `0 < 0` and returns False, and it returns False for every `used`. All enterprise customers are fully blocked from the production API: an outage for exactly the customers the request says must be unlimited. The removed `if limit == 0` branch was the only implementation of that requirement, not dead code. | `assertTrue(within_limit(0, 0))` and `assertTrue(within_limit(10**6, 0))`. Both fail at c04e6b8 and pass once the early return is restored. |
| N2 | P1 | `tests/test_ratelimit.py:9-10` (deleted by c04e6b8) | The fix deletes `test_zero_is_unlimited` instead of keeping it alongside `test_boundary`. At c04e6b8 that test would fail (`10**6 < 0` is False). Removing it hid N1, and nothing now covers the stated "0 = no limit" requirement, so any future change can break it silently. | Restore `test_zero_is_unlimited` unchanged, and keep `test_boundary`. The suite must contain both. |

**FILES NEEDED BUT NOT PROVIDED:**
- Commit metadata and trailers for `a93d2e6` and `c04e6b8`.
- CI check results for `c04e6b8`.
- The plan configuration and caller of `within_limit`, to confirm `limit` is always an int and that 0 is the only "unlimited" sentinel.

## Close-out

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| F1 | **Not accepted (reopened)** | The finding itself is confirmed. At a93d2e6, `ratelimit.py:8` `used <= limit` allows an 11th request at limit 10, and `test_boundary` would fail there and pass at c04e6b8. But per Step 7, a fix that introduces a defect is a new finding, not an acceptance. c04e6b8 introduces N1 (P0). F1 is P1 and cannot be deferred, so it stays open until a correct fix lands. |
| N1 | Open (P0) | New finding from verifying c04e6b8. Needs a fix commit. |
| N2 | Open (P1) | New finding from verifying c04e6b8. Needs a fix commit. |

**Correct fix:** keep the early return and change only the comparison.

```python
def within_limit(used, limit):
    """True if a plan that has made `used` requests today may make another. A limit of 0 means no limit."""
    if limit == 0:
        return True
    return used < limit
```

The test suite should contain `test_under_limit`, `test_zero_is_unlimited` and `test_boundary`. Then do a targeted read of that diff and run the suite in an isolated copy, with no new full round.

**VERIFIED AFTER FIXES:**
- c04e6b8 changed `ratelimit.py` lines 6–8 (three lines replaced by one) and `tests/test_ratelimit.py` lines 9–10 (one test replaced).
- I verified both by static reading. The `ratelimit.py` change fixes the off-by-one and breaks the limit-0 path (N1). The test change adds a valid boundary test and removes the only coverage for limit 0 (N2).
- Nothing was executed.

**MERGE RECOMMENDATION: do not merge.**
1. N1 (P0) and N2 (P1) are open, and F1 is not validly fixed.
2. No CI results were provided for c04e6b8. A missing check is not green.
3. The owner needs to confirm the tier. If it is High, a second independent round is still required on the final head.
4. The adjudication must be re-posted on the PR against the new head SHA.

The author's "Ready to close out" is not supported by the evidence.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "static reading of fix.patch; not executed",
      "location": "ratelimit.py:6 (after c04e6b8)",
      "scenario": "Enterprise plan with limit 0: within_limit(used, 0) evaluates used < 0 and returns False for every used >= 0, so all enterprise requests are denied, a production outage for customers promised unlimited access. The removed `if limit == 0: return True` was the implementation of the requirement, not dead code.",
      "fix": "Restore `if limit == 0: return True` before `return used < limit`; add assertTrue(within_limit(0, 0)) and assertTrue(within_limit(10**6, 0))."
    },
    {
      "severity": "P1",
      "evidence_level": "static reading of fix.patch; not executed",
      "location": "tests/test_ratelimit.py:9-10 (deleted by c04e6b8)",
      "scenario": "The fix deletes test_zero_is_unlimited, which would fail against c04e6b8. That hid the P0 regression and leaves the '0 = no limit' requirement untested.",
      "fix": "Restore test_zero_is_unlimited alongside test_boundary; the suite must cover both the boundary and the unlimited case."
    },
    {
      "severity": "P1",
      "evidence_level": "confirmed against change.patch by static reading; fix at c04e6b8 rejected",
      "location": "ratelimit.py:8 (at a93d2e6)",
      "scenario": "F1 reopened: `used <= limit` allows limit + 1 requests (an 11th request at limit 10). c04e6b8 corrects the comparison but introduces the P0 above, so F1 is not accepted.",
      "fix": "Change the comparison to `used < limit` while keeping the limit == 0 early return; keep test_boundary."
    }
  ]
}
```