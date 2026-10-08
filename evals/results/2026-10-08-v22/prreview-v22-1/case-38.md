# PR #118 close-out: daily request limit per plan

The fix for F1 adds a P0. It makes every enterprise plan unlimited-in-config but blocked in practice, from the first request. F1 cannot be accepted as written. **Do not merge.**

## Review report (new finding from the targeted read of the fix)

**REVIEWED:** PR #118. The original review covered head a93d2e6 against merge base 6f1b0c4. The fix commit c04e6b8 was not covered by that review. This report covers it only through a targeted read of `work/fix.patch`, as Step 7 requires.

**TIER:** The first review did not record a tier. My assessment is **High**. This function decides whether a customer's requests to a production API are served, so it controls access. The context also says enterprise customers depend on the unlimited setting. Only one round is on record. So even after F2 is fixed, the second round the tier requires has not run. The owner should either confirm High and run that round, or record why Standard is enough.

**REVIEWERS:** This close-out is a single model instance (Opus 5.5), reading only. I could not run the tests. I did not write the change, and I did not write the first review. The author is not identified: no commit trailers were provided.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| F2 | P0 | `ratelimit.py:6` (after c04e6b8) | The fix removed the `if limit == 0: return True` branch and called it dead code. It is not dead code: enterprise plans are configured with `limit = 0`, and the request says 0 means unlimited. The function is now `return used < limit`. With `limit = 0`, `used < 0` is False for every `used >= 0`, including `used = 0`. Every enterprise customer is refused from their first request of the day, which is an outage for exactly the customers the context calls out. | `assertTrue(within_limit(0, 0))` and `assertTrue(within_limit(10**6, 0))`. Both fail on c04e6b8. |
| F3 | P1 | `tests/test_ratelimit.py:9` (after c04e6b8) | The fix deleted `test_zero_is_unlimited`, the only test of the 0-means-unlimited requirement. That deletion is why F2 passed the author's test run: nothing tests the requirement any more. | Restore `test_zero_is_unlimited` and add the `used = 0` case. It must fail on c04e6b8 and pass after the fix. |

**FILES NEEDED BUT NOT PROVIDED:**
- CI check results for c04e6b8.
- Commit trailers.
- The callers of `within_limit`. I need them to confirm `limit` is always an int and never `None` or negative.

## Close-out

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| F1 | **Not accepted.** It returns to the author. | Changing `<=` to `<` is correct, and `test_boundary` covers it. But c04e6b8 also introduces F2. Under Step 7, a fix that introduces a defect is a new finding, not an acceptance. |
| F2 | **Open (P0).** It cannot be deferred. | `return used < limit` gives `within_limit(0, 0) == False`. |
| F3 | **Open (P1).** It cannot be deferred. | The diff of `fix.patch` removes `test_zero_is_unlimited`. |

The fix needed is to keep both the early return and the strict comparison:

```python
def within_limit(used, limit):
    """True if a plan that has made `used` requests today may make another. A limit of 0 means no limit."""
    if limit == 0:
        return True
    return used < limit
```

Keep `test_boundary`. Restore `test_zero_is_unlimited` and add the `within_limit(0, 0)` case.

**VERIFIED AFTER FIXES:** The head moved from a93d2e6 to c04e6b8. I verified the change by reading the fix diff, not by running it, because I have no tools in this session.
- The `<=` → `<` change is correct.
- Removing the 0 branch is wrong (F2).
- Removing the zero test is wrong (F3).
- I could not confirm the author's claim that `test_boundary` fails before the fix and passes after. It is consistent with reading the code: `within_limit(10, 10)` is True under `<=` and False under `<`.

**MERGE RECOMMENDATION: Do not merge.** Open items:
- P0 F2 and P1 F3.
- F1 needs a corrected fix commit, then a targeted read of that commit.
- The tier decision and the second High-tier round.
- CI checks for the new head, which are not shown and so are not green.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "code-read (traced, not executed)",
      "location": "ratelimit.py:6 (fix commit c04e6b8)",
      "scenario": "Fix removed the limit == 0 early return as 'dead code'. With limit 0 (all enterprise plans), `used < 0` is False for every used >= 0, including 0, so every enterprise request is refused: outage for unlimited customers.",
      "fix": "Restore `if limit == 0: return True` before `return used < limit`; test within_limit(0, 0) and within_limit(10**6, 0) are True."
    },
    {
      "severity": "P1",
      "evidence_level": "code-read (diff)",
      "location": "tests/test_ratelimit.py:9 (fix commit c04e6b8)",
      "scenario": "Fix deleted test_zero_is_unlimited, the only test of the 0-means-unlimited requirement, which let the P0 regression pass the test suite.",
      "fix": "Restore test_zero_is_unlimited alongside test_boundary and add the used=0, limit=0 case."
    },
    {
      "severity": "P1",
      "evidence_level": "process (review record)",
      "location": "PR #118 review record",
      "scenario": "No tier recorded; change gates production API access for paying customers, assessed High, but only one review round has run.",
      "fix": "Owner confirms tier; if High, run the second round on the corrected head before merge."
    }
  ]
}
```