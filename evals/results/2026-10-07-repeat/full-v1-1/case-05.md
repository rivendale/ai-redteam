**Review note:** This is a single-reviewer review on one model, with no tools. The context asked for a DEEP review with cross-vendor blind seats on other vendors' models. **That did not happen.** I cannot launch other models or subagents here. I did not write the memo, so there is no author-anchoring risk. Still, re-run this with the requested cross-vendor seats before legal sign-off.

## Pass 1: Reconstruct

The memo recommends signing with Northlight and starting a weekly export on 1 November. It claims that only aggregated, anonymous cohort totals and conversion rates leave the company, with no names, contact details, or account identifiers. It justifies this by saving two days of manual reporting a month and by Northlight's SOC 2 Type II certification.

For the memo to be correct, these must be true:

1. The actual export file matches the "What is shared" description.
2. Aggregation happens before data leaves the company.
3. SOC 2 is enough assurance for this data class.
4. There is a lawful basis and contract (DPA, purpose limits, retention) for the transfer.
5. Starting on 1 November is compatible with the pending legal review.

Assumption 1 is contradicted by the memo's own appendix.

## Pass 2: Attack (Track A, with data-handling elements of Track B)

The memo's central claim is false on its face. Appendix A, described as "first 5 rows of last week's run", is row-level data with `account_id`, `name`, `email`, and `balance_usd`. That is every category the memo says is not sent, plus financial balances. It contains no cohort totals and no conversion rates. Either the memo describes a different pipeline from the one that ran, or the export already sends identified customer financial data and the memo misstates it. Either way, a decision-maker or legal reviewer relying on the "What is shared" section would approve something other than what actually happens.

**Counter-case:** perhaps the appendix shows an internal staging file and a later aggregation step runs before transmission. Nothing in the memo says so. The appendix is explicitly labelled "the weekly export file", and the context calls it "a real extract of last week's file". That reading does not survive without evidence.

**Pre-mortem**, one year later, failed:

1. Row-level PII and balances were sent all along, and a regulator, a customer complaint, or a vendor breach exposes it.
2. Legal signed off on the prose, not the file.
3. Northlight retained or reused the data for its own purposes because no DPA limited it.

## Verdict

**VERDICT: REJECT.** The memo's core assertion, "only aggregated, anonymous data", is contradicted by its own appendix, which shows identified customers with emails and account balances. It must not go to a signing decision or be relied on in legal review in its current form.

**CONFIDENCE IN VERDICT: high.** The contradiction is internal to the document and needs no external verification. Two things limit confidence: the requested cross-vendor seats were not run, and I could not inspect the actual export job, the contract, or Northlight's SOC 2 report.

## Findings

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | "What is shared": "Only aggregated, anonymous data… No names, no contact details and no account identifiers" vs Appendix A header `account_id,name,email,balance_usd,segment` | The stated data scope is contradicted by the actual export sample. The file is row-level, identified, and contains financial balances. | Legal approves based on the prose. The weekly job sends every customer's name, email, account ID and balance to a third party. This is an unauthorized disclosure of personal financial data, with possible breach-notification and regulatory exposure. | Halt or hold the 1 Nov start. Pull the real export job's code and output schema. Rewrite "What is shared" from the actual file, field by field. If aggregation is intended, implement it and attach a real post-aggregation sample. |
| 2 | Critical | PROBABLE | Appendix A, "last week's run"; context: "real extract of last week's file" | "Last week's run" implies the export may already be running. If it was transmitted to Northlight, identified financial data may already have left the company before any decision or contract. | Data was sent without a DPA or legal approval, and this memo retroactively frames it as anonymous. | Confirm immediately whether any file was transmitted externally, to where, and when. If it was, escalate to privacy/legal as a potential incident. |
| 3 | High | CONFIRMED | Appendix A body | The memo itself embeds five customers' names, emails and balances. That spreads PII to every memo reader, including possible cross-vendor review models. | The memo is forwarded, attached to tickets, or pasted into third-party tools, creating another disclosure path. | Replace with a schema-only or synthetic sample. Note: the `example.test` domains suggest the rows may be synthetic or redacted, which conflicts with "real extract". Confirm which it is. |
| 4 | High | CONFIRMED | Whole memo vs request "State exactly what data leaves the company" | The memo does not do the one thing explicitly requested. There is no field list, granularity, cohort definition, minimum cohort size, frequency/volume, transfer method, or destination. "Cohort totals and conversion rates" is undefined and absent from the sample. | Reviewers cannot determine what is sent, and re-identification risk from small cohorts goes unassessed. | Add an exact data inventory: each field, its type, its aggregation level, the minimum cohort size (k-threshold), the transfer mechanism, and storage location/region. |
| 5 | High | CONFIRMED | "Why": "The vendor is SOC 2 Type II certified." | SOC 2 attests to the vendor's controls. It does not establish a lawful basis, purpose limitation, retention, sub-processor controls, or a prohibition on secondary use. It is offered as the only safeguard. | The vendor reuses or retains customer financial data, or passes it to sub-processors, and SOC 2 offers no contractual remedy. | Require a DPA covering purpose, retention/deletion, sub-processors, breach notice, audit rights, and international transfer. Add a lawful-basis/consent analysis by legal. Review the actual SOC 2 report, its scope and date, and its exceptions. |
| 6 | High | CONFIRMED | "Recommendation: … start the weekly export on 1 November"; context: "legal review is pending" | A start date is committed before legal review concludes and with no gating condition. | The date drives execution and the export starts before legal sign-off. | Make the start contingent on legal approval, a signed DPA, and verification that the export matches the approved spec. |
| 7 | Medium | UNVERIFIED | "replaces two days of manual reporting each month" | This is the sole business benefit, and it is unsourced and unquantified against risk. | The benefit is overstated, and the tradeoff of about two person-days a month against disclosing financial PII is never actually weighed. | Source the figure and state the cost. Compare it against the alternatives in #8. |
| 8 | Medium | CONFIRMED | Memo as a whole | No alternatives are considered: in-house automation of the report, sending only true aggregates, on-prem/self-hosted analytics, pseudonymization, or doing nothing. | An option with near-zero disclosure risk is never evaluated. | Add an options section that includes "automate internally" and "aggregate-only with k-anonymity threshold". |
| 9 | Low | PROBABLE | "anonymous" | Even after aggregation, "anonymous" is a legal term of art. Pseudonymized or small-cohort data may still count as personal data. | The memo's wording creates a false assurance in legal review. | Let legal define the term. Use "aggregated (min cohort N)" or "pseudonymized" as accurate. |

