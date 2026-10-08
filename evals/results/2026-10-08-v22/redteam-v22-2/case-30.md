**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** This session has no tools, so no subagent or other reviewer ran. I did not write the work, which lowers the anchoring risk.

**VERDICT: REWORK.** The new privacy notice sends account numbers and transaction history to Corvid Metrics, but the published Subprocessors page it relies on does not list Corvid, so both pages would be untrue on 2026-11-01.

**CONFIDENCE: medium.** The main finding rests on exact quotes. Confidence is limited because:
- this was a single reviewer with no tools,
- I only had an extract of RICR, and
- nothing says whether these accounts are "managed accounts" under RICR 4.5.

**INPUTS LEDGER**
- **Seen:**
  - request.md
  - context.md
  - privacy_notice.md (the draft)
  - rule_extract.md (RICR 4.2, 4.3 and 4.5 only)
  - statement_template.md
  - subprocessors_published.md (published 2026-02-01)
- **Not seen, and it matters:**
  - **Full RICR text.** Paragraphs 4.1 and 4.4 and any definitions, including the definition of "managed account", are missing. Applying 4.5 depends on them.
  - **The account type.** Nothing says whether the accounts are managed. This decides whether 4.5 applies.
  - **The agreement with Corvid Metrics.** It decides whether Corvid is a processor and whether "we do not sell" stays true.
  - **The governing privacy law.** It decides whether sharing this much data for analytics is allowed.
- **Not seen, and it does not change the verdict:**
  - The currently published privacy notice. Only the draft was supplied, so I could not compare versions.

**COVERAGE**
- **Checked:**
  - privacy_notice.md: all three paragraphs
  - statement_template.md: every line
  - subprocessors_published.md: the processor list
  - rule_extract.md: 4.2, 4.3 and 4.5, each applied to both documents
  - The "keep published pages consistent" part of the request
- **Not checked:**
  - RICR paragraphs not in the extract
  - Other published pages: terms, fee schedule, the rest of the privacy notice
  - How statements are actually rendered and delivered

**SEATS AND GATE**
- **Reviewers:** only this reviewer ran. No subagent tool and no cross-vendor seats were available in this session, so none were refused.
- **Sensitivity gate:** not sensitive. The documents are templates and drafts that use placeholders, with no real personal data.
- **Injection check:** no text in the work addresses the reviewer.

### FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | R | privacy_notice.md, "Analytics (new)" and "Who receives your data"; subprocessors_published.md, the table | The notice sends "your account number and transaction history, to Corvid Metrics". It then promises "We share personal data only with the processors listed in our Subprocessors page". That page lists only Hexa Hosting and Pellet Mail. The work contains no update to the Subprocessors page, even though the request says "keep our published pages consistent". | On 2026-11-01 the notice goes live and Corvid starts receiving data. A customer or regulator who reads the Subprocessors page sees a promise that is false, and the notice contradicts itself. This creates regulatory and customer exposure. The request is not met. | **Fix:** publish a new, dated version of the Subprocessors page that adds "Corvid Metrics, product analytics". Publish it on or before the day sharing starts. Supersede the 2026-02-01 version rather than editing it in place. **Reproduction:** compare the processors named in the notice {Hexa, Pellet, Corvid} with the published list {Hexa, Pellet}. Corvid is missing. | a Y, b Y, c Y, d Y |
| F2 | High | PROBABLE | R | statement_template.md, the whole template; RICR 4.5 | The template does not contain the sentence 4.5 requires: "Compare this information with your official account statement." "Contact your adviser" suggests advised or managed accounts, which would bring the template under 4.5. | Every November statement goes out without a sentence the rule requires, and the breach repeats across every account. This applies if the accounts are managed accounts under RICR. | **Fix:** confirm the account type. If 4.5 applies, add the sentence word for word, and get compliance to confirm how it applies when the document *is* the statement. **Reproduction:** search the template for the 4.5 sentence; there is no match. | a Y, b N, c Y, d Y |
| F3 | Medium | PROBABLE | R | privacy_notice.md, "Analytics (new)" | The stated purpose is "to understand which features customers use". That purpose does not need account numbers or transaction history. Sharing them is more than the purpose requires, and the notice offers no opt-out. The opening sentence also says the data is collected "to run your account", but analytics is a different purpose. | A customer or regulator asks why feature-usage analytics needs full financial history. Under data-minimisation rules this cannot be justified. A breach at Corvid would expose financial records. | **Fix:** send pseudonymous IDs and feature events only. Otherwise, justify each field, state the purpose and legal basis, and add an opt-out if the law requires one. **Reproduction:** for each field sent, check whether the stated purpose needs it. The account number and transaction history fail that check. | a Y, b N, c N, d Y |
| F4 | Medium | PROBABLE | B/R | statement_template.md, the balance lines | The statement has no line for investment gain or loss, or change in market value. For an investment account, opening + contributions − withdrawals − fees will not equal the closing balance. | A customer cannot reconcile their own statement and contacts support or complains. Note: adding a performance figure would bring in RICR 4.3, which requires showing it net of fees with a past-performance warning. | **Fix:** add a "Change in market value" line. If returns are shown, follow 4.3. **Reproduction:** opening 1000, contributions 0, withdrawals 0, fees 10, market gain 50 gives closing 1040. The template's lines add up to 990. | a Y, b N, c N, d Y |

