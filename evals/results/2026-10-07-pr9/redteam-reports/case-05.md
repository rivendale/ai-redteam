# Red team review: Northlight data-sharing decision memo

**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent or tools were available in this session, and cross-vendor seats were refused (see Seats and Gate).

**VERDICT: REWORK.** The memo's central claim, that only aggregated, anonymous data leaves the company, is contradicted by its own Appendix A. The appendix is row-level customer data with names, email addresses, account IDs and balances. The recommendation to sign rests on that false claim.

**CONFIDENCE: high** on the central contradiction, because it can be read directly from the memo. **Medium** overall, limited by:
- a same-context review with no tools;
- the actual export job, the contract and the SOC 2 report not being supplied.

**INPUTS LEDGER:**

| Item | Status | Matters? |
|---|---|---|
| Original request (request.md) | Seen, verbatim | Yes |
| Context (context.md) | Seen | Yes |
| memo.md, including Appendix A | Seen | Yes |
| The actual export job, query or field specification | Not seen | **Yes.** It is the only thing that can settle what really leaves. |
| Northlight contract or data processing agreement (retention, purpose limits, sub-processors, deletion) | Not seen | Yes |
| Northlight SOC 2 Type II report (scope, period, exceptions) | Not seen | Yes |
| Privacy notice and published subprocessor list | Not seen | Yes, for the regulatory findings |
| Whether last week's file was transmitted to the vendor | Not stated | **Yes.** It decides whether this is already a data incident. |
| Legal review | Pending, not seen | Yes |

