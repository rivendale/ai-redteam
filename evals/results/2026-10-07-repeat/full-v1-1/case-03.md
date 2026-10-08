# Redteam Report: Onboarding Checklist Retention Analysis

**Review independence:** The work was not produced in this conversation, so there is no inherited authoring context. This session has no tools. I checked arithmetic by hand and reasoned from the two files provided. I could not query any data beyond `cohorts.csv`.

---

**VERDICT: REWORK.** The numbers are correct and the difference is not chance. But the analysis treats a self-selected comparison as a causal effect, and then recommends a different intervention (mandatory) than the one it observed (optional).

**CONFIDENCE IN VERDICT: High.** The core flaw is visible in the work's own description of the design. What limits confidence: I could not see account-level data, segment breakdowns, or any pre-launch baseline. Those could narrow the effect estimate, but they cannot rescue the causal claim.

---

## Pass 1: Reconstruct

The work claims the checklist caused 30-day retention to rise from 40% to 52% (+12pp). It recommends making the checklist mandatory for all new accounts and building copies for two other products. For this to be correct, four things must be true:
1. Completers and non-completers would have retained equally without the checklist.
2. The 40% non-completer rate is a valid "before" baseline.
3. Forcing completion produces the same effect as choosing to complete.
4. The effect transfers to other products.

None of these is tested. Assumption 1 is the one the whole recommendation rests on.

---

