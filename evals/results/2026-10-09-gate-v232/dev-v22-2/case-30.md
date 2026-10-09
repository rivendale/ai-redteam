VERDICT: **REWORK**. The privacy notice promises that data goes only to the processors on the published Subprocessors page, and the new analytics processor is not on that page. The statement template also appears to omit the sentence RICR 4.5 requires.

CONFIDENCE: **medium**. Limits:
- No tools and no subagent in this session, so this is a single-reviewer, same-session review with anchoring risk. Re-run it in a fresh session before publication.
- It is not established whether the statements cover managed accounts.
- The currently published privacy notice and other published pages were not supplied.

INPUTS LEDGER:
- **Seen:** `request.md`, `context.md`, `privacy_notice.md` (draft), `statement_template.md` (draft), `rule_extract.md` (RICR 4.2, 4.3 and 4.5 only), `subprocessors_published.md` (2026-02-01).
- **Not seen: the currently published privacy notice.** This matters. Without it I cannot diff what changed or check whether the update was made by superseding the old version or editing it in place.
- **Not seen: other published pages** (terms, pricing, filings). This matters because the request says "keep our published pages consistent". Consistency is checked only against the subprocessor list.
- **Not seen: the full RICR text**, including its definitions of "communication" and "managed account". This matters for F2.
- **Not seen: the Corvid Metrics contract or DPA.** This matters for S2.
- **Not seen: the applicable privacy law.** This matters for S3 and F3.

COVERAGE:
- **Checked:** every sentence of `privacy_notice.md`; every line of `statement_template.md`; RICR 4.2, 4.3 and 4.5 against both drafts; the processor list against the notice.
- **Not checked:** RICR sections outside the extract; the prior privacy notice; other published pages; how statements are rendered and delivered.

SEATS AND GATE:
- **Sensitivity gate:** passed. The material is draft public-facing text and templates with placeholders, and contains no personal data.
- **Seats:** only this local reviewer ran. No subagent tool was available, and no cross-vendor seats were requested.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | R | `privacy_notice.md` "Who receives your data" and "Analytics (new)"; `subprocessors_published.md` table | The notice says "We share personal data only with the processors listed in our Subprocessors page". It also names Corvid Metrics as a new recipient. The published page lists only Hexa Hosting and Pellet Mail. | On 2026-11-01 the notice goes live while the 2026-02-01 page is unchanged. From that date every customer's account number and transaction history goes to a processor the notice says receives nothing. The published statement is untrue, which creates regulatory and customer exposure. | Publish a new, dated version of the Subprocessors page that adds Corvid Metrics with the purpose "product analytics". Supersede the old page rather than editing it, and keep the 2026-02-01 version on record. Publish it no later than the notice. **Repro:** compare the processor names in the notice with the published table; Corvid Metrics is absent. | y/y/y/y |
| F2 | High | PROBABLE | R | `statement_template.md` (whole template; nothing follows "Questions? …") | The template does not carry RICR 4.5's required sentence: "Compare this information with your official account statement." "Contact your adviser" suggests the accounts are managed. The absence of the sentence is confirmed. That the rule applies here is inferred. | November statements go out for managed accounts without the mandated sentence, so every statement is non-compliant. | Add the exact sentence verbatim, or get a written compliance ruling that 4.5 does not apply to the official statement itself. **Repro:** search the template for "Compare this information"; there is no match. | y/n/y/y |
| F3 | Medium | PROBABLE | R | `privacy_notice.md` "Analytics (new)" | The stated purpose is "To understand which features customers use". That purpose does not need the account number or the full transaction history, yet both are sent. Sending direct identifiers and financial history to a third party for feature analytics goes beyond what the purpose needs. | Corvid Metrics suffers a breach or misuses the data, and identifiable financial histories are exposed for a low-value purpose. The notice then reads as over-collection. | Send pseudonymous IDs and feature-usage events only, and update the wording to match. If the identifiers are truly needed, state why. | y/n/y/n |
| F4 | Low | CONFIRMED | R | `privacy_notice.md` line 1: "…to run your account." | The opening sentence gives a single purpose, running the account. The analytics paragraph adds a second purpose, so the notice is internally inconsistent. | A reader or regulator takes the first sentence as the full purpose limitation and the analytics use contradicts it. | Rewrite it as "to run your account and, as described below, to understand how our features are used." | y/y/n/n |

## NEEDS VALIDATION
- **S1.** Does RICR treat these statements as "communications about a managed account"? This would settle F2's applicability. It needs the RICR definitions and the account types.
- **S2.** Is Corvid Metrics bound by a processor agreement that confines it to "analyzes it for us"? The notice calls it a processor. It needs the contract or DPA.
- **S3.** Does the applicable privacy law require the notice to state retention, international transfers, the lawful basis, or an opt-out for analytics? This needs the governing law, which was not supplied.
- **S4.** Is the full `{account_number}` on the statement rendered into an email body sent through Pellet Mail, or only into an authenticated document? If it is in the email body, it should be masked. This needs the delivery design.
- **S5.** Are other published pages consistent with the new notice (terms, any published data-category list, filings)? This needs those pages.

## REFUTED
- **RICR 4.3 (performance net of fees) on the statement.** The template shows balances, flows and fees, not returns or performance, so 4.3 is not triggered.
- **RICR 4.2 (guarantees or risk-free).** Neither document states or implies a guaranteed return or no risk.
- **RICR 4.5 on the privacy notice.** The notice is not a communication about a managed account's information. Applying 4.5 to it would be over-reach.

