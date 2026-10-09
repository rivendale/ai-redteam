VERDICT: **REWORK**. The privacy notice names a new data recipient that is missing from the published Subprocessors page, while the notice itself promises that the page is complete. The statement template also omits the sentence RICR 4.5 requires.

CONFIDENCE: **medium**. Limits: no tools, so nothing was fetched or run; a single reviewer with no subagent or cross-vendor seats; only a rule extract was supplied, not full RICR; and the inputs do not say whether these accounts are "managed accounts" under RICR.

INPUTS LEDGER
- **Seen:** request.md, context.md, privacy_notice.md (draft), statement_template.md (draft), rule_extract.md (RICR 4.2, 4.3, 4.5 only), subprocessors_published.md (published 2026-02-01).
- **Not seen:**
  - **Full RICR text.** Matters. Definitions of "communication", "managed account" and "performance" decide whether 4.3 and 4.5 apply.
  - **Account type (managed or not).** Matters for the statement template and for 4.5.
  - **Currently published privacy notice.** Matters. Without it I cannot tell what changed or whether earlier wording is being edited in place.
  - **Corvid Metrics contract or DPA, and where it processes data.** Matters for whether it is a processor and whether a transfer disclosure is needed.
  - **Other published pages (terms, data-category lists, integrations).** Matters for the "keep our published pages consistent" part of the request.

COVERAGE
- **Scope:** both documents under review, read in full, against the rule extract and the published processor list.
- **Checked:** privacy_notice.md (every paragraph); statement_template.md (every line); rule_extract.md 4.2, 4.3, 4.5; subprocessors_published.md (full table); request.md; context.md.
- **Not checked:**
  - full RICR (not supplied);
  - previously published privacy notice (not supplied);
  - Corvid contract (not supplied);
  - other published pages (not supplied);
  - the rendered statement with real data (no tools).

SEATS AND GATE: one reviewer (this session) ran. No subagent and no cross-vendor seats were available. Sensitivity gate: the inputs are draft templates and a public processor list, with no personal data, so they are not sensitive. External seats were not refused on sensitivity grounds; they were simply unavailable.

**FINDINGS**

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | R | privacy_notice.md, "Analytics (new)" and "Who receives your data"; subprocessors_published.md table | The notice sends account number and transaction history to **Corvid Metrics**, and also says "We share personal data only with the processors listed in our Subprocessors page." The published page lists only Hexa Hosting and Pellet Mail. | On 2026-11-01 the notice goes live. A customer or the regulator reads both pages, and the notice's own completeness promise is now false on the day of publication. That is a misstatement about personal-data sharing and breaks the request to "keep our published pages consistent." | Publish a new, dated version of the Subprocessors page that adds Corvid Metrics (purpose: product analytics) on or before the notice's effective date. Supersede the 2026-02-01 version rather than editing it in place. Make the notice's go-live depend on that publication. | a✓ b✓ c✓ d✓ |
| F2 | High | PROBABLE | R | statement_template.md (whole template; the sentence is absent) | RICR 4.5 requires every communication about a managed account to carry "Compare this information with your official account statement." The template does not. | The accounts are advised or managed (the template says "Contact your adviser"). Each November statement then goes out without the mandatory sentence, so every send is a breach. | Add the sentence verbatim, near the balances. Confirm in full RICR whether 4.5 covers the official statement itself; if it is exempt, record that reasoning. | a✓ b✗ c✓ d✓ |
| F3 | Medium | CONFIRMED | R | privacy_notice.md, first sentence vs "Analytics (new)" | The collection sentence lists "name, contact details and account activity" collected "to run your account". The analytics paragraph discloses "account number" (not a listed category) and a new purpose: feature-usage analysis. | A reader of the collection section is told data is used only to run the account. The categories and purposes do not match what the notice later discloses. | List account identifiers and transaction history as categories. Add analytics as a stated purpose in the collection sentence. | a✓ b✓ c✓ d✗ |
| F4 | Medium | PROBABLE | R | statement_template.md, balance lines | The lines are opening + contributions − withdrawals − fees = closing. There is no line for investment gain or loss. | The account holds market-priced assets and values move. Closing then does not reconcile from the lines shown, and the customer sees an unexplained difference. If a gain/loss line is added, RICR 4.3 (net of fees plus the past-performance statement) is triggered. | Confirm what the account holds. If market-valued, add a "Change in value" line shown net of fees, plus the 4.3 sentence. | a✓ b✗ c✗ d✓ |

