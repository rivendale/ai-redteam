# Redteam review: pre-commit formatter hook proposal

VERDICT: **SHIP WITH FIXES.** The numbers reproduce, and the proposal is cheap and reversible. Its central claim, that a pre-commit hook will remove the formatting comments, is not supported by the evidence it cites.

CONFIDENCE: **medium.** This session did not write the work, but it had no tools and no subagent. Nothing was run. The actual review comments, CI config and formatter config were not supplied.

INPUTS LEDGER:
- **Seen:** the original request, context.md, `proposal.md` and `evidence/pr_review_sample.csv` (20 rows).
- **Not seen, and it matters:**
  - The text of the 9 formatting comments. Needed to know whether the formatter would have prevented them.
  - The CI formatter check config and version.
  - Whether a pre-commit config already exists.
- **Not seen, minor:**
  - Team size, which sets the total install cost.
  - The date range of the 20 PRs.

COVERAGE:
- **Checked:**
  - Every CSV row, with all figures recomputed.
  - All proposal sections: Proposal, Need, Who benefits, Alternatives, If nobody installs, Success measure.
  - Assumptions: comments are formatter-fixable, and the one-time install is the only burden.
- **Not checked:** the CI config, the formatter config and the PR comment text (none were supplied).

SEATS AND GATE:
- **Seats:** only a local single-session review ran. No subagent or cross-vendor seats were available because there were no tools.
- **Gate:** no sensitive data is present, so the gate passed.

## Recomputation

| Claim | Recomputed from CSV | Result |
|---|---|---|
| 5 of 20 PRs had formatting comments (25%) | PRs 1, 4, 7, 12, 17 | Correct |
| About 60 minutes in total | 14+9+16+11+10 = 60 | Correct |
| Average 12 minutes | 60 / 5 affected PRs = 12 | Correct per affected PR. Per comment it is 60 / 9 = about 6.7 minutes. |
| (not stated) total comments | 1+2+1+3+2 = 9 | The baseline in comments is 9 |

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED (that the claim is unsupported) | D/A | proposal.md "Alternatives considered", bullet 1: "so the formatting round trip still happens (that is the 5 of 20)" | The CSV records only comment counts and minutes. It does not record what the comments said or whether CI had failed. CI already blocks unformatted code, so comments on merged PRs may be about style the formatter accepts (naming, wrapping, ordering). A hook running the same formatter cannot catch those. | The hook is installed. The next 20 PRs still carry formatting comments on code the formatter considers clean. The success measure fails and the real cause stays unaddressed. | For each of the 9 comments, check out the commented revision and run the formatter. If the commented line changes, a hook would have caught it. If it does not change, the hook is irrelevant to that comment. Report the split before claiming the need. | a: yes, b: yes, c: no, d: unknown |
| F2 | Low | CONFIRMED | D | proposal.md "Alternatives considered" | The cheapest options are missing: a reviewer norm ("CI owns formatting; don't comment on it"), editor format-on-save, and a CI bot that pushes the formatting fix. A bot also covers engineers who never install the hook. | The team adopts the hook. Non-installers and new hires keep producing the same round trip, which a bot or norm would have removed at zero install cost. | Add these alternatives and give a reason for rejecting or adopting each one. | a: yes, b: yes, c: no, d: no |
| F3 | Low | CONFIRMED | D | proposal.md "Success measure" | The target is stated in comments ("fewer than 2"). The baseline is stated in PRs (5 of 20), and the baseline in comments (9) is never given. There is also no adoption measure, so the proposal cannot tell "hook didn't work" apart from "nobody installed it". | After 20 PRs there are 3 comments. It is unclear whether that counts as success (down from 9) or failure (not fewer than 2), and whether anyone installed the hook. | State the baseline as 9 comments in 5 of 20 PRs. Also track hook installs and the count of CI formatting failures. | a: yes, b: yes, c: no, d: no |

## NEEDS VALIDATION

- **S1. The hook's formatter version may drift from CI's.** The proposal says "the same check" but does not say the versions are pinned to match. A mismatch would make the hook pass while CI fails, or the reverse. *Settling fact:* whether the pre-commit config pins the same formatter version and options as the CI job.
- **S2. The minutes are unverified.** The proposal says the minutes were "recorded" by reviewers. They could be estimates or measurements. *Settling fact:* how the minutes column was collected.

## REFUTED

