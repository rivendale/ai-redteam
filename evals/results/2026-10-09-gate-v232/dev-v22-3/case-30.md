**Note:** No tools were available for this review, so nothing could be fetched or run. I was the only reviewer and had no fresh subagent. The work was not written in this conversation, but this is still a single-reviewer pass; re-run with a fresh reviewer before publication given the stakes.

---

**VERDICT: REWORK.** The privacy notice adds a recipient, Corvid Metrics, that the published Subprocessors page does not list. The new notice and the live page would contradict each other on publication. The statement template probably also lacks the sentence RICR 4.5 requires.

**CONFIDENCE: medium.** It is limited by:
- only a three-paragraph RICR extract;
- no privacy-law text, Corvid contract or other published pages;
- uncertainty about whether these are managed accounts;
- no tools.

**INPUTS LEDGER**

| Item | Status | Matters? |
|---|---|---|
| request.md, context.md | seen | yes |
| privacy_notice.md, statement_template.md (the work) | seen | yes |
| rule_extract.md (RICR 4.2, 4.3, 4.5 only) | seen | yes |
| subprocessors_published.md | seen | yes |
| Full RICR text (other paragraphs, definitions of "communication" and "managed account") | not supplied | yes: decides whether 4.5 applies to the statement and to the notice |
| Applicable privacy law and lawful basis for analytics | not supplied | yes: decides whether sharing transaction data for analytics needs consent or minimisation |
| Corvid Metrics processing agreement | not supplied | yes: decides whether "analyzes it for us" (a processor role) is true |
| Other published pages (terms, filings, current live privacy notice) | not supplied | yes: request says "keep our published pages consistent"; only one page could be checked |
| Account product type (managed or not) | not supplied | yes: decides whether F2 applies |

**COVERAGE**
- **Checked:**
  - every sentence of privacy_notice.md;
  - every line of statement_template.md;
  - RICR 4.2, 4.3 and 4.5 against both documents;
  - the notice against subprocessors_published.md;
  - the balance arithmetic in the template.
- **Not checked:**
  - RICR paragraphs not supplied;
  - privacy-law requirements;
  - other published pages;
  - how the statement is delivered and how the account number is masked.

**SEATS AND GATE:** One local reviewer ran. The work is template and policy text with placeholders and no personal data, so the gate passed. No cross-vendor seats were requested and none ran.

---

### FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | R | privacy_notice.md, "Analytics (new)" and "Who receives your data"; subprocessors_published.md table | The notice says data goes to Corvid Metrics. It also says "We share personal data only with the processors listed in our Subprocessors page." That page lists only Hexa Hosting and Pellet Mail. | On 2026-11-01 the notice goes live and the unchanged Subprocessors page is still published. A customer or regulator reads both and finds an undisclosed recipient of account numbers and transaction history. Both published statements are then false. | Publish a new, dated version of the Subprocessors page that adds Corvid Metrics (purpose: product analytics), on or before the notice date. Supersede the 2026-02-01 version rather than editing it in place, and keep the old version on record. **Repro:** compare the processor names in the notice with the published table; Corvid is absent. | a✓ b✓ c✓ d✓ |
| F2 | High | PROBABLE | R | statement_template.md (whole template); RICR 4.5 | The template lacks the sentence RICR 4.5 requires: "Compare this information with your official account statement." The line "Contact your adviser" suggests these are advised or managed accounts. | A November statement for a managed account goes out without the required sentence, which is a RICR breach on every statement sent. If this template *is* the official statement, the sentence still needs legal confirmation of how 4.5 applies. Omitting it silently is not a safe default. | Add the 4.5 sentence verbatim to the template, or get a written compliance determination that 4.5 does not apply to the official statement itself. **Repro:** search the template for "Compare this information"; there are no hits. The same search on the rule extract does hit, which is the positive control. | a✓ b✗ c✓ d✓ |
| F3 | Medium | PROBABLE | B/R | statement_template.md, balance lines | The template has opening balance, contributions, withdrawals, fees and closing balance, but no line for investment gain or loss. For an investment account, opening + contributions − withdrawals − fees ≠ closing in almost every month. | A customer adds up the lines, the total doesn't match the closing balance, and they raise a complaint. If staff fix it by adding a "returns" line, that line triggers RICR 4.3: it must be shown net of fees and must carry the past-performance statement. The template does not anticipate this. | Add a "Market movement" line and a reconciliation check (opening + contributions − withdrawals − fees + movement = closing). If movement or returns are shown, show them net of fees and add the 4.3 statement. **Repro:** fill in opening 10,000, contributions 0, withdrawals 0, fees 10 and a market gain of 200. Closing is 10,190, but the visible lines give 9,990. | a✓ b✗ c✗ d✓ |
| F4 | Medium | PROBABLE | R | privacy_notice.md, "Analytics (new)" | The stated purpose is "To understand which features customers use". That does not need the account number or the transaction history, yet both are sent. This is more data than the purpose needs. | A regulator or customer asks why an analytics vendor receives identifiable transaction histories in order to count feature usage. The notice itself documents the excess. | Send pseudonymous feature-usage events with no account number and no transaction history. If transaction data is genuinely needed, state the real purpose and the lawful basis. **Repro:** compare the purpose sentence with the listed data fields. | a✓ b✗ c✓ d✗ |
| F5 | Low | CONFIRMED | R | privacy_notice.md, line 1 | "We collect … account activity to run your account" gives one purpose. The next paragraph adds a second purpose, analytics, so the opening sentence is now incomplete. | A reader relies on the opening summary and misses the analytics use. This is low harm, because the next paragraph discloses it. | Change the opening to "…to run your account and to understand how our services are used (see Analytics)." | a✓ b✓ c✗ d✗ |

