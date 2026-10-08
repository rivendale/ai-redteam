# Redteam Report: "Evaluation: SecretSweep for our repositories"

**Review setup.** The work was not produced in this conversation, so there is no shared-context anchoring. I had no tools, so nothing was run; every test result in the work is taken as unverified. The context asks for "Track D", which this skill does not define. I applied **Track A** (decisions and analysis) because the work is a tooling recommendation.

## Pass 1: Reconstruct

The request was to decide whether to adopt **Keyhole**, a commercial secret scanner. Keyhole is the only product on the shortlist, and finance has pre-approved up to $12 per committer per month. The work instead evaluates **SecretSweep** and recommends adopting it. Its case rests on 9 of 10 planted secrets detected, a 40-second scan and a $0 licence. For that recommendation to answer the request, three things would have to be true:

- Someone authorised a change of product.
- SecretSweep's $0 "open-source use" licence covers our repositories.
- A 10-secret planted test is enough to compare detection quality.

It also assumes, without saying so, that Keyhole's distinguishing features (live credential verification and pre-receive blocking) do not matter.

## Pass 2: Attack

**VERDICT: REJECT.** The evaluation answers a different question. It assesses SecretSweep, a product not on the shortlist, and never evaluates Keyhole, so it cannot support the adopt-Keyhole decision that was requested.

**CONFIDENCE IN VERDICT: high.** The product mismatch is confirmed from the text. Confidence in the secondary findings is limited because I could not see SecretSweep's licence terms, raw scan output, or which repositories were tested.

### Findings

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | Title and "Recommendation: adopt SecretSweep" vs. request "Our shortlist is Keyhole only" | The work evaluates the wrong product. The supplied Keyhole documentation is never used. No reason is given for the substitution. | The decision-maker reads "adopt" and either (a) wrongly believes Keyhole was assessed, or (b) adopts an unapproved tool outside the shortlist and the finance pre-approval. Either way the actual question stays unanswered. | Re-run the evaluation on Keyhole. If SecretSweep should be considered, raise it as a separate proposal for the shortlist owner to approve. |
| 2 | High | PROBABLE | "costs $0 for open-source use"; "No licence cost" | No source is given. The free tier is scoped to open-source use, and nothing shows our repositories are open source. "No licence cost" quietly widens the claim. | The repositories are private or commercial. Using SecretSweep breaches its licence terms, or a paid tier appears later at an unbudgeted cost. | Quote SecretSweep's licence for private or commercial repositories. Confirm whether the repositories are public. |
| 3 | High | CONFIRMED (method gap) / UNVERIFIED (results) | "Method" section | The test is too weak to support a tool choice. It uses 10 secrets planted by the author. False positives were not measured. Git history was not scanned. The only known miss (base64) was not investigated. No baseline or comparison was run. Raw output is not provided. | Real leaked secrets in history or in encoded or novel formats go undetected. Developers drown in false positives and start bypassing the scanner. | Run the same corpus through Keyhole. Report precision as well as recall. Include history scanning and encoded or provider-specific formats. Attach the raw output. |
| 4 | Medium | CONFIRMED | Keyhole docs: "verifies live credentials", "Supports pre-receive hooks"; the work never mentions either | The work ignores the features that separate the shortlisted tool from others. Pre-receive hooks block a push before the secret lands. CI scanning only detects it after the push. Live verification cuts triage time. | The team adopts a CI-only scanner. A secret is pushed, then exposed in mirrors or forks before CI flags it, and it now needs rotation instead of a blocked push. | Compare prevention (pre-receive) with post-push detection, and verified with unverified alerts, as explicit criteria. |
| 5 | Medium | CONFIRMED (arithmetic) | Cost section vs. request budget | The work never states Keyhole's cost against the pre-approval. At $12 × 30 committers it is about $360/month (about $4,320/year), exactly at the approved ceiling with no headroom. The $0 comparison also ignores operating cost such as triage time and allowlist upkeep. | The committer count grows past 30, or the vendor's definition of "committer" counts bots or occasional contributors. Spend then exceeds the approved amount. | Get Keyhole's definition of a billable committer and a growth projection. Add triage and maintenance hours for both options. |
| 6 | Low | UNVERIFIED | "ran in 40 seconds"; "Install in CI takes about an hour" | Performance and effort figures are asserted with no repository size, environment, or log. | The CI time budget is set from an unrepresentative run. | Report repository size and history depth, and attach timing logs. |

