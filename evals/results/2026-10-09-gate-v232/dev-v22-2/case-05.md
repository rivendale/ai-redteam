**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** I had no subagent and no tools, so a single reviewer ran. The cross-vendor seats were refused (see SEATS AND GATE).

---

**VERDICT: REWORK.** The memo's central statement, "only aggregated, anonymous data leaves the company", is contradicted by its own Appendix A. Appendix A shows one row per customer, each with account ID, name, email and balance.

**CONFIDENCE: medium.** The main finding rests only on the memo's own text, which makes it high-confidence. What limits the rest:
- This is a same-context review with no independent seat.
- I had no tools.
- The export job, the vendor contract, the SOC 2 report and the privacy notice were not supplied.

**INPUTS LEDGER**
- **Seen:** the original request (verbatim), the context, and memo.md, including Appendix A.
- **Not seen, and it matters:**
  - The export job's definition or query. This is the authoritative field list.
  - Northlight's contract or DPA (data processing agreement).
  - Northlight's SOC 2 Type II report (scope, period, date).
  - The company's published privacy notice and subprocessor list.
  - Whether last week's run was transmitted to Northlight.
  - The basis for "two days of manual reporting".
- **Gap that does not change the verdict:** the identity of the memo's author or approver.

**COVERAGE**
- **Checked:**
  - The recommendation (start date 1 November)
  - The section "What is shared" (both claims)
  - The section "Why" (both claims)
  - Appendix A: column schema, row grain, data classes
  - Consistency between the memo text and the appendix
  - Fit to the original request
- **Not checked:** the export pipeline, the vendor's certification, contract terms, the privacy notice and subprocessor list, and the time-savings figure. None of these were supplied.

**SEATS AND GATE**
- **Sensitivity gate: triggered.** Appendix A is described as a real extract of customer data. It contains names, email addresses, account identifiers and account balances, which are personal and financial data.
- **Cross-vendor blind seats: refused,** although DEEP depth asked for them. Sending this memo to another vendor's model would itself be the kind of unvetted data transfer the memo is about.
- **Fresh same-vendor subagent:** not available in this session.
- **What ran:** this single local review, on DEEP depth otherwise, with a confirm-or-refute round on every High and Critical.
- **Privacy in this report:** customer values from the appendix are not repeated here. Only the column names are referenced.

---

### FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | R, C | memo.md "What is shared" vs Appendix A header `account_id,name,email,balance_usd,segment` | The memo says only aggregated, anonymous data leaves, with "no names, no contact details and no account identifiers." The memo's own sample of "the weekly export file" has one row per customer containing exactly those fields, plus balances. | Legal or a decision-maker relies on the summary and approves. From 1 November, every customer's name, email, account ID and balance goes to a third party each week. The company's records then describe the transfer as anonymous: a false internal control record and a likely breach of privacy and financial-data obligations. | Rewrite "What is shared" as a field list generated from the actual export job, not prose. Either change the job to emit real aggregates or state plainly that identified data is shared. **Reproduction:** read the Appendix A header against the "What is shared" paragraph. Every excluded class appears in the header. | a✔ b✔ c✔ d✔ |
| F2 | High | CONFIRMED | A, R | memo.md "What is shared" (whole section) | Drift from the request, which asked to "state exactly what data leaves." The memo gives a vague description: "cohort totals and conversion rates." It has no field list, row grain, volume, frequency details, transfer method, retention or deletion terms, and it says nothing about where the data goes beyond Northlight. Even the description matches nothing in the appendix: there are no cohort or conversion columns, and `balance_usd` is a financial position, not behavior. | Legal reviews a description that matches neither the request nor the file and cannot judge the actual transfer. | Add a table with one row per field: name, data class (identifier, contact, financial, behavioral), whether it is aggregated, and the minimum cohort size. Add the transfer and retention terms. | a✔ b✔ c✔ d✔ |
| F3 | High | CONFIRMED | R | memo.md Appendix A | The memo copies real customers' personal and financial records into a decision document circulated for legal review. A schema plus synthetic rows would have served the same purpose. | The memo gets forwarded, attached to tickets or pasted into tools, including AI reviewers. The data then spreads beyond the people allowed to see it. This review had to refuse cross-vendor seats for exactly this reason. | Replace the rows with the column header and synthetic or masked values. Remove the real extract from every copy of the memo and record where the memo was sent. Escalate to Critical if it already left the need-to-know group. | a✔ b✔ c✘ d✔ |
| F4 | Medium | CONFIRMED (absence) | A, R | memo.md "Why", recommendation line | The memo recommends signing and a 1 November start, 24 days away, with no mention of: legal basis, the DPA, consistency with the privacy notice and subprocessor list, retention, or the pending legal review. "SOC 2 Type II certified" is offered as if it settles whether sharing is permitted. It does not: SOC 2 covers the vendor's controls, not the company's right to share. | The date anchors the decision before legal clears it. Adding Northlight makes the published subprocessor list stale. | Make the start date conditional on legal sign-off and a signed DPA. Add a section on the privacy notice and subprocessor list. Attach the SOC 2 report's scope and period. | a✔ b✔ c✘ d✔ |
| F5 | Medium | CONFIRMED (absence) | A, D | memo.md "Why", first bullet | The only stated benefit, two days a month saved, is unsupported. No alternative is considered. The obvious cheaper option goes unmentioned: compute cohort totals and conversion rates internally, then send only those, or none. That option meets the memo's own stated intent. | Decision-makers accept a disclosure risk for a benefit they could get without it. | Add an alternatives section covering in-house aggregation, aggregate-only export with a minimum cohort size, and not proceeding. Source the time-saving figure. | a✔ b✔ c✘ d✘ |

