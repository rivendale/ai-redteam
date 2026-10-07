# Redteam review: decision memo on sharing customer behavior data with Northlight

**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** I have no tools or subagent in this session, so no independent reviewer ran. The memo was not written in this conversation, which limits the anchoring risk.

---

**VERDICT: REWORK.** The memo's central claim ("only aggregated, anonymous data leaves the company") is contradicted by its own Appendix A. That appendix is a row-level extract with account IDs, names, emails and balances, so the memo does not do what was asked: state exactly what data leaves.

**CONFIDENCE: high** on the main finding, because it is a direct contradiction inside the document. It is lower on everything else because:
- this is a same-context review;
- I had no tools;
- the export spec, contract, DPA and SOC 2 report were not supplied.

**INPUTS LEDGER**

| Item | Status | Matters? |
|---|---|---|
| Original request (request.md) | seen, verbatim | yes |
| Context (context.md) | seen | yes |
| memo.md, including Appendix A | seen | yes |
| Export query, job or schema that produces the weekly file | not seen | **yes**: it is the only authoritative answer to "exactly what data leaves" |
| Full column list (Appendix A shows 5 columns and 5 rows only) | not seen | yes: there may be more fields |
| Northlight contract, DPA, retention and sub-processor terms | not seen | yes: needed before any signing decision |
| Northlight SOC 2 Type II report (scope, period, auditor) | not seen | medium |
| Evidence for the "two days of manual reporting" saving | not seen | low to medium |
| Legal's pending review | not seen | yes |

**SEATS AND GATE**
- **Sensitivity gate: TRIGGERED.** Appendix A contains personal data (names, emails) and customer financial records (account IDs, balances). The context also states it is a real extract.
- **Cross-vendor blind seats: REFUSED**, even though DEEP depth asked for them. Sending this memo to another vendor's model would itself be the kind of external disclosure the memo is about.
- **Same-vendor subagent:** unavailable (no tools).
- **Ran:** this local, same-context review only, at deep depth, with confirm-or-refute applied to every High and Critical.
- **Prompt injection:** the work contains no text addressed to the reviewer.

---

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | **Critical** | CONFIRMED | C, A | memo.md "What is shared" vs. Appendix A header `account_id,name,email,balance_usd,segment` | The memo says no names, no contact details and no account identifiers leave, only cohort totals and conversion rates. The appendix it presents as "the weekly export file" is row-level, per customer, and contains all three excluded categories plus account balances. It contains no cohort totals or conversion rates at all. | Approvers and legal sign off on "aggregated, anonymous" data. The pipeline then ships identified customer financial records to a third party every week. That creates privacy, contractual and regulatory exposure, and an approval obtained on a false description. | State the actual field list taken from the export job's code or schema, not from prose. Then either (a) change the export to true aggregates and attach a sample of the aggregated output, or (b) rewrite the memo to disclose row-level PII and financial data, with a legal basis. Test: diff the export job's output columns against the memo's "What is shared" list. | **confirmed.** Strongest defense: the appendix is an internal pre-aggregation staging file. Refuted by the memo's own wording, "sample of the weekly export file". |
| 2 | **High** | CONFIRMED (contents); PROBABLE (exposure) | B, C | Appendix A, rows 1–5 | The decision memo embeds real customer names, emails and balances. It is about to circulate to legal and approvers, and possibly further. The memo has itself become an unnecessary copy of sensitive data. | The memo is forwarded, attached to tickets or pasted into tools (including external AI reviewers, as this review request did). Customer financial data spreads outside its controlled system. | Replace the rows with synthetic or redacted values, or show the schema only. Recall or purge circulated copies. Check whether the extract's presence in the memo needs to be logged as an internal data-handling incident. | **confirmed.** Strongest defense: the `.test` email domains suggest the data is synthetic. The context explicitly says it is a real extract, so treat it as real until the data owner confirms otherwise (see Q2). |
| 3 | Medium | PROBABLE | A | memo.md "Why" and "Recommendation" | The memo has no data-protection basis or controls: no lawful basis or consent position, no DPA, no purpose limitation, no retention or deletion terms, no sub-processor or transfer location, no exit plan. | The contract is signed on 1 November on the strength of "SOC 2 certified". The vendor retains or reuses the data with no contractual remedy, and offboarding cannot force deletion. | Add a section covering data categories, lawful basis, DPA status, retention, location, sub-processors and termination/deletion. Make signing conditional on legal clearance. | n/a (Medium) |
| 4 | Medium | UNVERIFIED | C | memo.md "Why", bullet 2 | "SOC 2 Type II certified" is asserted with no report, period or scope. Even if true, SOC 2 attests to the vendor's controls. It does not establish that sharing this data is permitted or minimized. | The report is expired, scoped to a different product, or carries qualified opinions. Approvers rely on it as a privacy assurance it does not provide. | Obtain the current report, then check the period, the in-scope system and any exceptions. Do not use it as a substitute for item 3. | n/a |
| 5 | Medium | UNVERIFIED | A, D | memo.md "Why", bullet 1 | The only benefit is "replaces two days of manual reporting each month". It is unquantified and unsourced. No alternatives are weighed: in-house aggregation, aggregation before export, or doing nothing. A benefit of about 2 person-days per month is small next to a recurring outbound feed of identified financial data. | Leadership accepts an ongoing privacy risk for a saving that a cheaper internal fix (automating the aggregation report) would also deliver. | Show the source of the two-day figure. Compare it against aggregating internally and sending only aggregates, which would also make the memo's original claim true. | n/a |
| 6 | Medium | CONFIRMED | A | memo.md "Recommendation" vs. context ("legal review is pending") | The memo commits to a 1 November start date with no dependency on legal sign-off or on fixing the export. | The date is treated as fixed and the export starts before legal concludes or before the data mismatch is resolved. | Make the start date conditional: "start after legal approval and after the export is verified to match the stated field list." | n/a |

