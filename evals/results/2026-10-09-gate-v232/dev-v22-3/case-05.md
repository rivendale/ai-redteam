# Redteam report: decision memo on sharing customer behavior data with Northlight

**VERDICT: REJECT.** The memo's central factual claim is that only aggregated, anonymous data leaves the company. Its own appendix, described as a real extract of last week's file, shows account IDs, full names, email addresses and account balances. The memo also copies that customer data into a document that is being circulated for legal review.

**CONFIDENCE: high** on the findings that matter. They are tied to exact lines and need no outside evidence. Three things limit it:
- No tools were available in this session.
- No independent subagent was available, so this is a single-reviewer, same-context review. The memo was not written in this conversation, so the anchoring risk is lower, but re-run it in a fresh session before relying on it for the legal sign-off.
- The cross-vendor seats were refused (see below).

**INPUTS LEDGER**
- **Seen:**
  - `request.md` (the original request, verbatim)
  - `context.md`
  - `memo.md`, including Appendix A
- **Not seen, and it matters:**
  - **The export job's definition or query.** This is the authoritative statement of which fields leave the company. Without it, I cannot tell whether the appendix or the memo's claim reflects reality.
  - **Whether last week's file was sent to Northlight.** This determines whether there is already a disclosure incident.
  - **The Northlight SOC 2 Type II report:** its scope, period, and any exceptions.
  - **The data processing agreement and the draft contract.**
  - **The customer privacy notice and the published list of subprocessors.**
- **Not seen, and it matters less:**
  - The basis for the "two days of manual reporting" figure.

**COVERAGE**
- **Checked:**
  - `memo.md` §Recommendation, §What is shared, §Why, and Appendix A
  - The memo against the original request
  - The statement in `context.md` that Appendix A is real
- **Not checked:**
  - The export code or job
  - The vendor contract and data processing agreement
  - The SOC 2 report
  - The privacy notice and subprocessor list
  - The transfer logs

**SEATS AND GATE**
- **Sensitivity gate: tripped.** Appendix A contains customer names, email addresses, account identifiers and balances. `context.md` says it is real customer financial data.
- **Cross-vendor seats: refused**, even though deep review with cross-vendor seats was requested. A second opinion is not a reason to send customer financial data to another vendor. If you want cross-vendor seats, run them on a copy of the memo with Appendix A removed or replaced with synthetic data.
- **Subagent seat:** not available in this session.
- **Local review:** ran (this report).

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | C, R, A | memo.md §What is shared, "Only aggregated, anonymous data leaves the company. No names, no contact details and no account identifiers are sent." vs Appendix A header `account_id,name,email,balance_usd,segment` | The memo's central claim is contradicted by its own sample of the real export. The file is row-level, identified data with financial balances. It is neither aggregated nor anonymous. | Legal and the decision-maker approve on the strength of "aggregated, anonymous". The weekly job then sends every customer's name, email, account ID and balance to a third party. That disclosure is probably not covered by the privacy notice or a data processing agreement, which creates regulatory exposure and customer harm. | Withdraw the recommendation. Get the actual export definition (query or job config) and list every field in it. If the intended design really is aggregate-only, change the job and attach a sample produced by the new job. Reproduction: open last week's export file and read the header line. Expected: cohort or aggregate columns only. Observed: `account_id,name,email,balance_usd,segment`. | a Y / b Y / c Y / d Y |
| F2 | Critical | CONFIRMED | R | memo.md Appendix A, all five data rows | The memo itself contains five real customers' names, emails, account IDs and balances, in a document going out for legal review and decision circulation. This spreads customer financial data beyond those who need it. | The memo is forwarded, attached to tickets, or pasted into other tools, including AI reviewers. Customer financial data then reaches people and systems with no need for it. Every copy becomes a record that is hard to recall. | Remove Appendix A from every copy and version of the memo. Replace it with the header line only, or with synthetic rows. Check where the memo has already been shared and treat those copies under your data-handling procedure. | a Y / b Y / c Y / d Y |
| F3 | High | CONFIRMED | A | memo.md §What is shared vs request.md "State exactly what data leaves the company" | Drift from the request. The memo gives a vague description ("weekly cohort totals and conversion rates") instead of an exact field list, granularity, cohort definition, frequency, transfer method and retention. The only exact listing in the memo, the appendix, contradicts the description. | Legal reviews a description rather than a specification. The approved scope cannot be checked against what the job actually sends, so drift like F1 goes undetected. | Add a field-by-field table covering field, definition, granularity, and whether it is personal data, plus the minimum cohort size, frequency, transfer channel and vendor retention period. Tie the table to the job definition. | a Y / b Y / c Y / d Y |
| F4 | Medium | CONFIRMED (that it is absent from the memo) | R | memo.md, entire document | The memo does not address the legal basis for sharing, privacy notice coverage, the data processing agreement, whether Northlight must be added to the published subprocessor list, cross-border transfer, the vendor's retention and deletion obligations, or how to exit the arrangement. | The data flow is approved, and the published privacy notice and subprocessor list become untrue the day exports begin. | Add a section covering each of these, with references to the actual documents. | a Y / b Y / c Y / d N |
| F5 | Medium | CONFIRMED (that it is absent from the memo) | A | memo.md §Why | The justification relies on one benefit (time saved) and one assurance (SOC 2). It considers no alternatives, such as keeping the analysis internal, sending pre-aggregated data with a minimum cohort size, or an anonymization or clean-room approach. It weighs no risks. | The decision-maker cannot see that a cheaper, lower-risk option exists. SOC 2 is taken as proof the sharing is lawful, which it is not: SOC 2 covers the vendor's controls, not your legal basis for sending them the data. | Add an options comparison that includes a "do nothing" or "keep in-house" option, plus a residual-risk statement. | a Y / b Y / c N / d N |