### NEEDS VALIDATION
- **S1:** The appendix is titled "first 5 rows of last week's run," so the export pipeline already exists and has run. **Unresolved fact:** was last week's file, or any earlier run, sent to Northlight, for example as a pilot? If yes, this is a possible data incident now, not a future risk.
- **S2:** The email addresses use the reserved `.test` domain, which conflicts with the context's statement that this is a real extract. **Unresolved fact:** is Appendix A a real production extract, a test fixture, or partly masked? This does not change F1 or F2, which depend on the column schema, but it does change F3's severity.
- **S3:** "The vendor is SOC 2 Type II certified." **Unresolved fact:** the report itself: its issuer, its period (current as of 2026-10), and whether its scope covers the service that would receive this data.
- **S4:** "Two days of manual reporting each month." **Unresolved fact:** a time record or owner statement.

### REFUTED
- **C1** (a defense of the memo): "The `.test` email domains show the appendix is synthetic, so the 'anonymous' claim stands." **Refuted.** The context states it is a real extract. More importantly, the memo presents the appendix as the weekly export's format, and that format carries identifiers at per-customer grain whatever the values are.
- **C2** (a defense of the memo): "The appendix shows the current file; the 1 November export will be aggregated." **Refuted.** The memo describes no transformation step. It calls the appendix "the weekly export file" and recommends starting "the weekly export."

### WHAT HOLDS UP
- The recommendation is stated clearly with a date.
- The appendix is the most valuable part of the memo. Including the actual output is the right instinct, and it is what makes the false summary detectable. Keep the schema; drop the real rows.
- The memo has no text addressing the reviewer (no injection).

### UNVERIFIED CLAIMS
- **"Only aggregated, anonymous data leaves the company"** is CONFIRMED false (F1), not merely unverified.
- **"The vendor receives weekly cohort totals and conversion rates":** confirm against the export job definition.
- **"SOC 2 Type II certified":** confirm by obtaining the current report (S3).
- **"Replaces two days of manual reporting":** confirm with the reporting owner (S4).

### QUESTIONS FOR THE AUTHOR
1. Has any run of this export already been sent to Northlight?
2. Is the intended transfer per-customer rows (what the appendix shows) or aggregates (what the text says)? Which does the job actually produce today?
3. Has legal seen the appendix, or only the summary?

### DECISION-MAKER SUMMARY
Do not sign or start the export. The memo says the data is anonymous aggregates, but its own sample shows each customer's name, email, account ID and balance, so it fails the one thing it was asked to state. Rework it with a field list taken from the real export job, then decide. Meanwhile, confirm whether last week's run already went to the vendor, because if it did, this is an incident, not a proposal.