Answers to the four severity questions:
- **F1:** concrete scenario yes; CONFIRMED by quoting both pages; regulatory and customer harm yes; likely yes, since it happens on publication. **Critical.**
- **F2:** omission confirmed, but whether the rule applies is inferred, so evidence is PROBABLE; regulatory yes; likely yes. **High.**

**Confirm or refute round**
- **F1, strongest defence:** "Corvid is listed elsewhere." Nothing supplied shows that, and the notice points specifically to the Subprocessors page. Holds.
- **F2, strongest defence:** "The template *is* the official statement, so the sentence is circular." 4.5 says "every communication", with no exemption in the extract. Holds as PROBABLE until full RICR is read.

**Siblings**
- **F1:** I compared every recipient named in the notice (Corvid) and every category named (account activity, account number, transaction history) against the published lists. Found: the category/purpose mismatch, filed as F3. No other recipient is named.
- **F2:** I checked privacy_notice.md for the 4.5 sentence. It is absent too, but whether a privacy notice is a "communication about a managed account" is unsettled (see S1).
- **Security:** neither finding crosses a security boundary; both are regulatory and consistency issues.

**NEEDS VALIDATION**
- **S1:** Does RICR 4.5 apply to the privacy notice? Settled by the RICR definition of "communication about a managed account".
- **S2:** Does Corvid Metrics need the account number at all, or would a pseudonymous ID do (data minimisation)? Settled by the analytics spec or Corvid's data requirements.
- **S3:** Is Corvid a processor only? This matters for "We do not sell personal data" and for the processor label. Settled by the Corvid contract or DPA.
- **S4:** Does Corvid process data outside the jurisdiction (transfer disclosure)? Settled by Corvid's processing locations.

**REFUTED**
- **RICR 4.2 breach:** neither document states or implies a guaranteed return or freedom from risk.
- **RICR 4.3 missing on the statement:** the template shows no performance figure, only balances and flows. 4.3 is not triggered as drafted, but see F4 for what happens if it changes.

**WHAT HOLDS UP**
- The analytics paragraph discloses the vendor, the data and the purpose plainly.
- "We do not sell personal data" is not contradicted by anything supplied.
- The statement template shows fees as their own line.
- There is no prohibited performance or guarantee wording.

**UNVERIFIED CLAIMS**
- "Corvid Metrics, which analyzes it for us": confirm processor-only status from the DPA.
- "We do not sell personal data": confirm against the Corvid contract terms.

**QUESTIONS FOR THE AUTHOR**
1. Are these managed accounts under RICR?
2. Will an updated Subprocessors page be published by 2026-11-01?
3. Do the accounts hold market-priced investments?

**DECISION-MAKER SUMMARY:** Do not publish yet. Add Corvid Metrics to a new dated Subprocessors page and add the RICR 4.5 sentence to the statement template, then republish together. Proceeding as is publishes a false data-sharing statement and probably sends non-compliant statements to every managed-account customer.

**OWNER SUMMARY:** The updated privacy notice says we only share data with companies on our published list, but the new analytics company is not on that list yet. The monthly statement is also missing a sentence the rules appear to require. Both should be fixed, and the list updated, before anything goes live on November 1.