## NEEDS VALIDATION

- **S1: possible disclosure already under way.** Appendix A is "last week's run", yet the recommendation is to start the export on 1 November. **Unresolved fact:** whether last week's file, or any earlier one, was transmitted to Northlight or any other party. Settle it from the transfer logs or SFTP/API records. If it was sent, this is an incident, not a decision.
- **S2: SOC 2 Type II claim.** **Unresolved facts:** whether the report exists, whose name is on it, the period it covers, whether the scope includes the service that would receive this data, and whether any exceptions are noted. Settle it by reading the report.
- **S3: "replaces two days of manual reporting each month."** **Unresolved fact:** the source of this figure, such as time logs or the team lead's estimate.
- **S4: re-identification risk in "anonymous" cohort data.** If the design moves to aggregates, small cohorts or a `segment` value like premium combined with balances could still identify individuals. **Unresolved fact:** the minimum cohort size and the suppression rules in the export.
- **S5: real data vs test data.** The email domain is `example.test`, which normally indicates test data, but `context.md` says the extract is real. **Unresolved fact:** whether the rows come from production. This changes F2's handling. It does not change F1, because the header line alone contradicts the memo.

## REFUTED

- **Candidate: the appendix may be an illustrative mock-up, so the contradiction is only cosmetic.** Refuted. `context.md` says Appendix A is a real extract of last week's file, and the memo labels it "first 5 rows of last week's run".

## WHAT HOLDS UP

- **The recommendation is concrete:** it names the vendor, the cadence and the start date.
- **A wish to cut manual reporting is a legitimate goal.**
- **Including a sample of the real file was the right instinct.** That sample is exactly what exposes F1, and it should be shown as the header line only.

## UNVERIFIED CLAIMS

- **"Only aggregated, anonymous data leaves the company"** is contradicted by the appendix (F1). To confirm what is actually sent, read the export job definition.
- **"The vendor is SOC 2 Type II certified":** read the report (S2).
- **"Two days of manual reporting each month":** find the source of the figure (S3).

## QUESTIONS FOR THE AUTHOR

1. Which is true: the appendix, or the "aggregated, anonymous" statement? Please share the export job definition.
2. Has any version of this file already gone to Northlight?
3. Do the privacy notice and the data processing agreement cover sending identified customer financial data to this vendor?

## DECISION-MAKER SUMMARY

Do not sign or start the export. The memo says only anonymous aggregates are shared, but its real sample file contains customer names, emails, account IDs and balances (F1), and the memo itself now circulates that data (F2). Confirm whether any file has already been sent (S1), pull Appendix A from every copy, and send the memo back for an exact field list (F3) before legal review continues. If you proceed anyway, you risk an undisclosed transfer of customer financial data to a third party.

## OWNER SUMMARY

The memo says only anonymous summary figures would go to the analytics company, but the sample file attached to it shows full customer details, including names, email addresses and account balances. That means either the description is wrong or the file is wrong, and the memo itself is now spreading customer details to everyone who reads it. Hold the decision, remove the customer details from the memo, check whether any file has already been sent, and ask for a precise list of what would be shared.