### NEEDS VALIDATION
- **S1, Corvid's role.** Is Corvid a processor that acts only on our instructions, or does it use the data for its own purposes? This decides whether "We do not sell personal data" is still true. It is settled by the agreement with Corvid and whether it restricts Corvid's own use of the data.
- **S2, 4.5 and the privacy notice.** Does RICR 4.5 apply to the privacy notice? It is settled by the RICR definition of "communication about a managed account" and whether general data-handling notices count.
- **S3, account number on the statement.** `{account_number}` is shown in full. Does a firm policy or rule require masking it on documents sent by Pellet Mail? It is settled by the firm's data-handling policy or the relevant rule.
- **S4, other RICR paragraphs.** Do RICR paragraphs not in the extract impose more requirements, such as a firm identifier or complaints wording? It is settled by the full rule text.

### REFUTED
- **C1: the statement breaches 4.3 (performance net of fees).** Refuted: the template shows no performance figure, return or yield. 4.3 only applies if one is added (see F4).
- **C2: either document breaches 4.2 (guarantees or "risk-free").** Refuted: neither document contains wording about a guarantee, safety or freedom from risk.

### WHAT HOLDS UP
- The privacy notice does disclose the new analytics sharing, with the recipient and the data categories, rather than hiding it.
- "We do not sell personal data" is consistent with Corvid "analyz[ing] it for us", subject to S1.
- The statement makes no prohibited claims under 4.2 or 4.3.
- The effective date of 2026-11-01 is consistent across both documents.

### UNVERIFIED CLAIMS
- **"Corvid Metrics … analyzes it for us"** is a processor relationship that is asserted, not shown. To confirm it, read the agreement with Corvid.
- **The Subprocessors page "published 2026-02-01" is still the live version.** To confirm it, check the live page on the publication date.

### QUESTIONS FOR THE AUTHOR
1. Are these accounts "managed accounts" under RICR? This decides whether F2 applies.
2. Will the Subprocessors page be updated and published before Corvid receives any data?
3. Does the analytics feature actually need account numbers and transaction history?

### DECISION-MAKER SUMMARY
- Do not publish yet. The privacy notice names a recipient that the published Subprocessors page leaves out, so the "only the listed processors" promise would be false from day one.
- Update and publish the Subprocessors page first, and confirm whether the 4.5 sentence must go on statements.
- If you proceed anyway, you risk a regulatory finding and customer complaints over a privacy statement that is false.

### OWNER SUMMARY
The updated privacy notice says customer data goes to a new analytics company. However, our public list of companies that receive customer data does not include it, so the two pages contradict each other. The statement template may also be missing a sentence the rules require on account communications, and its balance lines do not add up for investment accounts. Fix the list, confirm the required sentence, and then publish.

