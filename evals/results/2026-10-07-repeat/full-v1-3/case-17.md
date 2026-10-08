# Redteam Review: Lumen API vendor assessment

**Review independence:** The work was not produced in this conversation, so this is not a same-context review. I had no tools. All checks compare the assessment against the source text supplied inline. I could not confirm that those files match Lumen's live pages.

## Pass 1: Reconstruct

The assessment says the contracts team can safely send client contracts to the Lumen API because Lumen is "zero-retention." It supports this with three facts: Lumen has a SOC 2 Type II report, it does not train on inputs or outputs, and it has a 200,000-token context window. For the recommendation to hold, all of these must be true:

1. Lumen does not retain this account's inputs.
2. The cited pages say what is attributed to them.
3. "Zero-retention" is enough to make client-confidential use "safe."

The assessment's own last line ("standard plan; we have no enterprise agreement") decides assumption 1.

## Pass 2: Attack (claims review)

| Claim in assessment | Cited source says | Holds? |
|---|---|---|
| "Lumen is zero-retention, so it is safe to use with client documents" [1] | "retained for 30 days for abuse monitoring… ZDR is available only to accounts on an enterprise agreement that includes the signed ZDR addendum" | **No.** The source contradicts it. |
| SOC 2 Type II report [2] | "Lumen holds a SOC 2 Type II report (period ending 30 June 2026)" | Yes, as a vendor statement |
| Not used for training [1] | "not used to train Lumen models on any plan" | Yes |
| 200,000 tokens [2] | "context window of up to 200,000 tokens" | Yes |
| "enough for a 150-page contract" [2] | Not stated | **No.** This is the author's inference, cited as if Lumen said it. |

---

**VERDICT: REJECT.** The headline conclusion is the opposite of what the cited source says. On the standard plan, inputs are retained for 30 days, so the "safe" recommendation has no basis.

**CONFIDENCE IN VERDICT: high.** The contradiction is direct, quoted text against quoted text, and the assessment itself states the plan. The main limit is that I could not check the live vendor pages or the actual account terms.

## FINDINGS, ordered by severity

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | Summary: "Lumen is zero-retention, so it is safe to use with client documents [1]" | Source [1] says inputs and outputs are kept for 30 days. ZDR exists only under an enterprise agreement with a signed ZDR addendum. The assessment itself says "Our account is on the standard plan; we have no enterprise agreement." The claim misrepresents its own citation and contradicts the document's last line. | The team sends client contracts relying on this. Every contract is held by Lumen for 30 days for abuse monitoring, which may breach client confidentiality terms. Once sent, this cannot be undone. | Change the conclusion to: "On our standard plan, Lumen retains inputs and outputs for 30 days. Zero retention requires an enterprise agreement with the ZDR addendum, which we do not have." Do not send client documents until a ZDR addendum is signed, or until counsel approves 30-day retention. |
| 2 | Medium | CONFIRMED | Supporting facts: "enough for a 150-page contract [2]" | Source [2] gives only the 200,000-token figure. The 150-page sufficiency claim appears nowhere in Lumen's pages, yet it carries citation [2]. This breaks the request's rule to "base every claim on Lumen's own pages." | The figure is plausible for ordinary prose, but dense contracts with tables, schedules, or exhibits, plus prompt and output tokens, could exceed it. A reader trusts the citation and never tests it. | Either remove the 150-page clause or mark it as the team's own estimate. Then tokenize a real long contract with Lumen's tokenizer to confirm it fits. |
| 3 | Medium | CONFIRMED (gap) | Summary: "safe to use with client documents" | No source makes a safety or suitability judgment. "Safe" is the author's conclusion. Even with ZDR, the assessment never checks whether client contracts allow third-party processing, or whether a DPA or confidentiality terms with Lumen exist. | ZDR is later obtained, and the team treats this document as clearance. A client's NDA still forbids disclosure to a sub-processor. | Separate the sourced facts from the judgment. Add a step to check client confidentiality obligations and Lumen's contractual terms (DPA, sub-processors) before declaring the API usable. |
| 4 | Low | PROBABLE | Supporting facts: "Lumen holds a SOC 2 Type II report [2]" | The claim is accurately sourced, but it is the vendor's own assertion. The report itself, its scope, and the period ending 30 June 2026 were not reviewed. The finding also implies SOC 2 supports "safe," which it does not address with respect to retention. | Readers take SOC 2 as covering the API data path when its scope may exclude it. | Note the period and that it is a vendor claim. Request the report under NDA and confirm that the API service is in scope. |