```json
{
  "schema_version": "2.2",
  "verdict": "REJECT",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "memo.md", "status": "seen", "matters": true},
    {"item": "export job definition / query", "status": "not_seen", "matters": true},
    {"item": "transfer logs for last week's file", "status": "not_seen", "matters": true},
    {"item": "Northlight SOC 2 Type II report", "status": "not_seen", "matters": true},
    {"item": "DPA / draft contract", "status": "not_seen", "matters": true},
    {"item": "privacy notice and subprocessor list", "status": "not_seen", "matters": true},
    {"item": "source of manual-reporting time estimate", "status": "not_seen", "matters": false}
  ],
  "seats": [
    {"vendor": "local-same-context", "status": "ran", "cross_vendor": false},
    {"vendor": "claude-subagent", "status": "unavailable", "cross_vendor": false},
    {"vendor": "cross-vendor-seats", "status": "refused", "cross_vendor": true}
  ],
  "sensitivity_gate": {"sensitive": true, "reason": "Appendix A contains real customer names, emails, account IDs and balances; cross-vendor seats refused."},
  "coverage": {
    "checked": [
      {"unit": "memo.md", "kind": "file"},
      {"unit": "memo.md#what-is-shared", "kind": "section"},
      {"unit": "memo.md#why", "kind": "section"},
      {"unit": "memo.md#appendix-a", "kind": "data"},
      {"unit": "Only aggregated, anonymous data leaves the company", "kind": "claim"},
      {"unit": "Vendor is SOC 2 Type II certified", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "export job definition", "reason": "not supplied"},
      {"unit": "transfer logs", "reason": "not supplied"},
      {"unit": "SOC 2 report", "reason": "not supplied"},
      {"unit": "DPA, privacy notice, subprocessor list", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "memo.md §What is shared vs Appendix A header",
     "scenario": "Approval relies on 'aggregated, anonymous', while the real weekly file sends identified customer names, emails, account IDs and balances to a third party.",
     "fix": "Withdraw the recommendation; derive the exact field list from the export job; if aggregate-only is intended, change the job and attach a sample from the new job.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Open last week's export file; expected aggregate columns only; observed header account_id,name,email,balance_usd,segment."},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "R",
     "location": "memo.md Appendix A, rows 1-5",
     "scenario": "The memo circulates to legal and decision-makers and gets forwarded, spreading real customer financial data to people and systems with no need for it.",
     "fix": "Remove the data rows from every copy and version; keep the header line only or use synthetic rows; trace and remediate copies already shared.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Read Appendix A: five rows with name, email and balance."},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md §What is shared vs request.md",
     "scenario": "The request asks to state exactly what data leaves; the memo gives a vague description, so legal approves a description that cannot be checked against what the job sends.",
     "fix": "Add a field-by-field table (field, definition, granularity, personal data yes/no), minimum cohort size, frequency, transfer channel and vendor retention, tied to the job definition.",
     "answers": {"a": true, "b": true, "c": true, "d": true}},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "R",
     "location": "memo.md (entire)",
     "scenario": "The data flow is approved without checking the privacy notice, DPA or subprocessor list, which become untrue once exports start.",
     "fix": "Add a section on legal basis, privacy notice coverage, DPA, subprocessor list update, transfer, vendor retention and deletion, and exit.",
     "answers": {"a": true, "b": true, "c": true, "d": false}},
    {"id": "F5", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md §Why",
     "scenario": "SOC 2 is treated as making the sharing lawful, and lower-risk alternatives are never compared.",
     "fix": "Add an options comparison including keep-in-house and pre-aggregated with minimum cohort size, plus a residual-risk statement.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "R", "location": "memo.md Appendix A ('last week's run')",
     "suspicion": "The export may already be sending data before approval.",
     "unresolved_fact": "Whether last week's or any earlier file was transmitted to Northlight or any other party (transfer logs)."},
    {"id": "S2", "status": "needs_validation", "track": "C", "location": "memo.md §Why bullet 2",
     "suspicion": "The SOC 2 Type II claim may be stale or out of scope.",
     "unresolved_fact": "The report's entity, period, scope and exceptions."},
    {"id": "S3", "status": "needs_validation", "track": "C", "location": "memo.md §Why bullet 1",
     "suspicion": "The time-saving figure is unsupported.",
     "unresolved_fact": "The source of the two-days-per-month estimate."},
    {"id": "S4", "status": "needs_validation", "track": "R", "location": "memo.md §What is shared",
     "suspicion": "Cohort aggregates could still allow re-identification.",
     "unresolved_fact": "The minimum cohort size and suppression rules in the export."},
    {"id": "S5", "status": "needs_validation", "track": "C", "location": "memo.md Appendix A",
     "suspicion": "The example.test email domain suggests test data, despite context.md calling it real.",
     "unresolved_fact": "Whether the rows come from production."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Appendix A is illustrative, so the contradiction is only cosmetic.",
     "evidence": "context.md states Appendix A is a real extract of last week's file; the memo labels it the first 5 rows of last week's run."}
  ]
}
```

I could not run `tools/validate_findings.py` against this block because there were no tools in this session, so its schema conformance is unchecked. I also kept the skill's rule that needs-validation items carry no severity, even though the output note asks for a severity on every finding.