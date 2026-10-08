**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent or tools were available, so I could not run, fetch or open anything beyond the four supplied files.

**VERDICT: REWORK.** Publishing the privacy notice as drafted makes a published page false: the notice names Corvid Metrics as a recipient of account data, but Corvid Metrics is not on the published Subprocessors list. The statement template also probably omits a sentence that RICR 4.5 requires.

**CONFIDENCE: medium.** The main finding rests on exact quotes and is solid. Confidence is limited by:
- this being a same-context review with no tools;
- having only an extract of RICR, not the full rule;
- not being told whether the accounts are "managed accounts."

**INPUTS LEDGER**

| Item | Status | Matters? |
|---|---|---|
| request.md, context.md | seen | yes |
| privacy_notice.md, statement_template.md (the work) | seen | yes |
| rule_extract.md, subprocessors_published.md | seen | yes |
| Full RICR text (only paragraphs 4.2, 4.3 and 4.5 were supplied) | not seen | yes: other paragraphs may govern statements |
| The privacy notice currently published (to compare against the draft) | not seen | yes: can't tell what changed or whether anything was dropped |
| Whether accounts are managed accounts under RICR | not seen | yes: decides whether 4.5 applies |
| Contract or data processing agreement with Corvid Metrics | not seen | yes: affects the processor role and the data scope |
| Other published documents (terms, regulatory filings) | not seen | partially: they could repeat the subprocessor statement |

**COVERAGE**
- **Checked:**
  - privacy_notice.md: all three paragraphs
  - statement_template.md: every field and the footer
  - subprocessors_published.md: the opening statement and the table
  - rule_extract.md: paragraphs 4.2, 4.3 and 4.5, applied to both documents
  - The request's instruction to "keep our published pages consistent"
- **Not checked:**
  - the rest of RICR
  - the previously published privacy notice
  - the Corvid contract
  - how the template is rendered and delivered

**SEATS AND GATE**
- Reviewer: this session only. No subagent or cross-vendor seats were available.
- Sensitivity gate passed. The template uses placeholders and contains no real personal data, so cross-vendor seats would have been allowed if available.

**FINDINGS**

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | R | privacy_notice.md, "Analytics (new)" and "Who receives your data"; subprocessors_published.md table | The notice says data is shared "only with the processors listed in our Subprocessors page", then says account number and transaction history go to Corvid Metrics. The published list contains only Hexa Hosting and Pellet Mail. The work includes no update to the Subprocessors page, although the request said to keep published pages consistent. | On 2026-11-01 a customer or the regulator reads both pages. The notice's "only" statement is false, and the subprocessor list understates who receives personal data. | Publish a new, versioned Subprocessors page that adds Corvid Metrics ("analytics of feature usage"). Supersede the 2026-02-01 version rather than editing it in place. Publish it on or before the notice date. **Reproduction:** compare the processors named in the notice against the table; Corvid Metrics is absent. | a✓ b✓ c✓ d✓ |
| F2 | High | PROBABLE | R | statement_template.md (whole template); rule_extract.md 4.5 | RICR 4.5 requires every communication about a managed account to carry "Compare this information with your official account statement." The template does not include it. The footer's "Contact your adviser" suggests these are adviser-managed accounts. | Every monthly statement sent from November onward for a managed account lacks a required statement. This is a repeated breach that the regulator can see. | Add the 4.5 sentence verbatim, or record why 4.5 does not apply (for example, accounts are not managed, or the full rule exempts the official statement itself). **Reproduction:** search the template for the quoted sentence; it is absent. | a✓ b✗ c✓ d✓ |
| F3 | Medium | CONFIRMED | B/R | statement_template.md, balance lines | There is no line for investment gains, losses or income. Opening + Contributions − Withdrawals − Fees will not equal Closing in any month where the market moves. | A customer adds up the lines, finds the totals don't reconcile, and complains or loses trust. If someone later adds a "change in value" line, it becomes performance, and 4.3 then requires it to be shown net of fees with the past-performance sentence. | Add a "Change in value" line so the statement reconciles. If it is presented as performance, show it net of fees and add the 4.3 sentence. **Reproduction:** opening 1000, contributions 100, withdrawals 0, fees 10, market gain 50: the lines sum to 1090 while the closing balance is 1140. | a✓ b✓ c✗ d✓ |
| F4 | Medium | PROBABLE | R | privacy_notice.md, "Analytics (new)" | The notice says the purpose is to "understand which features customers use," yet it sends the full account number and transaction history to a third party. Feature-usage analytics does not need direct identifiers or transaction details. | If Corvid Metrics is breached, account numbers and transaction histories leak for a low-value purpose. The data minimisation choice is also hard to defend if the regulator asks. | Send pseudonymous IDs and feature-usage events instead, then narrow the notice text to match. Confirm the data actually sent matches the notice. **Reproduction:** check the analytics payload specification for account_number and transaction fields. | a✓ b✗ c✗ d✓ |

