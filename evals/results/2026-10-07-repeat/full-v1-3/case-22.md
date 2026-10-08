# Redteam review: pre-commit formatter hook proposal

**Review mode:** Track A (decisions, analysis, recommendations), covering need, cost, alternatives, and adoption. I did not author this work, so there is no authorship anchoring. I had no tools, so I checked all arithmetic by hand from the CSV as given. I could not see the actual review comments.

## Pass 1: Reconstruct

The proposal says 5 of 20 recent PRs had formatting-only review comments, costing about 60 reviewer-minutes. It recommends a pre-commit formatter hook, alongside the existing CI format check, to remove those comments. The fix only works if two things are true, and the proposal states neither:

1. The comments concern things the configured formatter would actually change.
2. Those comments exist because unformatted code reaches reviewers before CI's failure is noticed.

A third, also unstated, assumption is that engineers will install the hook in enough numbers to matter.

## Pass 2: Attack, summarized

The arithmetic holds. The PRs with formatting comments are 1, 4, 7, 12 and 17, which is 5 of 20. Their minutes are 14 + 9 + 16 + 11 + 10 = 60, so 12 minutes per affected PR.

The causal story does not hold. CI already fails unformatted code, so every merged PR passed the formatter. A reviewer comment about formatting therefore has only two possible explanations:

- **(a) The reviewer looked before CI was green.** The hook would help here, but so would a zero-cost rule: "request review only after CI passes."
- **(b) The comment was about style the formatter doesn't enforce.** Examples are blank lines, import grouping, line breaks the formatter leaves alone, or naming. The hook runs the same formatter, so it changes nothing.

The proposal calls these comments "the CI round trip," but that mixes up two separate events: a CI failure, which happens to the author, and a review comment, which costs the reviewer time. The time figures point toward (b). 14 or 16 minutes for one comment that a formatter could fix mechanically looks more like a style discussion than a "run the formatter" note. Across the 9 comments the average is about 6.7 minutes each. The "12 minutes" in the proposal is per affected PR, not per comment, and the text leaves that unclear.

The stakes are low and the change is reversible, so the hook does little harm. The risk is that the team ships it, the success measure misses, and the real cause goes unfixed.

## Report

**VERDICT:** REWORK. The hook is cheap and harmless, but the evidence never shows that it would remove the comments that were measured. The one diagnostic step that could flip the recommendation was skipped.

**CONFIDENCE IN VERDICT:** Medium. Seeing the text of the 9 comments, and when each was posted relative to CI, would settle the central question either way.

### Findings

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | High | PROBABLE | "Alternatives considered: CI check only… the formatting round trip still happens (that is the 5 of 20)" | Conflates CI failures with reviewer comments. Since CI blocks unformatted merges, the comments are either pre-CI reviews or about style the formatter doesn't enforce. The hook only helps the first case. | The hook ships, 100% of engineers install it, and reviewers keep leaving the same blank-line or import-order comments, because the formatter never touched those. The success measure fails. | Classify all 9 comments. Would the configured formatter have changed the flagged code? Was the comment posted before CI finished? Recommend the hook only if most are "formatter would fix" and "pre-CI". |
| 2 | Medium | PROBABLE | "Alternatives considered" (only two listed) | Cheaper or more direct options were not considered. (i) A review norm: wait for green CI, and don't comment on formatting because CI owns it. (ii) Extend the formatter or linter config to cover the style points reviewers actually raise. (iii) Format-on-save editor settings. (iv) A CI bot that pushes an autoformat commit. (v) Do nothing: about 3 reviewer-minutes per PR. | The team adopts the hook when a one-line review guideline or a config change would have removed the comments at no install cost. | Compare the options against the classified comments from finding #1. Pick the one that matches the actual cause. |
| 3 | Medium | CONFIRMED | "Success measure: … expected fewer than 2" | The unit is ambiguous: comments or PRs? The baseline is 9 comments in 5 PRs. With n=20 and a low base rate, the result is noisy. Nothing tracks hook installation, so a change can't be attributed to the hook. | Next window has 1 PR with 2 comments. Is that a pass or a fail? Or comments drop by chance and the hook gets credit. | State the unit and the baseline (e.g., "PRs with ≥1 format-only comment: 5/20 → ≤1/20"). Record the hook install rate. Tag each comment with whether the formatter covers it. |
| 4 | Low | CONFIRMED | "reviewers recorded an average of 12 minutes spent on those comments" | This is 12 minutes per affected PR, not per comment (60 / 9 ≈ 6.7 per comment). The method for recording minutes is not stated. | The reader overestimates the per-comment cost, or relies on minutes that were reconstructed after the fact. | Restate as "60 min across 9 comments in 5 PRs" and say how the minutes were captured. |
| 5 | Low | PROBABLE | "install the hook once (`pre-commit install`, about 5 minutes)… Nobody has to do anything daily" | The hook is per-clone, so it must be reinstalled on new clones and machines. It needs the `pre-commit` tool and its runtime, and it adds latency to every commit. | New hires or fresh clones skip the hook, and adoption decays. Some engineers disable it because commits feel slower. | Add an installation step to onboarding or a bootstrap script. Note that `--no-verify` exists and that CI remains the backstop. |

