**Review mode:** I did this review myself, not through a subagent, and had no tools. I didn't produce the work under review, so there's no carried-over author reasoning. I could not check anything beyond the four supplied files: no privacy-law text, no Corvid contract, no product data flows.

## Pass 1: Reconstruct

The work has two drafts for 2026-11-01. The first is a privacy notice. It adds an analytics disclosure (account activity, account number and transaction history sent to Corvid Metrics) and keeps the claim that data goes only to processors on the published Subprocessors page. The second is a monthly statement template showing balances, flows and fees. For the work to be correct, four things must hold:

- The published pages must agree with each other.
- Each RICR clause in the extract must either be met or not apply.
- The disclosed data flow must be appropriate for its stated purpose.
- The statement figures must make sense to a customer.

Unstated assumptions:

- The Subprocessors page will be updated alongside the notice. Nothing in the work does this.
- The statement is out of scope of RICR 4.5, or already satisfies it.
- The statement does not "show performance" under 4.3.

## Pass 2: Attack (Track A applied to regulated text; Track B lightly to the template)

**Cross-document consistency (the explicit request).**
- The notice says "We share personal data only with the processors listed in our Subprocessors page."
- That page (published 2026-02-01) lists only Hexa Hosting and Pellet Mail.
- Corvid Metrics is not on it, and no updated page is part of the deliverable.

As drafted, the notice makes a false statement on the day it publishes.

**RICR**
- **4.2:** no guarantee or risk-free language in either document. Holds.
- **4.3:** the template has no return or performance figure, so the clause isn't clearly triggered. The figures may also fail to reconcile (finding 3). If that is fixed by adding an investment-gain/loss line, 4.3 likely applies: net-of-fees presentation plus the past-performance sentence.
- **4.5:** "Contact your adviser" suggests advised or managed accounts. The template omits the mandatory sentence. Whether a statement must tell the reader to compare it with "your official account statement" depends on whether this *is* the official statement. That is unresolved, and the author has to decide it.

**Privacy content.** The stated purpose is "to understand which features customers use." That does not obviously need the account number or full transaction history. The notice's opening line ("to run your account") also no longer covers every purpose. No privacy law was supplied, so legal basis, opt-out, retention and transfer requirements can't be checked.

## Pass 3: Self-check

- I dropped a generic "notice lacks retention period" finding because there's no rule to tie it to. It is listed under unverified claims instead.
- I kept 4.5 as a question, not a confirmed breach.
- The most serious thing that could still be missed is the effective date. If Corvid already receives data, or will before 2026-11-01, the current published page is already inaccurate today.

---

**VERDICT: SHIP WITH FIXES.** Do not publish the privacy notice until the Subprocessors page lists Corvid Metrics, and resolve the RICR 4.5 scope question for the statement before release.

**CONFIDENCE IN VERDICT:** Medium. Limits:
- I only had a partial RICR extract and no privacy-law text.
- I can't tell whether accounts are "managed" or whether this document is the "official account statement."
- I had no tools, so I couldn't check the live site or the data flows.

### FINDINGS

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | privacy_notice.md "Who receives your data" vs subprocessors_published.md table | The notice says data goes only to listed processors and names Corvid Metrics, but Corvid is not on the published list. | On 2026-11-01 a customer or the regulator reads both pages: the notice discloses Corvid, and the page it points to excludes it. That is a false statement in a regulated, customer-facing document. If Corvid already receives data, the live page is already wrong. | Add "Corvid Metrics, product analytics" to the Subprocessors page. Re-date it and publish it no later than the notice. Confirm the date Corvid first receives data. |
| 2 | High | PROBABLE | privacy_notice.md "Analytics (new)": "including your account number and transaction history" | The stated purpose is feature-usage analytics, but the data sent includes a direct identifier and full financial history, which goes beyond that purpose. The notice also opens with "to run your account," which no longer covers all purposes. | A complaint or regulator inquiry asks why feature analytics needs account numbers and transactions. The firm can't justify it, and the disclosure becomes evidence of over-collection. | Product owner decides whether pseudonymised IDs or event-level usage data are enough. Either reduce the data sent, or state the real purpose and the legal basis. Update the first sentence to cover analytics. |
| 3 | Medium | PROBABLE | statement_template.md balance lines | There is no investment gain/loss or market-movement line. For an investment account, Opening + Contributions − Withdrawals − Fees ≠ Closing whenever markets move. | A customer sees figures that don't reconcile and assumes an error or missing money, which leads to complaints. | Add a "Change in value" line. That probably brings in 4.3: show it net of fees and add "past performance does not predict future results." Test with sample data where the market moves. |
| 4 | Medium | UNVERIFIED | statement_template.md (whole) vs rule_extract.md 4.5 | The mandatory 4.5 sentence is absent. Accounts appear to be advised or managed ("Contact your adviser"). | If the template counts as a "communication about a managed account" under RICR, every November statement is non-compliant. | Compliance confirms whether this template is the official statement or falls under 4.5. If in scope, add the exact sentence verbatim. |
| 5 | Low | UNVERIFIED | privacy_notice.md (whole) | No legal basis, opt-out, retention, or data-location statement for the new analytics processing. | The applicable privacy law may require these for a new purpose. The requirement isn't knowable from the inputs. | Check against the governing privacy law and the Corvid DPA before publishing. |