## WHAT HOLDS UP

- **No training on data:** accurate. The source says "on any plan," so it applies to the standard account.
- **SOC 2 Type II exists:** accurately quoted as a vendor statement.
- **200,000-token context window:** accurately quoted.
- **Source freshness:** both pages were retrieved 5 October 2026, two days ago, so they are not stale.
- **Plan disclosure:** the author stated the plan honestly. That fact is what settles finding 1.

## UNVERIFIED CLAIMS

- That the source files match Lumen's live pages. Confirm by re-fetching the pages and comparing.
- That the account is on the standard plan with no ZDR addendum. Confirm with procurement or the Lumen account console.
- That a 150-page contract fits in the context window. Confirm by tokenizing a real document.
- The scope of the SOC 2 report. Confirm by obtaining the report.

## QUESTIONS FOR THE AUTHOR

1. Is there a signed ZDR addendum, or one in negotiation? If so, the retention finding changes. If not, the conclusion must be reversed.
2. Do the clients' contracts or NDAs permit processing by a third-party AI vendor that retains data for 30 days?

## DECISION-MAKER SUMMARY

Do not send client contracts to Lumen on the basis of this assessment. Its central "zero-retention" claim is contradicted by the cited source: the standard plan keeps all inputs for 30 days. Get a signed enterprise ZDR addendum and confirm client confidentiality terms first. If you proceed anyway, client-confidential documents will sit with a third party for 30 days, and that exposure cannot be reversed.

```json
{
  "verdict": "REJECT",
  "findings": [
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "assessment.md Summary: \"Lumen is zero-retention, so it is safe to use with client documents [1]\"",
      "scenario": "Source [1] states inputs/outputs are retained 30 days and ZDR requires an enterprise agreement with a signed ZDR addendum; the assessment states the account is on the standard plan with no enterprise agreement. Team sends client contracts believing nothing is retained; Lumen holds them for 30 days, irreversibly exposing client-confidential material.",
      "fix": "Restate as: standard plan retains inputs/outputs 30 days; ZDR needs an enterprise agreement plus ZDR addendum, which we lack. Block client-document use until a ZDR addendum is signed or counsel accepts 30-day retention."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "assessment.md Supporting facts: \"enough for a 150-page contract [2]\"",
      "scenario": "Source [2] gives only the 200,000-token limit; the 150-page claim is the author's inference cited as Lumen's statement. Dense contracts with schedules/exhibits plus prompt and output tokens may exceed the window, and readers trust the citation without testing.",
      "fix": "Remove the clause or label it as an internal estimate; tokenize a real long contract to confirm fit."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "assessment.md Summary: \"safe to use with client documents\"",
      "scenario": "No source makes a safety judgment and the assessment does not check client confidentiality obligations or Lumen contractual terms (DPA, sub-processors). Even with ZDR, a client NDA could prohibit disclosure to a third-party processor.",
      "fix": "Separate sourced facts from the judgment; add a check of client contract terms and Lumen DPA/sub-processor terms before declaring the API usable."
    },
    {
      "severity": "Low",
      "evidence_level": "PROBABLE",
      "location": "assessment.md Supporting facts: \"Lumen holds a SOC 2 Type II report [2]\"",
      "scenario": "Accurately quoted but it is a vendor assertion; report scope and period (ending 30 June 2026) not reviewed, and SOC 2 does not address retention. Readers may assume it covers the API data path.",
      "fix": "Note the period and vendor-claim status; obtain the report under NDA and confirm the API service is in scope."
    }
  ]
}
```