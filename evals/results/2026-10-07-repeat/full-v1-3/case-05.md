# Redteam review: Northlight data-sharing decision memo

**Review setup:** No subagent tool was available, and I could not provide the cross-vendor blind seats that `context.md` asks for. This is a single-model review with no tools. The memo was not written in this conversation, so anchoring risk is lower, but the requested multi-vendor review has **not** been done. Re-run it with those seats before legal relies on this memo.

## Pass 1: Reconstruct

The memo recommends signing with Northlight and starting a weekly export on 1 November. Its central claim is that only aggregated, anonymous data leaves the company: cohort totals and conversion rates, with no names, contact details or account identifiers. It justifies the deal by time saved (two days a month) and the vendor's SOC 2 Type II certification.

For the memo to be correct, these must be true:
1. The export file actually matches the "What is shared" section.
2. The cohorts are large enough that individuals cannot be re-identified.
3. SOC 2 Type II covers the services in scope and is current.
4. No export has happened yet before legal approval.
5. The time-savings figure is real.

Appendix A breaks assumption 1 outright, and the phrase "last week's run" casts doubt on assumption 4.

---

**VERDICT: REJECT.** The memo's central claim is contradicted by its own Appendix A, which shows row-level customer records with direct identifiers and balances, so the memo cannot go to legal or be signed as written.

**CONFIDENCE IN VERDICT: high.** The decisive finding is a direct textual contradiction inside the memo, so tools are not needed to establish it. Confidence is limited on the secondary findings: whether data has already been shared, whether the appendix values are real, and the vendor's SOC 2 scope. The requested cross-vendor seats were not run.

## FINDINGS (by severity)

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | "What is shared": "Only aggregated, anonymous data leaves the company. No names, no contact details and no account identifiers" vs. Appendix A header `account_id,name,email,balance_usd,segment` | The memo's core assurance is false by its own evidence. The file is row-level, per-customer, and contains account IDs, full names, emails and financial balances. It has no cohort totals and no conversion rates. | Legal approves based on the prose. The weekly export then sends identified customer financial data to a third party. Possible exposures include privacy and financial-data law (e.g. GDPR or GLBA, depending on jurisdiction), breach of customer terms, and the reputational harm of a misleading internal record. | Rewrite "What is shared" from the actual export spec: a field-by-field schema, granularity, and a minimum cohort size. Regenerate Appendix A from the real aggregated output. Test: diff the export job's output schema against the memo's list and block on any mismatch. |
| 2 | Critical | PROBABLE (UNVERIFIED whether data was transmitted) | Appendix A caption: "first 5 rows of last week's run"; Recommendation: "start the weekly export on 1 November" | "Last week's run" means the export job already exists and has executed before approval. If that run was sent to Northlight, identified customer financial data may already have left the company. That could be an incident requiring notification, not a future decision. | The file was delivered to the vendor (pilot, SFTP drop, trial account) before a contract or DPA was in place. Every week of delay in finding out widens the exposure and any notification clock. | Ask immediately whether any run was transmitted externally, and where. Pull job logs and transfer logs, and check vendor-side receipt. If data was transmitted, escalate to privacy/security incident handling and disable the job pending review. |
| 3 | High | CONFIRMED | Appendix A rows (names, emails, balances) inside the memo itself; context.md: "Appendix A is a real extract" | The decision memo itself spreads real customer PII and financial data to everyone who reads it, including legal reviewers and any further distribution. (The `example.test` domains suggest the data may be synthetic, which conflicts with the context. See Questions.) | The memo is forwarded, attached to tickets, or pasted into tools, creating an uncontrolled internal copy of customer financial records. | Replace the appendix with a schema plus synthetic or redacted rows. Restrict and purge the existing copies of this memo. |
| 4 | High | CONFIRMED | Whole memo vs. request: "State exactly what data leaves the company" | The request asked for an exact statement. The memo gives a vague one: "cohort totals and conversion rates", with no fields, no cohort definitions, no granularity, no minimum group size, and no frequency or retention details beyond "weekly". | Even after Finding 1 is fixed, legal cannot assess re-identification risk. Small cohorts (e.g. "premium, balance > $25k, region X") can single out individuals. | List every field, cohort keys, the minimum cohort size (e.g. suppress cells with fewer than k members), rounding, and whether any join key persists. |
| 5 | High | CONFIRMED (absence) | Whole memo | There are no data-protection terms: no DPA, purpose limitation, retention or deletion terms, sub-processors, data location, onward-sharing ban, re-identification prohibition, audit rights, or termination and return terms. | The vendor retains or combines the data, or a sub-processor is breached. The company has no contractual remedy and cannot show due diligence. | Add a section on contract and DPA terms. Make signing conditional on legal sign-off of those terms. |
| 6 | Medium | UNVERIFIED | "The vendor is SOC 2 Type II certified." | The claim is unsourced. SOC 2 is an attestation report, not a certification, and its scope, period and exceptions matter. It also says nothing about whether *sharing* this data is lawful or appropriate. | The report is stale, scoped to a different product, or carries qualified exceptions. The memo then overstates assurance. | Attach the current SOC 2 Type II report and record its period, scope and exceptions. Treat it as a security control, not legal justification. |
| 7 | Medium | UNVERIFIED | "It replaces two days of manual reporting each month." | This is the only stated benefit, and it is unsourced. Weighed against Critical-level data risk, the cost-benefit case is thin. | A modest saving is accepted in exchange for regulatory and reputational exposure. | Quantify the saving with its source. Compare alternatives (Finding 8). |
| 8 | Medium | CONFIRMED (absence) | "Why" section | No alternatives are considered: in-house automation of the report, sending only pre-aggregated outputs, a vendor tool deployed in the company's own environment, or doing nothing. | A lower-risk option that achieves the same time saving is never evaluated. | Add an options table with risk and cost for each option. |
| 9 | Medium | CONFIRMED | Request says "customer behavior data"; Appendix A contains balances and segment only | The data shown is financial and identity data, not behavioral data. The memo and the export do not match the stated purpose of the deal. | The scope of sharing drifts from "behavior analytics" to "customer financial records" without anyone deciding that. | State the purpose, and show that each exported field is necessary for it (data minimization). |
| 10 | Low | CONFIRMED | Recommendation: "start ... on 1 November" | A fixed start date is set while legal review is pending, which pressures approval. | The date arrives and the job turns on before legal finishes. | Make the start date conditional on legal approval and on the export spec being verified. |

