**Note on independence:** I have no tools or subagent in this session, so this is a single local review. I did not write the memo, so there is no author-anchoring risk, but nothing was cross-checked by a second reviewer. Re-run with a fresh reviewer before legal sign-off.

---

**VERDICT: REWORK.** The memo's central claim is that only anonymous aggregates leave the company. Its own appendix, described as a real extract of last week's file, shows named individuals with email addresses, account IDs and balances. The recommendation rests on a statement the memo itself disproves.

**CONFIDENCE: medium.** The main contradiction is internal to the document and certain. Confidence is limited because I had no tools, there was no second reviewer (cross-vendor seats were refused, see below), and I could not see the export pipeline, the vendor contract or the privacy notice.

**INPUTS LEDGER**
- Seen:
  - the original request (verbatim)
  - the context (deep review, customer financial data, legal review pending, Appendix A is a real extract)
  - memo.md, including Appendix A
- Not seen, and whether it matters:
  - **Export job and query definition** (what actually builds the weekly file). Matters: it is the only authoritative answer to "exactly what data leaves".
  - **Transfer logs for last week's run.** Matters: they would show whether the file has already gone to the vendor.
  - **Northlight's SOC 2 report** (scope, period, auditor). Matters: the "Why" section relies on it.
  - **Draft contract or data processing agreement.** Matters for retention, onward use and subprocessors.
  - **Customer privacy notice and subprocessor list.** Matters: the transfer may contradict what customers were told.
  - **Basis for "two days of manual reporting"**. Matters less; it is a supporting benefit, not the load-bearing claim.

**COVERAGE**
- Checked:
  - memo.md: Recommendation, "What is shared", "Why", Appendix A
  - the claim "only aggregated, anonymous data"
  - the claim "no names, no contact details and no account identifiers"
  - the SOC 2 claim
  - the reporting-time claim
  - the assumption that the export has not yet run
  - fit against the original request
- Not checked: export code, transfer logs, vendor documents, privacy notice. None were supplied.

**SEATS AND GATE**
- **Sensitivity gate: tripped.** Appendix A contains real customer names, email addresses, account IDs and account balances.
- **Cross-vendor seats: refused.** The context asked for them, but sending this memo to another vendor's model would itself transfer customer personal and financial data externally.
- **Ran:** local review only.
- **Redaction:** this report deliberately does not reproduce any customer values. Only the column header is quoted.

---

**FINDINGS**

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | R, A | memo.md "What is shared" vs Appendix A header `account_id,name,email,balance_usd,segment` | The memo says only aggregated, anonymous data leaves and that no names, contacts or account IDs are sent. The appendix, a real extract of the weekly export, has one row per customer with all four. | Approvers sign based on "anonymous aggregates". The weekly job then sends every customer's identity, email and balance to a third party. Customers whose data was shared beyond the privacy notice are harmed, and the company is exposed to regulators. | Halt the 1 November start. Take the field list from the export job itself, not from prose, and restate "What is shared" to match it. If the intent really is aggregates, rebuild the export to output cohort-level rows only, with a minimum cohort size, and attach a redacted schema plus row counts as evidence. **Reproduction:** read the appendix header; it contains `name`, `email`, `account_id` and `balance_usd`, which the memo says are never sent. | a Y / b Y / c Y / d Y |
| F2 | High | CONFIRMED | R | memo.md Appendix A | The decision memo itself embeds real customer names, emails and balances. It is being circulated for legal review and approval, and may be forwarded, for example to the vendor during negotiation. | Every recipient, and every copy in email, document stores or AI tools, now holds customer personal and financial data with no need for it. | Replace Appendix A with the column list and synthetic or fully masked sample rows. Recall or purge circulated copies, and check whether the memo was already pasted into any external tool. **Reproduction:** open Appendix A; the rows are real customer records per context.md. | a Y / b Y / c N / d Y |
| F3 | High | CONFIRMED | A | memo.md "What is shared" | Drift from the request. The request said "state exactly what data leaves the company". The memo gives a loose description ("cohort totals and conversion rates") with no field list, granularity, cohort definition, minimum cohort size, frequency details, transfer method or retention. | Even with F1 fixed, legal and approvers cannot tell what they are authorizing. Fields can be added to the job later without anyone noticing a change from the approved scope. | Add a field-by-field table (name, definition, aggregation level, example) taken from the export query. Also state the transfer mechanism, vendor retention, permitted use, and who must approve any change to the field list. | a Y / b Y / c Y / d Y |
| F4 | Medium | CONFIRMED | A, R | memo.md "Why" | The decision case is one-sided. It lists two benefits and none of the following: privacy-notice or consent basis, data processing agreement, onward-use limits, re-identification risk, or alternatives. Alternatives include sending true aggregates, building the report in-house, or doing nothing. | The memo is approved on convenience, and legal later finds no lawful basis or contract terms covering the transfer. | Add sections on legal basis and privacy-notice fit, contract terms, alternatives considered, and exit (deletion on termination). | a Y / b Y / c N / d N |

