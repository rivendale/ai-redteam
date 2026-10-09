**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent or tools were available, so a single reviewer read the documents. I did not write this work.

**VERDICT: REWORK.** The privacy notice says data goes only to listed processors, but it adds a processor that the published list does not name. The statement template also omits a sentence that RICR 4.5 requires.

**CONFIDENCE: medium.** No tools were available. The governing privacy law, the Corvid Metrics contract and the account type were not supplied. Every finding below rests on exact quotes from the supplied files.

**INPUTS LEDGER**
- **Seen:** request.md, context.md, privacy_notice.md, rule_extract.md, statement_template.md, subprocessors_published.md.
- **Not seen:**
  - The privacy law or regulation that governs the notice. This matters because RICR covers investment communications, not privacy notices, so the privacy-law baseline is missing.
  - The Corvid Metrics agreement. This matters for whether Corvid is really a processor and whether "we do not sell" holds.
  - The currently published privacy notice. This matters somewhat: without it I cannot diff the draft against what customers already read.
  - Confirmation that accounts are "managed accounts" under RICR. This matters for how F2 applies.
  - The full RICR text. Only an extract was supplied, so other sections may apply.

**COVERAGE**
- **Scope:** the whole of the two draft documents, checked against the rule extract and the published processor list.
- **Checked:** all four content files, each sentence of the privacy notice, and each line of the template against RICR 4.2, 4.3 and 4.5.
- **Not checked:** the full RICR, privacy law, the Corvid contract and the prior notice. None of these were supplied.

**SEATS AND GATE:** One same-session Claude reviewer ran. Cross-vendor seats were not used: none were requested, and the templates involve customer account data. The gate found no actual personal data in the drafts (placeholders only).

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | R | privacy_notice.md "Analytics (new)" and "Who receives your data"; subprocessors_published.md table | The notice sends data to Corvid Metrics. It also says "We share personal data only with the processors listed in our Subprocessors page." That page (published 2026-02-01) lists only Hexa Hosting and Pellet Mail. | On 2026-11-01 the notice is published and the page is unchanged. The notice then contradicts itself in public, the page is untrue, and a customer or the regulator can show undisclosed sharing. This breaks the request's "keep our published pages consistent". | Publish a new, dated version of the Subprocessors page that adds Corvid Metrics (purpose: product analytics) on or before the notice goes live. Supersede the old page rather than editing it in place. Gate the notice's release on that page going live. | a✓ b✓ c✓ d✓ |
| F2 | High | PROBABLE | R | statement_template.md (whole template); rule_extract.md 4.5 | The template does not carry the mandated sentence "Compare this information with your official account statement." | If these are managed accounts (the "Contact your adviser" line suggests so), every November statement breaches RICR 4.5. | Add the 4.5 sentence verbatim. Confirm with compliance how it applies when the document is itself the statement. | a✓ b✗ c✓ d✓ |
| F3 | Medium | CONFIRMED | R | privacy_notice.md line 1 vs "Analytics (new)" | The notice says data is collected "to run your account", but the new section uses it for a different purpose (feature-usage analytics). It also adds "account number and transaction history", which are not clearly within "account activity". | A customer or regulator reads the opening summary as the complete list of purposes and categories, so it understates the use. | Revise the opening sentence to list the analytics purpose and name account number and transaction history explicitly. | a✓ b✓ c✗ d✓ |
| F4 | Medium | PROBABLE | R/D | privacy_notice.md "Analytics (new)" | The stated purpose ("which features customers use") does not need account numbers or full transaction history. | The sharing is broader than the stated purpose, which risks a data-minimisation objection, and a breach at Corvid exposes identifiable financial data. | Send pseudonymised IDs and event data only. If full data is truly needed, justify it in the notice. | a✓ b✗ c✗ d✓ |
| F5 | Low | PROBABLE | R | statement_template.md balance lines | There is no line for investment gain or loss, so Opening + Contributions − Withdrawals − Fees will not equal Closing for an invested account. | Customers cannot reconcile their statement and contact support. If a gain/loss line is added later, RICR 4.3 applies (net of fees plus the past-performance statement). | Add a market-movement line. If it is presented as performance, show it net of fees with the 4.3 statement. | a✓ b✗ c✗ d✓ |

**Severity check, siblings and security:**
- **F1:** I searched both drafts for other published lists made stale by the change. The data-category and purpose statement is also stale; that is recorded as F3. This is not a security finding: there is no boundary crossing, and the harm is regulatory and customer-facing.
- **F2:** I searched the other drafts for the same omission. The privacy notice also lacks the 4.5 sentence; whether it counts as a "communication about a managed account" is listed under needs-validation below. Not a security finding.

## NEEDS VALIDATION
- **V1:** Is the privacy notice a "communication about a managed account" under 4.5? The fact that settles it is the RICR scope or definitions section.
- **V2:** Is Corvid Metrics a processor acting only on instructions? Does any payment or data-for-service exchange make "We do not sell personal data" untrue? The Corvid agreement settles both.
- **V3:** Does the governing privacy law require a lawful basis, opt-out or prior notice period for the new analytics use? The applicable statute or regulator guidance settles it.

## REFUTED
- **R1: "The statement shows performance without net-of-fees and past-performance wording (4.3)."** Refuted. The template shows only balances, flows and fees, with no return or performance figure.
- **R2: "The drafts imply guaranteed returns or no risk (4.2)."** Refuted. Neither document contains return, guarantee or safety language.

## WHAT HOLDS UP
- The analytics section openly names the recipient and the data sent. That candour is good; the problem is only that the rest of the notice and the published list don't match it.
- The template shows fees explicitly.
- There is no 4.2 or 4.3 exposure in the current text.

