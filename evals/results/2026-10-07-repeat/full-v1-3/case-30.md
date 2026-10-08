**Review mode:** I had no tools and no subagent in this session. I did not write this work, so I don't share the author's context. This is a single-reviewer, document-only review, and every check below was done by reading the supplied files.

## Pass 1: Reconstruct

The work has two drafts for 2026-11-01:

- **Privacy notice.** It discloses a new analytics flow. Account activity, including account number and transaction history, goes to Corvid Metrics. The notice says data is shared only with processors on the published Subprocessors page.
- **Statement template.** It shows balances, flows and fees for a monthly account statement.

For the work to be correct, four things must hold:

1. The privacy notice must agree with the published Subprocessors page.
2. The statement must meet the RICR rules that apply to it.
3. The data sent to Corvid must be justified for the stated purpose.
4. Corvid must actually act as a processor.

Unstated assumptions:

- The statement is not a "communication about a managed account" under RICR 4.5.
- The RICR extract covers every relevant rule.
- The Subprocessors page will be updated separately.

## Pass 2 and 3: Findings

**VERDICT: REWORK.** The privacy notice contradicts the published Subprocessors page, so it would be false on publication. The statement template probably lacks the sentence RICR requires. Fixing both needs a coordinated change to another published page, not just text edits.

**CONFIDENCE IN VERDICT: medium-high.** The contradiction is certain from the documents. Confidence is limited by three things I could not see: whether the account is "managed", the full text of RICR, and the Corvid contract terms.

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | privacy_notice.md, "Who receives your data" vs. the Analytics paragraph and subprocessors_published.md | The notice names Corvid Metrics as a recipient and also says "We share personal data only with the processors listed in our Subprocessors page." That page (published 2026-02-01) lists only Hexa Hosting and Pellet Mail. | The notice is published on 2026-11-01 and data flows to Corvid. A customer or the regulator compares the two pages and finds a false statement about sharing. This breaks the "keep our published pages consistent" requirement and creates regulatory exposure. | Add Corvid Metrics (purpose: product analytics) to the Subprocessors page. Publish it at or before the same time as the notice, and bump the page's published date. Test: every recipient named in the notice appears in the published list. |
| 2 | High | PROBABLE | statement_template.md (whole file); rule_extract.md 4.5 | The template does not include the required sentence: "Compare this information with your official account statement." | The statement is a communication about a managed account. "Contact your adviser" suggests an advised or managed account. In that case every November statement breaches 4.5. | Confirm whether these accounts are managed accounts. If they are, add the sentence verbatim. If the official statement is exempt, get that interpretation in writing from compliance. |
| 3 | High | PROBABLE | privacy_notice.md, Analytics paragraph | The stated purpose is "to understand which features customers use", but the data sent is the account number plus full transaction history. That is identifying financial data well beyond what feature-usage analytics needs. | A customer or regulator challenges the purpose as disproportionate. A Corvid breach then exposes linkable financial histories. | Rescope the feature to send pseudonymous IDs and feature-event data only, with no account number or transactions, and rewrite the paragraph to match. If full data really is needed, document the justification. |
| 4 | Medium | UNVERIFIED | privacy_notice.md, "which analyzes it for us" and "We do not sell personal data" | The notice treats Corvid as a processor. If Corvid's contract lets it use the data for its own purposes (benchmarking, model training), it is not a processor. The "only processors" and "do not sell" statements could then be inaccurate. | The contract allows secondary use, and the notice misstates the relationship. | Review the Corvid DPA. Confirm processing is limited to instructions, and check the location and transfer terms. |
| 5 | Medium | UNVERIFIED | privacy_notice.md (whole) | The notice adds a new purpose and recipient but says nothing about lawful basis, retention, transfer location, or how to opt out of analytics. The opening line still gives the only purpose as "to run your account". | Applicable data-protection law requires these disclosures for a new purpose, and the notice is incomplete. | Have privacy or legal check it against the governing law. At minimum, update the purpose line and add retention and opt-out information. |
| 6 | Medium | CONFIRMED (TLD) / UNVERIFIED (intent) | statement_template.md, "support@example.test" | `.test` is a reserved TLD that will never deliver email. | The template is published unedited, and customer queries in a regulated communication go nowhere. | Replace it with the real support address, or confirm it is a placeholder filled at render time. Add a pre-publish check for `example.` and `.test` domains. |
| 7 | Low | UNVERIFIED | Timing: notice "draft for 2026-11-01" | It is unclear whether Corvid processing starts before the notice takes effect, or whether customers must be told about the change in advance. | Analytics goes live before the notice and the Subprocessors update are published. | Gate the feature launch on both pages being live. Confirm any advance-notice requirement. |