**SEATS AND GATE:**
- **Sensitivity gate: tripped.** Context states Appendix A is a real extract. It holds customer names, email addresses, account identifiers and account balances, which is personal and financial data.
- **Cross-vendor blind seats: refused**, even though the context asked for them. Sending this memo to another vendor's model would repeat the disclosure the memo is about. A second opinion is not a reason to send customer financial data somewhere it may not go.
- **Fresh same-vendor subagent:** not available in this session. Only this same-context review ran.
- **What would enable cross-vendor seats:** re-run them after Appendix A is replaced with a field list or a synthetic sample.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | C, R | "What is shared", paragraph 1, vs. Appendix A header `account_id,name,email,balance_usd,segment` | The memo says no names, no contact details and no account identifiers are sent. The export sample has all three, plus balances, one row per customer. | Approvers and legal sign off believing only anonymous aggregates leave. Identifiable customer financial data then goes weekly to a third party under a false description. This creates regulatory exposure (misdescribed sharing, possible privacy-notice breach) and real harm to customers. | Withhold approval. Produce the exact field list from the export job's code or query, not from prose. Then either rewrite the claim to match it or change the export to real aggregates. | **Confirmed.** Strongest defense: Appendix A is an internal pre-aggregation file, not what is sent. But the memo itself labels it "sample of the weekly export file". If the defense were true, the memo would still fail to say what leaves. |
| 2 | High | CONFIRMED (content); PROBABLE (exposure) | R | Appendix A, all 5 rows | The memo itself carries real customer personal and financial data. Every reader, every copy and every forward now holds it, including the legal review and any review tool. | The memo is circulated, attached to tickets or pasted into tools. Customer data spreads beyond need-to-know with no audit trail. | Remove the real rows now. Replace them with a column list plus synthetic values. Check where the memo has already been shared and treat those copies under the data-handling policy. | **Confirmed.** Defense: the emails use the `example.test` domain, which suggests synthetic data. But context explicitly says it is a real extract, so take the context at its word unless the author confirms otherwise. |
| 3 | High | PROBABLE | R, A | Appendix A heading: "last week's run" | The wording implies the export already ran before approval. It is not stated whether the file was sent to Northlight. | If it was sent, identifiable financial data may already be at a vendor with no signed agreement. That is a possible reportable incident, and the memo would be approving it after the fact. | Ask the author directly: was any file transmitted, to whom and when? If yes, escalate to privacy or incident response before continuing the decision. | **Confirmed** as a question that must be answered. Severity holds because the wording supports the reading and the downside is large. Downgrade it if the run was internal only. |
| 4 | High | CONFIRMED | A (drift) | Whole memo vs. request "State exactly what data leaves the company" | The memo answers with a reassurance ("aggregated, anonymous") instead of an exact statement. It gives no field list, row count, frequency details, transfer method, retention, or what "cohort totals and conversion rates" are computed from. The claimed contents (cohort totals, conversion rates) do not appear in the sample at all. | Legal reviews a description that cannot be checked against the system, and the gap between prose and pipeline goes unnoticed. | Add a table listing each field, its classification, whether it is aggregated, the minimum cohort size, frequency, transport, encryption, vendor retention and deletion. Derive it from the job definition. | **Confirmed.** Defense: a memo can summarize. But the request explicitly asked for "exactly", and this summary is wrong (finding 1). |
| 5 | High | UNVERIFIED | C, A | "Why", bullet 2: "SOC 2 Type II certified" | The claim is unsourced. SOC 2 is an attestation report, not a certification. Its scope and period are unknown. It also says nothing about how the vendor may use, retain or onward-share the data. | The decision leans on a control that does not cover purpose limitation, deletion or sub-processing. | Obtain the current report and check its period, the systems in scope and any exceptions. Require a data processing agreement covering purpose limits, retention, deletion, sub-processors and breach notification. | **Confirmed** as a gap; the claim itself remains UNVERIFIED. It keeps High severity because it is one of only two stated justifications. |
| 6 | Medium | CONFIRMED | A | "Why" section and Recommendation | There is no cost/risk comparison and no alternatives were considered. Options missing include sending real aggregates only, running analytics in-house, or delaying. The single benefit is about 2 days per month of manual work, with no evidence given. | A modest saving is traded for a large privacy exposure without anyone seeing the trade. | Add the alternatives, especially "export aggregates only", which may deliver the same benefit at much lower risk. Quantify the benefit. | — |
| 7 | Medium | CONFIRMED | A, R | Recommendation: "start the weekly export on 1 November" | The start date is set 3 weeks out while legal review is pending, and the memo does not mention that dependency. | The date anchors the schedule, so legal review gets compressed or the start goes ahead without it. | Make the start conditional on legal sign-off and a signed data processing agreement. | — |
| 8 | Medium | UNVERIFIED | R | Not covered anywhere in the memo | Possible impact on the privacy notice or subprocessor list. Depending on jurisdiction and the type of entity, sharing nonpublic financial data with a third party may require notice, a contract, or an opt-out. | Adding Northlight makes a published subprocessor list or privacy notice untrue. | Legal should check the privacy notice, subprocessor list and applicable rules by exact provision. | — |
| 9 | Low | PROBABLE | C | "anonymous" | Even real aggregates can re-identify people if cohorts are small, for example a "premium" segment with few members. | Small cohort totals reveal individual balances. | Set a minimum cohort size and suppress small cells. | — |

No Critical or High finding was refuted.

## What holds up

- The memo is short and states a clear recommendation and date.
- The operational benefit (replacing manual reporting) is plausible.
- Including a sample of the real export was the right instinct. It is what exposed the problem; it just needed field names, not real customer rows.
- No text in the work tries to instruct the reviewer.

## Unverified claims

| Claim | How to confirm |
|---|---|
| "Only aggregated, anonymous data" | Read the export job's query or code and a full current output file. |
| "Weekly cohort totals and conversion rates" | Same as above. These fields are absent from the sample. |
| "Replaces two days of manual reporting each month" | Get time records from the team that does the reporting. |
| "SOC 2 Type II certified" | Obtain the current report and read its scope, period and exceptions. |

## Questions for the author

1. Was last week's file, or any earlier file, transmitted to Northlight or any other external party?
2. Is Appendix A the file that is actually sent, or an internal intermediate? If an intermediate, what exactly is sent, and who maintains the aggregation step?
3. Is there a signed or draft data processing agreement, and what does it say about retention, use and sub-processors?

## Decision-maker summary

