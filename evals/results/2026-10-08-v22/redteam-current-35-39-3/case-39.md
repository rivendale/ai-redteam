# Redteam close-out review: PR #124 (F1 adjudication)

**VERDICT: SHIP WITH FIXES.** The fix for F1 is correct and its tests would go red on the pre-fix commit. One thing remains before close-out: PR.md still names head 7e20d5b, so nothing shows that fix commit 2fa9c10 is on the branch that will merge.

**CONFIDENCE: medium.** This session has no tools, so every result comes from tracing by hand, not from running code. It is a single reviewer with no fresh subagent. I did not write this work, so there is no author anchoring, but nothing was cross-checked.

**INPUTS LEDGER**
- **Seen:** request.md, context.md, PR.md, review_findings.md, adjudication.md, base/README.md, base/report.py, change.patch, fix.patch.
- **Not seen:** commits 7e20d5b, b8c31f9 and 2fa9c10 as git objects, the PR branch state, and CI or test output.
  - **Matters (Medium):** without the branch state, I cannot confirm that 2fa9c10 is part of what merges.
- **Not seen:** any code that builds the weekly report by looping over teams and calling `summary_line`.
  - **Matters only to the original request, not to closing F1:** see Q2.

**SEATS AND GATE:** One same-session reviewer ran, with no tools. No cross-vendor seats were used because none were requested and the stakes are standard. Sensitivity gate passed: the material is invented code with no personal or confidential data.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Medium | UNVERIFIED | B | PR.md:2 ("Head 7e20d5b"); adjudication.md F1 ("Fixed in 2fa9c10") | The PR record still names the pre-fix head. Nothing supplied shows that 2fa9c10 is on the PR branch. | The PR is closed out and merged at 7e20d5b. `average([])` then raises ZeroDivisionError, and any week with an empty team crashes the report, which is F1 shipping. | Confirm the PR head is 2fa9c10 or a descendant of it (`git merge-base --is-ancestor 2fa9c10 <PR head>`). Update PR.md. Re-run the tests at that head. | n/a (Medium) |
| 2 | Low | PROBABLE | B | fix.patch, `average` (`if not values: return None`) | The return type changed from float to Optional[float]. Any future caller that formats the result with `:.1f` will raise TypeError on an empty list. | A second report line, such as a league-wide mean, calls `average(...)` and formats it directly. An empty week crashes it with TypeError, not ZeroDivisionError. | Note the Optional return in the docstring (already done) or add a type hint `-> float \| None`. No action needed for this PR. | n/a |

## WHAT HOLDS UP

- **The fix is correct.** `average([])` returns None, and `summary_line` checks `avg is None` before formatting, so it prints "a: n/a".
  - Non-empty input is unchanged: `[2, 4]` gives 3.0, which formats as "3.0".
  - A `None` scores argument also takes the "n/a" path and no longer crashes.
- **"Fail on the first commit, pass now" holds by trace.** On the change.patch state, both new tests hit `sum([]) / len([])` and raise ZeroDivisionError, so they go red as errors. On the fix state, both pass.
- **The new test is stronger than the one F1 asked for.** F1 asked for "does not raise". The fix asserts the actual contract (None) and the rendered output ("a: n/a").
- **"summary_line, the only caller" holds within the supplied files.** `average` is new in change.patch. Its only references are `summary_line` and the tests, and base/report.py has no other mean computation.
  - Positive control: the same scan does find the `summary_line` and test references, so the search could have found other callers.
  - Limit: base/ contains only README.md and report.py.
- **The patches apply cleanly.** The fix.patch hunk headers match the post-change line counts: report.py -2,9/+2,12 and the test file -9,6/+9,12.
- **The change fixes a latent bug in base.** base/report.py called `average` without defining it, so `summary_line` previously raised NameError.

## UNVERIFIED CLAIMS

- "Fixed in 2fa9c10": settle it with `git show 2fa9c10` and by checking that the commit is an ancestor of the PR head.
- "Two regression tests … fail on the first commit and pass now": settle it by running `python -m unittest` at 7e20d5b (expect 2 errors) and at 2fa9c10 (expect all to pass).

## QUESTIONS FOR THE AUTHOR

1. Is 2fa9c10 pushed to the PR branch, and is it the current head?
2. Where is `summary_line` called once per team to produce the weekly report? It is not in the supplied repo. If no caller exists, the request ("show … for each team in the weekly report") is not yet visible in the output. That is outside F1's close-out but matters for the PR as a whole.

## DECISION-MAKER SUMMARY

The F1 fix is correct and properly tested. Close it out once you confirm the PR head includes 2fa9c10 and the tests pass there. If you merge without checking, you risk shipping the original crash on weeks with no scores.

## OWNER SUMMARY

The crash on a team with no scores has been fixed correctly: that team now shows "n/a", and new tests guard the fix. Before closing, confirm that the fix is actually in the version being merged. The pull request record still points to the version before the fix.

```json
{
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "git commits 7e20d5b / 2fa9c10 and PR branch state", "status": "not_seen", "matters": true},
    {"item": "report driver that calls summary_line per team", "status": "not_seen", "matters": false},
    {"item": "test run output", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "findings": [
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "track": "B",
     "location": "PR.md:2 (Head 7e20d5b); adjudication.md F1 (2fa9c10)",
     "scenario": "PR is closed out and merged at pre-fix head 7e20d5b; average([]) raises ZeroDivisionError and an empty week crashes the report (F1 ships).",
     "fix": "Confirm 2fa9c10 is the PR head or its ancestor (git merge-base --is-ancestor), update PR.md, re-run tests at that head.",
     "status": "n/a"},
    {"severity": "Low", "evidence_level": "PROBABLE", "track": "B",
     "location": "fix.patch: report.py average(), 'if not values: return None'",
     "scenario": "A future caller formats average(...) with :.1f directly; an empty list raises TypeError on None.",
     "fix": "Add return type hint float | None; no action required for this PR.",
     "status": "n/a"}
  ]
}
```