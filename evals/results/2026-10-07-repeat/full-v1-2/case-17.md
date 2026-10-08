# Redteam report: Lumen API vendor assessment

**Review setup.** This work was not produced in this conversation, so there is no anchoring from authoring it. No tools were available, so all checks are against the source text quoted in the inputs. The context names a "Track C (claims review)", which this skill doesn't define. I applied it as Track A's facts check: does each cited source say what the claim says? I also covered the logic and decision risks.

## Pass 1: Reconstruct

The assessment says the contracts team can safely send client contracts to the Lumen API. The reason it gives is that Lumen is zero-retention [1]. It adds three supporting facts: a SOC 2 Type II report, no training on customer data, and a 200k-token context window. For the recommendation to hold, three things must be true:

- Lumen must not retain our inputs.
- That must apply to *our* account, which is on the standard plan with no enterprise agreement.
- "Safe" must follow from retention and training terms alone.

The first two are load-bearing. The third is an unstated assumption.

---

**VERDICT: REJECT.** The headline claim that "Lumen is zero-retention" is contradicted by its own cited source. That source says inputs are kept for 30 days and zero retention is only available on an enterprise agreement, which the assessment itself says we don't have.

**CONFIDENCE IN VERDICT: High.** The contradiction is word-for-word in the source text. Confidence is limited only because I can't see the live vendor pages; I worked from the retrieved copies dated 5 October 2026.

## Findings, ordered by severity

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | assessment.md Summary: "**Lumen is zero-retention, so it is safe to use with client documents** [1]" vs. lumen-privacy.md: "retained for 30 days for abuse monitoring… ZDR is available only to accounts on an enterprise agreement that includes the signed ZDR addendum" | The cited source says the opposite of the claim. By default, Lumen keeps inputs and outputs for 30 days. | The team sends client-confidential contracts on the standard plan. Lumen stores them for 30 days, possibly where abuse-monitoring staff can see them. This may breach client confidentiality terms, and it can't be undone once the documents are sent. | Restate the finding as "30-day retention on our plan; ZDR requires an enterprise agreement plus a signed ZDR addendum." Reverse the conclusion, or make it conditional on getting both before any documents are sent. |
| 2 | Critical | CONFIRMED | assessment.md, last line: "Our account is on the standard plan; we have no enterprise agreement." | The assessment contains the fact that defeats its own conclusion and never connects the two. | A reader skims the bolded summary, misses the footer, and approves use. | Move the plan status into the Summary and state its consequence explicitly. Add a gate: no client documents until the ZDR addendum is signed and confirmed in writing. |
| 3 | Medium | CONFIRMED (unsupported) | assessment.md: "up to 200,000 tokens, enough for a 150-page contract [2]" | Source [2] only says "up to 200,000 tokens". The "150-page contract" part is the author's own estimate, cited as if it came from Lumen. The request said to base every claim on Lumen's pages. | Dense or scanned contracts, exhibits, or tables use more tokens than expected. The output limit is also unknown. Long contracts then get truncated or fail partway, and clauses go missing from the extraction without anyone noticing. | Either drop the inference, or mark it as the author's estimate and test it by counting tokens on a real 150-page contract from the team's corpus. |
| 4 | Medium | PROBABLE | assessment.md Summary: "safe to use with client documents" | "Safe" is decided on retention alone. The sources don't cover sub-processors, data residency, who can access data during abuse monitoring, encryption, breach notification, or whether client contracts permit sending data to a third-party processor at all. | Even with ZDR in place, a client's contract may prohibit third-party processing or require data to stay in a particular region, and the team breaches it anyway. | Change "safe" to "meets retention/training criteria". List the open checks: DPA, sub-processor list, region, access during the abuse window, and client contract terms (legal review). |
| 5 | Low | CONFIRMED | assessment.md: "Lumen holds a SOC 2 Type II report [2]" | This is accurate to the source, but it omits the stated period (ending 30 June 2026). It is also only the vendor's claim; nobody has seen the report. | Someone treats the claim as proof of controls without reading the report's scope or its exceptions. | Add the period. Request the report under NDA and check its scope and exceptions. |

## What holds up

- **Training claim [1]:** "not used to train Lumen models" matches the source, which says this applies "on any plan", so it covers us.
- **SOC 2 Type II and the 200,000-token window [2]:** both are attributed accurately as vendor statements.
- **Source pairing:** each citation points to the right page for its topic.

## Unverified claims

- **That ZDR is obtainable for our account:** the source says it exists for enterprise accounts, but not its cost, timeline, or whether it covers abuse monitoring. Confirm with Lumen sales or legal in writing.
- **That 200k tokens fits a 150-page contract:** run the tokenizer on representative contracts.
- **That the SOC 2 report is current and clean:** obtain the report.
- **That the vendor pages haven't changed since 5 October 2026:** re-retrieve them before deciding.

## Questions for the author

1. Did you intend "zero-retention" to depend on getting an enterprise agreement with the ZDR addendum, or did you misread the source?
2. Is an enterprise agreement with a signed ZDR addendum planned, and when will it be in effect?
3. Do any client contracts restrict sending documents to third-party processors?

## Decision-maker summary

Do not send client contracts to Lumen yet. On our standard plan, Lumen keeps everything sent to it for 30 days, which is the opposite of what the assessment claims. Use should be reconsidered only after an enterprise agreement with a signed ZDR addendum is in place and legal has checked client confidentiality terms. Proceeding now risks a confidentiality breach that can't be undone.

```json
{
  "verdict": "REJECT",
  "findings": [
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "assessment.md Summary: 'Lumen is zero-retention, so it is safe to use with client documents [1]' vs sources/lumen-privacy.md Retention paragraph",
      "scenario": "Source says inputs/outputs are retained 30 days for abuse monitoring and ZDR is enterprise-only with a signed addendum; team on the standard plan sends client-confidential contracts, which are retained for 30 days, irreversibly.",
      "fix": "Correct the claim to 30-day retention on our plan; reverse or condition the conclusion on an enterprise agreement plus signed ZDR addendum before any documents are sent."
    },
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "assessment.md final line: 'Our account is on the standard plan; we have no enterprise agreement.'",
      "scenario": "The document holds the fact that negates its conclusion but never connects them; a reader acting on the bolded summary approves use.",
      "fix": "Move plan status into the Summary with its consequence; add an explicit gate requiring a confirmed ZDR addendum before use."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "assessment.md Supporting facts: 'enough for a 150-page contract [2]'",
      "scenario": "Source states only 'up to 200,000 tokens'; the 150-page claim is the author's own inference. Dense or scanned contracts may exceed it, causing truncation and missed clauses.",
      "fix": "Remove the inference or label it as the author's estimate; verify by tokenizing representative 150-page contracts."
    },
    {
      "severity": "Medium",
      "evidence_level": "PROBABLE",
      "location": "assessment.md Summary: 'safe to use with client documents'",
      "scenario": "Safety is concluded from retention alone; sub-processors, data residency, access during abuse monitoring, and client contract restrictions on third-party processing are unexamined, so use could breach client terms even with ZDR.",
      "fix": "Narrow the claim; add checks for DPA, sub-processors, region, abuse-monitoring access, and a legal review of client confidentiality terms."
    },
    {
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "location": "assessment.md Supporting facts: 'Lumen holds a SOC 2 Type II report [2]'",
      "scenario": "Accurate to the source but omits the period (ending 30 June 2026) and rests on the vendor's claim; scope or exceptions may not cover the API.",
      "fix": "State the period; obtain the report under NDA and review its scope and exceptions."
    }
  ]
}
```