## WHAT HOLDS UP
- The memo is short and states a clear recommendation.
- The operational motivation (removing manual reporting) is plausible.
- Requiring a SOC 2 Type II report is a reasonable baseline vendor check, if it is actually evidenced.

## UNVERIFIED CLAIMS
- **"Only aggregated, anonymous data leaves the company."** This is contradicted by Appendix A. Confirm against the export job's code or config and its actual output.
- **Whether "last week's run" was transmitted externally.** Check transfer logs and the vendor account.
- **SOC 2 Type II status.** Obtain the report and check its period and scope.
- **"Two days of manual reporting."** Get timesheets or a statement from the report owner.
- **Whether Appendix A is real or synthetic.** The context says real; the `example.test` domains suggest synthetic. Confirm with the author.

## QUESTIONS FOR THE AUTHOR
1. Was any export run, including "last week's", sent to Northlight or any other external party?
2. Is Appendix A the true output of the export job? If not, what is the actual output schema?
3. Is Appendix A real customer data or synthetic?
4. What are the cohort definitions and the minimum cohort size?

## DECISION-MAKER SUMMARY
Do not sign or start the export. The memo says only anonymous aggregates are shared, but its own sample shows names, emails, account IDs and balances. First, confirm whether last week's run already left the company, and treat it as a possible incident if it did. Then require a corrected memo with an exact field-level schema and contract and DPA terms before legal review continues.

```json
{
  "verdict": "REJECT",
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "location": "'What is shared' section vs. Appendix A header account_id,name,email,balance_usd,segment", "scenario": "Legal approves the memo's claim of aggregated anonymous data while the export actually sends row-level identified customer records with financial balances to the vendor.", "fix": "Rewrite 'What is shared' from the real export spec (field-by-field, granularity, minimum cohort size); regenerate Appendix A from actual aggregated output; diff export schema against memo and block on mismatch."},
    {"severity": "Critical", "evidence_level": "PROBABLE", "location": "Appendix A caption 'last week's run' vs. recommendation to start on 1 November", "scenario": "The export already ran before approval; if it was sent to Northlight, identified financial data has already left the company, which may be a notifiable incident.", "fix": "Check job and transfer logs and vendor receipt now; if transmitted, escalate to incident response and disable the job pending review."},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "Appendix A rows; context.md says it is a real extract", "scenario": "The memo itself circulates real customer names, emails and balances to every reader and onward recipient.", "fix": "Replace with schema plus synthetic or redacted rows; restrict and purge existing copies."},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "Whole memo vs. request 'State exactly what data leaves the company'", "scenario": "Vague 'cohort totals and conversion rates' gives legal no basis to assess re-identification; small cohorts can single out individuals.", "fix": "List every field, cohort keys, minimum cohort size with small-cell suppression, rounding, and any persistent join keys."},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "Whole memo (absence)", "scenario": "No DPA, retention, deletion, sub-processor, purpose-limitation or re-identification terms; vendor misuse or breach leaves no contractual remedy.", "fix": "Add a contract and DPA terms section; make signing conditional on legal sign-off of those terms."},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "location": "'The vendor is SOC 2 Type II certified.'", "scenario": "The report is stale, out of scope, or has exceptions; the memo overstates assurance and conflates security attestation with lawfulness of sharing.", "fix": "Attach the current report with period, scope and exceptions; do not use it as legal justification."},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "location": "'It replaces two days of manual reporting each month.'", "scenario": "An unquantified, modest benefit is traded for Critical-level data risk.", "fix": "Source and quantify the saving; weigh it against alternatives."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "'Why' section (absence of alternatives)", "scenario": "Lower-risk options (in-house automation, pre-aggregated outputs only, in-environment tooling, do nothing) are never evaluated.", "fix": "Add an options comparison with risk and cost per option."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "Request says 'customer behavior data'; Appendix A contains balances and segment", "scenario": "Sharing scope drifts from behavior analytics to customer financial and identity data without an explicit decision.", "fix": "State the purpose and justify each field against it (data minimization)."},
    {"severity": "Low", "evidence_level": "CONFIRMED", "location": "Recommendation: 'start the weekly export on 1 November'", "scenario": "A fixed date set while legal review is pending pressures approval, and the job may start before review completes.", "fix": "Make the start date conditional on legal approval and verified export spec."}
  ]
}
```