# pr-review close-out: PR #118 (daily request limit per plan)

## Review report (targeted read of the fix)

**REVIEWED:** PR #118, original head `a93d2e6`, merge base `6f1b0c4`. The author's fix is claimed as `c04e6b8`. I was given only `work/fix.patch`, not the commit, so I cannot confirm that SHA matches the patch. This read covers the patch applied on top of `change.patch` and nothing else.

**TIER:** Standard. The change is ordinary code with no auth, secrets, migrations, money or personal data. The stakes note (enterprise customers depend on the unlimited setting) raises the consequence of a defect, not the tier. The first round already ran, so this is the targeted read of the correction that Step 6 and Step 7 require, not a new full round.

**REVIEWERS:** This instance (Sonnet 5.5, claude-sonnet-5-5) reviewed the fix. The authors are not stated: no commit trailers were provided, so I cannot confirm who wrote the change or the fix. I had no tools, so nothing was run. All verdicts below come from reading the code.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| F1 (first round) | P1 | `ratelimit.py:8` (original) | `used <= limit` allowed an 11th request at limit 10. The finding is correct, and the `<` comparison in the fix resolves it. | `within_limit(10, 10)` is False (the author's `test_boundary`) |
| F2 (new, introduced by the fix) | **P0** | `ratelimit.py:6` (after fix) | The fix deletes the `if limit == 0: return True` branch, calling it "dead code". It is the stated requirement: "A limit of 0 means the plan has no limit (enterprise plans are configured with 0)". After the fix, `within_limit(0, 0)` evaluates `0 < 0`, which is False, so every request from an enterprise plan is denied from the first one. This is an outage for the customers the stakes note names. | `within_limit(10**6, 0)` is True and `within_limit(0, 0)` is True. The original `test_zero_is_unlimited` already covers this. |
| F3 (new) | P1 | `tests/test_ratelimit.py:9` (after fix) | The fix replaces `test_zero_is_unlimited` with `test_boundary` instead of adding to it. Deleting the only test of the requirement is why F2 passes the suite. | Keep `test_zero_is_unlimited` alongside `test_boundary`. |

**Verification of the author's test claim.** `test_boundary` fails on the original: `10 <= 10` is True, so `assertFalse` fails. It passes on the fix: `9 < 10` is True and `10 < 10` is False. This is by reading, not by running. The claim is plausible, but it does not show the fix is correct, because the suite no longer tests the zero case.

**Suggested fix (UNVERIFIED, not run):**
```python
def within_limit(used, limit):
    if limit == 0:
        return True
    return used < limit
```
Check this against the consumer, which is the enterprise-plan configuration where the limit is 0. Keep both tests.

**FILES NEEDED BUT NOT PROVIDED:** the commit `c04e6b8` itself, CI or check status, commit trailers, and the callers that read plan limits. I could not confirm that a limit of 0 reaches `within_limit` unchanged, or whether negative or `None` limits can occur.

## Close-out

**ADJUDICATION:** The reviewer does not adjudicate its own findings. This table is the reviewer's read of the author's claim, and the author or closer must record the final decisions.

| # | Decision | Evidence or fix commit |
|---|---|---|
| F1 | **Not Accepted as submitted.** The `<` change is right, but Step 7 requires that the fix's own diff be read for new defects, and it contains one (F2). | `c04e6b8` is unverified. The patch removes the zero branch. |
| F2 | Open, P0. It cannot be deferred. | `fix.patch` lines removing `if limit == 0: return True` |
| F3 | Open, P1. It cannot be deferred. | `fix.patch` removes `test_zero_is_unlimited` |

**VERIFIED AFTER FIXES:** The only change after the first review is the fix patch, and my targeted read of it found a regression. The author's claim that the early return is "dead code" is wrong, because `limit == 0` is the unlimited path.

**MERGE RECOMMENDATION:** **Do not merge.** No written rule was supplied beyond the original request, so I cite none. The request says "A limit of 0 means the plan has no limit", and the fix violates it. Open items:
- F2 (P0) and F3 (P1) are unresolved.
- No check status was provided, and a missing check is not green.
- After the author restores the zero branch and its test, a targeted read of that correction is enough. Another full round is not needed.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "read-verified from fix.patch; not executed",
      "location": "ratelimit.py:6 (after fix.patch)",
      "scenario": "fix.patch removes the `if limit == 0: return True` branch. With limit 0 (enterprise plans), within_limit evaluates `used < 0`, which is always False, so every request from an unlimited plan is denied, including the first.",
      "fix": "Restore `if limit == 0: return True` before `return used < limit`; assert within_limit(10**6, 0) and within_limit(0, 0) are True."
    },
    {
      "severity": "P1",
      "evidence_level": "read-verified from fix.patch",
      "location": "tests/test_ratelimit.py:9 (after fix.patch)",
      "scenario": "test_zero_is_unlimited was replaced by test_boundary rather than kept alongside it, so no test covers the unlimited requirement and the P0 regression passes the suite.",
      "fix": "Keep test_zero_is_unlimited and test_boundary together."
    },
    {
      "severity": "P1",
      "evidence_level": "read-verified; first-round finding confirmed, resolved by `<`",
      "location": "ratelimit.py:8 (original)",
      "scenario": "`used <= limit` allowed limit + 1 requests; with limit 10 and 10 used, an 11th was allowed.",
      "fix": "Use `used < limit` while keeping the zero-limit early return."
    }
  ]
}
```