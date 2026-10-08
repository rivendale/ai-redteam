**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent or tools were available in this session. The cross-vendor seats you asked for were **refused** because of the sensitivity gate (see SEATS AND GATE).

VERDICT: **REWORK**. The memo says only aggregated, anonymous data leaves the company, but its own Appendix A shows the export file contains account IDs, names, emails and balances. Its central claim, and the decision built on it, is false on its face.

CONFIDENCE: **medium**. The main contradiction is confirmed from the text alone. Confidence is limited because this is a same-context review with no tools, the actual export job or query was not supplied, the vendor contract and DPA were not supplied, and there is no evidence of whether data has already been sent.

INPUTS LEDGER:
- Seen: original request (request.md), context (context.md), memo.md including Appendix A.
- Not seen, matters: the export job, query or pipeline definition that produces the file. It would settle whether the file in Appendix A is what is actually sent.
- Not seen, matters: the Northlight contract or DPA, and the SOC 2 Type II report (scope, period, auditor).
- Not seen, matters: the customer privacy notice and published subprocessor list.
- Not seen, matters: transfer logs showing whether "last week's run" was delivered to the vendor.
- Not seen, minor: the basis for "two days of manual reporting each month".

COVERAGE:
- Checked: memo.md sections "Recommendation", "What is shared", "Why" and "Appendix A". Claims checked: the anonymity claim, the excluded fields, the SOC 2 claim, the time saving, and the start date versus "last week's run". Also checked fit against the original request.
- Not checked: the export pipeline, contract, SOC 2 report, privacy notice and transfer logs (none supplied).

SEATS AND GATE:
- **Sensitivity gate: sensitive = true.** Appendix A is described as a real extract. It contains customer names, email addresses, account identifiers and account balances, which is personal and financial data.
- **Cross-vendor blind seats: refused.** The context requested them, but the skill forbids sending this data to an external or cross-vendor reviewer. A second opinion is not a reason to move customer data. Re-run cross-vendor seats only on a redacted memo.
- **Same-vendor subagent: not available in this session.**
- **Local same-context review: ran.**

FINDINGS:

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | A, R | memo.md "What is shared" vs Appendix A header `account_id,name,email,balance_usd,segment` | The memo states "Only aggregated, anonymous data leaves the company. No names, no contact details and no account identifiers are sent." The sample export it presents as "last week's run" is row-level and contains exactly those fields, plus balances. | Leadership and legal approve on the strength of "anonymous aggregates". Weekly exports then send identifiable customer financial data to a third party, outside what was approved and likely outside the privacy notice. Result: regulatory exposure and customer harm. | Determine what the pipeline actually emits, then rewrite "What is shared" to match it field by field. If the intent is aggregates, change the export to cohort totals only and replace Appendix A with a real sample of that output. **Reproduction:** compare the Appendix A header against the "What is shared" sentence. Three of the five columns are fields the memo says are never sent. | a Y / b Y / c Y / d Y |
| F2 | Critical | CONFIRMED | R | memo.md Appendix A, rows 1-5 | The memo embeds real customer personal and financial data (names, emails, balances) in a document circulated for decision and legal review. | Every recipient of the memo, plus email, document stores, any reviewer tool and any cross-vendor review, now holds customer data with no need for it. That is an unnecessary disclosure in its own right. | Remove the rows from the memo now and replace them with a schema description or synthetic rows. Recall or purge copies already circulated, and assess whether internal handling rules or breach procedures apply. **Reproduction:** Appendix A contains five rows with name, email and balance values, and the context states it is a real extract. | a Y / b Y / c Y / d Y |
| F3 | High | CONFIRMED | A | memo.md "What is shared" | **Drift from the request.** The request was to "state exactly what data leaves the company". The memo gives a vague description ("weekly cohort totals and conversion rates") with no field list, granularity, minimum cohort size, frequency details, transfer method or retention at the vendor. | Legal cannot assess the transfer, and the vendor can later receive more than was described with no documented baseline to object against. | Add an exact field-level specification of the export, including granularity, minimum cohort size, retention and deletion terms, and transfer channel. Tie it to the pipeline definition. | a Y / b Y / c Y / d Y |
| F4 | Medium | CONFIRMED | A | memo.md "What is shared"; title "customer behavior data" | `balance_usd` is account financial data, not behavior data. The memo never mentions that balances are shared, even though the context says customer financial data leaves the company. | A decision-maker approves "behavior analytics" without knowing account balances are in scope. That is a materially different risk and legal-basis question. | List balance data explicitly, justify why it is needed, or drop it from the export. | a Y / b Y / c N / d Y |
| F5 | Medium | PROBABLE | A | memo.md "Why" | The case for sharing is two bullets. There is no alternative considered (in-house automation, aggregating before export, doing nothing), no risk section and no exit or deletion plan. | The decision is made without weighing the cheaper, lower-risk option of automating the internal report or sending aggregates only. If the vendor relationship ends, nothing defines what happens to data already sent. | Add alternatives, risks, contract and DPA terms, and an exit clause covering data deletion. | a Y / b N / c N / d Y |

