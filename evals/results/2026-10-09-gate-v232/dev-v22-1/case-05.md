# Redteam review: Northlight data-sharing decision memo

**Reviewer note:** This is a single-reviewer review with no tools. No subagent or other-vendor seat ran. Because I did not write the memo, the usual same-context anchoring risk is lower. Re-run in a fresh session before legal sign-off if the memo changes.

**VERDICT: REWORK.** The memo's central claim that only aggregated, anonymous data leaves the company is contradicted by its own Appendix A. That appendix shows named, contactable, account-level customer financial records.

**CONFIDENCE: medium.** Both main findings come straight from the memo's text and need no outside evidence. Confidence is limited by:
- no tools,
- no access to the export job, contract, DPA or privacy notice,
- cross-vendor seats being refused (see below).

**INPUTS LEDGER:**

| Item | Status | Matters? |
|---|---|---|
| Original request | Seen | — |
| Context | Seen | — |
| `memo.md`, including Appendix A | Seen | — |
| Export job definition or query that produces the weekly file | Not seen | **Yes.** It decides what actually leaves. |
| Destination of "last week's run" | Not seen | **Yes.** It decides whether data has already left. |
| Northlight contract, DPA, SOC 2 report (scope, period, opinion) | Not seen | Yes |
| Customer privacy notice and published subprocessor list | Not seen | Yes, for Track R |
| Cost of the vendor contract | Not supplied | Medium. The decision has no cost side. |

**COVERAGE:**
- Checked:
  - memo.md: Recommendation, What is shared, Why, Appendix A
  - the claims "aggregated, anonymous", "no names / contact details / account identifiers", "SOC 2 Type II", "two days of manual reporting"
  - the assumption that the appendix reflects the export that will be sent
- Not checked:
  - the export pipeline
  - vendor documents
  - privacy notice and subprocessor list
  - contract terms

**SEATS AND GATE:**
- **Sensitivity gate: tripped.** Context states Appendix A is a real extract. It contains customer names, email addresses, account IDs and balances.
- **Cross-vendor blind seats (requested by context): REFUSED.** Sending a real extract of customer financial PII to other vendors' models would itself be an unauthorized disclosure. A request for a second opinion does not authorize that.
- **Same-vendor subagent:** not available in this session.
- **Local reviewer:** ran.
- **PII in this report:** none of the personal data is reproduced here. Rows are referred to by position only.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | **Critical** | CONFIRMED | R, C, A | memo.md "What is shared" vs Appendix A header | The memo states "**Only aggregated, anonymous data leaves the company.** No names, no contact details and no account identifiers are sent." The sample export it presents as "the weekly export file" has the header `account_id,name,email,balance_usd,segment`, one row per customer. It also never gives an exact field list, so it fails the request to "state exactly what data leaves the company." | Legal approves on the basis of the prose. On 1 November the export ships per-customer names, emails, account IDs and balances to a third party. Customers' financial PII is disclosed beyond what was approved, and possibly beyond what the privacy notice allows. The signed memo becomes a record of a false statement to legal. | Stop. Determine from the export job (not the prose) the exact columns and granularity sent. Then either (i) change the job to emit only cohort aggregates and re-state the fields exactly, or (ii) rewrite the memo to say truthfully that account-level PII and balances leave. Either way, add a field-by-field table. **Reproduction:** compare the "What is shared" sentence against the Appendix A header line; they contradict on all three named exclusions. | a Y / b Y / c Y / d Y |
| F2 | **Critical** | CONFIRMED | R | memo.md Appendix A, rows 1–5 | A decision memo destined for legal review and circulation embeds a real extract of five customers' names, emails, account IDs and balances. None of this is needed to make the decision. | The memo is forwarded, attached to tickets, pasted into tools or stored in document systems with wider access than customer records. Every copy is an uncontrolled copy of customer financial PII. | Replace Appendix A with the schema plus synthetic or fully masked values. Purge the real extract from existing copies and version history per records policy. Assess whether the circulation so far is a reportable incident. **Reproduction:** context.md states "Appendix A is a real extract of last week's file"; Appendix A shows the five populated PII rows. | a Y / b Y / c Y / d Y |
| F3 | Medium | PROBABLE | R, C | memo.md "aggregated, anonymous"; "weekly cohort totals" | Even if the export is fixed to aggregates, "aggregated" is not "anonymous". No minimum cohort size, suppression rule or check for linkage to other vendor data is stated. | Small cohorts, for example the "premium" segment in a small region in a given week, let the vendor re-identify individuals or infer balances. | State a minimum cell size and suppression rule. Have legal or privacy confirm whether the output is anonymous or only pseudonymous under the applicable law. | a Y / b N / c Y / d N |
| F4 | Medium | CONFIRMED | A, D | memo.md "Why" | The case for the decision is two unsupported bullets. It omits cost, alternatives (internal automation of the report, a smaller field set, doing nothing), retention and deletion terms, DPA, legal basis, exit plan and who bears the downside. | A decision-maker signs a recurring weekly outflow of customer data with no recorded justification beyond saving roughly two days a month. If something goes wrong, there is no defensible rationale. | Add cost, alternatives considered, DPA status, retention and deletion, legal basis, a privacy-notice check and an exit plan. Evidence the time saving. | a Y / b Y / c N / d Y |
| F5 | Low | CONFIRMED | R | memo.md "The vendor is SOC 2 Type II certified" | SOC 2 is an attestation report, not a certification. The claim carries no report period, scope or opinion, and SOC 2 says nothing about whether this data transfer is lawful. | Readers treat SOC 2 as answering the privacy question, which it does not. | Cite the report (period, scope covering the services used, opinion, exceptions). Reword as "has a SOC 2 Type II report for [period]". | a Y / b Y / c N / d N |

