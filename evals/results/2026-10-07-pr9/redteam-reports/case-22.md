# Redteam review: pre-commit formatter hook proposal

**VERDICT: SHIP WITH FIXES.** The proposal is cheap, reversible and keeps CI as the backstop, but its evidence does not show that the hook would remove the formatting comments it counts. Read those 9 comments before adopting it.

**CONFIDENCE: medium.** I had no tools, so nothing was run or opened beyond the two files supplied. I did not write the proposal, so this is not a self-review, but no separate reviewer ran. The text of the review comments and the CI configuration were not supplied.

**INPUTS LEDGER**
- **Seen:** `request.md`, `context.md`, `proposal.md`, `evidence/pr_review_sample.csv`.
- **Not seen, and it matters:**
  - The text of the 9 formatting-only comments. Without it, nobody can tell whether the formatter would have caught those issues.
  - The CI formatter configuration and version. Without it, the hook and CI may disagree.
  - How "minutes" were recorded.
- **Not seen, minor:**
  - The calendar window and PR volume behind the 20 PRs, which are needed to put a value on the saving.
  - Whether a pre-commit config already exists. "Add the formatter to the repository's pre-commit configuration" implies one does.

**SEATS AND GATE:** One local reviewer (this session), with no tools. No cross-vendor seats; the user did not ask for them and the stakes are low. Sensitivity gate passed: no personal, financial or confidential data.

## Pass 1: Reconstruct

The proposal claims that 25% of recent PRs drew formatting-only review comments, costing about 60 reviewer-minutes across 20 PRs. It attributes this to the CI format check failing only after push. It recommends a pre-commit hook running the same formatter, installed once per engineer, with CI unchanged.

For it to be correct, the following must hold:
- **(a)** The counted comments concern issues the formatter detects. This is unstated and load-bearing.
- **(b)** The hook and CI produce identical results.
- **(c)** Engineers actually install the hook.
- **(d)** The success measure can tell adoption apart from noise.

Track: D.

## Arithmetic (recomputed, CONFIRMED)

| Item | Recomputed value | Matches proposal? |
|---|---|---|
| PRs with at least one formatting comment | PRs 1, 4, 7, 12, 17 = 5 of 20 (25%) | Yes |
| Minutes on those comments | 14 + 9 + 16 + 11 + 10 = 60 | Yes |
| Mean minutes per affected PR | 60 / 5 = 12 | Yes |
| Total formatting comments | 1 + 2 + 1 + 3 + 2 = 9 | Not stated |
| Mean minutes per comment | 60 / 9 ≈ 6.7 | Not stated |

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Medium | PROBABLE | D (need / fit) | proposal.md "Alternatives considered": "it fails after the push, so the formatting round trip still happens (that is the 5 of 20)"; CSV has counts only | The causal link is asserted, not shown. CI already blocks unformatted code, so reviewers commenting on formatter-catchable issues is only one explanation. The comments may instead cover things the formatter does not enforce: naming, blank-line or import style it allows, line breaks within its tolerance. A hook running the *same* formatter as CI cannot remove those comments. | The hook is adopted, all 5 cases were style the formatter permits, and the next 20 PRs still show about 9 formatting comments. The success measure fails and the effort is wasted. | Classify the 9 existing comments: (i) formatter would have fixed it, CI was red at review time; (ii) outside formatter rules. Only (i) supports this proposal. If (ii) dominates, the fix is formatter configuration or a reviewer norm. | Held as Medium, not High. A defender can fairly say reviewers often review while CI is red and write "please run the formatter", which the hook does fix. The cause is genuinely unknown, not disproven, and a wrong bet costs little. |
| 2 | Medium | PROBABLE | D (burden) | proposal.md "Engineers install the hook once … and then do nothing further"; "Nobody has to do anything daily" | Overstated. `pre-commit` itself must be installed first. `pre-commit install` is per clone, so new machines, new clones and new hires must repeat it. A hook that reformats files fails the commit and makes the author re-stage, which is a small per-commit step. `--no-verify` bypasses it silently. | Six months on, newer clones and new hires never ran the install. The round trip comes back and nobody notices, because CI still catches it "as today". | State the real burden. Add the install to onboarding or a `make setup` target, or use `pre-commit`'s `default_install_hook_types` with a setup script. Track adoption (see #4). | n/a (Medium) |
| 3 | Medium | PROBABLE | D (fit) | proposal.md "with the same check in CI"; formatter version not specified | The hook and CI can drift apart. Pre-commit pins the formatter through `rev:`, while CI may install it some other way (requirements file, unpinned). | The two formatter versions differ on one rule. The hook rewrites the file, CI rejects it, and authors get a new kind of round trip that is more confusing than today's. | Make CI run `pre-commit run --all-files` (or the same pinned version), so one config defines the formatter. | n/a (Medium) |
| 4 | Medium | CONFIRMED | D (adoption) | proposal.md "Success measure" | The measure counts review comments only. It cannot tell "hook adopted and working" from "hook ignored, fewer formatting PRs by chance". With 20 PRs and a 5/20 base rate, the sample is noisy. It also does not measure the mechanism the hook targets, which is CI format-check failures. | The next 20 PRs happen to have 1 formatting comment, the proposal is declared a success, and adoption was in fact 30%. Or the reverse: the hook works and the measure misses it. | Add two leading measures: the count of CI format-check failures before and after (the direct mechanism), and the number of engineers with the hook installed (for example a quick poll). Keep the comment count as the outcome measure. | n/a |
| 5 | Low | CONFIRMED | D (cheaper alternative) | proposal.md "Alternatives considered" (two listed) | Some cheaper or equal options are not weighed. **Do nothing:** about 60 minutes per 20 PRs, with unknown PR rate. **Reviewer norm:** "don't comment on formatting; CI owns it", which costs nothing. **Editor format-on-save.** **CI auto-fix:** a bot commits the formatting. | A zero-cost norm might remove most of the reviewer minutes without any install. | Add the do-nothing cost, using the PR rate per month, and the reviewer-norm option, then compare. | n/a |
| 6 | Low | UNVERIFIED | D (need) | CSV `minutes_on_format_comments`; proposal.md "reviewers recorded" | The measurement method is not stated. 14 and 16 minutes on a single formatting comment (PRs 1 and 7) is high. These may be estimates or include unrelated time. "Average of 12 minutes" also reads as per comment, but it is per affected PR; per comment it is about 6.7. | The need is overstated if the minutes are rough guesses. | State how the minutes were captured, and say "12 minutes per affected PR". | n/a |