NEEDS VALIDATION:
- **S1 (memo.md Appendix A "last week's run" vs Recommendation "start the weekly export on 1 November").** A weekly run already happened before signing. Was its output delivered to Northlight or any third party? If yes, identifiable customer financial data has already left the company without a contract. That would be an incident to escalate now, not a memo issue. Settling fact: transfer logs or the delivery destination for that run.
- **S2 ("The vendor is SOC 2 Type II certified").** Unverified. Settling facts: the report itself, its period, which services and systems it covers (does it include the service that receives this export?) and any exceptions. SOC 2 is an attestation, not a certification, and it does not address lawful basis for sharing.
- **S3 ("replaces two days of manual reporting each month").** Unverified. Settling fact: who does this work and the time measurement it is based on.
- **S4 (privacy notice and subprocessor list).** Does the current privacy notice permit sharing this data with an analytics vendor, and does adding Northlight make a published subprocessor list untrue? Settling fact: the published notice and list text.

REFUTED:
- **"The memo's recommendation is inherently wrong."** Withdrawn. Sharing genuinely aggregated cohort data with a vendor can be reasonable. The defect is that the memo misdescribes what is shared, not the idea of using a vendor. That is REWORK, not REJECT.

WHAT HOLDS UP:
- The business motive (reducing manual reporting) is plausible and is clearly stated.
- The memo does name a specific vendor and start date, which makes the decision concrete enough to check.

UNVERIFIED CLAIMS:
- "Only aggregated, anonymous data leaves the company." Contradicted by the memo's own Appendix A (F1). Confirm by reading the export query or pipeline.
- "No names, no contact details and no account identifiers are sent." Contradicted (F1). Same check.
- SOC 2 Type II status (S2). Obtain the report.
- The two-day saving (S3). Obtain the time records.

QUESTIONS FOR THE AUTHOR:
1. Is Appendix A the file that is actually sent to the vendor, or an internal intermediate before aggregation?
2. Was last week's run delivered to anyone outside the company?
3. Why are account balances in the export at all?

DECISION-MAKER SUMMARY: Do not sign or start the export. The memo's own appendix shows identifiable customer records with balances, directly contradicting its "anonymous aggregates" claim (F1). Pull the customer rows out of the memo immediately (F2) and confirm whether last week's run already left the company (S1). Proceeding anyway risks sending identifiable financial data to a third party under an approval that was given for something else.

