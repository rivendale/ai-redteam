# Redteam Report: Keyhole Adoption Evaluation

**Review setup:** The work under review was not produced in this conversation, so I reviewed it directly without delegating to a subagent. I have no tools in this session, so nothing could be run, opened, or checked against external sources. The context asks for "Track D", which this skill does not define. Because the work is a tooling recommendation, I applied **Track A (decisions, analysis, recommendations)**.

---

**VERDICT: REJECT.** The evaluation answers a different question. It assesses SecretSweep, but the request was whether to adopt Keyhole, the only shortlisted tool, and it contains no assessment of Keyhole at all.

**CONFIDENCE IN VERDICT: high.** The core defect is visible in the text itself. Confidence in the secondary findings is limited because I had no tools: the SecretSweep test results and licence terms could not be checked, and the Keyhole evidence is a three-line vendor extract.

## Pass 1: Reconstruct

The request asks for a decision on adopting Keyhole. Keyhole is a commercial scanner at $12 per committer per month, which is exactly the ceiling finance pre-approved. The evaluation instead recommends SecretSweep. It cites 9 of 10 planted secrets detected, a 40-second scan of the largest repository, and $0 cost "for open-source use."

For the evaluation to be a valid answer, several things would have to be true:
- (a) Replacing the shortlist was in scope.
- (b) SecretSweep's free licence covers our repositories.
- (c) A 10-secret planted test is a sufficient basis for a tooling decision.
- (d) Keyhole offers nothing material that SecretSweep lacks.

None of these is established. The first contradicts the request directly.

## Findings

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | evaluation.md title and "Recommendation"; request.md "Our shortlist is Keyhole only" | The evaluation is about SecretSweep. Keyhole is never tested, discussed, or scored. This is drift to a different question. | The decision-maker reads "adopt" and either approves a tool nobody asked about, or believes Keyhole was evaluated when it was not. The Keyhole decision stays unmade. | Re-run the evaluation on Keyhole, ideally with the same planted-secret method. If SecretSweep is offered as an alternative, label it explicitly as an out-of-shortlist comparison and get agreement to widen the scope. |
| 2 | High | CONFIRMED (claim wording); UNVERIFIED (licence terms) | "costs $0 for open-source use"; "No licence cost" | Free use is conditioned on open-source use, yet "No licence cost" drops the condition. Nothing says whether our repositories are open source or whether internal or commercial use is covered. | If the repositories are private or commercial, the tool may require a paid licence, or adopting it may breach the licence terms. The cost basis of the recommendation then collapses. | Quote SecretSweep's actual licence and pricing page. State whether our repositories qualify. Get legal or procurement sign-off. |
| 3 | High | CONFIRMED | evaluation.md "Method"; keyhole_docs.md | The evaluation never weighs the capabilities the vendor documents for Keyhole: live-credential verification and pre-receive hooks. A pre-receive hook blocks the secret at push time. A CI-only scan detects it after the secret has already reached the remote. | SecretSweep is adopted as a CI step. A secret is pushed and lands in the remote and its forks before CI flags it. The credential must then be rotated, which Keyhole's pre-receive hook could have prevented. Without verification, triage cannot separate live secrets from dead ones. | Compare the two on push-time blocking versus post-push detection, and on verified versus unverified alerts. Test whether Keyhole's pre-receive hooks work on our Git hosting. |
| 4 | Medium | CONFIRMED | "Method" | The test basis is thin. It uses 10 secrets and reports no false-positive rate, even though false positives are named as the main risk. It does not say whether git history was scanned or which secret types were planted. The one known miss, a base64-encoded value, is a realistic pattern. | The tool goes live and either misses encoded or uncommon secret types, or floods the team with fixture alerts. Either way, the team learns to ignore the scanner. | Plant a larger and more varied set covering encodings, multiline keys, and history-only secrets. Measure precision on clean repositories. Run the identical set against Keyhole. |
| 5 | Medium | PROBABLE | keyhole_docs.md "$12 per committer per month"; request.md "up to $12" | The vendor list price equals the pre-approved cap with zero headroom. Neither document addresses tax, minimum seat counts, tier pricing, or how "committer" is counted (for example, bots and contractors). The Keyhole cost was never checked against the budget. | Committers are counted as 30 plus bots or occasional contributors, or tax or tier surcharges apply. Spend then exceeds the approval, and finance re-approval delays rollout. | Get a written quote for about 30 committers. Confirm the counting rules and total cost, at roughly $360/month or $4,320/year at list price. |
| 6 | Medium | UNVERIFIED | keyhole_docs.md "verifies live credentials against the issuing service" | Live verification means Keyhole uses or transmits discovered secrets, and the data flow is undocumented. This is a security and compliance question the Keyhole evaluation must answer. | Keyhole sends found credentials to the vendor's cloud or exercises them in ways that trip provider alarms or breach policy. | Ask the vendor for its data-flow and processing documentation. Confirm whether verification can run on-premises or be disabled. Check this against internal policy. |
| 7 | Low | UNVERIFIED | "ran in 40 seconds"; "Install in CI takes about an hour" | These are assertions without supporting detail. There is no repository size, no hardware or environment description, and no definition of what the hour includes (allowlists, alert routing, rollout to 5+ repositories). | Effort is underestimated, especially once allowlist tuning across repositories and remediation workflow are included. | Record repository size, the environment, and timing. Scope effort to include tuning, alert ownership, and secret rotation procedure. |