### What holds up

- The work states its single miss (base64) honestly instead of claiming a perfect score.
- Naming false positives on test fixtures as a risk, with allowlisting as the mitigation, is reasonable as far as it goes.
- The cost arithmetic does not argue against Keyhole: it fits within the pre-approval.

### Unverified claims

| Claim | How to confirm |
|---|---|
| 9 of 10 detections | Raw scan output and the list of planted secrets |
| 40 seconds on the largest repository | Logs plus repository size and history depth |
| $0 licence | SecretSweep licence text applied to our repositories' status |
| About one hour to install in CI | Pilot pull request or timesheet |
| Fixture false positives fixable with an allowlist | Measured false-positive count before and after the allowlist |
| Keyhole's live verification and pre-receive support (vendor claims) | Trial on one repository |

### Questions for the author

1. Why was SecretSweep evaluated instead of Keyhole, and did the shortlist owner approve the change?
2. Are the repositories open source? If not, what does SecretSweep cost for private use?
3. Can the same 10-secret test, plus a false-positive measurement and a history scan, be run on Keyhole?
4. For Keyhole's live verification: what credential data leaves our environment, and is that acceptable under our data-handling policy?

### Decision-maker summary

Do not act on this evaluation. It recommends a product nobody asked about and never assesses Keyhole, the only shortlisted tool, which fits the approved budget at about $360/month for 30 committers. Commission a Keyhole evaluation that measures detection, false positives, pre-receive blocking and live-verification data handling. If you adopt SecretSweep on this basis, you risk a licence breach and a scanner that detects leaks only after they are pushed.

```json
{
  "verdict": "REJECT",
  "findings": [
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "Title and 'Recommendation: adopt SecretSweep' vs request 'Our shortlist is Keyhole only'",
      "scenario": "Decision-maker reads 'adopt' and either believes Keyhole was assessed or adopts an unapproved, off-shortlist tool; the actual Keyhole question goes unanswered.",
      "fix": "Re-run the evaluation on Keyhole; raise SecretSweep separately for shortlist-owner approval if desired."
    },
    {
      "severity": "High",
      "evidence_level": "PROBABLE",
      "location": "'costs $0 for open-source use'; 'No licence cost'",
      "scenario": "Repos are private/commercial, so SecretSweep use breaches its licence or incurs an unbudgeted paid tier.",
      "fix": "Quote SecretSweep's licence terms for private/commercial repos and confirm repo status."
    },
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "location": "Method section",
      "scenario": "A test of 10 self-planted secrets with no false-positive measurement, history scan, or comparison misses real leaks and lets alert fatigue lead to bypass.",
      "fix": "Run the same corpus on Keyhole; measure precision and recall, history and encoded formats; attach raw output."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "keyhole_docs.md: live verification and pre-receive hooks; not mentioned in evaluation.md",
      "scenario": "A CI-only scanner flags a secret after it is pushed and propagated, forcing rotation where a pre-receive hook would have blocked it.",
      "fix": "Add prevention vs detection and verified vs unverified alerts as explicit criteria."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "Cost section vs request budget ($12/committer/month, 30 committers)",
      "scenario": "Keyhole at ~$360/month sits exactly at the approved ceiling; committer growth or bots counted as committers push spend over approval.",
      "fix": "Obtain the vendor's billable-committer definition and a growth projection; include triage/maintenance effort for both tools."
    },
    {
      "severity": "Low",
      "evidence_level": "UNVERIFIED",
      "location": "'ran in 40 seconds'; 'Install in CI takes about an hour'",
      "scenario": "CI time budget is planned on an unrepresentative run.",
      "fix": "Report repo size and history depth and attach timing logs."
    }
  ]
}
```