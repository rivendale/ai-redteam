**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent or tools were available, so this is a single-reviewer pass. No customer personal data is repeated in this report. Appendix A is cited by row and column header only.

**VERDICT: REJECT.** The memo's central claim, "only aggregated, anonymous data leaves the company", is contradicted by its own appendix, which shows row-level names, emails, account IDs and balances. The memo itself also now carries real customer data to everyone who reads it.

**CONFIDENCE: high** on findings 1 to 2. Medium overall, limited by:
- same-context review;
- no tools;
- no access to the contract, the data processing agreement (DPA), the privacy notice or the vendor's SOC 2 report.

**INPUTS LEDGER:**
- **Seen:**
  - the original request (request.md);
  - the context (context.md);
  - the memo (memo.md), including Appendix A.
- **Not seen:**
  - **Export job definition or schema.** Matters: it decides which of the memo body or the appendix is true.
  - **Vendor contract and DPA.** Matters for retention, onward use and breach terms.
  - **Customer privacy notice.** Matters for whether this sharing is disclosed.
  - **Northlight's SOC 2 Type II report** (scope, period, exceptions). Matters because the "Why" section relies on it.
  - **Evidence for "two days of manual reporting".** Matters less; it is the only benefit stated.
  - **Where "last week's run" was sent.** Matters greatly; data may already have left the company.

**SEATS AND GATE:**
- **Sensitivity gate: SENSITIVE.** Appendix A is described as a real extract. It contains customer names, email addresses, account identifiers and account balances.
- **Cross-vendor blind seats: REFUSED.** They were requested at depth `deep`, but they may not receive this data. A second opinion is not a reason to send customer financial records to another vendor.
- **Fresh same-vendor subagent:** unavailable in this session.
- **Ran:** this local same-context review only.
- **To get independent seats:** redact Appendix A first, replacing it with the column list and synthetic rows. Then re-run with cross-vendor seats on the redacted memo.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | R, C | memo.md "What is shared" vs Appendix A header `account_id,name,email,balance_usd,segment` | The body says "No names, no contact details and no account identifiers are sent" and that the vendor gets "cohort totals and conversion rates". The appendix, labeled "sample of the weekly export file", is row-level data with name, email, account ID and balance. The memo fails the request to "state exactly what data leaves the company". | Legal approves on the strength of the body text. The export actually ships identified customer financial data to a third party. The result is unlawful disclosure, a privacy notice breach, and regulatory and customer harm. | Get the actual export job and schema. State the exact field list, granularity, cohort definitions and minimum cell size in the memo. Then re-review. If the appendix reflects the real export, the recommendation must be withdrawn. | **confirmed.** Strongest defense: the appendix is a pre-aggregation staging file. But the memo labels it the export file. Either way the memo misstates what leaves the company, so the finding stands. |
| 2 | Critical | CONFIRMED | R | memo.md Appendix A, rows 1–5 | The decision memo embeds real customer personal and financial data. It is being circulated for legal review and was submitted for external model review. | The memo is forwarded, attached or pasted into tools that are not approved for customer data. This is a data handling incident that the memo itself causes. | Remove Appendix A from all copies now and replace it with the column list plus synthetic values. Find out where the memo has already been sent. Assess whether the data protection officer or privacy incident process must be notified. | **confirmed.** The context states the extract is real. The `example.test` domains do not override that statement. |
| 3 | High | PROBABLE | R, A | Appendix A heading: "last week's run" vs "start the weekly export on 1 November" | A run already happened last week, before any signing or approval. If that file went to Northlight, identified data has already left the company without a contract or DPA. | Disclosure has already occurred, and the decision is being framed as prospective. Legal reviews a choice that has, in part, already been made. | Confirm the destination of last week's run and any earlier runs, plus the vendor's access logs. If data was sent, treat it as an incident and request deletion with certification. | **confirmed** as an open risk. The wording establishes that a run occurred; its destination is UNVERIFIED. |
| 4 | High | UNVERIFIED | R | "What is shared"; the memo as a whole | The memo has no legal basis, privacy notice check, DPA, retention period, deletion terms, onward-use or subprocessor limits, transfer location, or check that the subprocessor list is updated. This is financial data, so sector rules may apply. | Even truly aggregated sharing may contradict the published privacy notice or subprocessor list. Disclosures become untrue, and the regulator or customers find out first. | Add a section covering each of the items above. Cite the specific privacy notice clause and the applicable rule text, not a summary. | **confirmed** as an omission. Whether the notice is actually violated is UNVERIFIED. |
| 5 | High | PROBABLE | C, A | "Why": "The vendor is SOC 2 Type II certified." | SOC 2 is an attestation report, not a certification. The memo gives no scope, period, exceptions or bridge letter. SOC 2 also says nothing about whether this sharing is permitted. It is the only security assurance offered. | The report's scope excludes the analytics product, or it is stale or has exceptions. The decision rests on an assurance that does not cover the risk. | Obtain and read the current SOC 2 Type II report. Record its scope, period, opinion and exceptions in the memo. Describe it as an attestation. | **confirmed.** The wording is factually loose, and the substance is UNVERIFIED. |
| 6 | Medium | PROBABLE | A | "Only aggregated, anonymous data…" | "Aggregated" is not "anonymous". Small cohorts, such as a premium segment with few members, can re-identify individuals or their balances. | Weekly cohort totals for small segments let the vendor, or anyone who breaches it, infer individual balances. | Define a minimum cohort size and suppression rule. Have privacy review the anonymization claim. | n/a |
| 7 | Medium | UNVERIFIED | A, D | "Why": "replaces two days of manual reporting each month" | This is the only benefit stated and it has no evidence. The memo considers no alternatives: in-house automation, sending only aggregates produced internally, or doing nothing. | The company takes on third-party data risk to save about 2 person-days a month when a cheaper internal option exists. | Quantify the cost. Compare against automating the report internally and against sending only aggregates computed in-house. | n/a |
| 8 | Low | PROBABLE | A | the memo as a whole | No exit plan: no termination clause, data return or deletion on exit, or way to stop the export. | The vendor relationship ends and historical data stays with the vendor indefinitely. | Add exit and deletion terms and an owner for the export kill switch. | n/a |

