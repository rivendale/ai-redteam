# Redteam review: pre-commit formatter hook proposal

**Single reviewer, no tools.** I did not write this work. I reviewed it in one pass without a subagent or tools, so I could not open the pull requests, the CI configuration or the pre-commit configuration. Re-run in a fresh session if the stakes rise.

**VERDICT: SHIP WITH FIXES.** The proposal is cheap, reversible and safe if nobody installs the hook. However, the evidence does not show that the hook would remove the comments it targets, and it skips cheaper options that need no installation.

**CONFIDENCE: medium.** The arithmetic checks out. Confidence is limited because I had no tools, I could not see the comment text or CI status for the 20 PRs, and I could not see the repository's pre-commit or CI configuration.

**INPUTS LEDGER**
- **Seen:** the original request, the context, `evidence/pr_review_sample.csv` and `proposal.md`.
- **Not seen:** the 20 PRs and their comment text (**matters**, because the causal claim depends on it), CI and formatter configuration (matters), the existing pre-commit configuration (minor), team size and PR rate (minor), and how the minutes were recorded (matters for sizing the benefit).

**COVERAGE**
- **Scope:** the whole work, which is two files.
- **Checked:** both files; every figure in "Need"; each section (Need, Who benefits, Alternatives, If nobody installs, Success measure); the assumptions "CI fails after push causes the 5 of 20" and "install once, nothing daily".
- **Not checked:** the PRs themselves and the CI and pre-commit configuration (not supplied).

**SEATS AND GATE:** One local reviewer ran. No cross-vendor seats were used because the stakes are low and none were requested. Nothing sensitive was found.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED | D | proposal.md, Alternatives: "that is the 5 of 20" | The claim that the 5 PRs are caused by CI failing after the push is never tested. The CSV has only counts and minutes. It has no comment text and no CI result. CI already blocks unformatted code, so comments that remain may be about things the formatter does not enforce: line breaks it leaves alone, naming, or ordering it does not manage. | If reviewers mostly comment after CI is green, the comments are about style the formatter does not touch. The hook then changes nothing, and the "fewer than 2" target misses. | Classify the 9 comments in the 5 PRs. For each, ask: would running the formatter have fixed it? Was the format check red at the time? Ship the hook only if most comments meet both. | T/T/F/F |
| F2 | Medium | CONFIRMED | D | proposal.md, Alternatives | Cheaper options that need no installation were never considered. The "guide" option is a strawman. | The team adds a per-clone step when one of these would cut the round trip with no adoption at all: a review norm ("formatting is CI's job; don't comment on it"), a CI job or bot that commits the formatter's fix, or format-on-save in a shared editor config. | Compare at least the reviewer norm and CI autofix against the hook. The hook can still win, but the comparison should be stated. | T/T/F/F |
| F3 | Low | CONFIRMED | D | proposal.md, Success measure | The success measure cannot tell its causes apart. It does not track hook adoption. "Fewer than 2" does not say whether it counts comments (baseline 9) or PRs (baseline 5). It does not re-measure minutes. | Comments fall without anyone installing the hook, or stay flat with everyone installed. In either case the team cannot tell whether to keep the hook. | Track three things: install rate or CI format-check failures per PR, comment count and PR count separately, and minutes. | T/T/F/T |
| F4 | Low | PROBABLE | D | proposal.md, Proposal and Who benefits | "Install once… then do nothing further" overstates how easy this is. `pre-commit install` runs once per clone, not once per person. New joiners must be told. The hook adds time to every commit. `--no-verify` skips it. The "about 5 minutes" figure is unverified. | New clones and new joiners never install the hook, so the round trip continues for them unnoticed. | Say "per clone". Add the install to the setup script or onboarding. | T/F/F/T |

## Needs validation

- **S1. Where the minutes came from.** The CSV does not say who recorded them or how. 12 minutes per formatting-comment PR is high for formatting alone and may include the rework round trip. What would settle it: the method used to record the minutes.
- **S2. Hook and CI formatter versions.** If the hook's formatter version or configuration differs from CI's, the hook passes and CI still fails, and the round trip remains. What would settle it: whether `.pre-commit-config.yaml` pins the same formatter version and configuration as the CI job.

## Refuted

- **"The figures are wrong."** I recomputed them. PRs 1, 4, 7, 12 and 17 have format comments, so 5/20 = 25%. Their minutes are 14 + 9 + 16 + 11 + 10 = 60, and 60/5 = 12. All three claims reproduce.
- **"Low adoption breaks things."** The CI check stays in place, so unformatted code is still blocked. The fallback holds.
- **"The proposal drifts from the request."** The request was "whether and how to cut the formatting-only noise". The proposal answers both parts. No drift.

## What holds up

- The arithmetic.
- Keeping CI as the backstop.
- Removal is just deleting one config block.
- The cost to try it is low.
- The success measure is roughly sized against a baseline of 9 comments.