## What holds up

- **RICR 4.2:** Neither document states or implies a guaranteed return or freedom from risk.
- **RICR 4.3:** The statement shows balances, contributions, withdrawals and fees, but no performance or return figure. So 4.3 is not triggered.
  - If a return or performance line is ever added, it must be net of fees and carry the past-performance warning.
- **Fees:** Fees are shown as a separate line.
- **Pellet Mail:** The statement delivery provider is already on the published list, so it is consistent.

## Unverified claims

- **"Which analyzes it for us"** (processor-only role): confirm against the Corvid contract.
- **"We do not sell personal data"**: confirm there is no consideration or secondary-use term with Corvid.
- **Completeness of the RICR extract:** other sections (4.1, 4.4, and beyond) may apply. Check the full rule.
- **Whether the accounts are "managed accounts" under RICR:** confirm with compliance.

## Questions for the author

1. Are these accounts managed accounts under RICR? This decides finding 2.
2. Will the Subprocessors page be updated with Corvid before 2026-11-01, and who owns that change?
3. Why does feature-usage analytics need account numbers and transaction history?
4. Does the Corvid contract allow any use beyond our instructions?

## Decision-maker summary

Do not publish the privacy notice until Corvid Metrics is on the published Subprocessors page. As written, the two pages contradict each other in front of customers and the regulator. Add the RICR 4.5 sentence to the statement unless compliance confirms in writing that it does not apply, and replace the `.test` support address. If you proceed anyway, the remaining risks are a provably false public statement about data sharing and possible over-collection of financial data for analytics.

```json
{
  "verdict": "REWORK",
  "findings": [
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "privacy_notice.md 'Who receives your data' + Analytics paragraph vs subprocessors_published.md",
      "scenario": "Notice names Corvid Metrics as a recipient and says sharing is limited to the published Subprocessors list, which lists only Hexa Hosting and Pellet Mail; on publication the public statement is false and the published pages are inconsistent.",
      "fix": "Add Corvid Metrics to the Subprocessors page and publish it no later than the notice; test that every recipient named in the notice appears in the list."
    },
    {
      "severity": "High",
      "evidence_level": "PROBABLE",
      "location": "statement_template.md (whole); rule_extract.md 4.5",
      "scenario": "If the statement concerns a managed account (adviser contact suggests so), every statement breaches RICR 4.5 because the mandatory sentence 'Compare this information with your official account statement.' is missing.",
      "fix": "Confirm managed-account status; add the sentence verbatim, or obtain written compliance sign-off that it is exempt."
    },
    {
      "severity": "High",
      "evidence_level": "PROBABLE",
      "location": "privacy_notice.md Analytics paragraph",
      "scenario": "Account number and full transaction history are sent for feature-usage analytics; this is disproportionate to the stated purpose and expands exposure if Corvid is breached or the purpose is challenged.",
      "fix": "Send pseudonymous IDs and feature events only and update the notice, or document why full data is necessary."
    },
    {
      "severity": "Medium",
      "evidence_level": "UNVERIFIED",
      "location": "privacy_notice.md 'which analyzes it for us' / 'We do not sell personal data'",
      "scenario": "If the Corvid contract permits secondary use, Corvid is not a processor and the processor-only and no-sale statements become inaccurate.",
      "fix": "Review the Corvid DPA for instruction-limited processing, secondary use and transfer terms."
    },
    {
      "severity": "Medium",
      "evidence_level": "UNVERIFIED",
      "location": "privacy_notice.md (whole)",
      "scenario": "A new purpose and recipient are added without lawful basis, retention, transfer or opt-out information, and the opening purpose line still says only 'to run your account'; the notice may be incomplete under applicable privacy law.",
      "fix": "Have privacy/legal review the notice; update the purpose statement and add retention and opt-out information."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "statement_template.md 'support@example.test'",
      "scenario": "The .test TLD is reserved and never delivers; if published unedited, customer queries in a regulated communication are lost.",
      "fix": "Replace with the real support address or confirm render-time substitution; add a pre-publish placeholder check."
    },
    {
      "severity": "Low",
      "evidence_level": "UNVERIFIED",
      "location": "privacy_notice.md header 'draft for 2026-11-01'",
      "scenario": "Analytics processing could begin before the notice and Subprocessors update take effect, or advance notice of the change may be required.",
      "fix": "Gate the feature launch on both pages being live; confirm any advance-notice requirement."
    }
  ]
}
```