## UNVERIFIED CLAIMS
- **"We do not sell personal data":** confirm against the Corvid contract terms.
- **"Corvid Metrics … analyzes it for us"** (that is, processor-only use): confirm against the agreement's use-restriction clause.

## QUESTIONS FOR THE AUTHOR
1. Are these managed accounts under RICR?
2. Will an updated Subprocessors page publish on or before 2026-11-01?
3. Does Corvid need account numbers at all?

## DECISION-MAKER SUMMARY
Do not publish until the Subprocessors page lists Corvid Metrics and the statement template carries the RICR 4.5 sentence. If published as is, the privacy notice is publicly false on day one, and every November statement may breach RICR. The remaining fixes are wording and data-minimisation improvements.

## OWNER SUMMARY
The new privacy notice says we only share data with companies on our published list, but the new analytics company isn't on that list yet, so the two pages contradict each other. The monthly statement is also missing a sentence the regulator requires on account communications. Both are quick to fix and should be fixed before anything goes out.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "privacy_notice.md", "status": "seen", "matters": true},
    {"item": "rule_extract.md", "status": "seen", "matters": true},
    {"item": "statement_template.md", "status": "seen", "matters": true},
    {"item": "subprocessors_published.md", "status": "seen", "matters": true},
    {"item": "governing privacy law", "status": "not_seen", "matters": true},
    {"item": "Corvid Metrics agreement", "status": "not_seen", "matters": true},
    {"item": "currently published privacy notice", "status": "not_seen", "matters": false},
    {"item": "full RICR text / managed-account definition", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Drafts contain placeholders only; no actual personal data."},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "privacy_notice.md", "kind": "document"},
      {"unit": "rule_extract.md", "kind": "document"},
      {"unit": "statement_template.md", "kind": "document"},
      {"unit": "subprocessors_published.md", "kind": "document"},
      {"unit": "RICR 4.2, 4.3, 4.5 against both drafts", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "governing privacy law", "reason": "not_supplied"},
      {"unit": "Corvid Metrics agreement", "reason": "not_supplied"},
      {"unit": "full RICR text", "reason": "not_supplied"},
      {"unit": "currently published privacy notice", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "R",
     "location": "privacy_notice.md 'Analytics (new)' and 'Who receives your data'; subprocessors_published.md table",
     "scenario": "Notice published 2026-11-01 says data is shared only with listed processors, but Corvid Metrics is not on the published list (Hexa Hosting, Pellet Mail); the published pages contradict each other and disclose sharing inaccurately.",
     "fix": "Publish a new dated Subprocessors version adding Corvid Metrics before or with the notice; supersede rather than edit in place; gate notice release on it.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "both drafts for other published lists or statements made stale by the analytics change", "found": "opening data-category/purpose sentence (F3)"}},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "R",
     "location": "statement_template.md (whole); rule_extract.md 4.5",
     "scenario": "If accounts are managed accounts, every November statement omits the mandatory sentence 'Compare this information with your official account statement.' and breaches RICR 4.5.",
     "fix": "Add the 4.5 sentence verbatim; confirm applicability with compliance.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "privacy_notice.md for the 4.5 sentence", "found": "also absent; applicability unresolved (V1)"}},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "R",
     "location": "privacy_notice.md line 1 vs 'Analytics (new)'",
     "scenario": "Opening sentence limits purpose to 'to run your account' and categories to name, contact details and account activity, while analytics uses account number and transaction history for a different purpose.",
     "fix": "Revise the opening sentence to include the analytics purpose and name the added categories.",
     "answers": {"a": true, "b": true, "c": false, "d": true}},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "R",
     "location": "privacy_notice.md 'Analytics (new)'",
     "scenario": "Feature-usage analytics does not need account numbers or full transaction history; over-sharing raises minimisation objections and breach impact at Corvid.",
     "fix": "Send pseudonymised identifiers and event data only, or justify the full data in the notice.",
     "answers": {"a": true, "b": false, "c": false, "d": true}},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "PROBABLE", "track": "R",
     "location": "statement_template.md balance lines",
     "scenario": "No gain/loss line, so opening + contributions - withdrawals - fees will not equal closing for invested accounts; customers cannot reconcile.",
     "fix": "Add a market-movement line; if presented as performance, show net of fees with the RICR 4.3 statement.",
     "answers": {"a": true, "b": false, "c": false, "d": true}},
    {"id": "V1", "status": "needs_validation", "track": "R", "location": "privacy_notice.md",
     "suspicion": "Privacy notice may also need the RICR 4.5 sentence.",
     "unresolved_fact": "Whether RICR treats a privacy notice as a communication about a managed account."},
    {"id": "V2", "status": "needs_validation", "track": "R", "location": "privacy_notice.md 'We do not sell personal data'",
     "suspicion": "Corvid arrangement may not be pure processing, making 'processor' or 'do not sell' untrue.",
     "unresolved_fact": "Use-restriction and payment terms in the Corvid Metrics agreement."},
    {"id": "V3", "status": "needs_validation", "track": "R", "location": "privacy_notice.md 'Analytics (new)'",
     "suspicion": "New analytics use may require a lawful basis, opt-out or advance notice.",
     "unresolved_fact": "The governing privacy law's requirements for a new processing purpose."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Statement shows performance without 4.3 wording.", "evidence": "Template contains only balances, flows and fees; no return or performance field."},
    {"id": "R2", "candidate": "Drafts imply guaranteed returns or no risk (4.2).", "evidence": "No return, guarantee or safety language in either draft."}
  ]
}
```