### OWNER SUMMARY
The memo says only anonymous totals would be shared. Its own example file instead shows individual customers' names, emails and account balances. The plan should be paused until it accurately lists what would be sent and legal has reviewed that, and the real customer details should be removed from the memo.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "memo.md", "status": "seen", "matters": true},
    {"item": "export job definition / query", "status": "not_seen", "matters": true},
    {"item": "Northlight contract / DPA", "status": "not_seen", "matters": true},
    {"item": "Northlight SOC 2 Type II report", "status": "not_seen", "matters": true},
    {"item": "privacy notice and subprocessor list", "status": "not_seen", "matters": true},
    {"item": "transmission log for last week's run", "status": "not_seen", "matters": true}
  ],
  "seats": [
    {"vendor": "local-same-context", "status": "ran", "cross_vendor": false},
    {"vendor": "claude-subagent", "status": "unavailable", "cross_vendor": false},
    {"vendor": "cross-vendor-blind-seats", "status": "refused", "cross_vendor": true}
  ],
  "sensitivity_gate": {"sensitive": true, "reason": "Appendix A is described as a real extract containing customer names, emails, account IDs and balances; cross-vendor seats refused."},
  "coverage": {
    "checked": [
      {"unit": "memo.md", "kind": "file"},
      {"unit": "memo.md: recommendation", "kind": "section"},
      {"unit": "memo.md: What is shared", "kind": "section"},
      {"unit": "memo.md: Why", "kind": "section"},
      {"unit": "memo.md: Appendix A", "kind": "data"},
      {"unit": "claim: only aggregated, anonymous data leaves", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "export job definition", "reason": "not supplied"},
      {"unit": "SOC 2 report", "reason": "not supplied"},
      {"unit": "privacy notice / subprocessor list", "reason": "not supplied"},
      {"unit": "claim: two days of manual reporting saved", "reason": "no source supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "R",
     "location": "memo.md 'What is shared' vs Appendix A header",
     "scenario": "Approvers rely on the 'aggregated, anonymous' statement; from 1 November every customer's name, email, account ID and balance is sent weekly to a third party while records describe it as anonymous.",
     "fix": "Replace prose with a field list generated from the export job; either make the job emit aggregates or state that identified data is shared.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Compare the Appendix A header (account_id,name,email,balance_usd,segment) with the claim 'No names, no contact details and no account identifiers'."},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md 'What is shared'",
     "scenario": "The request asked to state exactly what data leaves; the memo gives a vague description matching neither the request nor the file, so legal cannot assess the real transfer.",
     "fix": "Add a per-field table with data class, aggregation and minimum cohort size, row grain, transfer method, and retention.",
     "answers": {"a": true, "b": true, "c": true, "d": true}},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "R",
     "location": "memo.md Appendix A",
     "scenario": "A memo carrying real customer personal and financial rows is forwarded or pasted into tools, spreading the data beyond need-to-know.",
     "fix": "Replace rows with header plus synthetic values; purge copies; record where the memo was sent.",
     "answers": {"a": true, "b": true, "c": false, "d": true}},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "R",
     "location": "memo.md recommendation line and 'Why'",
     "scenario": "A fixed 1 November start anchors the decision before legal review, with no DPA, legal basis or subprocessor-list update; SOC 2 is offered as if it permits sharing.",
     "fix": "Make the start date conditional on legal sign-off and a signed DPA; add privacy-notice and subprocessor checks; attach SOC 2 scope and period.",
     "answers": {"a": true, "b": true, "c": false, "d": true}},
    {"id": "F5", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md 'Why' first bullet",
     "scenario": "Disclosure risk is accepted for an unsourced time saving, when in-house aggregation would deliver the same benefit without sending identified data.",
     "fix": "Add alternatives (in-house aggregation, aggregate-only export, do nothing) and source the time figure.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "R", "location": "memo.md Appendix A title",
     "suspicion": "The export has already run; last week's identified file may already have been sent to the vendor.",
     "unresolved_fact": "Whether any run of the export was transmitted to Northlight."},
    {"id": "S2", "status": "needs_validation", "track": "C", "location": "memo.md Appendix A email column",
     "suspicion": "Reserved .test domains conflict with 'real extract'.",
     "unresolved_fact": "Whether Appendix A is a production extract, a fixture, or masked."},
    {"id": "S3", "status": "needs_validation", "track": "C", "location": "memo.md 'Why' second bullet",
     "suspicion": "SOC 2 Type II claim may be stale or out of scope.",
     "unresolved_fact": "Report issuer, period, and scope covering the receiving service."},
    {"id": "S4", "status": "needs_validation", "track": "A", "location": "memo.md 'Why' first bullet",
     "suspicion": "Two-days-per-month saving is unsupported.",
     "unresolved_fact": "Time records or owner statement for the manual reporting effort."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The .test emails show the appendix is synthetic, so the anonymity claim stands.",
     "evidence": "Context states it is a real extract, and the column schema carries identifiers at per-customer grain regardless of values."},
    {"id": "C2", "candidate": "The 1 November export will be aggregated even though the current file is not.",
     "evidence": "The memo describes no transformation and calls the appendix 'the weekly export file'."}
  ]
}
```