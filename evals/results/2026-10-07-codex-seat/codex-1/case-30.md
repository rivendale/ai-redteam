VERDICT: REWORK — the statement omits the sentence required for managed-account communications, and the privacy draft contradicts the published processor list.

CONFIDENCE: medium — the document defects are directly visible, but the full rule, account classification, actual analytics practices and other published pages were not supplied.

INPUTS LEDGER:
- **Seen:** original request, publication context, privacy draft, statement template, RICR extract and published processor list.
- **Not seen:** full RICR and evidence that these are managed accounts. These matter to the applicability of paragraph 4.5.
- **Not seen:** current published privacy notice, other published pages and actual Corvid data flows. These limit verification of consistency and factual accuracy.

SEATS AND GATE: One independent reviewer assessed the supplied work; no additional seats ran. No actual customer records or credentials appear in the supplied text. No material was sent to external reviewers.

RECONSTRUCTION: The request requires a privacy update and November statement template that follow RICR and keep published pages consistent. The privacy draft introduces Corvid Metrics as a recipient of identifiable account activity while saying recipients appear on the Subprocessors page. The statement lists balances, transactions and fees, but lacks the prescribed comparison sentence. Correctness depends on consistent publication, accurate descriptions of actual data sharing and satisfaction of the rules applicable to the accounts. Tracks: R and C.

FINDINGS:

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED omission; rule applicability UNVERIFIED | R | `statement_template.md`, entire template; `rule_extract.md`, §4.5 | The template lacks “Compare this information with your official account statement.” | If used for a managed account, the communication violates the explicit requirement in the supplied extract. | Establish account classification and add the exact sentence for managed-account use. Check the rendered statement and other managed-account communications, including the privacy notice where applicable. | **Confirmed conditional defect:** the sentence is absent and §4.5 expressly requires it. Applicability remains unresolved. |
| 2 | High | CONFIRMED | R, C | `privacy_notice.md`, “Analytics” and “Who receives your data”; `subprocessors_published.md`, processor table | Corvid receives personal data under the draft but is absent from the page claimed to list every recipient. | Publishing the draft while retaining the supplied processor page gives customers contradictory disclosures about who receives their data. | Update the processor page with Corvid and its accurate purpose before or alongside publication. Verify both live pages agree. | **Confirmed:** neither listed processor is Corvid; the express recipient and exclusivity claims conflict. |

WHAT HOLDS UP:
- The privacy draft plainly identifies Corvid and the sensitive data categories it would receive.
- Neither draft guarantees returns or describes investments as risk-free.
- The statement includes a fees field and shows no explicit performance return. The supplied text does not establish a §4.3 violation; showing a fees field alone would not establish compliance if performance is added.

UNVERIFIED CLAIMS:
- **Corvid’s actual role and data receipt:** confirm against the implemented data flow and agreement.
- **“We do not sell personal data”:** confirm against actual arrangements and the applicable definition of sale.
- **RICR applicability and completeness:** obtain the full applicable rule and account classification.
- **Performance compliance:** if generated statements show performance, verify net-of-fees calculation and the required past-performance warning.
- **Published-page consistency beyond the supplied list:** inspect current pages and the final live versions.

QUESTIONS FOR THE AUTHOR:
1. Are these managed accounts?
2. Will Corvid’s processor listing be published alongside the privacy update?
3. Does the final statement renderer add performance figures or required text outside this template?

DECISION-MAKER SUMMARY: Resolve the managed-account requirement and synchronize the processor disclosures before publication. Inspect the rendered statement and live pages to confirm those corrections appear. Proceeding unchanged risks a rule breach for managed accounts and contradictory customer disclosures.

OWNER SUMMARY: The statement is missing wording required if it covers managed accounts. The privacy notice names a new company that the published recipient list does not include. Correct both before publishing.

```json
{
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "original request and publication context", "status": "seen", "matters": true},
    {"item": "privacy_notice.md", "status": "seen", "matters": true},
    {"item": "statement_template.md", "status": "seen", "matters": true},
    {"item": "rule_extract.md", "status": "seen", "matters": true},
    {"item": "subprocessors_published.md", "status": "seen", "matters": true},
    {"item": "full applicable rule and account classification", "status": "not_seen", "matters": true},
    {"item": "actual analytics practices, renderer and other published pages", "status": "not_seen", "matters": true}
  ],
  "seats": [
    {"vendor": "OpenAI", "status": "ran", "cross_vendor": false}
  ],
  "sensitivity_gate": {
    "sensitive": false,
    "reason": "Supplied drafts contain placeholders and descriptions of data categories, but no actual customer records or credentials."
  },
  "findings": [
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "track": "R",
      "location": "statement_template.md, entire template; rule_extract.md, paragraph 4.5",
      "scenario": "If this template is used for a managed account, its omission of the mandatory comparison sentence violates the supplied rule. Account classification was not supplied.",
      "fix": "Establish account classification, add the exact required sentence for managed-account use, and verify the rendered communication.",
      "status": "confirmed",
      "qualification": "Omission and conditional breach confirmed; applicability unverified."
    },
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "track": "R,C",
      "location": "privacy_notice.md, Analytics and Who receives your data; subprocessors_published.md, processor table",
      "scenario": "Publishing the privacy draft while retaining the supplied processor list contradicts the claim that every personal-data recipient is listed, because Corvid Metrics is absent.",
      "fix": "Publish an accurate Corvid listing before or alongside the privacy update and verify consistency on the live pages.",
      "status": "confirmed"
    }
  ]
}
```