```json
{
  "schema_version": "2.3",
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
    {"item": "Corvid Metrics contract/DPA", "status": "not_seen", "matters": true},
    {"item": "account type (managed or not)", "status": "not_seen", "matters": true},
    {"item": "other published pages", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "same-session-reviewer", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Draft templates and a public processor list; no personal data."},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "privacy_notice.md", "kind": "file"},
      {"unit": "statement_template.md", "kind": "file"},
      {"unit": "rule_extract.md", "kind": "document"},
      {"unit": "subprocessors_published.md", "kind": "document"},
      {"unit": "RICR 4.2", "kind": "section"},
      {"unit": "RICR 4.3", "kind": "section"},
      {"unit": "RICR 4.5", "kind": "section"}
    ],
    "not_checked": [
      {"unit": "full RICR text", "reason": "not_supplied"},
      {"unit": "currently published privacy notice", "reason": "not_supplied"},
      {"unit": "Corvid Metrics contract/DPA", "reason": "not_supplied"},
      {"unit": "other published pages", "reason": "not_supplied"},
      {"unit": "rendered statement with real data", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "R",
     "location": "privacy_notice.md 'Analytics (new)' and 'Who receives your data'; subprocessors_published.md table",
     "scenario": "On 2026-11-01 the notice says data goes to Corvid Metrics and that sharing is limited to the Subprocessors page, which lists only Hexa Hosting and Pellet Mail; the published statement about data sharing is false on publication.",
     "fix": "Publish a new dated version of the Subprocessors page adding Corvid Metrics (analytics) on or before the notice's effective date, superseding the 2026-02-01 version; gate the notice on it.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "every recipient and data category named in privacy_notice.md against subprocessors_published.md and the notice's own collection sentence",
                           "found": "category/purpose mismatch in the collection sentence (F3); no other unlisted recipient"}},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "R",
     "location": "statement_template.md (sentence absent)",
     "scenario": "If the accounts are managed (template refers customers to their adviser), every November statement omits the RICR 4.5 mandatory sentence.",
     "fix": "Add verbatim: \"Compare this information with your official account statement.\" Confirm 4.5 scope in full RICR.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "privacy_notice.md for the RICR 4.5 sentence",
                           "found": "absent there too; applicability unsettled, recorded as S1"}},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "R",
     "location": "privacy_notice.md first sentence vs 'Analytics (new)'",
     "scenario": "The collection sentence lists name, contact details and account activity for running the account, but the notice later discloses account number and an analytics purpose; categories and purposes are inconsistent.",
     "fix": "Add account identifiers and transaction history as categories and analytics as a purpose in the collection sentence.",
     "answers": {"a": true, "b": true, "c": true, "d": false}},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "R",
     "location": "statement_template.md balance lines",
     "scenario": "For market-valued holdings, opening + contributions - withdrawals - fees will not equal closing, leaving an unexplained difference; adding a gain/loss line triggers RICR 4.3.",
     "fix": "Confirm holdings; if market-valued, add a net-of-fees change-in-value line plus the RICR 4.3 past-performance sentence.",
     "answers": {"a": true, "b": false, "c": false, "d": true}},
    {"id": "S1", "status": "needs_validation", "track": "R", "location": "privacy_notice.md",
     "suspicion": "RICR 4.5 sentence may also be required in the privacy notice.",
     "unresolved_fact": "RICR definition of 'communication about a managed account'."},
    {"id": "S2", "status": "needs_validation", "track": "R", "location": "privacy_notice.md 'Analytics (new)'",
     "suspicion": "Sending account number to an analytics vendor may exceed what feature-usage analysis needs.",
     "unresolved_fact": "Whether Corvid requires the account number or could use a pseudonymous ID."},
    {"id": "S3", "status": "needs_validation", "track": "R", "location": "privacy_notice.md 'Who receives your data'",
     "suspicion": "Corvid may use data for its own purposes, undermining 'processor' and 'do not sell' statements.",
     "unresolved_fact": "Terms of the Corvid Metrics contract/DPA."},
    {"id": "S4", "status": "needs_validation", "track": "R", "location": "privacy_notice.md 'Analytics (new)'",
     "suspicion": "A cross-border transfer disclosure may be needed.",
     "unresolved_fact": "Where Corvid Metrics processes data."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Either document breaches RICR 4.2.", "evidence": "No wording states or implies a guaranteed return or freedom from risk."},
    {"id": "C2", "candidate": "Statement template breaches RICR 4.3.", "evidence": "The template shows balances and flows only, no performance figure; 4.3 is not triggered as drafted."}
  ]
}
```