**Self-check:** Every finding has a location and a scenario. No SHIP is possible with open Criticals.

**Most likely place for a missed problem:** the export pipeline itself, for example a "segment" or other field that leaks more than its name suggests, or other files sent alongside this one. It cannot be seen without the job definition.

## WHAT HOLDS UP
- The memo has a clear recommendation and a start date. The decision being asked for is unambiguous.
- Including a real sample was the right instinct for evidencing "exactly what data leaves". It is the evidence that exposes the problem. It should have been described by schema, not pasted in.

## UNVERIFIED CLAIMS
- **"No names, no contact details and no account identifiers are sent."** Contradicted by the appendix. Settle it with the export job code, its output schema and a vendor-side receipt log.
- **"Vendor receives weekly cohort totals and conversion rates."** Settle it the same way.
- **"SOC 2 Type II certified."** Settle it by reading the report: scope, period, opinion and exceptions.
- **"Two days of manual reporting each month."** Settle it with time records or the report owner's estimate.

## QUESTIONS FOR THE AUTHOR
1. Is Appendix A what Northlight actually receives, or an internal staging file? Paste the export job's output schema.
2. Where did "last week's run" go? Has any file already reached Northlight?
3. Does the current privacy notice, and any subprocessor list, permit this sharing?

## DECISION-MAKER SUMMARY
Do not sign. The memo says only anonymous aggregates leave the company, but its own appendix shows identified customer financial records. A run may also already have been sent. Pull Appendix A from every copy, confirm what was actually exported and to whom, and resubmit with an exact field list, DPA terms and privacy notice alignment. Proceeding as-is risks unlawful disclosure of customer financial data.