### WHAT HOLDS UP
- Neither document implies guaranteed returns or no risk (RICR 4.2).
- Fees are shown as a separate line, so they are disclosed.
- "We do not sell personal data" is not contradicted by anything supplied.
- The analytics disclosure itself is plain and specific about the recipient and data categories.

### UNVERIFIED CLAIMS
- "We share personal data only with the processors listed": false against the supplied page. Check the live site and every actual data recipient.
- Corvid "analyzes it for us" (processor role): confirm with the contract or DPA that Corvid has no independent use of the data.
- Whether the statement shows "performance" or is a managed-account communication: confirm with compliance and the full RICR text.

### QUESTIONS FOR THE AUTHOR
1. Will the Subprocessors page be updated, and does Corvid receive data before 2026-11-01?
2. Is this template the official account statement, and are these managed accounts under RICR?
3. Does analytics actually need account numbers and transaction history?
4. Is market movement deliberately omitted from the statement?

### DECISION-MAKER SUMMARY
Hold the privacy notice until the Subprocessors page adds Corvid Metrics; otherwise you publish a false statement to customers and the regulator. Have compliance rule on RICR 4.5 and 4.3 scope for the statement, and add a value-change line so the figures reconcile. If you proceed anyway, the main risks are a regulator finding on inaccurate disclosure and over-collection of financial data for analytics.

```json
{
  "verdict": "SHIP WITH FIXES",
  "findings": [
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "privacy_notice.md 'Who receives your data' vs subprocessors_published.md table",
      "scenario": "Notice names Corvid Metrics and says data is shared only with processors on the Subprocessors page, but the published page (2026-02-01) lists only Hexa Hosting and Pellet Mail; on publication the notice is false to customers and the regulator.",
      "fix": "Add Corvid Metrics (product analytics) to the Subprocessors page, re-date it, publish no later than the notice; confirm when Corvid first receives data."
    },
    {
      "severity": "High",
      "evidence_level": "PROBABLE",
      "location": "privacy_notice.md 'Analytics (new)': 'including your account number and transaction history'",
      "scenario": "Feature-usage analytics does not evidently need account numbers and full transaction history; a regulator or complainant challenges over-collection and the notice documents it. Opening sentence 'to run your account' no longer covers all purposes.",
      "fix": "Minimise to pseudonymised usage events or justify and state the purpose and legal basis; update the first sentence to include analytics."
    },
    {
      "severity": "Medium",
      "evidence_level": "PROBABLE",
      "location": "statement_template.md balance lines",
      "scenario": "No investment gain/loss line, so opening + contributions - withdrawals - fees does not equal closing when markets move; customers see unreconciled figures and complain.",
      "fix": "Add a change-in-value line; if added, apply RICR 4.3 (net of fees plus past-performance sentence). Test with sample data including market movement."
    },
    {
      "severity": "Medium",
      "evidence_level": "UNVERIFIED",
      "location": "statement_template.md vs rule_extract.md 4.5",
      "scenario": "Accounts appear advised/managed; if the statement is a communication about a managed account under RICR, every November statement lacks the mandatory sentence.",
      "fix": "Compliance to confirm scope; if in scope, add 'Compare this information with your official account statement.' verbatim."
    },
    {
      "severity": "Low",
      "evidence_level": "UNVERIFIED",
      "location": "privacy_notice.md (whole)",
      "scenario": "Applicable privacy law may require legal basis, opt-out, retention, and transfer details for the new analytics purpose; not determinable from supplied inputs.",
      "fix": "Check against governing privacy law and the Corvid DPA before publication."
    }
  ]
}
```