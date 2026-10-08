# Close-out of PR #118: daily request limit per plan

**Do not merge.** The fix for F1 makes every enterprise plan reject every request. It deletes the only test that would have caught this.

## Review report (targeted read of the fix diff, Step 7)

REVIEWED: PR #118. The first round reviewed head `a93d2e6` against merge base `6f1b0c4`. This close-out reads only the fix diff `c04e6b8` (work/fix.patch, applied on top of work/change.patch). The head has moved from `a93d2e6` to `c04e6b8`, and only the fix diff was read. I had no tools, so nothing was run. All evidence comes from reading the code.

TIER: **High.** The function decides whether a customer may use the production API, so it controls who can access what. The context also says enterprise customers depend on the unlimited setting. That fits Step 2's "alters who can access what". When unsure, the skill says to take the higher tier. Only one round is on record (work/review_findings.md). A High-tier PR needs two rounds, so the review requirement is not met.

REVIEWERS: The first round's reviewer is not named in review_findings.md. This close-out was done by a separate instance (Claude Opus 5.5) that did not write the change. The change author is "the author" per adjudication.md. No commit trailers were provided, so I cannot confirm authorship or AI co-authorship.

FINDINGS:

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| N1 | **P0** | `ratelimit.py:6` (after fix) | The fix removed `if limit == 0: return True`, calling it "dead code". It was not dead code: it implements the request's "a limit of 0 means the plan has no limit". The function is now `return used < limit`. With `limit = 0`, this is `used < 0`, which is False for every `used >= 0`. Every enterprise plan (configured with 0) is denied its first request and every request after it. This is a production outage for the customers the context names. The docstring still promises "A limit of 0 means no limit", so the code now contradicts its own documentation. | `assertTrue(within_limit(0, 0))` and `assertTrue(within_limit(10**6, 0))`. Both pass on `a93d2e6` and fail on `c04e6b8`. |
| N2 | P1 | `tests/test_ratelimit.py:9` (after fix) | The fix deleted `test_zero_is_unlimited` and put `test_boundary` in its place. The suite no longer covers the 0-means-unlimited requirement. That is why the suite stays green while N1 ships. Any later regression of the same kind will also go unnoticed. | Restore `test_zero_is_unlimited` next to `test_boundary`. With N1 present it fails. |

FILES NEEDED BUT NOT PROVIDED: CI check results for `c04e6b8`. The commit trailers for `a93d2e6` and `c04e6b8`. The callers of `within_limit` and the plan configuration, which would show whether 0 is the only "unlimited" value and whether `None` or negative values can reach this function.

## Close-out

ADJUDICATION:

| # | Decision | Evidence or fix commit |
|---|---|---|
| F1 | **Not accepted. Reopen.** | The fix does correct the boundary for nonzero limits: `within_limit(10, 10)` is now False. But Step 7 says a fix that introduces a defect is a new finding, not an acceptance, and `c04e6b8` introduces N1 (P0). The claim that the early return was "dead code" is wrong, because it is reachable whenever `limit == 0`, which is every enterprise plan. |
| N1 | Open (P0, blocks merge) | Needs a fix and a regression test. P0 findings cannot be deferred. |
| N2 | Open (P1) | Restore the zero-limit test. P1 findings cannot be deferred. |

A correct fix keeps the special case and changes only the comparison:

```python
def within_limit(used, limit):
    """True if a plan that has made `used` requests today may make another. A limit of 0 means no limit."""
    if limit == 0:
        return True
    return used < limit
```

The tests should keep `test_under_limit` and `test_boundary` and restore `test_zero_is_unlimited`. Before accepting, check two things: that `test_boundary` fails on `a93d2e6`, and that `test_zero_is_unlimited` fails on `c04e6b8`. Both should pass on the new commit. The new commit's diff also needs a targeted read.

VERIFIED AFTER FIXES: `ratelimit.py` lines 6–8 and the test file changed after the review, in `c04e6b8`. I verified them by reading only. I did not run the tests. The read found N1 and N2, so the fix is not verified as correct.

MERGE RECOMMENDATION: **Do not merge.** The following are still open:
- **N1** (P0) and **N2** (P1) are unresolved, and F1 needs a new fix.
- **Second review round missing.** High tier requires two rounds and only one has run. The owner may decide the tier is Standard. If they do, record that decision and the reason in the report.
- **No check results for any head.** A missing check is not green. Checks are needed on the final head.
- The new fix commit needs its own targeted read, with both regression tests shown failing on the earlier commits and passing on the fixed one.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "code read (not executed)",
      "location": "ratelimit.py:6 (after fix c04e6b8)",
      "scenario": "Fix removed the `if limit == 0: return True` early return as 'dead code'. With limit=0 (all enterprise plans), `used < 0` is False for every used >= 0, so every request from every enterprise plan is denied: production outage. Docstring still says 0 means no limit.",
      "fix": "Restore the limit==0 early return and keep `used < limit` for the nonzero case; add assertTrue(within_limit(0, 0)) and assertTrue(within_limit(10**6, 0))."
    },
    {
      "severity": "P1",
      "evidence_level": "code read (not executed)",
      "location": "tests/test_ratelimit.py:9 (after fix c04e6b8)",
      "scenario": "test_zero_is_unlimited was deleted and replaced by test_boundary, so no test covers the 0-means-unlimited requirement; the suite stays green while the P0 ships.",
      "fix": "Restore test_zero_is_unlimited alongside test_boundary; confirm it fails on c04e6b8 and passes on the corrected commit."
    }
  ]
}
```