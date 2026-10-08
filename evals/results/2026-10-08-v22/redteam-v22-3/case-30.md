**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent or tools were available in this session, so nothing below was run or opened beyond the supplied text.

VERDICT: **REWORK**. On publication the privacy notice would be false, because it names a processor that is missing from the published Subprocessors list it points to, and the statement template appears to omit the sentence RICR 4.5 requires.

CONFIDENCE: **medium**. Limited by the same-context review, no tools, an extract of RICR rather than the full rule, and no confirmation of whether these statements cover managed accounts.

INPUTS LEDGER:
- Seen: request.md, context.md, privacy_notice.md (draft), statement_template.md (draft), rule_extract.md (RICR 4.2, 4.3, 4.5 only), subprocessors_published.md (2026-02-01).
- Not seen:
  - Full RICR text. **Matters**: other sections such as 4.1 and 4.4 could add required statements.
  - The current published privacy notice, so I cannot diff what changed. Partly matters.
  - The Corvid Metrics agreement or DPA. **Matters** for F2 and S1.
  - Which account types receive this statement. **Matters** for F3.
  - The applicable privacy law and any advance-notice requirement. **Matters** for S1.

COVERAGE:
- Checked: every sentence of privacy_notice.md; every line of statement_template.md; RICR 4.2, 4.3 and 4.5 against both documents; the processor list against the notice.
- Not checked: RICR sections outside the extract; the Corvid contract; privacy-law obligations; how the published pages are versioned.

SEATS AND GATE: Local reviewer only (ran). No cross-vendor seats were requested or used. Sensitivity gate passed: the documents are templates with placeholders and contain no personal or confidential data.

FINDINGS:

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | R | privacy_notice.md "Analytics (new)" and "Who receives your data"; subprocessors_published.md table | The notice says data is shared "only with the processors listed in our Subprocessors page", then names Corvid Metrics. The published list (2026-02-01) contains only Hexa Hosting and Pellet Mail. | The notice goes live on 2026-11-01 and Corvid starts receiving account numbers and transaction history. Both published pages are now untrue. A customer or the regulator reading them together sees an undisclosed processor. This is the "keep our published pages consistent" requirement failing. | Publish a new, dated version of the Subprocessors page that adds Corvid Metrics (purpose: product analytics). Supersede the 2026-02-01 version rather than editing it in place. Do this before or alongside the notice, and before any data flows. Reproduction: compare the processor names in the notice with the published table. "Corvid Metrics" is absent. | a✓ b✓ c✓ d✓ |
| F3 | High | PROBABLE | R | statement_template.md (whole file); rule_extract.md 4.5 | The template does not contain the sentence "Compare this information with your official account statement." RICR 4.5 requires it on every communication about a managed account. "Contact your adviser" suggests these accounts are adviser-managed. | November statements go to managed-account customers without the mandatory sentence, which is a breach of RICR 4.5 on every statement sent. | Add the exact sentence verbatim, or record why 4.5 does not apply (for example, the account type is not managed). Reproduction: search the template for the 4.5 sentence. No match. | a✓ b✗ c✓ d✓ |
| F2 | Medium | CONFIRMED | R | privacy_notice.md "Analytics (new)" | The notice says account number and full transaction history go to an analytics vendor "to understand which features customers use". Feature-usage analytics does not need account numbers or transaction history. | Corvid holds directly identifying financial data it does not need. A breach or misuse at the vendor exposes customers' account numbers and transactions, beyond what the stated purpose justifies. | Send only pseudonymised identifiers and feature events. Then narrow the notice text to match. If the full data really is needed, state why. | a✓ b✓ c✗ d✗ |
| F4 | Medium | CONFIRMED | R | statement_template.md balance lines | There is no line for investment gain or loss, so opening + contributions − withdrawals − fees will not equal closing whenever market value changes. | A customer cannot reconcile their statement, which leads to complaints and support load. If a "change in value" line is added, it becomes performance and RICR 4.3 applies: it must be net of fees and carry the past-performance statement. | Add a "Change in market value" line. If it is shown as a return, present it net of fees and add the 4.3 statement. Reproduction: opening 100, contributions 0, withdrawals 0, fees 1, market gain 5 gives closing 104, which the lines shown sum to 99. | a✓ b✓ c✗ d✓ |
| F5 | Low | CONFIRMED | R | privacy_notice.md line 1 | The purpose statement ("to run your account") no longer covers all uses now that account activity is also used for analytics. | A reader of the opening sentence believes activity is used only to run the account. | Extend the purpose list to include product analytics. | a✓ b✓ c✗ d✗ |

NEEDS VALIDATION:
- **S1 (privacy_notice.md, analytics)**: Whether a lawful basis, consent, or advance notice to customers is required before sharing with Corvid. Settled by the applicable privacy law and the Corvid DPA.
- **S2 (statement_template.md)**: Whether RICR sections outside the extract impose further required statements on account statements. Settled by the full RICR text.

REFUTED:
- **C1: the statement breaches RICR 4.3.** The template shows balances and fees, not performance or returns, so 4.3 is not triggered as drafted. It becomes relevant only if F4's fix adds a return figure.
- **C2: either document breaches RICR 4.2.** Neither document contains guarantee or "risk-free" language.