### What holds up

- **Arithmetic:** 5/20 PRs and 60 total minutes are correct.
- **Failure mode:** "If nobody installs the hook, nothing breaks" is true, because CI remains the enforcement point.
- **Reversibility:** the change is cheap and can be undone by deleting one config block.
- **Low-cost rejection:** rejecting a prose formatting guide as non-mechanical is reasonable.

### Unverified claims

- **"Formatting-only" classification.** It is unknown whether the configured formatter would change the code those comments flagged. To confirm, read the 9 comments and re-run the formatter on the commented revisions.
- **"Round trip still happens."** To confirm, compare comment timestamps against CI completion times for PRs 1, 4, 7, 12 and 17.
- **"Reviewers recorded" minutes.** To confirm, ask how and when the minutes were captured.
- **"About 5 minutes" to install.** To confirm, time a fresh install on a clean machine.

### Questions for the author

1. For the 9 comments, would running the formatter have resolved each one, yes or no?
2. Were those comments posted before CI reported its result?
3. How were the minutes recorded?

### Decision-maker summary

Before adopting anything, spend about 30 minutes classifying the 9 comments. The hook only helps if they concern things the formatter fixes and were posted before CI finished. If they are about style the formatter doesn't enforce, the fix is to extend the formatter or linter config, or to agree a review norm. If you ship the hook anyway, the risk is small (a few minutes per person, easily reversed), but the review noise will likely continue.

```json
{
  "verdict": "REWORK",
  "findings": [
    {
      "severity": "High",
      "evidence_level": "PROBABLE",
      "location": "proposal.md, Alternatives considered: 'the formatting round trip still happens (that is the 5 of 20)'",
      "scenario": "CI already blocks unformatted code, so the format-only review comments are either posted before CI finishes or concern style the formatter does not enforce; in the latter case the hook (same formatter) removes none of them and the success measure fails.",
      "fix": "Classify the 9 comments: would the configured formatter have changed the flagged code, and was the comment posted before CI finished? Recommend the hook only if most are both."
    },
    {
      "severity": "Medium",
      "evidence_level": "PROBABLE",
      "location": "proposal.md, Alternatives considered",
      "scenario": "Cheaper or better-targeted options (review norm: review after green CI and leave formatting to CI; extend formatter/linter config; format-on-save; CI autofix bot; do nothing at ~3 min/PR) were never compared, so the team may adopt a hook when a guideline or config change would remove the comments.",
      "fix": "Compare these options against the classified comments and choose the one matching the actual cause."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "proposal.md, Success measure: 'expected fewer than 2'",
      "scenario": "Unit (comments vs PRs) is ambiguous against a baseline of 9 comments in 5 PRs; n=20 is noisy and hook adoption is not tracked, so the outcome cannot be judged or attributed to the hook.",
      "fix": "State unit and baseline explicitly, record hook install rate, and tag each future comment as formatter-covered or not."
    },
    {
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "location": "proposal.md, Need: 'average of 12 minutes spent on those comments'",
      "scenario": "12 is per affected PR, not per comment (60/9 ≈ 6.7); readers overestimate per-comment cost, and the recording method is unstated.",
      "fix": "Restate as 60 min across 9 comments in 5 PRs and describe how minutes were captured."
    },
    {
      "severity": "Low",
      "evidence_level": "PROBABLE",
      "location": "proposal.md, Proposal: 'install the hook once… about 5 minutes'; Who benefits: 'Nobody has to do anything daily'",
      "scenario": "The hook is per-clone, so new clones and new hires skip it, and some engineers disable it because of commit latency; adoption decays.",
      "fix": "Add installation to onboarding or a bootstrap script; keep CI as the enforcement backstop."
    }
  ]
}
```