- **The figures are miscomputed.** Refuted: recomputation gives 5/20 = 25%, 60 minutes total, and 12 minutes per affected PR.
- **The plan depends on daily manual action.** Refuted: the hook is a one-time `pre-commit install`, and CI remains the backstop for anyone who skips it. The "If nobody installs" section holds.

## WHAT HOLDS UP

- The figures match the CSV.
- The need is stated at its real, modest size (about 60 reviewer-minutes per 20 PRs) rather than inflated.
- Keeping CI as the enforcement point means non-adoption breaks nothing.
- The cost is small and the change is reversible. That fits the low stakes.

## UNVERIFIED CLAIMS

- **"Install takes about 5 minutes."** Confirm by timing one fresh install.
- **The formatting round trip is caused by CI failing after the push.** Confirm with the F1 check.

## QUESTIONS FOR THE AUTHOR

1. Would the formatter have changed the lines those 9 comments pointed at?
2. Does the hook pin the same formatter version and options as CI?

## DECISION-MAKER SUMMARY

Approve the hook as a cheap, reversible experiment, but first check whether the 9 formatting comments were things the formatter actually fixes. If they were not, the hook will not move the success measure. Also consider a reviewer norm or a CI auto-fix bot, which need no installs.

## OWNER SUMMARY

The idea is cheap, easy to undo, and the numbers behind it are correct. What is not yet shown is that the formatting complaints in reviews are the kind an automatic formatter would prevent. Check a handful of those complaints first, and consider simply agreeing that reviewers leave formatting to the automated check.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "proposal.md", "status": "seen", "matters": true},
    {"item": "evidence/pr_review_sample.csv", "status": "seen", "matters": true},
    {"item": "text of the 9 formatting-only review comments", "status": "not_seen", "matters": true},
    {"item": "CI formatter check config and version", "status": "not_seen", "matters": true},
    {"item": "team size and PR date range", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "local-single-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "evidence/pr_review_sample.csv", "kind": "data"},
      {"unit": "proposal.md", "kind": "file"},
      {"unit": "proposal.md#Need (measured)", "kind": "section"},
      {"unit": "proposal.md#Alternatives considered", "kind": "section"},
      {"unit": "proposal.md#If nobody installs the hook", "kind": "section"},
      {"unit": "proposal.md#Success measure", "kind": "section"},
      {"unit": "formatting comments are formatter-fixable", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "CI formatter config", "reason": "not supplied"},
      {"unit": "PR review comment text", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "D",
     "location": "proposal.md Alternatives considered, bullet 1 ('that is the 5 of 20')",
     "scenario": "CI already blocks unformatted code; if the 9 comments concern style the formatter accepts, the hook (same formatter) prevents none of them and the success measure fails.",
     "fix": "Run the formatter on each commented revision and report how many of the 9 comments it would have fixed before claiming the need.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "For each of the 9 comments, check out the commented revision, run the formatter, and diff the commented line; unchanged means the hook would not have prevented it."},
    {"id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "D",
     "location": "proposal.md Alternatives considered",
     "scenario": "Non-installers and new hires keep generating the round trip that a reviewer norm or CI auto-fix bot would remove at zero install cost.",
     "fix": "Evaluate a reviewer norm, editor format-on-save and a CI auto-fix bot as alternatives.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "D",
     "location": "proposal.md Success measure",
     "scenario": "After 20 PRs with 3 comments, success is ambiguous (baseline 9 comments never stated) and non-adoption cannot be told apart from ineffectiveness.",
     "fix": "State baseline as 9 comments in 5 of 20 PRs; also track hook installs and CI formatting-failure count.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "D", "location": "proposal.md Proposal ('the same check in CI')",
     "suspicion": "Hook and CI formatter versions may drift, causing hook-pass/CI-fail.",
     "unresolved_fact": "Whether the pre-commit config pins the same formatter version and options as CI."},
    {"id": "S2", "status": "needs_validation", "track": "C", "location": "evidence/pr_review_sample.csv minutes_on_format_comments",
     "suspicion": "Minutes may be estimates rather than measurements.",
     "unresolved_fact": "How the minutes column was collected."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The 25%, 60-minute and 12-minute figures are miscomputed.",
     "evidence": "Recomputed from CSV: PRs 1,4,7,12,17 = 5/20; 14+9+16+11+10 = 60; 60/5 = 12 per affected PR."},
    {"id": "C2", "candidate": "The plan depends on a daily manual step.",
     "evidence": "Install is one-time; CI remains the enforcement backstop, so non-installation breaks nothing."}
  ]
}
```