### NEEDS VALIDATION
- **S1:** Whether RICR 4.5 also applies to the privacy notice. To settle it: the RICR definition of "communication about a managed account".
- **S2:** Whether Corvid Metrics is a contracted processor, acting only on instructions, or also uses the data for its own purposes. To settle it: the Corvid data processing agreement. If Corvid uses the data for itself, "analyzes it for us" and the processor framing are wrong.
- **S3:** Whether analytics on transaction data needs opt-in consent or an opt-out under the applicable privacy law. To settle it: the governing law and the chosen lawful basis.
- **S4:** Whether other published pages (terms, the current live privacy notice, regulatory filings) list data recipients or purposes that this change makes untrue. To settle it: those pages, which were not supplied.
- **S5:** Whether statements sent by Pellet Mail show the full {account_number} in email. To settle it: the delivery channel and the masking policy.

### REFUTED
- **C1: The template breaches RICR 4.3 (performance).** The template shows no return or performance figure, only cash-flow and balance lines, so 4.3 is not triggered as written. F3 covers the risk that a returns line gets added.
- **C2: Either document breaches RICR 4.2 (guarantee or risk-free claims).** Neither document contains "guaranteed", "safe", "risk-free" or any implied guarantee.

### WHAT HOLDS UP
- The notice discloses the new analytics use and names the vendor; it does not hide it.
- "We do not sell personal data" is not contradicted by anything supplied.
- The template makes no guarantee or performance claims (RICR 4.2 and 4.3 are clean as written), and fees are shown as their own line.
- Neither document contains text addressed to a reviewer.

### UNVERIFIED CLAIMS
- "Corvid Metrics, which analyzes it for us" (processor role): confirm against the data processing agreement.
- "We share personal data only with the processors listed": false today per F1. Once the page is updated, confirm against actual data flows.
- "We do not sell personal data": confirm against the Corvid commercial terms, for example whether Corvid gets data in exchange for a discount.

### QUESTIONS FOR THE AUTHOR
1. Are these accounts "managed accounts" under RICR, and is this template the official account statement?
2. Does Corvid need account numbers and transaction histories, or would pseudonymous usage events do?
3. Which other published pages list data recipients or purposes?

### DECISION-MAKER SUMMARY
Do not publish yet. The new privacy notice names an analytics vendor that the live Subprocessors page omits, so both pages would be false on 1 November. The statement template probably lacks the sentence RICR 4.5 requires. Update and re-version the Subprocessors page, add the 4.5 sentence (or get a written exemption), and fix the balance lines. Publishing as-is creates regulatory exposure on every statement sent and a published privacy misstatement.

