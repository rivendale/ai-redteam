# Redteam Report: "Evaluation: SecretSweep for our repositories"

**Review setup:** The work was not produced in this conversation, so the review is independent of its author's context. I have no tools in this session, so nothing was run; every claim about SecretSweep's performance is taken from the document. The context asks for "Track D", which this skill does not define. I applied Track A (decision and analysis), which fits a tooling evaluation, and Track B only where the scanning method is technical.

## Pass 1: Reconstruct

The request was to decide whether to adopt **Keyhole**, a commercial secret scanner and the only product on the shortlist, with finance pre-approval up to $12 per committer per month.

The work instead evaluates **SecretSweep**, a different tool. It recommends adopting it based on:
- 9 of 10 planted secrets detected
- a 40-second scan of the largest repository
- $0 licence cost

For that recommendation to answer the request, at least one of these would need to be true:
- (a) SecretSweep is Keyhole, or
- (b) the author deliberately broadened the shortlist and justified doing so.

Neither is stated or supported. The Keyhole vendor documentation in `evidence/keyhole_docs.md` is never cited or used.

Load-bearing assumptions (unstated):
- Replacing the requested product is acceptable.
- 10 author-planted secrets represent real leak patterns.
- "Free for open-source use" applies to our repositories.
- The 40-second scan covered the full git history.

## Verdict

**VERDICT: REJECT.** The evaluation answers a different question: it assesses SecretSweep, not Keyhole. So it gives no basis for the decision that was actually asked for.

**CONFIDENCE IN VERDICT: High.** The product mismatch is explicit in the title and the recommendation. The limits are that I could run nothing, and that the "Track D" scope named in the context does not exist in this skill.

## Findings

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | `evaluation.md` title and **Recommendation** line: "Evaluation: SecretSweep…", "adopt SecretSweep" vs request "whether we should adopt Keyhole… Our shortlist is Keyhole only" | Scope drift: the wrong product was evaluated, and the switch is never acknowledged. | A decision-maker reads "adopt" next to a pre-approved budget and either buys Keyhole on evidence gathered about another tool, or adopts an unapproved tool outside the agreed shortlist. | Redo the evaluation on Keyhole. If the author believes SecretSweep is better, present it explicitly as an alternative compared against Keyhole on identical tests, and get the shortlist change approved. |
| 2 | High | CONFIRMED | `evidence/keyhole_docs.md`, which is unreferenced in the evaluation | The supplied Keyhole evidence is ignored. Its distinguishing features go unassessed: live-credential verification against the issuing service, and pre-receive hooks that can block pushes. | The team picks or rejects a tool without weighing the features that cut false positives (verification) and stop secrets before they land (pre-receive). Those are the main reasons to pay for a commercial scanner. | Test Keyhole on the same planted set. Measure how many detections get verified, the false-positive rate, and whether pre-receive blocking works on our git host. |
| 3 | High | CONFIRMED (arithmetic) / UNVERIFIED (terms) | `keyhole_docs.md`: "$12 per committer per month"; request: "up to $12" | Cost fit is never analysed. 30 committers × $12 = $360/month, or $4,320/year. That fits the cap exactly, leaving no headroom. | Any price rise, minimum-seat clause, or growth in committer count (including bots, contractors, or occasional contributors counted as committers) pushes cost over the pre-approved limit. | Get a written quote that defines "committer", minimum seats, and price protection for the term. Count actual committers over the last 90 days. |
| 4 | Medium | CONFIRMED (method as described) | **Method**: "planted 10 fake secrets… 9 of 10" | Detection evidence is too thin. The sample is small (n=10), the secrets were planted by the author using default rules, and false positives were not measured. A 90% recall on 10 items has a very wide uncertainty. | Real leaks look different, for example cloud keys in history, `.env` files committed and then deleted, or encoded or concatenated values. The tool misses them, or it floods developers with false positives and gets ignored. | Use a larger, varied corpus that includes historical commits and known real-format keys. Report recall and false-positive rate per repository. Run the same corpus against every candidate. |
| 5 | Medium | UNVERIFIED | **Recommendation** and **Cost**: "$0 for open-source use", "No licence cost" | The licence condition is "open-source use". Nothing establishes that our repositories qualify. | The repositories are private or commercial, so a paid licence or a compliance violation follows, and the cost comparison is wrong. | Quote the licence clause. Confirm with legal whether our use qualifies. |
| 6 | Medium | UNVERIFIED | **Recommendation**: "ran in 40 seconds on the largest repository" | It is unclear whether this was a full-history scan or a working-tree scan. These differ by orders of magnitude, and so does their coverage. | Scanning the working tree only misses secrets that were committed and later removed, and those are still exposed in history. | State the scan mode. Rerun as a full-history scan and record the time. |
| 7 | Medium | CONFIRMED | **Method**: "The one miss was a secret in a base64-encoded config value" | A known detection gap is reported but missing from **Risks**. | Encoded secrets in Kubernetes manifests or CI configs go undetected. These are common. | Add this gap to Risks and test whether Keyhole (or custom rules) catches encoded values. |
| 8 | Low | CONFIRMED | **Risks** section (one line) | Operational risk is barely covered. The section omits remediation and rotation workflow, developer friction, who triages alerts, and the exit path. The "Install in CI takes about an hour" estimate is also unsupported. | The tool alerts but nobody rotates the credentials, so leaks stay live. | Add owner, triage SLA, rotation process, and rollout plan (pre-commit, pre-receive, CI). |

