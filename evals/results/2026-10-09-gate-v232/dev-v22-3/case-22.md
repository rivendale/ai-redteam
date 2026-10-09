# Redteam report: pre-commit formatter hook proposal

**VERDICT: SHIP WITH FIXES.** The change is cheap and reversible, and the numbers reproduce. But the evidence never shows that the hook targets what reviewers actually comment on, and the success measure cannot tell whether the hook caused any change.

**CONFIDENCE: medium.** Three things limit it:
- I had no tools, so nothing was run, and the CI and pre-commit configuration were not opened.
- There was a single reviewer and no independent seats.
- The decisive fact is missing: what the 9 formatting comments actually said.

This is not a same-context review. The work was not written in this conversation.

## Inputs ledger

**Seen:**
- request.md
- context.md
- proposal.md
- evidence/pr_review_sample.csv (20 rows)

**Not seen:**
| Item | Matters? | Why |
|---|---|---|
| Existing CI formatter check and its config | Yes | The proposal relies on it existing and enforcing the same rules as the hook. |
| Text of the 9 formatting-only review comments | Yes | The causal claim depends on it. |
| How "minutes" were recorded | Somewhat | It affects how big the need is. |
| Team size and PR rate | Somewhat | It affects the cost/benefit. |
| Formatter name and version | Yes | Hook and CI version drift is a known failure. |

## Coverage

**Checked:**
- Every row of the CSV, recomputed.
- Every section of proposal.md: Proposal, Need, Who benefits, Alternatives, If nobody installs, Success measure.
- Assumptions: CI already enforces formatting, the cause of the comments, the size of the burden.

**Not checked:**
- CI config and pre-commit config (not supplied).
- The PR comment text (not supplied).

## Seats and gate

- **Sensitivity gate:** passed. The data is PR numbers and counts, with no personal or confidential data.
- **Seats:** only this reviewer ran. No subagent or cross-vendor seats were available because this session has no tools. None were refused.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED (evidence gap) | D/A | proposal.md "Alternatives considered", CI-only bullet: "the formatting round trip still happens (that is the 5 of 20)"; CSV columns | The proposal blames the 5 PRs on CI failing *after* push. The CSV records only comment counts and minutes: nothing ties the comments to CI failures. CI already fails unformatted code, so merged PRs passed the formatter. Human formatting comments therefore either came before CI finished, or were about things the formatter does not enforce (naming, blank-line taste, import order, line wraps the tool allows). The hook runs the same formatter, so it helps only in the first case. | The comments were about style outside the formatter's rules. Everyone installs the hook. The next 20 PRs still get about 9 formatting comments, and the proposal "fails" even though it was implemented correctly. | Before adopting, classify the 9 comments in PRs 1, 4, 7, 12 and 17 (about 15 minutes). For each, record whether CI was red when the comment was made and whether the formatter would have changed the line. Rewrite "Need" to match. If most are out of the formatter's scope, the fix is formatter config or a reviewer norm, not a hook. | a Y / b Y / c N / d N (unknown) |
| F2 | Medium | CONFIRMED | D | proposal.md "Success measure" and "If nobody installs the hook" | The measure counts comments but not hook adoption. The hook is optional ("Nothing breaks" if nobody installs it). A drop or no drop therefore cannot be attributed to the hook. The baseline is also small: 5 PRs and 9 comments. | Half the team installs the hook and comments fall from 9 to 5. That is read as a miss, or as a partial success, with no way to tell which, or whether it was chance. | Track installs: a hook marker, or a CI step noting whether the commit was pre-formatted. Report formatting comments per PR for authors with and without the hook. State the baseline as 9 comments in 5/20 PRs. | a Y / b Y / c N / d N |
| F3 | Low | CONFIRMED | D | proposal.md "Alternatives considered" | Cheaper options with no per-person step are missing: format-on-save in shared editor settings, a CI bot that commits the formatting fix, and a team norm that reviewers skip formatting because CI owns it. "Do nothing" is not costed either: 60 reviewer-minutes per 20 PRs, about 3 minutes per PR. | The hook is adopted while a zero-install option, such as an autofix bot, would have removed the round trip for people who never install anything. | Add these alternatives with cost and burden. Compare against the measured 3 min/PR. | a Y / b Y / c N / d N |
| F4 | Low | PROBABLE | D | proposal.md: "install the hook once … then do nothing further"; "Nobody has to do anything daily" | The burden is understated. Install is per clone, not per person. New joiners need onboarding. The pre-commit tool itself must be installed. `--no-verify` bypasses it. If the hook pins a different formatter version than CI, commits can flip-flop. | A new hire or a fresh clone never runs `pre-commit install`. A version mismatch makes the hook reformat code that CI then rejects, and people disable the hook. | Pin the formatter version once and share it between hook and CI. Add `pre-commit install` to the setup script or README. | a Y / b N / c N / d N |

## Needs validation

- **S1:** That a CI formatter check exists and fails unformatted code. Settled by: the CI config and one recent red run on unformatted code.
- **S2:** How "minutes_on_format_comments" was recorded. Settled by: whether reviewers self-reported, and what the minutes include. PR 7 shows 16 minutes for one comment, which suggests round-trip time rather than reading time.
- **S3:** The "about 5 minutes" install cost. Settled by: one engineer timing a clean install, including installing the pre-commit tool.
- **S4 (central to F1):** What the 9 comments said. Settled by: the comment text and the CI status at the time each comment was made.

## Refuted