## Findings

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | analysis.md: "shown to every new account… as an optional panel" vs. "the checklist raised 30-day retention" | **Self-selection.** Users chose whether to complete the checklist. Users who spend ten minutes on optional setup are already more engaged and more likely to stay. The 12pp gap mixes any checklist effect with who chose to do it. | The true causal effect is 0–3pp and most of the gap is user motivation. The company makes onboarding mandatory for all accounts based on a selection artifact. | Run a randomized holdout (for example, 50% see the panel, 50% don't) and compare retention by **assignment**, not by completion. At minimum, compare completers against non-completers with similar first-day engagement, plan, and acquisition channel. |
| 2 | Critical | CONFIRMED | analysis.md: "Completion takes about ten minutes over the first week" | **Immortal-time / survivorship bias.** A user must stay active through roughly the first week to complete. Anyone who churned on day 1–6 is automatically in "did not complete," which drags that group's retention down by construction. | A user signs up on day 0 and leaves on day 2. They can never be a completer, so they count against "not completed." Even a useless checklist would show a gap. | Condition on users still active at day 7 (the landmark method) and compare day-30 retention only among them. Or measure retention from completion date versus a matched day-7 point. |
| 3 | High | CONFIRMED | Finding line: "raised 30-day retention from 40% to 52%" | **Wrong baseline.** The 40% is the non-completer rate within the same post-launch cohort, not retention before the checklist existed. Overall cohort retention is 2,144/5,000 = 42.9%. No pre-launch cohort is shown, so "raised from 40%" is not a before/after statement. | Pre-launch retention was already about 43%, and overall retention did not move at all. The "raise" is just a split of the same population. | Compare overall 30-day retention for accounts created before launch against June/July 2026, adjusting for seasonality and acquisition mix. |
| 4 | High | PROBABLE | Recommendation: "Make the checklist mandatory" | **Optional is not mandatory.** Even if completion helped volunteers, forcing it on users who skipped it adds friction for the people least inclined to engage. That can raise early drop-off. The data contains no mandatory condition. | A mandatory ten-minute gate causes some first-login users to abandon, and overall retention falls. | Before any rollout, A/B test mandatory against optional against none, with day-1 activation and day-30 retention as outcomes. |
| 5 | High | PROBABLE | Recommendation: "build the same panel for the other two products next quarter" | **Unsupported extrapolation.** One product, two months, an observational design. Nothing shows the effect transfers to products with different users or onboarding needs. | A quarter of engineering effort goes into checklists that do nothing, or hurt, in the other products. | Defer until a causal effect is established in product 1. Then pilot as a randomized test in one other product. |
| 6 | Medium | CONFIRMED (reasoning) / holds numerically | analysis.md: "the groups are large… so it cannot be chance" | **The reasoning is wrong, though the conclusion survives.** Group size alone does not establish significance. A two-proportion test gives pooled p = 0.4288, SE ≈ 0.0164, z ≈ 7.3, so chance is very unlikely. But statistical significance says nothing about causation. The sentence implies "not chance" means "real effect of the checklist." | A reader takes "cannot be chance" as proof of causation and skips findings 1–3. | Report the test and a confidence interval (roughly 12pp ± 3pp). State explicitly that this excludes noise, not confounding. |
| 7 | Medium | UNVERIFIED | evidence/cohorts.csv (aggregate only); definitions absent | **Undefined terms and no segments.** "Completed" (all steps? any?) and "active at day 30" (login? key action?) are undefined. Data is pooled across June and July and across all segments, so mix effects (Simpson's paradox) by channel, plan, or month cannot be ruled out. | Completers are mostly paid or sales-led accounts, which retain better regardless. The aggregate gap reflects that mix. | Provide the definitions and break retention down by month, plan, and acquisition channel, comparing within strata. |
| 8 | Low | PROBABLE | Whole analysis | **Alternatives not considered.** Doing nothing, keeping it optional with stronger nudges, shortening it, or running a test first are never weighed. Only "mandatory everywhere" is offered. | The most expensive and least reversible option gets picked by default. | Add an options comparison that includes "run a two-to-four week randomized test first." |

---

## WHAT HOLDS UP

- **Arithmetic and data fidelity.** The table matches `cohorts.csv` exactly. 624/1,200 = 52.0%, 1,520/3,800 = 40.0%, and the totals sum to 5,000 accounts.
- **The gap is not noise.** z ≈ 7.3, so the difference between groups is real.
- **The date window is adequate.** Accounts created through 31 July 2026 have full day-30 observation by 30 August.
- **The checklist is a reasonable candidate.** The association is consistent with a real effect. It just does not demonstrate one.

## UNVERIFIED CLAIMS

| Claim | How to confirm |
|---|---|
| "The checklist raised 30-day retention" | Randomized holdout comparing users by assignment, or a pre/post comparison of overall cohort retention |
| "From 40%" (as a baseline) | Pull 30-day retention for accounts created before launch |
| Completion takes "about ten minutes over the first week" | Product telemetry: distribution of time-to-complete and elapsed days |
| Mandatory will reproduce the effect | A/B test of mandatory against optional |
| Effect generalizes to other two products | A pilot in one other product |

## QUESTIONS FOR THE AUTHOR

1. Is there 30-day retention for accounts created **before** the checklist launched, and how does it compare with the 42.9% overall for June and July?
2. Among users still active at **day 7**, what is day-30 retention for completers versus non-completers?
3. Was any group of new accounts **not shown** the panel, whether by holdout, platform, or rollout lag?
4. Exactly how are "completed" and "active at day 30" defined?

## DECISION-MAKER SUMMARY

The analysis shows that users who chose to finish the checklist retained better. It does not show that the checklist caused this, and the design (optional, takes a week to finish) would produce a gap like this even if the checklist did nothing. Do not make it mandatory or build it for other products yet. Run a short randomized test (mandatory vs. optional vs. none) first. Proceeding now risks spending a quarter of engineering effort and adding first-login friction for every new account on an effect that may be mostly selection.

```json
{
  "verdict": "REWORK",
  "findings": [
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "analysis.md: 'shown to every new account... as an optional panel' / 'the checklist raised 30-day retention'",
      "scenario": "Completion is self-selected; more engaged users both complete the checklist and retain. True causal effect may be near zero while observed gap is 12pp, leading to a mandatory rollout justified by selection bias.",
      "fix": "Randomized holdout comparing retention by assignment (shown vs not shown), not by completion; at minimum stratify by early engagement, plan, and channel."
    },
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "analysis.md: 'Completion takes about ten minutes over the first week'",
      "scenario": "Users who churn in days 1-6 cannot complete and are all placed in 'did not complete', depressing that group's retention by construction (immortal-time bias); a useless checklist would still show a gap.",
      "fix": "Landmark analysis: restrict to users active at day 7 and compare day-30 retention by completion status."
    },
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "location": "analysis.md Finding: 'raised 30-day retention from 40% to 52%'",
      "scenario": "40% is the non-completer rate in the same post-launch cohort, not a pre-launch baseline; overall cohort retention is 42.9% and may equal pre-launch retention, meaning no aggregate improvement.",
      "fix": "Compare overall 30-day retention of pre-launch cohorts vs June-July 2026 cohorts, adjusting for seasonality and acquisition mix."
    },
    {
      "severity": "High",
      "evidence_level": "PROBABLE",
      "location": "analysis.md Recommendation: 'Make the checklist mandatory'",
      "scenario": "Forcing a ten-minute task on users who would have skipped it adds friction at first login, increasing early abandonment and possibly lowering overall retention; no mandatory condition was observed.",
      "fix": "A/B test mandatory vs optional vs none, measuring day-1 activation and day-30 retention before rollout."
    },
    {
      "severity": "High",
      "evidence_level": "PROBABLE",
      "location": "analysis.md Recommendation: 'build the same panel for the other two products next quarter'",
      "scenario": "Effect from one product, two months, observational data is extrapolated to different products and users; a quarter of engineering is spent on checklists with no or negative effect.",
      "fix": "Defer until a causal effect is shown in product 1, then pilot as a randomized test in one other product."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "analysis.md: 'the groups are large... so it cannot be chance'",
      "scenario": "Group size is not a significance test; the gap is in fact significant (z about 7.3) but readers take 'not chance' as proof of causation and ignore confounding.",
      "fix": "Report a two-proportion test and confidence interval (about 12pp +/- 3pp) and state explicitly that it rules out noise, not confounding."
    },
    {
      "severity": "Medium",
      "evidence_level": "UNVERIFIED",
      "location": "evidence/cohorts.csv (aggregate only); definitions of 'completed' and 'active' absent",
      "scenario": "Completers are concentrated in high-retention segments (paid, sales-led, one month); the aggregate gap reflects mix (Simpson's paradox) rather than the checklist.",
      "fix": "Define 'completed' and 'active at day 30'; break down retention by month, plan, and acquisition channel and compare within strata."
    },
    {
      "severity": "Low",
      "evidence_level": "PROBABLE",
      "location": "analysis.md (whole document)",
      "scenario": "Only 'mandatory everywhere' is offered; cheaper, reversible options (keep optional, nudge, shorten, test first) are never weighed, so the most costly option is chosen by default.",
      "fix": "Add an options comparison including 'run a 2-4 week randomized test first'."
    }
  ]
}
```
