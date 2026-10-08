**Review setup:** The memo was not written in this conversation, so this review doesn't share the author's context. The requested cross-vendor blind seats could not be run because this session has no tools or subagents. Treat this as a single-reviewer, single-model review. Nothing could be executed or looked up. Every finding rests on the text of the memo itself.

## Pass 1: Reconstruct

The memo recommends signing with Northlight and starting a weekly export on 1 November. Its central claim is that only aggregated, anonymous data leaves the company: cohort totals and conversion rates, with no names, contact details or account identifiers. The justification is time saved (two days a month) and the vendor's SOC 2 Type II certification.

For the recommendation to hold, these must be true:
1. The export really is aggregated and anonymous.
2. Sharing it is lawful under the company's privacy and financial-data obligations.
3. The vendor's controls fit this data.
4. The benefit is worth the risk.

The original request also required the memo to "state exactly what data leaves the company."

## Pass 2: Attack (Track A)

- **Facts:** The memo contradicts its own appendix. Appendix A, described by the context as a real extract of last week's file, contains `account_id`, `name`, `email` and `balance_usd` at row level. These are exactly the identifiers the memo says are not sent, plus financial data. There are no cohort totals or conversion rates anywhere in the file.
- **Logic:** SOC 2 Type II is about the vendor's controls. It says nothing about whether the company may lawfully share the data, or whether the vendor needs it. The time-saving benefit does not require row-level PII, because cohort totals could be computed in-house.
- **Alternatives not considered:** aggregating before export, pseudonymizing, doing reporting in-house with existing tooling, or delaying until legal review finishes.
- **Counter-case:** The strongest argument against signing is that the memo itself is the evidence. The actual file is identified, financial, row-level data. Sending it under an "anonymous" label means data subjects, legal, and possibly regulators are misinformed. The memo does not survive this.
- **Pre-mortem:**
  1. The vendor is breached, or a subprocessor misuses the data, and the identified balances are exposed.
  2. A regulator or auditor finds the disclosure was described as anonymous when it was not.
  3. The pipeline was already running before any contract or DPA existed.
- **Missing information:**
  - a DPA or contract terms
  - the lawful basis or regulatory analysis (for example GLBA, GDPR or CCPA, depending on jurisdiction)
  - retention and deletion terms
  - subprocessors
  - the full field list and row counts
  - the transfer mechanism and encryption
  - the vendor's SOC 2 report scope and date
  - cost

## Pass 3: Self-check

The core contradiction is directly visible in the text, so it does not depend on inference. One possible doubt: the `example.test` domains could suggest synthetic data. The context explicitly calls the appendix a real extract, and the memo calls it "last week's run," so I treat it as real. That is also the safer assumption given the stakes.

The most serious problem that could still be missed is whether this file has already been sent to Northlight. "Last week's run" implies the export exists. Whether it was transmitted is unknown.

---

**VERDICT: REJECT.** The memo's central claim, "only aggregated, anonymous data," is directly contradicted by its own Appendix A, which shows row-level names, emails, account IDs and balances.

**CONFIDENCE IN VERDICT: high.** The decisive finding is in the text. Confidence is limited by:
- the blind cross-vendor seats not being run
- not knowing whether the export has already been transmitted

**FINDINGS**

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | "What is shared": "Only aggregated, anonymous data… No names, no contact details and no account identifiers" vs. Appendix A header `account_id,name,email,balance_usd,segment` | The core claim is false according to the memo's own evidence. The export is row-level, directly identifying customer financial data. | Legal approves based on the "anonymous" claim. Identified balances for every customer go to Northlight weekly without an appropriate lawful basis, DPA or notice. This creates breach and regulatory exposure, and the company has misrepresented its disclosures. | Halt sign-off. Rewrite "What is shared" from the actual export spec. Either change the export to genuine aggregates computed in-house, or restate honestly that PII and financial data are shared and run the full legal analysis. |
| 2 | Critical | CONFIRMED | Appendix A ("real extract of last week's file") | The memo itself carries real customer PII and balances. It is being circulated to reviewers, including legal and this review. | The memo is forwarded, attached to tickets, or pasted into tools such as AI review sessions. Customer data spreads beyond need-to-know, which may itself be a reportable incident under internal policy. | Replace the appendix with a schema and synthetic rows. Purge copies. Check whether circulating the memo triggers incident handling. |
| 3 | High | PROBABLE | Appendix A: "first 5 rows of last week's run" vs. recommendation to "start the weekly export on 1 November" | A run already exists before signing. The export pipeline may already be live, and the data may already have been transmitted. | Data has already left the company with no contract or DPA, so the memo would be ratifying a past disclosure rather than deciding a future one. | Confirm from transfer logs whether any file reached Northlight. If it did, escalate to legal and privacy as a possible unauthorized disclosure. |
| 4 | High | CONFIRMED | Request: "State exactly what data leaves the company"; memo: "weekly cohort totals and conversion rates" | The memo fails the request. It has no field list, row counts, transfer method, encryption, retention or recipient scope, and the vague description it does give matches nothing in the file. | Legal reviews a description that does not match the actual data. Approval scope and actual practice diverge. | Add an exact field-level spec (column, type, sensitivity), row volume, frequency, transport and encryption, retention and deletion terms, and subprocessors. Attach it to the contract. |
| 5 | High | CONFIRMED | "Why": "The vendor is SOC 2 Type II certified." | This is unsourced. It also does not address lawful basis, purpose limitation, data minimization, DPA terms or financial-data regulation. | The certification has lapsed or its scope excludes the analytics service. Even if valid, it doesn't make the sharing lawful or minimal. | Obtain the current SOC 2 report and check its scope and period. Add a regulatory and DPA section, signed off by legal before any date is committed. |
| 6 | Medium | CONFIRMED | Recommendation and "Why" | No alternatives were considered. The stated benefit is reporting automation, which does not require PII leaving the company. | The company accepts the full exposure of row-level PII for a benefit that in-house aggregation or a pseudonymized feed would deliver. | Compare options: in-house aggregation, aggregate-only export, pseudonymized export, or status quo. Include cost and risk for each. |
| 7 | Medium | CONFIRMED | "replaces two days of manual reporting each month"; no cost stated | The benefit is unsourced and small, no contract cost is given, and the risk is not weighed against it. | The decision is made on an asymmetric basis: a minor time saving against a large and irreversible exposure. | Source the time estimate, add contract cost, and add a risk assessment. |
| 8 | Medium | CONFIRMED | "start the weekly export on 1 November" (about 3 weeks from today); context: "legal review is pending" | The date is committed before legal review completes. | Schedule pressure pushes the export live before legal findings are resolved. | Make the start date conditional on legal sign-off and an executed DPA. |
| 9 | Low | CONFIRMED | Title "customer behavior data" vs. file fields | The file contains balances and segment, which are financial and profile data, not behavior data. The label understates sensitivity. | Reviewers apply a lower sensitivity classification than the data warrants. | Label the data accurately as customer financial and identity data. |