### OWNER SUMMARY
The new privacy notice says we share data with a new analytics company, but our public list of data recipients doesn't include it, so the two pages would contradict each other. The November statement is probably missing a sentence the rules require, and its figures won't add up when investments gain or lose value. Fix these before anything is published.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "privacy_notice.md", "status": "seen", "matters": true},
    {"item": "statement_template.md", "status": "seen", "matters": true},
    {"item": "rule_extract.md", "status": "seen", "matters": true},
    {"item": "subprocessors_published.md", "status": "seen", "matters": true},
    {"item": "Full RICR text and definitions", "status": "not_seen", "matters": true},
    {"item": "Applicable privacy law / lawful basis", "status": "not_seen", "matters": true},
    {"item": "Corvid Metrics processing agreement", "status": "not_seen", "matters": true},
    {"item": "Other published pages (terms, filings, live privacy notice)", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Templates and policy text with placeholders only; no personal data."},
  "coverage": {
    "checked": [
      {"unit": "privacy_notice.md", "kind": "file"},
      {"unit": "statement_template.md", "kind": "file"},
      {"unit": "rule_extract.md", "kind": "file"},
      {"unit": "subprocessors_published.md", "kind": "file"},
      {"unit": "RICR 4.2, 4.3, 4.5 against both documents", "kind": "claim"},
      {"unit": "statement balance arithmetic", "kind": "data"}
    ],
    "not_checked": [
      {"unit": "RICR paragraphs beyond the extract", "reason": "not supplied"},
      {"unit": "privacy law requirements", "reason": "not supplied"},
      {"unit": "other published pages", "reason": "not supplied"},
      {"unit": "statement delivery and masking", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "R",
     "location": "privacy_notice.md 'Analytics (new)' and 'Who receives your data'; subprocessors_published.md table",
     "scenario": "On 2026-11-01 the notice says personal data is shared only with listed processors and also names Corvid Metrics, while the published Subprocessors page (2026-02-01) lists only Hexa Hosting and Pellet Mail; both published statements become false.",
     "fix": "Publish a new dated Subprocessors version adding Corvid Metrics (product analytics) on or before the notice date, superseding the 2026-02-01 version and retaining it on record.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Compare processor names in the notice with the published table; Corvid Metrics is absent."},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "R",
     "location": "statement_template.md (whole); RICR 4.5",
     "scenario": "Managed-account statements are sent in November without the mandatory sentence 'Compare this information with your official account statement.', breaching RICR 4.5 on every statement.",
     "fix": "Add the 4.5 sentence verbatim, or obtain a written compliance determination that 4.5 does not apply to the official statement.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "reproduction": "Search the template for 'Compare this information': no hits; the same search on rule_extract.md hits (positive control)."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "statement_template.md balance lines",
     "scenario": "With any market gain or loss, opening + contributions - withdrawals - fees does not equal closing; customers cannot reconcile the statement, and adding a returns line would trigger RICR 4.3 unaddressed.",
     "fix": "Add a market-movement line and a reconciliation check; if returns are shown, show them net of fees with the 4.3 past-performance statement.",
     "answers": {"a": true, "b": false, "c": false, "d": true},
     "reproduction": "Opening 10,000, fees 10, market gain 200: closing 10,190 but the visible lines sum to 9,990."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "R",
     "location": "privacy_notice.md 'Analytics (new)'",
     "scenario": "To learn which features are used, the analytics vendor receives account numbers and full transaction histories, more than the stated purpose needs; the notice itself documents the excess.",
     "fix": "Send pseudonymous feature-usage events without account number or transaction history, or state the real purpose and lawful basis.",
     "answers": {"a": true, "b": false, "c": true, "d": false},
     "reproduction": "Compare the stated purpose with the listed data fields."},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "R",
     "location": "privacy_notice.md line 1",
     "scenario": "The opening sentence gives 'to run your account' as the only purpose, omitting the new analytics purpose.",
     "fix": "Amend to '...to run your account and to understand how our services are used (see Analytics).'",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Read line 1 against the Analytics paragraph."},
    {"id": "S1", "status": "needs_validation", "track": "R", "location": "privacy_notice.md",
     "suspicion": "RICR 4.5 may also apply to the privacy notice.",
     "unresolved_fact": "RICR definition of 'communication about a managed account'."},
    {"id": "S2", "status": "needs_validation", "track": "R", "location": "privacy_notice.md 'Analytics (new)'",
     "suspicion": "Corvid Metrics may not be acting purely as a processor.",
     "unresolved_fact": "Terms of the Corvid data processing agreement."},
    {"id": "S3", "status": "needs_validation", "track": "R", "location": "privacy_notice.md 'Analytics (new)'",
     "suspicion": "Analytics on transaction data may require consent or an opt-out.",
     "unresolved_fact": "Governing privacy law and chosen lawful basis."},
    {"id": "S4", "status": "needs_validation", "track": "R", "location": "other published pages",
     "suspicion": "Other published pages may list recipients or purposes this change makes untrue.",
     "unresolved_fact": "Contents of terms, live privacy notice and filings."},
    {"id": "S5", "status": "needs_validation", "track": "R", "location": "statement_template.md {account_number}",
     "suspicion": "Full account numbers may be sent unmasked by email.",
     "unresolved_fact": "Delivery channel and masking policy for statements."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Template breaches RICR 4.3.", "evidence": "No return or performance figure is shown; only cash-flow and balance lines."},
    {"id": "C2", "candidate": "Either document breaches RICR 4.2.", "evidence": "No guarantee, 'safe' or 'risk-free' wording in either document."}
  ]
}
```