## What holds up

- The planted-secret method is a reasonable approach in principle, and it could be reused directly for Keyhole.
- The evaluation reports its miss (base64) honestly instead of claiming a perfect score.
- Identifying false positives on fixtures as a risk, with allowlisting as mitigation, is sound.

## Unverified claims

- **9 of 10 detections and the 40-second runtime:** confirm by re-running with logs and the list of planted secrets.
- **SecretSweep "$0 for open-source use":** confirm against the actual licence text.
- **Install takes about an hour:** confirm against a timed install plus the tuning effort.
- **Keyhole verifies live credentials and supports pre-receive hooks:** these are vendor claims only. Confirm with a trial on our hosting.
- **Keyhole costs $12 per committer per month:** confirm with a written quote that includes counting rules and tax.

## Questions for the author

1. Why was SecretSweep evaluated when the shortlist was Keyhole only? Was the scope change authorized?
2. Are the repositories open source, and does SecretSweep's free licence cover our use?
3. Do we need push-time blocking via pre-receive hooks, or is post-push CI detection acceptable?
4. Is a Keyhole trial available so the same 10-secret test can be run on it?

## Decision-maker summary

Do not act on this evaluation. It recommends a tool that was not on the shortlist and says nothing about Keyhole, which is what was asked. Commission a Keyhole evaluation using the same test method, plus a written quote and a review of how Keyhole handles the credentials it verifies. If you adopt SecretSweep anyway, you risk licence non-compliance and you lose push-time blocking, based on a 10-sample test with no false-positive measurement.

```json
{
  "verdict": "REJECT",
  "findings": [
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "evaluation.md title and Recommendation; request.md 'Our shortlist is Keyhole only'",
      "scenario": "Evaluation assesses SecretSweep instead of Keyhole; decision-maker approves an unrequested tool or believes Keyhole was evaluated when it was not.",
      "fix": "Re-run the evaluation on Keyhole with the same planted-secret method; label any SecretSweep comparison as out-of-shortlist and get agreement to widen scope."
    },
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "location": "evaluation.md Recommendation '$0 for open-source use' and Cost 'No licence cost'",
      "scenario": "Free tier is conditioned on open-source use; if repos are private or commercial, a paid licence may be required or use may breach the licence.",
      "fix": "Quote SecretSweep licence terms, confirm whether our repositories qualify, and obtain legal or procurement sign-off."
    },
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "location": "evaluation.md Method; keyhole_docs.md (live verification, pre-receive hooks)",
      "scenario": "CI-only scanning detects secrets after they reach the remote, forcing rotation that pre-receive blocking would have prevented; unverified alerts slow triage.",
      "fix": "Compare push-time blocking and live verification explicitly; trial Keyhole pre-receive hooks on our Git hosting."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "evaluation.md Method",
      "scenario": "10-secret sample with no false-positive rate, no history scan, and a known base64 miss; in production, encoded secrets are missed or alert fatigue sets in.",
      "fix": "Use a larger, varied planted set including history-only and encoded secrets, measure precision on clean repos, and run the same set on Keyhole."
    },
    {
      "severity": "Medium",
      "evidence_level": "PROBABLE",
      "location": "keyhole_docs.md '$12 per committer per month'; request.md 'up to $12'",
      "scenario": "Price equals the cap with zero headroom; bots, contractors, tax, or seat minimums push spend over the approval and delay rollout.",
      "fix": "Get a written quote for about 30 committers with counting rules and total cost (about $4,320 per year at list price)."
    },
    {
      "severity": "Medium",
      "evidence_level": "UNVERIFIED",
      "location": "keyhole_docs.md 'verifies live credentials against the issuing service'",
      "scenario": "Discovered credentials are transmitted to the vendor or exercised against providers, breaching policy or triggering provider alarms.",
      "fix": "Obtain vendor data-flow documentation; confirm whether verification can run on-premises or be disabled; review against internal policy."
    },
    {
      "severity": "Low",
      "evidence_level": "UNVERIFIED",
      "location": "evaluation.md 'ran in 40 seconds'; 'Install in CI takes about an hour'",
      "scenario": "Performance and effort figures lack repository size, environment, and tuning scope; rollout effort is underestimated.",
      "fix": "Record repository size, environment, and timing; scope effort to include allowlist tuning, alert ownership, and rotation procedure."
    }
  ]
}
```