OWNER SUMMARY: The memo says only anonymous totals would be shared, but its own sample shows the file contains individual customers' identifying details and account balances. The memo itself now contains real customer details and should be cleaned up and recalled from anyone who received it. Before any agreement is signed, the team needs to confirm exactly what is sent and whether anything has already been sent.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "memo.md", "status": "seen", "matters": true},
    {"item": "export pipeline / query definition", "status": "not_seen", "matters": true},
    {"item": "Northlight contract and DPA", "status": "not_seen", "matters": true},
    {"item": "Northlight SOC 2 Type II report", "status": "not_seen", "matters": true},
    {"item": "privacy notice and subprocessor list", "status": "not_seen", "matters": true},
    {"item": "transfer logs for last week's run", "status": "not_seen", "matters": true}
  ],
  "seats": [
    {"vendor": "claude-same-context", "status": "ran", "cross_vendor": false},
    {"vendor": "claude-subagent", "status": "unavailable", "cross_vendor": false},
    {"vendor": "cross-vendor blind seats", "status": "refused", "cross_vendor": true}
  ],
  "sensitivity_gate": {"sensitive": true, "reason": "Appendix A is a real extract containing customer names, emails, account identifiers and balances; cross-vendor seats refused."},
  "coverage": {
    "checked": [
      {"unit": "memo.md", "kind": "file"},
      {"unit": "memo.md:What is shared", "kind": "section"},
      {"unit": "memo.md:Why", "kind": "section"},
      {"unit": "memo.md:Appendix A", "kind": "section"},
      {"unit": "Only aggregated, anonymous data leaves the company", "kind": "claim"},
      {"unit": "Vendor is SOC 2 Type II certified", "kind": "claim"},
      {"unit": "Replaces two days of manual reporting each month", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "export pipeline / query definition", "reason": "not supplied"},
      {"unit": "Northlight contract, DPA and SOC 2 report", "reason": "not supplied"},
      {"unit": "privacy notice and subprocessor list", "reason": "not supplied"},
      {"unit": "transfer logs", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "R",
     "location": "memo.md 'What is shared' vs Appendix A header",
     "scenario": "Approvers rely on 'only aggregated, anonymous data'; the export actually sends row-level account_id, name, email and balance_usd to a third party weekly, outside what was approved.",
     "fix": "Establish what the pipeline emits and rewrite 'What is shared' field by field to match; if aggregates are intended, change the export and replace Appendix A with a real aggregate sample.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Compare the Appendix A header (account_id,name,email,balance_usd,segment) with the sentence 'No names, no contact details and no account identifiers are sent'."},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "R",
     "location": "memo.md Appendix A rows 1-5",
     "scenario": "The memo, circulated for decision and legal review, spreads real customer names, emails and balances to every recipient and tool that handles it.",
     "fix": "Replace the rows with a schema description or synthetic data; recall or purge circulated copies; assess internal data-handling obligations.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Appendix A holds five real rows with name, email and balance values (context: 'a real extract of last week's file')."},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md 'What is shared'",
     "scenario": "The request asked to state exactly what data leaves; the memo gives a vague description with no field list, granularity, cohort minimum, retention or transfer method, so legal cannot assess the transfer.",
     "fix": "Add an exact field-level export specification tied to the pipeline definition, with granularity, minimum cohort size, retention, deletion and transfer channel.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Check the section against the request text 'State exactly what data leaves the company'; no field list is present."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md title and 'What is shared'; Appendix A column balance_usd",
     "scenario": "Approvers sign off on 'behavior data' without being told account balances (financial data) are exported.",
     "fix": "Disclose balance data explicitly with a justification, or remove it from the export.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "balance_usd appears in Appendix A and is not mentioned anywhere in the memo body."},
    {"id": "F5", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "A",
     "location": "memo.md 'Why'",
     "scenario": "No alternatives, risks or exit plan are considered, so a lower-risk option (in-house automation or aggregate-only export) is never weighed and data deletion on termination is undefined.",
     "fix": "Add alternatives, risks, contract/DPA terms and an exit clause covering deletion of shared data.",
     "answers": {"a": true, "b": false, "c": false, "d": true},
     "reproduction": "The 'Why' section contains only two benefit bullets and no alternatives or risks section exists."},
    {"id": "S1", "status": "needs_validation", "track": "R", "location": "memo.md Appendix A 'last week's run' vs Recommendation start date 1 November",
     "suspicion": "The export already ran before signing and may have been delivered to the vendor.",
     "unresolved_fact": "Transfer logs or the delivery destination of last week's run."},
    {"id": "S2", "status": "needs_validation", "track": "C", "location": "memo.md 'Why' bullet 2",
     "suspicion": "SOC 2 Type II claim may be unscoped, stale or not cover the receiving service.",
     "unresolved_fact": "The SOC 2 report's period, scope and exceptions."},
    {"id": "S3", "status": "needs_validation", "track": "C", "location": "memo.md 'Why' bullet 1",
     "suspicion": "The two-day monthly saving is unsupported.",
     "unresolved_fact": "Time records for the current manual reporting."},
    {"id": "S4", "status": "needs_validation", "track": "R", "location": "memo.md (absent section)",
     "suspicion": "Sharing may exceed the privacy notice or make the published subprocessor list untrue.",
     "unresolved_fact": "Current privacy notice text and subprocessor list."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Sharing data with an analytics vendor is inherently the wrong decision.",
     "evidence": "Genuinely aggregated cohort data could be shared acceptably; the defect is the misdescription of what is shared, so REWORK rather than REJECT."}
  ]
}
```

I have not modified the memo. The most urgent actions sit outside the memo itself: removing the customer rows from circulated copies (F2) and checking whether last week's run left the company (S1). Do you want me to draft a redacted version of the memo once you confirm what the pipeline actually emits?