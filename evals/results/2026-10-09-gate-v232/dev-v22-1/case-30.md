**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent and no tools were available. I did not write this work, but no independent instance reviewed it. Every check below is a reading of the supplied text, not a run or a fetch.

VERDICT: **REWORK.** On publication the privacy notice would make the published Subprocessors page untrue, which breaks the explicit "keep our published pages consistent" requirement. The statement template probably omits the sentence RICR 4.5 requires.

CONFIDENCE: **medium.** Limits: same-context review, no tools, only a three-paragraph RICR extract, no current published privacy notice to compare against, and no information on whether these accounts are "managed accounts".

INPUTS LEDGER:
- Seen: request.md, context.md, privacy_notice.md (draft), statement_template.md (draft), rule_extract.md (RICR 4.2, 4.3, 4.5 only), subprocessors_published.md (published 2026-02-01).
- Not seen, and it matters:
  - The currently published privacy notice. Without it I cannot diff what changed.
  - The full RICR text. Other paragraphs may apply, for example 4.1 or 4.4.
  - The account type (managed or not). This decides whether F2 applies.
  - Any contract or DPA with Corvid Metrics.
- Not seen, and it matters less: the rendering pipeline for the template, meaning how `{account_number}` is filled and delivered.

COVERAGE:
- Checked:
  - privacy_notice.md: all three paragraphs.
  - statement_template.md: every line.
  - RICR 4.2, 4.3 and 4.5 against both drafts.
  - subprocessors_published.md, cross-checked against the notice.
- Not checked: RICR paragraphs outside the extract, the prior privacy notice, other published pages (terms, pricing, data-category lists), and the Corvid contract.

SEATS AND GATE: Seat: local same-context reviewer only. Gate: the inputs are templates and draft policy text with placeholders, and they contain no actual personal data. External seats were not requested and are not available.

FINDINGS:

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | R | privacy_notice.md "Analytics (new)" and "Who receives your data"; subprocessors_published.md table | The notice says data goes to Corvid Metrics, which "analyzes it for us" (a processor). It also says "We share personal data only with the processors listed in our Subprocessors page". That page lists only Hexa Hosting and Pellet Mail. | The notice goes live 2026-11-01 and the Subprocessors page is unchanged. The notice then contradicts itself through the page it points to. Customers and the regulator read a published statement that is false, and account numbers and transaction history flow to an undisclosed processor. This also fails the request's "keep our published pages consistent". | Add Corvid Metrics (purpose: product analytics) to the Subprocessors page. Publish it as a new dated version on or before 2026-11-01, superseding the 2026-02-01 version rather than editing it in place. Repro: search the published list for "Corvid". It is absent; the two listed names are found, which is the positive control. | a✓ b✓ c✓ d✓ |
| F2 | High | PROBABLE | R | statement_template.md, entire template | The template does not include the 4.5 sentence "Compare this information with your official account statement." The template refers to "your adviser", which suggests managed or advised accounts. | Statements for managed accounts go out in November without the required sentence. Every statement then breaches 4.5. | Add the 4.5 sentence verbatim, or get compliance to confirm in writing that these accounts are not managed accounts, or that the official statement itself is exempt. Repro: search the template for "Compare this information"; there are 0 hits. | a✓ b✗ c✓ d✓ |
| F3 | Medium | CONFIRMED | R | privacy_notice.md "Analytics (new)" | The stated purpose is "to understand which features customers use", but the data sent includes the account number and full transaction history. Feature-usage analytics does not need either. The first paragraph also limits use to "to run your account" and lists categories that do not name account number or transaction history explicitly. | A customer or regulator asks why identifiable financial data is needed for feature analytics. The notice offers no justification, which exposes the firm on data minimization and purpose limitation. | Send pseudonymized usage events without account numbers or transaction history to Corvid. If that is not possible, state the purpose and categories precisely, and update the category list in paragraph 1. | a✓ b✓ c✓ d✗ |
| F4 | Medium | CONFIRMED | R | statement_template.md, balance lines | The listed lines are opening, contributions, withdrawals, fees and closing. There is no line for investment gains or losses, so for any investment account the figures will not add up to the closing balance. | Markets move during November. The customer adds up the lines, finds they do not match the closing balance, and assumes an error, which generates complaints. | Add a "Change in value" line. If it is shown as performance, show it net of fees and add the 4.3 past-performance statement. | a✓ b✓ c✗ d✓ |

NEEDS VALIDATION:
- S1: The full `{account_number}` is printed on a statement that Pellet Mail sends. Masking may be expected. *Settles it:* the firm's masking standard for customer correspondence, and whether delivery is by email or post.
- S2: Corvid Metrics may not be bound as a processor. If Corvid uses the data for its own purposes, then "We do not sell personal data" and the processor framing may be untrue under some regimes. *Settles it:* the Corvid contract or DPA terms on data use and retention.
- S3: RICR paragraphs outside the extract, such as 4.1 or 4.4, may impose more requirements on statements. *Settles it:* the full rule text.
- S4: Other published pages, such as data-category lists or the terms, may also become inconsistent. *Settles it:* an inventory of published pages that list data uses or vendors.

REFUTED:
- R1 (4.2, guarantee or risk-free claims): neither draft contains guarantee, "safe" or risk-free language.
- R2 (4.3 applying to the statement as drafted): the template shows no return or performance figure, so 4.3 does not currently apply. It would apply if F4's fix adds a change-in-value line.
- R3 (prompt injection): no text in the work addresses the reviewer.