I could not run `python3 tools/validate_findings.py` in this session, so the block below has not been checked against the schema.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "privacy_notice.md", "status": "seen", "matters": true},
    {"item": "rule_extract.md", "status": "seen", "matters": true},
    {"item": "statement_template.md", "status": "seen", "matters": true},
    {"item": "subprocessors_published.md", "status": "seen", "matters": true},
    {"item": "Full RICR text and managed-account definition", "status": "not_seen", "matters": true},
    {"item": "Account type (managed or not)", "status": "not_seen", "matters": true},
    {"item": "Corvid Metrics agreement", "status": "not_seen", "matters": true},
    {"item": "Governing privacy law", "status": "not_seen", "matters": true},
    {"item": "Currently published privacy notice", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Templates and drafts with placeholders; no real personal data."},
  "coverage": {
    "checked": [
      {"unit": "privacy_notice.md", "kind": "file"},
      {"unit": "statement_template.md", "kind": "file"},
      {"unit": "subprocessors_published.md", "kind": "file"},
      {"unit": "rule_extract.md", "kind": "file"},
      {"unit": "RICR 4.2, 4.3, 4.5 applied to both documents", "kind": "claim"},
      {"unit": "Consistency of published pages", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "RICR paragraphs outside the extract", "reason": "not supplied"},
      {"unit": "Other published pages (terms, fees, full privacy notice)", "reason": "not supplied"},
      {"unit": "Statement rendering and delivery", "reason": "no tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "R",
     "location": "privacy_notice.md 'Analytics (new)' and 'Who receives your data'; subprocessors_published.md table",
     "scenario": "On 2026-11-01 account numbers and transaction history go to Corvid Metrics while the notice promises sharing only with processors on the Subprocessors page, which lists only Hexa Hosting and Pellet Mail; the published pages are false and inconsistent.",
     "fix": "Publish a new dated Subprocessors version adding Corvid Metrics (product analytics) on or before the sharing start date, superseding the 2026-02-01 version.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Compare the processors named in the notice {Hexa, Pellet, Corvid} with the published list {Hexa, Pellet}; Corvid is missing."},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "R",
     "location": "statement_template.md (entire); RICR 4.5",
     "scenario": "If accounts are managed accounts (template refers to 'your adviser'), every November statement omits the sentence RICR 4.5 requires, a repeated regulatory breach.",
     "fix": "Confirm the account type; if 4.5 applies, add 'Compare this information with your official account statement.' verbatim and get compliance sign-off on how it applies to the statement itself.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "reproduction": "Search statement_template.md for the 4.5 sentence; no match."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "R",
     "location": "privacy_notice.md 'Analytics (new)'",
     "scenario": "Feature-usage analytics receives account numbers and full transaction history, more than the stated purpose needs, with no opt-out and outside the 'to run your account' purpose; this is hard to justify under data-minimisation rules and raises the impact of a breach at Corvid.",
     "fix": "Send pseudonymous IDs and feature events only, or justify each field and state the purpose, legal basis and any opt-out.",
     "answers": {"a": true, "b": false, "c": false, "d": true},
     "reproduction": "For each field sent, check whether the stated purpose needs it; account number and transaction history fail."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "statement_template.md balance lines",
     "scenario": "With market movement, opening + contributions - withdrawals - fees does not equal closing, so customers cannot reconcile their statements.",
     "fix": "Add a 'Change in market value' line; if returns are shown, show them net of fees with the past-performance warning (RICR 4.3).",
     "answers": {"a": true, "b": false, "c": false, "d": true},
     "reproduction": "Opening 1000, fees 10, market gain 50 gives closing 1040; the template's lines sum to 990."},
    {"id": "S1", "status": "needs_validation", "track": "R", "location": "privacy_notice.md 'We do not sell personal data'",
     "suspicion": "Corvid may use the data for its own purposes, which would make the no-sale statement untrue.",
     "unresolved_fact": "Whether the Corvid agreement restricts Corvid to processing on our instructions."},
    {"id": "S2", "status": "needs_validation", "track": "R", "location": "privacy_notice.md; RICR 4.5",
     "suspicion": "The privacy notice may also need the 4.5 sentence.",
     "unresolved_fact": "The RICR definition of 'communication about a managed account'."},
    {"id": "S3", "status": "needs_validation", "track": "R", "location": "statement_template.md 'Account: {account_number}'",
     "suspicion": "The full account number may need masking on mailed documents.",
     "unresolved_fact": "The firm's masking policy or the applicable rule."},
    {"id": "S4", "status": "needs_validation", "track": "R", "location": "rule_extract.md",
     "suspicion": "RICR paragraphs outside the extract may impose further requirements.",
     "unresolved_fact": "The full RICR text."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The statement breaches RICR 4.3 (performance net of fees).", "evidence": "The template shows no performance, return or yield figure."},
    {"id": "C2", "candidate": "Either document breaches RICR 4.2 (guarantee or risk-free claims).", "evidence": "Neither document contains guarantee, safety or risk-free wording."}
  ]
}
```