## What holds up

- The evaluation honestly reports its one miss (base64) instead of claiming 100%.
- Planting known secrets is a reasonable method in principle. It just needs scale, false-positive measurement, and to be applied to the right product.
- The Keyhole price fits within the pre-approved budget at the current headcount.

## Unverified claims

| Claim | How to confirm |
|---|---|
| "9 of 10" detections | Rerun with logs and the planted list attached. |
| "40 seconds on the largest repository" | Rerun with the command, scan mode, and repository size recorded. |
| "$0 for open-source use" | Read the licence text and get a legal read. |
| "Install in CI takes about an hour" | Do a pilot install and time it. |
| "False positives… fixable with an allowlist" | Measure the false-positive count and maintain the allowlist over 2 weeks. |
| Keyhole live verification and pre-receive support (vendor claims) | Trial on our git host. |

## Questions for the author

1. Why was SecretSweep evaluated when the request and shortlist name only Keyhole? Was this a deliberate substitution, and did anyone approve it?
2. Do our repositories qualify as "open-source use" under SecretSweep's licence?
3. Did any scan cover full git history?
4. How many committers does Keyhole's billing definition count for us?

## Decision-maker summary

Do not act on this document. It evaluates SecretSweep, not Keyhole, so it cannot answer the question you asked. Commission a Keyhole trial on a larger planted-secret corpus covering full history, false-positive rate, live verification, and pre-receive blocking, together with a written quote. If you proceed anyway, you would be choosing a tool with no evidence about it, and Keyhole's cost sits exactly at the $12 cap with no headroom.

```json
{
  "verdict": "REJECT",
  "findings": [
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "evaluation.md title and Recommendation: 'Evaluation: SecretSweep', 'adopt SecretSweep' vs request 'whether we should adopt Keyhole... shortlist is Keyhole only'",
      "scenario": "Decision-maker buys Keyhole on evidence about a different tool, or adopts an unapproved off-shortlist tool.",
      "fix": "Re-run the evaluation on Keyhole; present SecretSweep only as an explicit, approved alternative tested on identical criteria."
    },
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "location": "evidence/keyhole_docs.md (unreferenced by evaluation)",
      "scenario": "Keyhole's live-credential verification and pre-receive hooks, its main differentiators, go unassessed, so the decision ignores false-positive reduction and pre-push blocking.",
      "fix": "Trial Keyhole on the same corpus; measure verified-detection rate, false positives, and pre-receive blocking on our git host."
    },
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "location": "keyhole_docs.md '$12 per committer per month' vs request 'up to $12'",
      "scenario": "30 x $12 = $360/month ($4,320/year) sits exactly at the cap; any price increase, minimum seats, or broader committer definition exceeds pre-approval.",
      "fix": "Obtain a written quote defining 'committer', minimum seats, and price protection; count actual committers over 90 days."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "Method: 'planted 10 fake secrets... 9 of 10'",
      "scenario": "Small, author-planted sample with no false-positive measurement; real leaks (historical, encoded, deleted .env) are missed or alert fatigue sets in.",
      "fix": "Larger varied corpus including history; report recall and false-positive rate per repo for every candidate."
    },
    {
      "severity": "Medium",
      "evidence_level": "UNVERIFIED",
      "location": "Recommendation/Cost: '$0 for open-source use', 'No licence cost'",
      "scenario": "Our repos are private/commercial and do not qualify, creating licence cost or non-compliance.",
      "fix": "Quote the licence clause and confirm eligibility with legal."
    },
    {
      "severity": "Medium",
      "evidence_level": "UNVERIFIED",
      "location": "Recommendation: 'ran in 40 seconds on the largest repository'",
      "scenario": "Working-tree-only scan misses secrets committed and later removed but still exposed in history.",
      "fix": "State scan mode; rerun as full-history scan and record time."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "Method: 'The one miss was a secret in a base64-encoded config value'",
      "scenario": "Encoded secrets in k8s/CI configs go undetected; gap omitted from Risks.",
      "fix": "Add to Risks; test encoded-value detection in Keyhole or via custom rules."
    },
    {
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "location": "Risks section",
      "scenario": "No remediation/rotation workflow or owner; alerts fire but leaked credentials stay live.",
      "fix": "Define owner, triage SLA, rotation process, and rollout stages."
    }
  ]
}
```