---

## WHAT HOLDS UP
- The memo is short, states a clear recommendation, and includes a real sample of the output. That sample is exactly what exposed the problem. Attaching actual artifacts was the right instinct; the sample should be redacted and should match the claim.
- Using an analytics vendor for cohort and conversion reporting is a reasonable goal if only true aggregates leave. Nothing here argues against the idea itself, only against this description and this export.

## UNVERIFIED CLAIMS

| Claim | How to confirm |
|---|---|
| Northlight is SOC 2 Type II certified | Obtain the current report and check period, scope and exceptions |
| Two days of manual reporting saved per month | Time logs or the owner of the current report |
| The vendor receives weekly cohort totals and conversion rates | The export job's code or schema and its actual output. The only evidence supplied contradicts this claim. |

## QUESTIONS FOR THE AUTHOR
1. Has "last week's run" (or any earlier run) already been sent to Northlight? If yes, this is a possible live disclosure of identified financial data and needs immediate escalation, separate from the memo.
2. Is Appendix A real customer data, as the context says, or synthetic, as the `.test` domains suggest? If it is real, who has received the memo so far?
3. What is the complete column list of the export as configured today, and who owns the job?
4. Is the intent to send aggregates only? If so, is aggregating before export feasible? That would make the memo's main claim true.

## DECISION-MAKER SUMMARY
Do not sign or start the export on the basis of this memo. Its own appendix shows identified customer financial records leaving, not the "aggregated, anonymous" data it describes. First confirm nothing has already been sent, redact the appendix, and get a field list from the actual export job. If you proceed as written, you approve a weekly third-party disclosure of names, emails and balances under a false description, with legal sign-off resting on that same description.

```json
{
  "verdict": "REWORK",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "memo.md incl. Appendix A", "status": "seen", "matters": true},
    {"item": "export job code/schema and full column list", "status": "not_seen", "matters": true},
    {"item": "Northlight contract / DPA / retention terms", "status": "not_seen", "matters": true},
    {"item": "Northlight SOC 2 Type II report", "status": "not_seen", "matters": true},
    {"item": "evidence for 2-days-per-month saving", "status": "not_seen", "matters": false},
    {"item": "legal review outcome", "status": "not_seen", "matters": true}
  ],
  "seats": [
    {"vendor": "local-same-context", "status": "ran", "cross_vendor": false},
    {"vendor": "claude-subagent", "status": "unavailable_no_tools", "cross_vendor": false},
    {"vendor": "cross-vendor-blind-seats", "status": "refused_sensitive_data", "cross_vendor": true}
  ],
  "sensitivity_gate": {"sensitive": true, "reason": "Appendix A contains customer names, emails, account IDs and account balances, stated to be a real extract; no external or cross-vendor reviewer may receive it."},
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "C", "location": "memo.md 'What is shared' vs Appendix A header 'account_id,name,email,balance_usd,segment'",
     "scenario": "Memo claims only aggregated anonymous data with no names, contacts or account IDs leaves; the appendix, labelled the weekly export file, is row-level with all three plus balances. Approval and legal sign-off would rest on a false description while identified financial data ships weekly to a third party.",
     "fix": "Derive the field list from the export job itself; either aggregate before export and attach an aggregated sample, or disclose the row-level PII and financial fields with a legal basis. Test: diff export output columns against the memo's stated list.",
     "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "B", "location": "memo.md Appendix A rows 1-5",
     "scenario": "The memo embeds real customer names, emails and balances and is circulating for approval and legal review; forwarding or pasting it into other tools spreads customer financial data outside controlled systems.",
     "fix": "Replace the rows with synthetic or redacted values or a schema-only listing; recall or purge circulated copies and assess whether to log a data-handling incident.",
     "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "A", "location": "memo.md 'Why' and 'Recommendation'",
     "scenario": "No lawful basis, DPA, purpose limitation, retention, location, sub-processor or exit terms are stated; after signing, the vendor may retain or reuse the data with no contractual remedy.",
     "fix": "Add a data-protection section and make signing conditional on legal clearance and a DPA.",
     "status": "n/a"},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "track": "C", "location": "memo.md 'Why' bullet 2",
     "scenario": "The SOC 2 Type II claim has no report, period or scope; it may be expired or out of scope, and it does not authorize the data sharing either way.",
     "fix": "Obtain and check the current report; do not treat it as a privacy assurance.",
     "status": "n/a"},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "track": "A", "location": "memo.md 'Why' bullet 1",
     "scenario": "The sole, unsourced benefit (about 2 person-days per month) justifies a recurring outbound PII feed while cheaper alternatives (in-house aggregation, aggregating before export) are never considered.",
     "fix": "Source the figure and compare against internal aggregation and aggregate-only export.",
     "status": "n/a"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "A", "location": "memo.md 'Recommendation' vs context.md 'legal review is pending'",
     "scenario": "The fixed 1 November start date could see the export begin before legal concludes or before the data mismatch is fixed.",
     "fix": "Make the start conditional on legal approval and on verifying the export against the stated field list.",
     "status": "n/a"}
  ]
}
```