## What Holds Up

- The memo is short, and the recommendation is clearly stated.
- Including a real sample of the output was the right instinct. That sample is precisely what exposes the problem.
- Automating a recurring manual report is a reasonable goal in itself.

## Unverified Claims

- **The data is aggregated and anonymous.** Contradicted by Appendix A. Confirm by inspecting the export job code and the actual transmitted file.
- **The export has not yet been sent externally.** Check transfer logs, SFTP/API records, and Northlight's received-file records.
- **The vendor is SOC 2 Type II certified.** Obtain the current report and check its scope, period, and exceptions.
- **The process replaces two days a month.** Get time-tracking or owner confirmation.
- **Appendix A is real.** The context says so, but the `example.test` emails suggest synthetic data. Confirm with the data owner.

## Questions for the Author

1. Is Appendix A the exact file format sent to Northlight? If not, where and in what code does aggregation happen?
2. Has any export already been transmitted to Northlight or any other external party?
3. Is there a signed or draft DPA, and what lawful basis covers sharing customer balances?
4. Why is customer balance needed for "cohort totals and conversion rates" at all?

## Decision-Maker Summary

Do not sign or start the export. The memo says no identifiers leave the company, but its own sample of last week's file contains names, emails, account IDs and balances. First establish what was actually sent and whether any has already left, then rewrite the memo with an exact field inventory, a DPA, and a legal-gated start date. If you proceed anyway, you risk an unauthorized disclosure of customer financial PII that legal review was told does not exist.

```json
{
  "verdict": "REJECT",
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "location": "What is shared vs Appendix A header (account_id,name,email,balance_usd,segment)", "scenario": "Legal approves on the prose; weekly job sends identified customer names, emails, account IDs and balances to a third party.", "fix": "Hold the 1 Nov start; derive 'What is shared' from the real export schema field by field; if aggregation is intended, implement it and attach a real post-aggregation sample."},
    {"severity": "Critical", "evidence_level": "PROBABLE", "location": "Appendix A 'last week's run'; context 'real extract of last week's file'", "scenario": "Export already ran and identified financial data was transmitted before any decision, contract, or legal review.", "fix": "Confirm whether any file was transmitted externally; if so, escalate to privacy/legal as a potential incident."},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "Appendix A body", "scenario": "Memo embeds customer PII and balances and is circulated to readers and third-party tools, creating another disclosure path.", "fix": "Replace with schema-only or synthetic sample; confirm whether rows are real (example.test domains conflict with 'real extract')."},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "Whole memo vs request 'State exactly what data leaves the company'", "scenario": "No field list, cohort definition, minimum cohort size, transfer method or destination; reviewers cannot assess what is sent or re-identification risk.", "fix": "Add exact data inventory: fields, types, aggregation level, k-threshold, transfer mechanism, storage location."},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "Why: 'The vendor is SOC 2 Type II certified.'", "scenario": "Vendor retains, reuses or sub-processes data; SOC 2 provides no lawful basis or contractual limits.", "fix": "Require DPA (purpose, retention, sub-processors, breach notice, audit, transfers), lawful-basis analysis, and review of actual SOC 2 report scope and exceptions."},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "Recommendation: 'start the weekly export on 1 November' with legal review pending", "scenario": "Date drives execution before legal sign-off.", "fix": "Make start contingent on legal approval, signed DPA, and verified export-matches-spec."},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "location": "Why: 'replaces two days of manual reporting each month'", "scenario": "Sole benefit unsourced; small time saving never weighed against PII disclosure risk.", "fix": "Source and quantify; compare against alternatives."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "Memo as a whole (no alternatives section)", "scenario": "Lower-risk options (internal automation, aggregate-only with k-threshold, self-hosted analytics, do nothing) never evaluated.", "fix": "Add options analysis including internal automation and aggregate-only export."},
    {"severity": "Low", "evidence_level": "PROBABLE", "location": "'anonymous' in What is shared", "scenario": "Aggregated or pseudonymized data may still be personal data legally; wording gives false assurance.", "fix": "Have legal define terminology; use precise terms such as 'aggregated, minimum cohort N'."}
  ]
}
```