Do not sign or schedule the 1 November start on this memo. Its key assurance, that only anonymous aggregates leave, is contradicted by its own sample, which shows named customers with emails and balances.

First confirm whether data has already been sent. Then rebuild the "what leaves" section from the actual export job and remove real customer rows from the memo. Proceeding as is risks sharing identifiable financial data under a false description while legal review is still pending.

## Owner summary

The memo says only anonymous totals would go to the vendor, but the sample file attached to it contains real customers' names, emails and account balances. The decision should wait until we know exactly what the file contains and whether any of it has already been sent. The real customer details should also be taken out of the memo itself.

```json
{
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "memo.md incl. Appendix A", "status": "seen", "matters": true},
    {"item": "export job definition / query", "status": "not_seen", "matters": true},
    {"item": "Northlight contract / DPA", "status": "not_seen", "matters": true},
    {"item": "Northlight SOC 2 Type II report", "status": "not_seen", "matters": true},
    {"item": "privacy notice and subprocessor list", "status": "not_seen", "matters": true},
    {"item": "transmission status of last week's file", "status": "not_seen", "matters": true}
  ],
  "seats": [
    {"vendor": "same-context (this session)", "status": "ran", "cross_vendor": false},
    {"vendor": "claude-subagent", "status": "unavailable", "cross_vendor": false},
    {"vendor": "cross-vendor blind seats", "status": "refused", "cross_vendor": true}
  ],
  "sensitivity_gate": {"sensitive": true, "reason": "Appendix A is a real extract containing customer names, email addresses, account identifiers and balances; cross-vendor seats refused."},
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "C,R", "location": "memo.md 'What is shared' para 1 vs Appendix A header", "scenario": "Approvers sign believing only anonymous aggregates leave; identifiable customer financial data is sent weekly to a third party under a false description.", "fix": "Withhold approval; derive the exact field list from the export job; rewrite the claim or change the export to true aggregates.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "R", "location": "memo.md Appendix A rows 1-5", "scenario": "The memo itself spreads real customer personal and financial data to every reader, copy and tool it reaches.", "fix": "Replace real rows with a column list and synthetic values; trace and handle existing copies.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "PROBABLE", "track": "R,A", "location": "memo.md Appendix A heading 'last week's run'", "scenario": "The export may already have been sent to the vendor without an agreement, making this a possible reportable incident.", "fix": "Confirm whether any file was transmitted; if so, escalate to privacy or incident response first.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "A", "location": "memo.md whole vs request 'State exactly what data leaves'", "scenario": "The memo gives a reassurance instead of an exact field-level statement, and its claimed contents are absent from the sample; legal reviews an uncheckable description.", "fix": "Add a field-level table (classification, aggregation, cohort minimum, frequency, transport, retention) derived from the job definition.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "UNVERIFIED", "track": "C,A", "location": "memo.md 'Why' bullet 2", "scenario": "The decision relies on an unsourced SOC 2 claim that does not govern vendor use, retention or onward sharing of the data.", "fix": "Obtain and review the current SOC 2 report; require a DPA with purpose, retention, deletion, sub-processor and breach terms.", "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "A", "location": "memo.md 'Why' and Recommendation", "scenario": "A small unquantified benefit is traded for a large privacy risk with no alternatives considered.", "fix": "Compare aggregates-only export, in-house analytics and delay; quantify the benefit.", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "A,R", "location": "memo.md Recommendation '1 November'", "scenario": "A fixed start date while legal review is pending compresses or bypasses that review.", "fix": "Make the start conditional on legal sign-off and a signed DPA.", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "track": "R", "location": "memo.md (omission)", "scenario": "Adding the vendor makes the published privacy notice or subprocessor list untrue, or triggers notice or opt-out obligations.", "fix": "Legal checks the privacy notice, subprocessor list and applicable rules by exact provision.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "PROBABLE", "track": "C", "location": "memo.md 'anonymous'", "scenario": "Small-cohort aggregates re-identify individuals.", "fix": "Set a minimum cohort size and suppress small cells.", "status": "n/a"}
  ]
}
```