**WHAT HOLDS UP:** The automation motive is plausible, and SOC 2 Type II is a reasonable baseline requirement for a vendor. Neither fact supports the memo's central claim.

**UNVERIFIED CLAIMS:**
- **Northlight's SOC 2 Type II status:** confirm by obtaining the report and checking its scope and period.
- **"Two days of manual reporting each month":** confirm against time logs or by asking the report owners.
- **Whether last week's file was transmitted:** confirm from SFTP/API transfer logs and with the vendor.
- **Whether Appendix A is complete:** the full file may contain more rows or fields than the 5-row sample. Confirm against the export job definition.

**QUESTIONS FOR THE AUTHOR:**
1. Has any export file already been sent to Northlight? If so, when, and under what agreement?
2. Is the intended export the row-level file in Appendix A, or a genuinely aggregated one that has not been built yet?
3. Does Northlight need anything beyond cohort-level aggregates for the stated reporting use?

**DECISION-MAKER SUMMARY:** Do not sign or start the export. The memo says the data is anonymous aggregates, but its own appendix shows names, emails, account IDs and balances. First confirm whether data has already left the company, and remove the real PII from the memo. If you proceed anyway, you would be sending identified customer financial data under a false description, with no DPA or legal basis on record.

```json
{
  "verdict": "REJECT",
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "location": "What is shared: 'Only aggregated, anonymous data... No names, no contact details and no account identifiers' vs Appendix A header account_id,name,email,balance_usd,segment", "scenario": "Legal approves on the 'anonymous' claim; identified customer balances go to the vendor weekly without lawful basis/DPA, creating breach and regulatory exposure and misrepresented disclosures.", "fix": "Halt sign-off; rewrite the data section from the actual export spec; either aggregate in-house before export or restate that PII/financial data is shared and run full legal analysis."},
    {"severity": "Critical", "evidence_level": "CONFIRMED", "location": "Appendix A (real extract of last week's file)", "scenario": "The memo itself spreads real customer PII and balances to every reader and tool it is pasted into, possibly an internal incident.", "fix": "Replace with schema plus synthetic rows; purge copies; check incident-handling obligations."},
    {"severity": "High", "evidence_level": "PROBABLE", "location": "Appendix A 'last week's run' vs recommendation to start export on 1 November", "scenario": "Export pipeline already ran and may have transmitted data before any contract or DPA.", "fix": "Check transfer logs; if transmitted, escalate to legal/privacy as possible unauthorized disclosure."},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "Request 'State exactly what data leaves' vs memo 'weekly cohort totals and conversion rates'", "scenario": "Legal reviews a description that matches nothing in the actual file; approval scope diverges from practice.", "fix": "Add field-level spec, volumes, transport/encryption, retention, subprocessors; bind it to the contract."},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "Why: 'The vendor is SOC 2 Type II certified.'", "scenario": "Certification unsourced, possibly lapsed or out of scope; even if valid it does not establish lawful basis or minimization.", "fix": "Obtain current SOC 2 report and verify scope; add regulatory/DPA analysis signed off by legal."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "Recommendation and Why section", "scenario": "Full PII exposure accepted for a benefit achievable with in-house or aggregate-only export.", "fix": "Compare in-house aggregation, aggregate-only, pseudonymized, and status-quo options with cost and risk."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "'replaces two days of manual reporting each month'; no cost stated", "scenario": "Decision made on minor, unsourced benefit versus large irreversible exposure.", "fix": "Source the estimate, add contract cost and a risk assessment."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "'start the weekly export on 1 November' with legal review pending", "scenario": "Schedule pressure starts export before legal findings are resolved.", "fix": "Make start conditional on legal sign-off and executed DPA."},
    {"severity": "Low", "evidence_level": "CONFIRMED", "location": "Title 'customer behavior data' vs balance_usd, segment fields", "scenario": "Mislabeling leads reviewers to apply a lower sensitivity classification.", "fix": "Label as customer financial and identity data."}
  ]
}
```