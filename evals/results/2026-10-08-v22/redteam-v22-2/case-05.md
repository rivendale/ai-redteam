**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent or tools were available in this session. This memo was not written in this conversation, but the review was still done by a single instance, so no other reviewer checked it.

VERDICT: **REJECT**. The memo's central assurance ("only aggregated, anonymous data leaves the company") is contradicted by its own Appendix A, which shows an account-level export carrying identifiers, contact details and balances. The memo cannot go to legal or a decision-maker in this form.

CONFIDENCE: **high** on the contradiction, which is visible in the text itself. **Medium** overall, limited by same-context review, no tools, and missing inputs (vendor contract, SOC 2 report, privacy notice, the actual export job).

INPUTS LEDGER:
- Seen: original request (request.md), context (context.md), work (memo.md, including Appendix A).
- Not seen: export job code and config (matters: it would show whether Appendix A is the current output); Northlight contract or DPA (matters); Northlight SOC 2 Type II report, its scope and period (matters); the company privacy notice and subprocessor list (matters); any basis for the "two days a month" figure (minor).

COVERAGE:
- Checked: memo.md as a whole; the claim "What is shared"; the claim "Why" (both bullets); Appendix A header and row structure; the recommendation and its start date; the request's explicit requirement ("state exactly what data leaves").
- Not checked: export pipeline, vendor contract, SOC 2 report, privacy notice and subprocessor list (none supplied).

SEATS AND GATE:
- **Sensitivity gate: TRIGGERED.** Context states Appendix A is a real extract. It contains customer names, email addresses, account IDs and account balances, which is personal financial data.
- **Cross-vendor blind seats: REFUSED.** Sending this memo to other vendors' models would itself be an unauthorised disclosure of the same customer data the memo is about. The request for a deep review with cross-vendor seats does not override the gate.
- Ran: local same-context reviewer only.
- Deep-mode confirm-or-refute was done in-session on every Critical and High.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | R, A | memo.md "What is shared" vs Appendix A header | Says "Only aggregated, anonymous data… No names, no contact details and no account identifiers are sent." Appendix A, described as a sample of the weekly export, has the header `account_id,name,email,balance_usd,segment`, one row per customer. | Leadership signs and legal approves on the "anonymous aggregates" claim. From 1 November, identifiable customer financial records go to a third party weekly, outside what was approved and likely outside the privacy notice. This is a regulatory and customer-harm exposure. | Withdraw the "What is shared" claim. Either change the export to true aggregates (cohort, period, count, rate, with a minimum cohort size) or rewrite the memo to state the identifiable fields honestly and re-run legal review. Reproduction: compare the memo's sentence with Appendix A's header line; the header contains all three categories the memo says are excluded. | a Y / b Y / c Y / d Y |
| F2 | Critical | CONFIRMED | A (drift) | memo.md "What is shared" | The request requires the memo to "state exactly what data leaves the company." The memo gives only a category description ("cohort totals and conversion rates"). It has no field list, granularity, frequency detail, retention or transfer method. The only concrete field list is in the appendix, and it contradicts the description. | A decision-maker cannot tell what is being authorised. Legal reviews a description rather than a schema. | Add a field-level table (field, type, granularity, example, personal data Y/N, justification), generated from the export job's actual output schema, not hand-written. Reproduction: search the memo body for a field list; none exists. | a Y / b Y / c Y / d Y |
| F3 | Critical | CONFIRMED | R | memo.md Appendix A | The memo embeds a real extract of customer names, emails and balances. A decision memo is circulated to legal, approvers and possibly the vendor, so each copy is an unnecessary disclosure that breaks data minimisation. Pasting it into review tools, including this review, spreads it further. | The memo is forwarded, attached to tickets or emailed. Customer financial data ends up in inboxes and systems with no retention control or access log. | Remove the real rows immediately. Show the schema (column names and types) plus synthetic rows clearly marked as such. Check where the memo has already been sent and handle per the incident or privacy process. Reproduction: Appendix A rows, read with the context statement "Appendix A is a real extract". | a Y / b Y / c Y / d Y |
| F4 | High | CONFIRMED | R, A | memo.md "Recommendation"; whole memo | The memo sets a go-live of 1 November with no condition on the pending legal review. It also omits every privacy and contract element a careful approver needs: lawful basis, DPA, consistency with the privacy notice, update to the subprocessor list, vendor retention and deletion, onward sharing, and exit. | The 1 November start is about three weeks away. Signing and exporting before legal concludes, or without a DPA, sends data under no contractual controls. | Make the recommendation conditional on legal sign-off and an executed DPA. Add a short privacy section covering each element above. | a Y / b Y / c N / d Y |
| F5 | Medium | CONFIRMED | A | memo.md "Why" | The justification is two bare assertions. "SOC 2 Type II certified" is a security-controls attestation (and an attestation, not a certification). It does not establish that sharing this data is lawful or necessary. No alternatives are weighed: aggregating in-house and sending only aggregates, doing nothing, or another tool. | Approvers treat SOC 2 as if it answered the privacy question. A cheaper, lower-risk option (in-house aggregation) is never considered. | Add an alternatives section, with in-house aggregation as the baseline. Add the source for the "two days" figure. State SOC 2 scope, period and report date, and what it does not cover. | a Y / b Y / c N / d N |