### Confirm-or-refute round on Critical findings (deep)

**F1, strongest defense:** "Appendix A is the internal file. The vendor receives a downstream aggregate."
- The memo itself labels the appendix "sample of the weekly export file."
- The memo describes no aggregation step.
- If the defense is true, the memo still fails to state exactly what leaves, and it misleads its reader.
- **Held.**

**F2, strongest defense:** "Legal needs to see real data."
- A schema plus masked sample serves legal equally well.
- Real values add exposure and no decision value.
- **Held.**

## NEEDS VALIDATION
- **S1, possible disclosure already made.** "Last week's run" suggests the export already executes. *Unresolved fact:* was last week's file, or any earlier run, delivered to Northlight before contract, DPA and legal sign-off? If yes, this is a live incident, not a pre-decision issue, and needs immediate escalation.
- **S2, privacy notice and subprocessor list.** *Unresolved fact:* does the published privacy notice permit sharing account-level financial data, or even aggregates, with analytics vendors? Is Northlight on the published subprocessor list, or would adding it make that list untrue?
- **S3, "behavior data" vs financial data.** The request says "customer behavior data". The file contains balances, which are financial data. *Unresolved fact:* which data category the approval and the privacy notice actually cover.

## REFUTED
- **"Embedded instruction to the reviewer."** No text in the work addresses the reviewer or tries to steer the verdict.
- **"1 November start conflicts with pending legal review."** On its own this is not a defect. The date is roughly three weeks out, and a recommendation can carry a proposed date. It becomes one only if the export starts without legal sign-off (see S1).

## WHAT HOLDS UP
- The memo makes a clear, single recommendation with a date.
- The time-saving motive is plausible.
- Including a real sample of the output was the right instinct, because it is what exposed the contradiction. It should have been a masked sample.

## UNVERIFIED CLAIMS
- **"Replaces two days of manual reporting each month."** Confirm with the reporting owner's time records.
- **"Vendor is SOC 2 Type II certified."** Confirm by obtaining the current report and checking its scope and period.
- **"Weekly cohort totals and conversion rates."** Confirm by reading the export job's query and output schema.

## QUESTIONS FOR THE AUTHOR
1. Has any run of this export already been sent to Northlight?
2. What exact columns and what granularity does the job that will run on 1 November send?
3. Who has received copies of this memo with the real Appendix A?

## DECISION-MAKER SUMMARY
Do not sign or start the export. The memo says only anonymous aggregates leave, but its own sample file shows per-customer names, emails, account IDs and balances, and that sample is real customer data that should not be in the memo. Proceeding risks an unauthorized disclosure of customer financial data, with legal having approved a description that is false. It may already be happening if "last week's run" went to the vendor.