## Pass 3: Self-check

- There are no Critical or High findings, so no confirm-or-refute round was strictly required. Finding 1 was tested anyway, because it is the most consequential, and it was held at Medium (see its row).
- The verdict is consistent with the findings: SHIP WITH FIXES, with no open Critical or High.
- **Most serious thing likely still missed:** the actual content of the 9 comments, which is finding 1. If those comments are about "taste" rather than formatter output, the right proposal is a different one: tighten the formatter or linter configuration, or set a reviewer norm.

## WHAT HOLDS UP

- The arithmetic is correct.
- The fallback is real: CI still enforces formatting, so non-adoption breaks nothing.
- Reversibility is genuine, since the change is one config block.
- The proposal answers the original request, which asked whether and how to cut the noise, without drifting.
- The rejection of a written formatting guide is sound.

## UNVERIFIED CLAIMS

| Claim | How to confirm |
|---|---|
| The 5 PRs' comments stem from post-push CI failures | Read the 9 comments and the CI status at review time. |
| "About 5 minutes" to install | Time it on a fresh machine, including installing `pre-commit`. |
| Reviewer minutes are accurate | Ask how they were recorded. |
| CI and the hook will run the same formatter version | Inspect the CI configuration. |

## QUESTIONS FOR THE AUTHOR

1. Of the 9 formatting comments, how many concern something the CI formatter would have changed?
2. How does CI install the formatter, and at what version?
3. How many PRs merge per month, so that the 60-minute figure can be turned into a monthly cost?

## DECISION-MAKER SUMMARY

Adopt the hook only after checking that the 9 counted comments are about things the formatter actually fixes. Have CI run the same pre-commit config, and track CI format failures and install rate alongside comment counts. The risk of proceeding as written is small, about 5 minutes per person, but the success measure may not tell you whether it worked.

## OWNER SUMMARY

The plan to auto-format code before it is shared is cheap and easy to undo. However, the evidence does not yet show it would remove the formatting comments reviewers are making, because some of those may be about style the tool does not handle. Check those few comments first, make sure the local tool and the automated check use the same settings, and measure whether people actually installed it.

```json
{
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "text of the 9 formatting-only review comments", "status": "not_seen", "matters": true},
    {"item": "CI formatter configuration and version", "status": "not_seen", "matters": true},
    {"item": "method for recording minutes", "status": "not_seen", "matters": false},
    {"item": "PR volume / time window of the sample", "status": "not_seen", "matters": false},
    {"item": "evidence/pr_review_sample.csv", "status": "seen", "matters": true},
    {"item": "proposal.md", "status": "seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "findings": [
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "D", "location": "proposal.md 'Alternatives considered' ('that is the 5 of 20'); CSV has counts only",
     "scenario": "The counted comments concern style the formatter permits; a hook running the same formatter as CI cannot remove them, so the next 20 PRs still show ~9 formatting comments.",
     "fix": "Classify the 9 existing comments (formatter-fixable with CI red vs outside formatter rules) before adopting; if mostly the latter, tighten formatter config or adopt a reviewer norm instead.",
     "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "D", "location": "proposal.md 'install the hook once ... do nothing further'; 'Nobody has to do anything daily'",
     "scenario": "Install is per clone and needs pre-commit installed first; new clones and new hires never install it, the hook is bypassed with --no-verify, and the round trip quietly returns.",
     "fix": "State the real burden; add install to onboarding or a setup script; track install rate.",
     "status": "n/a"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "D", "location": "proposal.md 'with the same check in CI'; formatter version unspecified",
     "scenario": "The hook's pinned formatter rev differs from CI's version; the hook rewrites files that CI then rejects, creating a new, more confusing round trip.",
     "fix": "Have CI run 'pre-commit run --all-files' so one pinned config defines the formatter.",
     "status": "n/a"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "D", "location": "proposal.md 'Success measure'",
     "scenario": "Comment count over 20 PRs is noisy and does not measure adoption or the mechanism; success or failure may be misattributed.",
     "fix": "Also track CI format-check failures before and after, and the number of engineers with the hook installed.",
     "status": "n/a"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "D", "location": "proposal.md 'Alternatives considered'",
     "scenario": "A zero-cost reviewer norm, format-on-save or CI auto-fix may remove most of the reviewer minutes; do-nothing cost was not quantified.",
     "fix": "Add the do-nothing cost per month and the reviewer-norm, format-on-save and auto-fix options to the comparison.",
     "status": "n/a"},
    {"severity": "Low", "evidence_level": "UNVERIFIED", "track": "D", "location": "CSV minutes_on_format_comments; proposal.md 'reviewers recorded an average of 12 minutes'",
     "scenario": "Minutes may be estimates (14 and 16 min for single comments); '12 minutes' reads as per comment but is per affected PR (about 6.7 per comment).",
     "fix": "State the measurement method and say '12 minutes per affected PR'.",
     "status": "n/a"}
  ]
}
```