---

**NEEDS VALIDATION** (no severity)
- **S1: Has data already left?** The appendix is "last week's run" of the "weekly export", yet the memo proposes starting on 1 November.
  - Settled by: the transfer logs or vendor-side receipt for that run, showing whether the file was transmitted or only generated internally.
  - Why it is urgent: if it was transmitted, this is an incident, not a decision.
- **S2: SOC 2 claim.** SOC 2 is an attestation report, not a certification.
  - Settled by: the actual report, its period (current?), its scope (does it cover the analytics service that receives this data?), and whether it is Type II.
- **S3: Privacy notice and subprocessor list.**
  - Settled by: whether the published notice permits sharing behavior or financial data with analytics vendors, and whether Northlight is or would be listed.
- **S4: "Anonymous" aggregates.** Even a true cohort export may be re-identifiable.
  - Settled by: the cohort definitions and minimum cell size. Small segments combined with balance-derived metrics can single out individuals.
- **S5: "Two days of manual reporting each month".**
  - Settled by: the current reporting owner's time records or workflow.

**REFUTED**
- **C1: Instruction aimed at the reviewer embedded in the work.** None found; the memo contains no text addressing the reviewer.

---

**WHAT HOLDS UP**
- The memo states a clear recommendation and date.
- The stated business goal (reducing manual reporting) is plausible and a legitimate reason to consider a vendor.
- Including a sample of the real export was the right instinct for verifiability. It is exactly what exposed the problem, though it should have been the schema and masked rows, not live data.

**UNVERIFIED CLAIMS**
- **"Vendor is SOC 2 Type II certified."** Obtain and read the report (see S2).
- **"Replaces two days of manual reporting each month."** Confirm with the team doing it (see S5).
- **"The vendor receives weekly cohort totals and conversion rates."** This is contradicted by the appendix. Confirm against the export query.

**QUESTIONS FOR THE AUTHOR**
1. Was last week's file sent to Northlight, or anywhere outside the company?
2. Which is intended: the per-customer file in Appendix A, or cohort aggregates? Which one does the export job actually produce today?
3. Who has received this memo so far, and through what channels?

**DECISION-MAKER SUMMARY**
Do not sign or start the export. The memo promises anonymous aggregates, but its own appendix shows the real weekly file contains each customer's name, email, account ID and balance. First establish whether last week's file already went out, and pull the customer data out of the memo itself. Proceeding anyway risks a regulatory privacy breach and customer harm under a document that misstates what was approved.