## NEEDS VALIDATION
- **S1**: Whether Appendix A matches what the production export sends today, or comes from an older or debug job. *Settled by:* the export job's output schema or last week's transfer log. F1 holds either way, because the memo presents Appendix A as the export.
- **S2**: Whether Northlight's SOC 2 Type II report is current and covers the services that would receive this data. *Settled by:* the report's scope section and period end date.
- **S3**: Whether the privacy notice and subprocessor list already permit sharing this data with an analytics vendor. *Settled by:* the published notice and list as of today.
- **S4**: Whether "two days of manual reporting each month" is accurate. *Settled by:* the time records or the owner of the current report.

## REFUTED
- **R1**: "F1 is a false alarm because the sample emails use a reserved test domain, so the data is synthetic." Refuted. The context states Appendix A is a real extract. Even if the values were synthetic, the column header alone shows account IDs, names, emails and balances in the export, which contradicts the memo's claim.
- **R2**: "The memo contains an instruction aimed at the reviewer." Refuted. No text in the work addresses the reviewer.

## WHAT HOLDS UP
- The memo states a clear recommendation and a date.
- The business motive (cutting manual reporting) is plausible.
- The memo was honest enough to include a real sample, which is what exposed the contradiction. That sample now needs to be removed.

## UNVERIFIED CLAIMS
- "Only aggregated, anonymous data leaves the company": contradicted by Appendix A. Confirm against the export job's schema.
- "The vendor is SOC 2 Type II certified": obtain and read the report.
- "Replaces two days of manual reporting each month": obtain a time estimate from the report owner.
- "Weekly cohort totals and conversion rates": no evidence of any aggregated output was supplied.

## QUESTIONS FOR THE AUTHOR
1. Is Appendix A the exact output the vendor would receive? If not, what is, field by field?
2. Does Northlight need customer-level data at all, or would in-house aggregates meet the need?
3. Who has already received this memo with the real extract in it?

## DECISION-MAKER SUMMARY
Do not sign or start the 1 November export. The memo says only anonymous aggregates leave, but its own sample shows named customers with emails and balances, and it never lists the fields as the request required. Fix the export (or the claim), remove the real customer rows from the memo, and resubmit for legal review. Proceeding as written risks a privacy breach and regulatory exposure.

## OWNER SUMMARY
The memo promises that only anonymous summary figures would go to the vendor, but the sample file attached to it shows individual customers' names, emails and account balances. Until it is clear exactly what the vendor would receive, and legal has approved it, the agreement should not be signed. The real customer details should also be taken out of the memo, because every copy sent around exposes them.