**NEEDS VALIDATION**
- **S1: does 4.5 apply to the privacy notice too?** The notice is arguably a communication about a managed account. This is settled by the full RICR definition of "communication," plus whether the accounts are managed.
- **S2: should the statement show the full account number?** `{account_number}` is shown unmasked. This is settled by internal policy or the rules on masking identifiers in documents sent by mail or email.
- **S3: is Corvid Metrics really acting as a processor?** It may instead use the data for its own purposes, which would make it a recipient that the notice describes differently. This is settled by the Corvid contract or data processing agreement.
- **S4: was anything dropped from the previous notice?** The draft may have removed sections that are still legally required. This is settled by comparing it against the currently published privacy notice.

**REFUTED**
- **R1: "The statement breaches 4.2."** The template contains no guarantee or "risk-free" wording.
- **R2: "The statement breaches 4.3."** The template shows no performance figures, so 4.3 is not triggered as drafted. This changes if F3's fix adds a performance line.
- **R3: "Statements are sent through an unlisted processor."** Pellet Mail is listed for "sending statements and notices."

**WHAT HOLDS UP**
- The notice openly discloses the new analytics use and names the recipient, rather than hiding it.
- The template shows fees as a separate line.
- Neither document makes a prohibited return or risk claim.
- No invented approval controls appear in either document.
- No text in the work addresses or instructs the reviewer.