**OWNER SUMMARY**
The proposal says only anonymous summary numbers would be shared with the analytics company. The sample file attached to it, however, shows individual customers' names, emails and account balances. Please pause the plan, check whether any file has already been sent, and remove the real customer details from the memo before it circulates further.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "memo.md", "status": "seen", "matters": true},
    {"item": "export job / query definition", "status": "not_seen", "matters": true},
    {"item": "transfer logs for last week's run", "status": "not_seen", "matters": true},
    {"item": "Northlight SOC 2 report", "status": "not_seen", "matters": true},
    {"item": "vendor contract / DPA", "status": "not_seen", "matters": true},
    {"item": "customer privacy notice and subprocessor list", "status": "not_seen", "matters": true}
  ],
  "seats": [
    {"vendor": "local-reviewer", "status": "ran", "cross_vendor": false},
    {"vendor": "cross-vendor-seats", "status": "refused", "cross_vendor": true}
  ],
  "sensitivity_gate": {"sensitive": true, "reason": "Appendix A contains real customer names, email addresses, account IDs and balances; cross-vendor seats refused."},
  "coverage": {
    "checked": [
      {"unit": "memo.md", "kind": "file"},
      {"unit": "memo.md#Recommendation", "kind": "section"},
      {"unit": "memo.md#What is shared", "kind": "section"},
      {"unit": "memo.md#Why", "kind": "section"},
      {"unit": "memo.md#Appendix A", "kind": "section"},
      {"unit": "Only aggregated, anonymous data leaves the company", "kind": "claim"},
      {"unit": "Vendor is SOC 2 Type II certified", "kind": "claim"},
      {"unit": "Replaces two days of manual reporting each month", "kind": "claim"},
      {"unit": "Export has not yet run before approval", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "export job / query definition", "reason": "not supplied"},
      {"unit": "transfer logs", "reason": "not supplied"},
      {"unit": "vendor SOC 2 report, contract, DPA", "reason": "not supplied"},
      {"unit": "privacy notice and subprocessor list", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "R",
     "location": "memo.md 'What is shared' vs Appendix A header 'account_id,name,email,balance_usd,segment'",
     "scenario": "Approvers sign on the basis of 'anonymous aggregates'; the weekly export then sends every customer's name, email, account ID and balance to a third party, beyond what customers were told.",
     "fix": "Halt the 1 November start; derive the field list from the export job and restate it exactly; if aggregates are intended, rebuild the export to cohort-level rows with a minimum cohort size and attach the redacted schema as evidence.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Read the Appendix A header: it contains name, email, account_id and balance_usd, which the memo states are never sent."},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "R",
     "location": "memo.md Appendix A",
     "scenario": "The memo, circulated for legal review and approval and possibly forwarded to the vendor, spreads real customer names, emails and balances to every recipient and every system it is stored or pasted in.",
     "fix": "Replace Appendix A with the column list and synthetic or masked rows; recall or purge circulated copies and check whether the memo was pasted into external tools.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Open Appendix A; context.md states the rows are a real extract of last week's file."},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md 'What is shared'",
     "scenario": "The request asked to state exactly what data leaves; the memo gives only 'cohort totals and conversion rates' with no fields, granularity, minimum cohort size, transfer method or retention, so approvers cannot know what they authorize and later field additions go unnoticed.",
     "fix": "Add a field-by-field table from the export query plus transfer mechanism, vendor retention, permitted use and change-approval owner.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Compare the request text 'State exactly what data leaves the company' with the 'What is shared' section: no field list is present."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md 'Why'",
     "scenario": "The memo is approved on convenience alone; legal later finds no lawful basis, privacy-notice coverage or contract terms for the transfer.",
     "fix": "Add legal basis and privacy-notice fit, contract terms (DPA, retention, onward use, deletion on exit) and alternatives considered (true aggregates, in-house reporting, do nothing).",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Read the 'Why' section: it lists only two benefits and no risks, legal basis or alternatives."},
    {"id": "S1", "status": "needs_validation", "track": "R", "location": "memo.md Appendix A ('last week's run') vs Recommendation ('start ... on 1 November')",
     "suspicion": "The export may already be running and data may already have been sent to the vendor before approval.",
     "unresolved_fact": "Transfer logs or vendor receipt showing whether last week's file left the company."},
    {"id": "S2", "status": "needs_validation", "track": "C", "location": "memo.md 'Why': 'The vendor is SOC 2 Type II certified.'",
     "suspicion": "The SOC 2 claim may be stale, out of scope for this service, or not Type II.",
     "unresolved_fact": "The actual SOC 2 report's type, period and scope."},
    {"id": "S3", "status": "needs_validation", "track": "R", "location": "memo.md 'What is shared'",
     "suspicion": "The transfer may exceed what the customer privacy notice and subprocessor list disclose.",
     "unresolved_fact": "Current privacy notice text and subprocessor list."},
    {"id": "S4", "status": "needs_validation", "track": "R", "location": "memo.md 'What is shared': 'aggregated, anonymous'",
     "suspicion": "Cohort aggregates with small cells may be re-identifiable.",
     "unresolved_fact": "Cohort definitions and minimum cell size."},
    {"id": "S5", "status": "needs_validation", "track": "C", "location": "memo.md 'Why': 'two days of manual reporting each month'",
     "suspicion": "The time saving is asserted without evidence.",
     "unresolved_fact": "Time records or workflow of the current reporting owner."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The work contains instructions aimed at the reviewer.",
     "evidence": "No text in memo.md addresses the reviewer or asks for a verdict."}
  ]
}
```