## Unverified claims

- **"The CI check already fails unformatted code."** Confirm by reading the CI configuration.
- **"Reviewers recorded" the minutes.** Confirm by asking how they were recorded.
- **"About 5 minutes" to install.** Confirm by timing a fresh clone.
- **"That is the 5 of 20."** Confirm by classifying the comments as described in F1.

## Questions for the author

1. In the 5 PRs, would running the formatter have fixed each comment, and was the CI format check red when the comment was posted?
2. Why not a CI autofix job or a reviewer norm instead of an install step for each clone?

## Decision-maker summary

The hook is cheap and safe to try, but nothing yet shows that it targets the comments actually seen. Spend 15 minutes classifying the 9 comments before adopting it. If you proceed anyway, the worst case is that 5 minutes per clone produces no improvement, and the success measure would not show why.

## Owner summary

The plan to format code automatically before it is shared is low-cost and easy to undo. However, we have not checked whether the formatting complaints in reviews are the kind this tool would actually fix. A quick look at those few complaints, and a comparison with options that need no setup at all, should come first.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "evidence/pr_review_sample.csv", "status": "seen", "matters": true},
    {"item": "proposal.md", "status": "seen", "matters": true},
    {"item": "the 20 PRs' comment text and CI status", "status": "not_seen", "matters": true},
    {"item": "CI and formatter configuration", "status": "not_seen", "matters": true},
    {"item": "existing pre-commit configuration", "status": "not_seen", "matters": false},
    {"item": "method used to record minutes", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "evidence/pr_review_sample.csv", "kind": "data"},
      {"unit": "proposal.md", "kind": "document"},
      {"unit": "proposal.md#Need figures (25%, 12 min, 60 min)", "kind": "claim"},
      {"unit": "CI-after-push explains the 5 of 20", "kind": "assumption"},
      {"unit": "install once, nothing daily", "kind": "assumption"},
      {"unit": "proposal.md#Alternatives considered", "kind": "section"},
      {"unit": "proposal.md#Success measure", "kind": "section"}
    ],
    "not_checked": [
      {"unit": "the 20 PRs and their comments", "reason": "not_supplied"},
      {"unit": "CI, formatter and pre-commit configuration", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "D",
     "location": "proposal.md, Alternatives considered: 'that is the 5 of 20'",
     "scenario": "If the formatting comments concern style the formatter does not enforce, or were made after CI was green, the hook changes nothing and the under-2 target misses.",
     "fix": "Classify the 9 comments: formatter-fixable? CI format check red at the time? Ship the hook only if most are both.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "D",
     "location": "proposal.md, Alternatives considered",
     "scenario": "The team adds a per-clone install when a reviewer norm, a CI autofix job or format-on-save would remove the round trip with no adoption step.",
     "fix": "Compare the hook against a reviewer norm and CI autofix explicitly before choosing.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "D",
     "location": "proposal.md, Success measure",
     "scenario": "Comments change, or do not, and the team cannot tell whether adoption or mechanism explains it; 'fewer than 2' is ambiguous between comments (baseline 9) and PRs (baseline 5).",
     "fix": "Track hook adoption or CI format-failure rate, count comments and PRs separately, and re-measure minutes.",
     "answers": {"a": true, "b": true, "c": false, "d": true}},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "PROBABLE", "track": "D",
     "location": "proposal.md, Proposal and Who benefits: 'install the hook once... then do nothing further'",
     "scenario": "New clones and new joiners never run pre-commit install, or bypass it with --no-verify, so the round trip continues for them.",
     "fix": "State that the install is per clone and add it to the setup script or onboarding.",
     "answers": {"a": true, "b": false, "c": false, "d": true}},
    {"id": "S1", "status": "needs_validation", "track": "D", "location": "evidence/pr_review_sample.csv, minutes_on_format_comments",
     "suspicion": "12 minutes per formatting-comment PR may include rework, not reviewer time.",
     "unresolved_fact": "How and by whom the minutes were recorded."},
    {"id": "S2", "status": "needs_validation", "track": "D", "location": "proposal.md, Proposal",
     "suspicion": "Hook and CI formatter versions or configuration may differ, so the hook passes while CI fails.",
     "unresolved_fact": "Whether the pre-commit config pins the same formatter version and configuration as the CI job."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The Need figures are wrong.", "evidence": "PRs 1,4,7,12,17 are nonzero: 5/20=25%; 14+9+16+11+10=60; 60/5=12."},
    {"id": "C2", "candidate": "Low adoption breaks the build or lets unformatted code through.", "evidence": "The CI check is retained and still fails unformatted code."},
    {"id": "C3", "candidate": "Drift from the request.", "evidence": "The request asks whether and how to cut formatting noise; the proposal answers both."}
  ]
}
```