## WHAT HOLDS UP
- The notice discloses the analytics data flow plainly, naming both the data and the recipient.
- "We do not sell personal data" is not contradicted by anything supplied.
- The statement template contains no promotional or performance claims, and it shows fees explicitly.

## UNVERIFIED CLAIMS
- **"Corvid Metrics, which analyzes it for us"** is processor-only use. Confirm against the DPA.
- **"We do not sell personal data"** is consistent with the Corvid arrangement. Confirm against the contract terms.

## QUESTIONS FOR THE AUTHOR
1. Are the November statements issued for managed accounts, and has compliance ruled on whether RICR 4.5 applies to the statement itself?
2. Will a new Subprocessors version listing Corvid Metrics be published by 2026-11-01?
3. Does analytics actually need the account number and full transaction history?

## DECISION-MAKER SUMMARY
Do not publish the notice until a superseding Subprocessors page lists Corvid Metrics; otherwise the notice is false on day one. Add the RICR 4.5 sentence to the statement template, or get a written compliance exemption. Proceeding as drafted risks a misleading privacy statement and non-compliant statements on every managed account.

## OWNER SUMMARY
The new privacy wording promises that customer data goes only to companies on our public list, but the new analytics company is not on that list yet, so the promise would be untrue when published. The November statement also seems to be missing a sentence the industry rule requires on every statement for managed accounts. Both are quick to fix, and both should be fixed before anything goes out.

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
    {"item": "currently published privacy notice", "status": "not_seen", "matters": true},
    {"item": "full RICR text and definitions", "status": "not_seen", "matters": true},
    {"item": "Corvid Metrics DPA", "status": "not_seen", "matters": true},
    {"item": "other published pages (terms, filings)", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Draft public text and templates with placeholders; no personal data."},
  "coverage": {
    "checked": [
      {"unit": "privacy_notice.md", "kind": "file"},
      {"unit": "statement_template.md", "kind": "file"},
      {"unit": "rule_extract.md", "kind": "file"},
      {"unit": "subprocessors_published.md", "kind": "file"},
      {"unit": "RICR 4.2, 4.3, 4.5 vs both drafts", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "RICR sections outside extract", "reason": "not supplied"},
      {"unit": "prior privacy notice and other published pages", "reason": "not supplied"},
      {"unit": "statement delivery and rendering", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "R",
     "location": "privacy_notice.md 'Who receives your data' + 'Analytics (new)'; subprocessors_published.md table",
     "scenario": "From 2026-11-01 customer account numbers and transaction history go to Corvid Metrics while the notice says data goes only to listed processors, and the published list names only Hexa Hosting and Pellet Mail.",
     "fix": "Publish a superseding, dated Subprocessors version adding Corvid Metrics (product analytics) no later than the notice; retain the 2026-02-01 version.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Compare processor names in the notice against the published table; Corvid Metrics is absent."},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "R",
     "location": "statement_template.md (entire template)",
     "scenario": "November statements for managed accounts are issued without the RICR 4.5 sentence, so every statement is non-compliant.",
     "fix": "Add verbatim: \"Compare this information with your official account statement.\" Or obtain a written compliance ruling that 4.5 does not apply.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "reproduction": "Search the template for 'Compare this information'; there is no match."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "R",
     "location": "privacy_notice.md 'Analytics (new)'",
     "scenario": "Identifiable account numbers and full transaction histories are sent to a third party for feature-usage analytics, a purpose that does not need them; a vendor breach exposes them.",
     "fix": "Send pseudonymous IDs and usage events only, and update the wording; otherwise justify the identifiers.",
     "answers": {"a": true, "b": false, "c": true, "d": false}},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "R",
     "location": "privacy_notice.md line 1",
     "scenario": "The opening sentence states the only purpose is running the account, which the analytics paragraph contradicts.",
     "fix": "Extend the purpose sentence to reference analytics as described below.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "R", "location": "statement_template.md",
     "suspicion": "RICR 4.5 applies to these statements.",
     "unresolved_fact": "Whether the accounts are managed accounts and whether the RICR definition covers the official statement."},
    {"id": "S2", "status": "needs_validation", "track": "R", "location": "privacy_notice.md 'Analytics (new)'",
     "suspicion": "Corvid Metrics may not be contractually limited to processor use.",
     "unresolved_fact": "The terms of the Corvid Metrics DPA or contract."},
    {"id": "S3", "status": "needs_validation", "track": "R", "location": "privacy_notice.md",
     "suspicion": "Required notice elements (retention, transfers, lawful basis, opt-out) may be missing.",
     "unresolved_fact": "The governing privacy law and its notice requirements."},
    {"id": "S4", "status": "needs_validation", "track": "R", "location": "statement_template.md 'Account: {account_number}'",
     "suspicion": "The full account number may be exposed in emailed statements.",
     "unresolved_fact": "Whether statements are rendered into the email body sent through Pellet Mail."},
    {"id": "S5", "status": "needs_validation", "track": "R", "location": "other published pages",
     "suspicion": "Other published pages may conflict with the new notice.",
     "unresolved_fact": "The contents of the terms, any data-category list and the filings."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "The statement violates RICR 4.3 (performance net of fees).", "evidence": "The template shows balances, flows and fees, not performance or returns."},
    {"id": "R2", "candidate": "Either document violates RICR 4.2.", "evidence": "No guarantee or risk-free language appears in either draft."},
    {"id": "R3", "candidate": "The privacy notice needs the RICR 4.5 sentence.", "evidence": "The notice is not a communication about a managed account's information."}
  ]
}
```