- **R1:** "25% and 60 minutes are miscomputed." Refuted. The nonzero rows are PRs 1, 4, 7, 12 and 17, which is 5/20 = 25%. The minutes are 14+9+16+11+10 = 60.
- **R2:** "An average of 12 minutes is misleading." Refuted. 60/5 = 12 per affected PR, and the text pairs it with the 60-minute total. (Per comment it would be 6.7, but the proposal does not claim per comment.)
- **R3:** "The hook requires daily action." Refuted. A pre-commit hook runs automatically once installed.

## What holds up

- Every figure reproduces from the CSV.
- The proposal is cheap and reversible, and correctly keeps CI as the backstop, so non-adoption cannot make things worse.
- It answers the request: it says both whether to act and how.
- It names a measurable success criterion.

## Unverified claims

| Claim | How to confirm |
|---|---|
| The CI check exists. | Open the CI config. |
| CI timing caused the comments. | Check comment timestamps against CI runs. |
| Install takes about 5 minutes. | Time a clean install. |
| Minutes were "recorded" by reviewers. | Ask for the method. |

## Questions for the author

1. What did the 9 formatting comments say, and would the formatter have changed those lines?
2. Was CI red when each comment was written?
3. How will you know who installed the hook?

## Decision-maker summary

Adopting is low risk, but first spend about 15 minutes classifying the 9 comments. The main risk is that they concern style the formatter does not enforce, in which case the hook removes none of them. Add hook-adoption tracking so the success measure can be interpreted.

## Owner summary

The plan to format code automatically before it is shared is cheap and easy to undo, and its numbers check out. What is not yet shown is that the formatting complaints reviewers make are the kind the tool would fix, so look at those few complaints first. Also track who actually turns the tool on, so the team can tell whether it worked.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "proposal.md", "status": "seen", "matters": true},
    {"item": "evidence/pr_review_sample.csv", "status": "seen", "matters": true},
    {"item": "CI formatter check config", "status": "not_seen", "matters": true},
    {"item": "text of the 9 formatting-only review comments", "status": "not_seen", "matters": true},
    {"item": "method for recording minutes", "status": "not_seen", "matters": true},
    {"item": "team size and PR rate", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "PR numbers and counts only; no personal or confidential data"},
  "coverage": {
    "checked": [
      {"unit": "proposal.md", "kind": "file"},
      {"unit": "evidence/pr_review_sample.csv", "kind": "data"},
      {"unit": "proposal.md#Need", "kind": "section"},
      {"unit": "proposal.md#Alternatives considered", "kind": "section"},
      {"unit": "proposal.md#If nobody installs the hook", "kind": "section"},
      {"unit": "proposal.md#Success measure", "kind": "section"},
      {"unit": "CI timing causes the formatting comments", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "CI and pre-commit configuration", "reason": "not supplied; no tools"},
      {"unit": "PR comment text", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "D",
     "location": "proposal.md, Alternatives considered: 'the formatting round trip still happens (that is the 5 of 20)'",
     "scenario": "The 9 comments concern style the formatter does not enforce; everyone installs the hook, the next 20 PRs still draw about 9 formatting comments, and the proposal fails despite full adoption.",
     "fix": "Classify the 9 comments in PRs 1, 4, 7, 12, 17 by CI status at comment time and whether the formatter would change the line; rewrite Need accordingly.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "D",
     "location": "proposal.md, Success measure; If nobody installs the hook",
     "scenario": "Partial, untracked adoption leaves comments at about 5 of 9; the result cannot be attributed to the hook or distinguished from noise on a 5-PR baseline.",
     "fix": "Track hook adoption and report formatting comments split by authors with and without the hook; state the baseline as 9 comments in 5/20 PRs.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "D",
     "location": "proposal.md, Alternatives considered",
     "scenario": "A per-person hook is adopted while a zero-install CI autofix bot or shared format-on-save would have removed the round trip for everyone.",
     "fix": "Add autofix bot, format-on-save and a reviewer norm as costed alternatives against the measured 3 min/PR.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "PROBABLE", "track": "D",
     "location": "proposal.md: 'install the hook once ... then do nothing further'",
     "scenario": "New clones and joiners never install the hook, or the hook and CI pin different formatter versions and people disable the hook.",
     "fix": "Pin one formatter version shared by hook and CI; put pre-commit install in the setup script.",
     "answers": {"a": true, "b": false, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "D", "location": "proposal.md, Proposal",
     "suspicion": "The CI formatter check may not exist or may differ from the hook.",
     "unresolved_fact": "CI config and one red run on unformatted code."},
    {"id": "S2", "status": "needs_validation", "track": "D", "location": "evidence/pr_review_sample.csv, minutes_on_format_comments",
     "suspicion": "Minutes may be self-reported or include round-trip time (PR 7: 16 minutes for one comment).",
     "unresolved_fact": "How the minutes were recorded and what they include."},
    {"id": "S3", "status": "needs_validation", "track": "D", "location": "proposal.md, 'about 5 minutes'",
     "suspicion": "Install cost may exceed 5 minutes if the pre-commit tool itself is not installed.",
     "unresolved_fact": "A timed clean install."},
    {"id": "S4", "status": "needs_validation", "track": "D", "location": "evidence/pr_review_sample.csv rows 1, 4, 7, 12, 17",
     "suspicion": "The comments may be outside the formatter's scope.",
     "unresolved_fact": "Comment text and CI status at the time of each comment."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "25% and 60 minutes are miscomputed.", "evidence": "Nonzero rows 1, 4, 7, 12, 17 give 5/20; minutes 14+9+16+11+10 = 60."},
    {"id": "R2", "candidate": "'Average of 12 minutes' is misleading.", "evidence": "60/5 = 12 per affected PR, stated alongside the 60-minute total."},
    {"id": "R3", "candidate": "The hook requires daily action.", "evidence": "Pre-commit hooks run automatically on commit once installed."}
  ]
}
```