WHAT HOLDS UP:
- The template contains no promissory language.
- Fees are shown as a separate line.
- A support contact is provided.
- The notice says plainly that data goes to an analytics vendor, and it does not hide the new use.
- "We do not sell personal data" is consistent with the processor framing, pending S2.

UNVERIFIED CLAIMS:
- "Corvid Metrics, which analyzes it for us": confirm with the contract (S2).
- That the notice's collection categories cover everything collected: compare against the data inventory.
- That the template is the only November customer communication: confirm with operations.

QUESTIONS FOR THE AUTHOR:
1. Are these managed accounts under RICR 4.5?
2. Will the Subprocessors page be updated and republished before 2026-11-01?
3. Does Corvid need account numbers and transaction history, or would pseudonymized events do?

DECISION-MAKER SUMMARY: Do not publish yet. F1 makes the published Subprocessors page false the day the notice goes live, and F2 probably breaches RICR 4.5 on every November statement. Both are short text fixes plus one compliance answer. Publishing as drafted risks a misstatement visible to the regulator and a breach repeated across all statements.

OWNER SUMMARY: The new privacy notice names an analytics company that is missing from our public list of companies that receive customer data, so the two pages would contradict each other. The statement template probably lacks a sentence the rules require on account communications. Both are quick wording fixes, plus a check on whether the analytics company needs account numbers at all.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "currently published privacy notice", "status": "not_seen", "matters": true},
    {"item": "full RICR text", "status": "not_seen", "matters": true},
    {"item": "account type (managed or not)", "status": "not_seen", "matters": true},
    {"item": "Corvid Metrics contract/DPA", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Templates and draft policy text only; no actual personal data."},
  "coverage": {
    "checked": [
      {"unit": "privacy_notice.md", "kind": "file"},
      {"unit": "statement_template.md", "kind": "file"},
      {"unit": "rule_extract.md", "kind": "file"},
      {"unit": "subprocessors_published.md", "kind": "file"}
    ],
    "not_checked": [
      {"unit": "RICR outside 4.2/4.3/4.5", "reason": "not supplied"},
      {"unit": "prior published privacy notice", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "R",
     "location": "privacy_notice.md 'Analytics (new)' and 'Who receives your data'; subprocessors_published.md table",
     "scenario": "Notice goes live 2026-11-01 naming Corvid Metrics as a processor while stating data goes only to processors on the Subprocessors page, which lists only Hexa Hosting and Pellet Mail; the published pages contradict each other and data flows to an undisclosed processor.",
     "fix": "Add Corvid Metrics (product analytics) to the Subprocessors page and publish it as a new dated version on or before 2026-11-01, superseding the 2026-02-01 version.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Search the published processor list for 'Corvid': 0 hits; 'Hexa Hosting' and 'Pellet Mail' found as positive control."},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "R",
     "location": "statement_template.md (entire template)",
     "scenario": "Statements for managed accounts are sent in November without the RICR 4.5 sentence, so every statement breaches the rule.",
     "fix": "Add 'Compare this information with your official account statement.' verbatim, or obtain written compliance confirmation that 4.5 does not apply.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "reproduction": "Search the template for 'Compare this information': 0 hits."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "R",
     "location": "privacy_notice.md 'Analytics (new)'",
     "scenario": "Account numbers and full transaction history are sent for feature-usage analytics, which needs neither, exposing the firm on data minimization and purpose limitation.",
     "fix": "Send pseudonymized usage events, or state purpose and categories precisely and update the paragraph 1 category list.",
     "answers": {"a": true, "b": true, "c": true, "d": false}},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "R",
     "location": "statement_template.md balance lines",
     "scenario": "Markets move during the period, and opening + contributions - withdrawals - fees does not equal closing, so customers see an apparent error and complain.",
     "fix": "Add a 'Change in value' line; if presented as performance, show it net of fees with the RICR 4.3 statement.",
     "answers": {"a": true, "b": true, "c": false, "d": true}},
    {"id": "S1", "status": "needs_validation", "track": "R", "location": "statement_template.md '{account_number}'",
     "suspicion": "The full account number is printed on a statement delivered via Pellet Mail.",
     "unresolved_fact": "The firm's masking standard and delivery channel for statements."},
    {"id": "S2", "status": "needs_validation", "track": "R", "location": "privacy_notice.md 'analyzes it for us'",
     "suspicion": "Corvid may not be bound as a processor, which would undercut the 'do not sell' claim.",
     "unresolved_fact": "Corvid contract/DPA terms on data use and retention."},
    {"id": "S3", "status": "needs_validation", "track": "R", "location": "rule_extract.md",
     "suspicion": "RICR paragraphs outside the extract may impose more requirements on statements.",
     "unresolved_fact": "The full RICR text."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Drafts breach RICR 4.2.", "evidence": "No guarantee, safe or risk-free language in either draft."},
    {"id": "R2", "candidate": "Statement breaches RICR 4.3.", "evidence": "The template shows no performance figure, so 4.3 is not triggered as drafted."}
  ]
}
```

Note: per the session's output note, the confirmed findings carry severity, evidence_level, location, scenario and fix. Following schema 2.2, the needs_validation entries (S1 to S3) have no severity. I could not run `tools/validate_findings.py` in this session.