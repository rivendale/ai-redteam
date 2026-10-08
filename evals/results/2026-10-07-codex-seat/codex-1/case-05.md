VERDICT: REWORK — the memo says only anonymous aggregates leave the company, but its real export sample contains customer identifiers and individual financial balances.

CONFIDENCE: high on the contradiction; low on the actual transfer and vendor safeguards because no tools, complete export, contract, or operational evidence were available.

INPUTS LEDGER:
- **Seen:** original request, context, complete supplied memo, and five rows identified as a real extract of last week’s export.
- **Not seen:** complete export and export logic, actual transfer records, vendor agreement, retention and deletion terms, SOC 2 report, or legal review. These gaps matter to establishing exactly what leaves the company and whether sharing should proceed.
- The sample establishes the file’s visible contents. It does not establish that Northlight received it.

SEATS AND GATE: One reviewer ran on the supplied text. Cross-vendor seats were refused because the appendix contains real customer personal and financial data. No additional seats or tools were available; the requested deep review is therefore limited to textual examination and confirmation against the supplied evidence.

**Reconstruction**

The memo recommends signing with Northlight and beginning a weekly export on 1 November. It describes that export as anonymous cohort totals and conversion rates, while its appendix shows individual account records with identifiers, contact details, balances, and segments. For the recommendation to hold, the actual outbound data must match the disclosure, the business benefit must justify the sharing, and the vendor’s permitted use and handling must be acceptable. Load-bearing assumptions include an unseen aggregation step, adequate contractual safeguards, and evidence supporting the certification and time savings; relevant tracks are A, B, C, and R.

**FINDINGS**

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | C, R | “What is shared”; Appendix A header | “Only aggregated, anonymous data” and “no account identifiers” contradict the real export sample, which contains `account_id`, `name`, `email`, `balance_usd`, and `segment` for individual accounts. | A decision-maker authorizes sharing on the stated anonymity premise; the described export exposes identifiable customer financial records. | Trace the actual outbound file and any transformation. State every outbound field accurately. If aggregates are intended, verify the final transmitted artifact excludes individual records and identifiers. | **Confirmed:** an unseen aggregation step could change what is transmitted, but none is supplied and the appendix is explicitly called the weekly export file. Actual vendor receipt remains unverified. |
| 2 | High | CONFIRMED | A, R | Recommendation; “What is shared”; supplied context | The unconditional signing and launch recommendation lacks decision conditions for identifiable financial data: permitted uses, recipients, retention, deletion, onward sharing, and applicable legal review. | The company signs terms allowing broader use or longer retention than decision-makers expected, then starts a recurring transfer without resolving those terms. | Make the recommendation conditional on verified data scope, acceptable handling terms, and completed legal review of the proposed sharing. | **Confirmed:** legal review being pending does not itself prohibit a recommendation; the defect is recommending commitment and launch without identifying unresolved conditions that could change the decision. |
| 3 | Medium | UNVERIFIED | A, C | “Why”: manual-reporting savings and SOC 2 claim | Neither benefit claim has supporting evidence. Certification alone also leaves the suitability of this specific data transfer unresolved. | Decision-makers accept an inaccurate savings estimate or rely on an assurance report whose scope does not cover the proposed service. | Supply the savings calculation and relevant assurance report, including service scope, reporting period, and material exceptions. Evaluate transfer safeguards separately. | Not established; evidence would settle it. |

**WHAT HOLDS UP:** The memo gives a clear proposed action and cadence. The appendix makes the disclosure error directly detectable. Its visible schema supports identifying five fields in the sample without guessing about unseen columns or transfers.

**UNVERIFIED CLAIMS:**

- **Exactly what Northlight receives:** inspect the complete final outbound artifact, transformations, and transfer records.
- **Weekly cohort totals and conversion rates:** inspect the delivered schema; the supplied sample contains neither.
- **SOC 2 Type II certification and reporting savings:** inspect the assurance evidence and reproduce the savings calculation.
- **Acceptability of sharing:** examine the proposed agreement and completed legal review. No legal violation can be established from this text alone.

**QUESTIONS FOR THE AUTHOR:**

1. Is Appendix A transmitted to Northlight, or transformed first? Provide the complete final outbound schema and transformation evidence.
2. What uses, recipients, retention, deletion, and onward sharing would the agreement permit, and what remains unresolved in legal review?

**DECISION-MAKER SUMMARY:** Return the memo for correction before relying on its recommendation. Establish the actual transmitted fields and resolve the handling terms and legal review. Proceeding on the current text risks authorizing identifiable financial-data sharing under a materially false anonymity description.

**OWNER SUMMARY:** The memo says customer information is anonymous, but its sample contains personal details and individual balances. Confirm what the vendor actually receives and correct the description before signing or starting exports. The agreement also needs clear limits on how the information can be used and kept.

```json
{
  "verdict": "REWORK",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "Original request, context, memo, and five-row real extract", "status": "seen", "matters": true},
    {"item": "Complete final outbound export, transformation logic, and transfer records", "status": "not_seen", "matters": true},
    {"item": "Vendor agreement, assurance report, savings evidence, and legal review", "status": "not_seen", "matters": true}
  ],
  "seats": [
    {"vendor": "OpenAI", "status": "ran", "cross_vendor": false},
    {"vendor": "other vendors", "status": "refused", "cross_vendor": true}
  ],
  "sensitivity_gate": {
    "sensitive": true,
    "reason": "The appendix is identified as real customer personal and financial data; external cross-vendor review is refused."
  },
  "findings": [
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "track": "C,R",
      "location": "memo.md: What is shared; Appendix A header",
      "scenario": "Sharing is authorized on an anonymity premise, while the described export contains identifiable individual financial records.",
      "fix": "Verify the final transmitted artifact and disclose every outbound field accurately; verify any intended aggregation removes individual records and identifiers.",
      "status": "confirmed"
    },
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "track": "A,R",
      "location": "memo.md: Recommendation; What is shared; context.md: legal review pending",
      "scenario": "Signing and recurring exports proceed before decision-makers resolve permitted uses, recipients, retention, deletion, onward sharing, and legal review.",
      "fix": "Condition signing and launch on verified data scope, acceptable handling terms, and completed legal review.",
      "status": "confirmed"
    },
    {
      "severity": "Medium",
      "evidence_level": "UNVERIFIED",
      "track": "A,C",
      "location": "memo.md: Why",
      "scenario": "The decision relies on unsupported savings or assurance evidence that does not cover the proposed service.",
      "fix": "Provide and reproduce the savings calculation; inspect the assurance report's scope, period, and exceptions; assess transfer safeguards separately.",
      "status": "unverified"
    }
  ]
}
```