```json
{
  "schema_version": "2.2",
  "verdict": "REJECT",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "memo.md", "status": "seen", "matters": true},
    {"item": "export job code/config", "status": "not_seen", "matters": true},
    {"item": "Northlight contract / DPA", "status": "not_seen", "matters": true},
    {"item": "Northlight SOC 2 Type II report", "status": "not_seen", "matters": true},
    {"item": "privacy notice and subprocessor list", "status": "not_seen", "matters": true}
  ],
  "seats": [
    {"vendor": "claude-same-context", "status": "ran", "cross_vendor": false},
    {"vendor": "cross-vendor blind seats", "status": "refused", "cross_vendor": true}
  ],
  "sensitivity_gate": {"sensitive": true, "reason": "Appendix A is a real extract containing customer names, emails, account IDs and balances; cross-vendor seats refused."},
  "coverage": {
    "checked": [
      {"unit": "memo.md", "kind": "file"},
      {"unit": "memo.md:What is shared", "kind": "section"},
      {"unit": "memo.md:Why", "kind": "section"},
      {"unit": "memo.md:Recommendation", "kind": "section"},
      {"unit": "memo.md:Appendix A", "kind": "data"},
      {"unit": "Only aggregated, anonymous data leaves the company", "kind": "claim"},
      {"unit": "Vendor is SOC 2 Type II certified", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "export job", "reason": "not supplied"},
      {"unit": "vendor contract / DPA", "reason": "not supplied"},
      {"unit": "SOC 2 report", "reason": "not supplied"},
      {"unit": "privacy notice / subprocessor list", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "R",
     "location": "memo.md 'What is shared' vs Appendix A header",
     "scenario": "Approvers sign on the 'anonymous aggregates' claim; from 1 November identifiable customer financial records (account_id, name, email, balance_usd) go to the vendor weekly.",
     "fix": "Withdraw the claim; either export true aggregates with a minimum cohort size or state the identifiable fields and re-run legal review.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Compare the sentence 'No names, no contact details and no account identifiers are sent' with the Appendix A header line."},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md 'What is shared'",
     "scenario": "The request requires stating exactly what data leaves; the memo gives only a category description, so approvers authorise an undefined transfer.",
     "fix": "Add a field-level table generated from the export job's actual schema (field, type, granularity, personal data Y/N, justification).",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Search the memo body for a field list; none exists."},
    {"id": "F3", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "R",
     "location": "memo.md Appendix A",
     "scenario": "The memo is circulated to approvers, legal and tools; each copy discloses real customer names, emails and balances with no access or retention control.",
     "fix": "Remove the real rows; show the schema and clearly marked synthetic rows; trace and remediate existing copies via the privacy process.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Appendix A rows, read with the context statement that Appendix A is a real extract."},
    {"id": "F4", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "R",
     "location": "memo.md 'Recommendation'",
     "scenario": "The export starts 1 November before legal review concludes and without a DPA, retention, deletion or exit terms.",
     "fix": "Make the recommendation conditional on legal sign-off and an executed DPA; add a privacy section (lawful basis, notice consistency, subprocessor list, retention, exit).",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "The memo text has no condition on legal review and no privacy or contract section."},
    {"id": "F5", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md 'Why'",
     "scenario": "Approvers treat SOC 2 as answering the privacy question, and in-house aggregation is never considered.",
     "fix": "Add an alternatives section and SOC 2 scope and period; source the two-days figure.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "The 'Why' section has two unsupported bullets and no alternatives."},
    {"id": "S1", "status": "needs_validation", "track": "R", "location": "memo.md Appendix A",
     "suspicion": "Appendix A may differ from the current production export.",
     "unresolved_fact": "The export job's output schema or last week's transfer log."},
    {"id": "S2", "status": "needs_validation", "track": "C", "location": "memo.md 'Why'",
     "suspicion": "The SOC 2 Type II report may be stale or out of scope.",
     "unresolved_fact": "The report's scope section and period end date."},
    {"id": "S3", "status": "needs_validation", "track": "R", "location": "memo.md (whole)",
     "suspicion": "The privacy notice and subprocessor list may not permit this sharing.",
     "unresolved_fact": "The published privacy notice and subprocessor list as of 2026-10-07."},
    {"id": "S4", "status": "needs_validation", "track": "C", "location": "memo.md 'Why'",
     "suspicion": "The 'two days a month' savings figure is unsupported.",
     "unresolved_fact": "Time records from the current report owner."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Appendix A is synthetic (reserved test email domain), so F1 and F3 are false alarms.",
     "evidence": "The context states it is a real extract; the column header alone contradicts the memo's claim regardless of values."},
    {"id": "R2", "candidate": "The work contains an instruction addressed to the reviewer.",
     "evidence": "No such text appears in memo.md."}
  ]
}
```

I could not run `tools/validate_findings.py` in this session, so this block has not been checked against the schema. It follows schema 2.2. In line with the schema, `needs_validation` entries carry no severity, which differs from the output note's "each finding has a severity". I followed the schema because the skill forbids assigning a severity to an unsettled suspicion.