## OWNER SUMMARY
The proposal says only anonymous summary figures would go to the outside company, but its own example file contains individual customers' names, emails and account balances, so the proposal cannot be approved as written. The document itself also contains that real customer information and should be cleaned up and recalled wherever it was sent. Before anything is signed, the team needs to confirm what has actually been sent so far and lay out exactly what would be shared and under what protections.

```json
{
  "verdict": "REJECT",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "memo.md incl. Appendix A", "status": "seen", "matters": true},
    {"item": "export job definition / schema", "status": "not_seen", "matters": true},
    {"item": "vendor contract and DPA", "status": "not_seen", "matters": true},
    {"item": "customer privacy notice / subprocessor list", "status": "not_seen", "matters": true},
    {"item": "Northlight SOC 2 Type II report", "status": "not_seen", "matters": true},
    {"item": "destination of last week's run", "status": "not_seen", "matters": true}
  ],
  "seats": [
    {"vendor": "claude-same-context", "status": "ran", "cross_vendor": false},
    {"vendor": "claude-subagent", "status": "unavailable", "cross_vendor": false},
    {"vendor": "cross-vendor blind seats", "status": "refused", "cross_vendor": true}
  ],
  "sensitivity_gate": {"sensitive": true, "reason": "Appendix A is a real extract containing customer names, emails, account IDs and balances; may not be sent to cross-vendor reviewers."},
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "R", "location": "memo.md 'What is shared' vs Appendix A header", "scenario": "Body claims only anonymous aggregates leave; appendix labeled as the export file contains name, email, account_id, balance_usd. Approval on the body text ships identified financial data to a third party.", "fix": "Obtain the real export schema; state exact fields, granularity, cohort definitions and suppression thresholds; withdraw the recommendation if the appendix is accurate.", "status": "confirmed"},
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "R", "location": "memo.md Appendix A rows 1-5", "scenario": "The memo embeds real customer PII and balances and is being circulated for legal and external review, spreading the data to unapproved recipients.", "fix": "Redact Appendix A to schema plus synthetic values in all copies; trace distribution; assess via the privacy incident process.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "PROBABLE", "track": "R", "location": "Appendix A heading 'last week's run' vs 'start ... on 1 November'", "scenario": "An export already ran before approval; if sent to the vendor, identified data has already left without a contract or DPA.", "fix": "Confirm the destination of all prior runs; if sent, treat as an incident and obtain certified deletion.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "UNVERIFIED", "track": "R", "location": "memo.md whole", "scenario": "No legal basis, privacy-notice check, DPA, retention, onward-use or subprocessor-list update; sharing may contradict published disclosures.", "fix": "Add these items, citing the specific privacy notice clause and the applicable rule text.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "PROBABLE", "track": "C", "location": "memo.md 'Why': 'SOC 2 Type II certified'", "scenario": "SOC 2 is an attestation; scope, period and exceptions are unknown and may not cover the product; it is the only security assurance offered.", "fix": "Read the current report; record scope, period, opinion and exceptions; reword as an attestation.", "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "A", "location": "memo.md 'Only aggregated, anonymous data'", "scenario": "Small cohorts allow re-identification of individuals or their balances.", "fix": "Set a minimum cohort size and suppression rule; get privacy sign-off on the anonymization claim.", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "track": "A", "location": "memo.md 'Why': two days of manual reporting", "scenario": "Third-party data risk is accepted for an unquantified saving, with no internal alternative considered.", "fix": "Quantify the saving; compare against internal automation and sending only internally computed aggregates.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "PROBABLE", "track": "A", "location": "memo.md whole", "scenario": "No exit, termination or deletion-on-exit terms; data persists at the vendor after the relationship ends.", "fix": "Add exit and deletion terms and an owner for stopping the export.", "status": "n/a"}
  ]
}
```