WHAT HOLDS UP:
- Neither document makes a return guarantee or risk claim (RICR 4.2).
- Fees are shown as a separate line on the statement.
- The notice clearly names the new recipient and the purpose, rather than hiding the change.
- "We do not sell personal data" does not conflict with anything supplied.

UNVERIFIED CLAIMS:
- "Corvid Metrics, which analyzes it for us" assumes Corvid acts as a processor, not a controller. Confirm from the contract.
- "We do not sell personal data" cannot be checked without the commercial terms with Corvid.

QUESTIONS FOR THE AUTHOR:
1. Do these statements go to managed-account customers? This settles F3.
2. Will the Subprocessors page be republished before 2026-11-01?
3. Does Corvid actually need account numbers and transaction history?
4. Have you checked the full RICR text, not only the extract?

DECISION-MAKER SUMMARY: Do not publish yet. The privacy notice names a vendor that the published Subprocessors list omits (F1), and the statement likely lacks the RICR 4.5 sentence (F3). Fix both, republish the processor list as a new dated version, and confirm the account type. Proceeding as drafted makes both pages untrue to customers and the regulator from day one.

OWNER SUMMARY: The new privacy notice mentions an analytics company that is missing from our public list of companies we share data with, so the two pages contradict each other and the list must be updated first. The monthly statement appears to be missing a sentence that the investment rules require on managed-account communications. We should also check whether the analytics company really needs account numbers and transaction history, and add a line so statement balances add up.

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
    {"item": "Full RICR text", "status": "not_seen", "matters": true},
    {"item": "Currently published privacy notice", "status": "not_seen", "matters": false},
    {"item": "Corvid Metrics agreement/DPA", "status": "not_seen", "matters": true},
    {"item": "Account types receiving the statement", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Templates and policy text with placeholders; no personal or confidential data."},
  "coverage": {
    "checked": [
      {"unit": "privacy_notice.md", "kind": "file"},
      {"unit": "statement_template.md", "kind": "file"},
      {"unit": "rule_extract.md", "kind": "file"},
      {"unit": "subprocessors_published.md", "kind": "file"},
      {"unit": "RICR 4.2", "kind": "claim"},
      {"unit": "RICR 4.3", "kind": "claim"},
      {"unit": "RICR 4.5", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "RICR sections outside the extract", "reason": "not supplied"},
      {"unit": "Corvid Metrics agreement", "reason": "not supplied"},
      {"unit": "Applicable privacy law notice requirements", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "R",
     "location": "privacy_notice.md 'Analytics (new)' and 'Who receives your data'; subprocessors_published.md table",
     "scenario": "On 2026-11-01 the notice names Corvid Metrics as a recipient while promising sharing only with listed processors; the published list names only Hexa Hosting and Pellet Mail, so both published pages are untrue.",
     "fix": "Publish a new dated Subprocessors version adding Corvid Metrics (superseding 2026-02-01, not editing in place) before data flows.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Compare processor names in privacy_notice.md with subprocessors_published.md; Corvid Metrics is absent."},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "R",
     "location": "statement_template.md (whole file); rule_extract.md 4.5",
     "scenario": "November statements to adviser-managed accounts are sent without the RICR 4.5 mandatory sentence, breaching the rule on every statement.",
     "fix": "Add verbatim: \"Compare this information with your official account statement.\" or document why 4.5 does not apply.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "reproduction": "Search statement_template.md for the 4.5 sentence; no match."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "R",
     "location": "privacy_notice.md 'Analytics (new)'",
     "scenario": "Account numbers and full transaction history are sent to an analytics vendor for feature-usage analysis; a vendor breach exposes identifying financial data not needed for the stated purpose.",
     "fix": "Send pseudonymised IDs and feature events only, and narrow the notice text, or justify the full data set.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "R",
     "location": "statement_template.md balance lines",
     "scenario": "With a market gain or loss, opening + contributions - withdrawals - fees does not equal closing, so customers cannot reconcile the statement.",
     "fix": "Add a 'Change in market value' line; if presented as a return, show it net of fees with the RICR 4.3 statement.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Opening 100, fees 1, market gain 5: closing 104, but the listed lines sum to 99."},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "R",
     "location": "privacy_notice.md line 1",
     "scenario": "The opening purpose statement says activity is used to run the account, omitting the new analytics use.",
     "fix": "Extend the purpose statement to include product analytics.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "R", "location": "privacy_notice.md 'Analytics (new)'",
     "suspicion": "Sharing with Corvid may need a lawful basis, consent or advance customer notice.",
     "unresolved_fact": "The applicable privacy law requirements and the Corvid DPA terms."},
    {"id": "S2", "status": "needs_validation", "track": "R", "location": "statement_template.md",
     "suspicion": "RICR sections outside the extract may require further statements.",
     "unresolved_fact": "The full RICR text."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Statement breaches RICR 4.3 (performance net of fees and past-performance statement).",
     "evidence": "Template shows balances and fees only, no performance or return figure; 4.3 is not triggered as drafted."},
    {"id": "C2", "candidate": "Either document breaches RICR 4.2 (guarantee or risk-free claims).",
     "evidence": "Neither document contains guarantee, 'safe' or risk-free language."}
  ]
}
```