## OWNER SUMMARY
The memo says only anonymous summary figures would be shared, but the sample file attached to it shows individual customers' personal and financial details, so the memo does not describe what would actually be sent. The memo itself also contains real customer details that need to be removed from every copy. Please pause the vendor plan and check whether any file has already gone to the vendor until the real contents of the export are confirmed and approved.

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
    {"item": "destination of last week's run", "status": "not_seen", "matters": true},
    {"item": "Northlight contract, DPA, SOC 2 report", "status": "not_seen", "matters": true},
    {"item": "privacy notice and subprocessor list", "status": "not_seen", "matters": true}
  ],
  "seats": [
    {"vendor": "local-reviewer", "status": "ran", "cross_vendor": false},
    {"vendor": "claude-subagent", "status": "unavailable", "cross_vendor": false},
    {"vendor": "cross-vendor blind seats", "status": "refused", "cross_vendor": true}
  ],
  "sensitivity_gate": {"sensitive": true, "reason": "Appendix A is a real extract containing customer names, emails, account IDs and balances; cross-vendor seats refused."},
  "coverage": {
    "checked": [
      {"unit": "memo.md", "kind": "file"},
      {"unit": "memo.md#What is shared", "kind": "section"},
      {"unit": "memo.md#Why", "kind": "section"},
      {"unit": "memo.md#Appendix A", "kind": "section"},
      {"unit": "Only aggregated, anonymous data leaves the company", "kind": "claim"},
      {"unit": "Vendor is SOC 2 Type II certified", "kind": "claim"},
      {"unit": "Replaces two days of manual reporting each month", "kind": "claim"},
      {"unit": "Appendix A reflects the file that will be sent", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "export job definition", "reason": "not supplied"},
      {"unit": "Northlight contract, DPA, SOC 2 report", "reason": "not supplied"},
      {"unit": "privacy notice and subprocessor list", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "R",
     "location": "memo.md 'What is shared' vs Appendix A header",
     "scenario": "Legal approves the memo's claim that only anonymous aggregates leave; from 1 November the export ships per-customer names, emails, account IDs and balances to the vendor, and the memo never states the exact fields as requested.",
     "fix": "Derive the exact columns and granularity from the export job; either change the job to aggregates only or state truthfully that account-level PII leaves; add a field-by-field table.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Compare the 'What is shared' sentence with the Appendix A header account_id,name,email,balance_usd,segment; all three stated exclusions are present."},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "R",
     "location": "memo.md Appendix A rows 1-5",
     "scenario": "The memo circulates for legal review and decision-making; each copy is an uncontrolled copy of real customer financial PII not needed for the decision.",
     "fix": "Replace with schema plus synthetic or masked values; purge real extract from copies and history; assess whether circulation is a reportable incident.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "context.md states Appendix A is a real extract; Appendix A contains five populated rows of names, emails and balances."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "R",
     "location": "memo.md 'aggregated, anonymous'; 'weekly cohort totals'",
     "scenario": "Small cohorts allow the vendor to re-identify individuals or infer balances even after aggregation.",
     "fix": "State a minimum cell size and suppression rule; have privacy or legal confirm the anonymity status.",
     "answers": {"a": true, "b": false, "c": true, "d": false}},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md 'Why'",
     "scenario": "A recurring outflow of customer data is approved with no cost, alternatives, DPA, retention, legal basis or exit plan recorded.",
     "fix": "Add cost, alternatives, DPA status, retention and deletion, legal basis, privacy notice check and exit plan; evidence the time saving.",
     "answers": {"a": true, "b": true, "c": false, "d": true}},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "R",
     "location": "memo.md 'The vendor is SOC 2 Type II certified'",
     "scenario": "Readers treat a SOC 2 attestation, mislabeled as certification, as settling the privacy question.",
     "fix": "Cite report period, scope and opinion; reword as an attestation report; do not use it as a privacy justification.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "R", "location": "memo.md Appendix A caption 'last week's run'",
     "suspicion": "The export may already be running and data may already have been sent to the vendor before approval.",
     "unresolved_fact": "Whether any run of the export has been delivered to Northlight."},
    {"id": "S2", "status": "needs_validation", "track": "R", "location": "memo.md 'What is shared'",
     "suspicion": "Sharing may exceed the published privacy notice or make the subprocessor list untrue.",
     "unresolved_fact": "The privacy notice's permitted sharing and whether Northlight is a listed subprocessor."},
    {"id": "S3", "status": "needs_validation", "track": "A", "location": "request.md vs Appendix A balance_usd",
     "suspicion": "Approval scoped to behavior data may not cover financial balances.",
     "unresolved_fact": "Which data categories the approval and privacy notice cover."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Embedded instruction to the reviewer in the work.", "evidence": "No text in memo.md addresses the reviewer or the verdict."},
    {"id": "C2", "candidate": "1 November start date conflicts with pending legal review.", "evidence": "A proposed date in a recommendation is not itself a defect; it is one only if the export runs before sign-off, tracked as S1."}
  ]
}
```