**UNVERIFIED CLAIMS**
- **"We do not sell personal data."** Confirm by checking the commercial terms with all processors, including Corvid Metrics.
- **"which analyzes it for us"** (that is, Corvid acts only on the firm's behalf). Confirm against the Corvid contract.

**QUESTIONS FOR THE AUTHOR**
1. Are these managed accounts under RICR?
2. Will the Subprocessors page be republished with Corvid Metrics before 2026-11-01?
3. Does the analytics feature need account numbers and transaction histories, or would pseudonymous usage events do?

**DECISION-MAKER SUMMARY**
Do not publish yet. First republish the Subprocessors page with Corvid Metrics (F1), and add or justify the RICR 4.5 sentence in the statement (F2). Publishing as drafted makes a public privacy statement false on day one and probably repeats a regulatory omission on every monthly statement.

**OWNER SUMMARY**
The new privacy notice says we share data only with companies on our published list, but the new analytics company isn't on that list yet. The list needs updating before the notice goes live. The monthly statement also seems to be missing a sentence the rules require, and its figures won't add up because it has no line for changes in investment value.

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
    {"item": "full RICR text", "status": "not_seen", "matters": true},
    {"item": "currently published privacy notice", "status": "not_seen", "matters": true},
    {"item": "managed-account status of accounts", "status": "not_seen", "matters": true},
    {"item": "Corvid Metrics contract/DPA", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Template placeholders only; no real personal data supplied."},
  "coverage": {
    "checked": [
      {"unit": "privacy_notice.md", "kind": "file"},
      {"unit": "statement_template.md", "kind": "file"},
      {"unit": "rule_extract.md", "kind": "file"},
      {"unit": "subprocessors_published.md", "kind": "file"},
      {"unit": "RICR 4.2, 4.3, 4.5 applied to both documents", "kind": "section"},
      {"unit": "Request: keep published pages consistent", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "full RICR text", "reason": "not supplied"},
      {"unit": "currently published privacy notice", "reason": "not supplied"},
      {"unit": "Corvid Metrics contract/DPA", "reason": "not supplied"},
      {"unit": "template rendering and delivery", "reason": "not supplied; no tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "R",
     "location": "privacy_notice.md 'Analytics (new)' and 'Who receives your data'; subprocessors_published.md table",
     "scenario": "On 2026-11-01 the notice says data goes only to listed processors and also sends account number and transaction history to Corvid Metrics, which is absent from the published Subprocessors list; the published statement is false to customers and the regulator.",
     "fix": "Publish a new versioned Subprocessors page adding Corvid Metrics (superseding the 2026-02-01 version) on or before the notice date.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Compare processors named in privacy_notice.md against the subprocessors_published.md table; Corvid Metrics is missing."},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "R",
     "location": "statement_template.md (whole template); rule_extract.md 4.5",
     "scenario": "If accounts are managed (the footer refers to 'your adviser'), every monthly statement from November omits the RICR 4.5 required sentence.",
     "fix": "Add 'Compare this information with your official account statement.' verbatim, or document why 4.5 does not apply.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "reproduction": "Search statement_template.md for the 4.5 sentence; it is absent."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "statement_template.md balance lines",
     "scenario": "With any market movement, opening + contributions - withdrawals - fees does not equal closing; customers see a statement that does not reconcile.",
     "fix": "Add a change-in-value line; if presented as performance, show it net of fees with the RICR 4.3 sentence.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Opening 1000, contributions 100, withdrawals 0, fees 10, gain 50: lines sum to 1090, closing shows 1140."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "R",
     "location": "privacy_notice.md 'Analytics (new)'",
     "scenario": "Account numbers and transaction histories are sent to a third party for feature-usage analytics that does not need them; a breach at Corvid Metrics exposes them.",
     "fix": "Send pseudonymous IDs and usage events only, and narrow the notice text to match.",
     "answers": {"a": true, "b": false, "c": false, "d": true},
     "reproduction": "Inspect the analytics payload specification for account_number and transaction fields."},
    {"id": "S1", "status": "needs_validation", "track": "R", "location": "privacy_notice.md",
     "suspicion": "RICR 4.5 sentence may also be required in the privacy notice.",
     "unresolved_fact": "Full RICR definition of 'communication' and whether accounts are managed."},
    {"id": "S2", "status": "needs_validation", "track": "R", "location": "statement_template.md {account_number}",
     "suspicion": "Full account number shown unmasked on a mailed or emailed statement.",
     "unresolved_fact": "Internal masking policy or rule for identifiers in delivered documents."},
    {"id": "S3", "status": "needs_validation", "track": "R", "location": "privacy_notice.md 'which analyzes it for us'",
     "suspicion": "Corvid Metrics may use the data for its own purposes rather than as a processor.",
     "unresolved_fact": "Terms of the Corvid Metrics contract or DPA."},
    {"id": "S4", "status": "needs_validation", "track": "R", "location": "privacy_notice.md",
     "suspicion": "The draft may drop sections present in the currently published notice.",
     "unresolved_fact": "Comparison against the currently published privacy notice."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Statement template breaches RICR 4.2.", "evidence": "No guarantee or risk-free wording appears in the template."},
    {"id": "R2", "candidate": "Statement template breaches RICR 4.3.", "evidence": "No performance figures are shown, so 4.3 is not triggered as drafted."},
    {"id": "R3", "candidate": "Statements are sent through an unlisted processor.", "evidence": "Pellet Mail is listed for 'sending statements and notices'."}
  ]
}
```