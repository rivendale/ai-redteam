**Single-reviewer review: no tools and no independent seat.** I reviewed the work as supplied text only. I did not run or open anything. Re-run in a fresh session before publication if the stakes call for it.

---

**VERDICT: REWORK.** The page contains a return guarantee and a risk-free claim that RICR 4.2 prohibits. It also describes a pre-publication approval control that the firm's filed procedure says does not exist.

**CONFIDENCE: high** for the two Critical findings, which are direct text-against-rule and text-against-procedure comparisons. **Medium** overall, because only a rule *extract* was supplied, nothing about the actual holdings was supplied, and no tools or independent reviewer were available.

**INPUTS LEDGER**
- Seen: request.md, context.md, page.md, compliance_procedure.md, performance.csv, rule_extract.md.
- Not seen:
  - The full RICR. This matters only for possible additional requirements beyond 4.2, 4.3 and 4.5.
  - Portfolio holdings or the investment mandate. This matters because "holds high-grade bonds" cannot be checked.
  - How the firm computes "five-year average." This matters only slightly, because both methods give 7.1%.

**COVERAGE**
- Scope: the whole page, all 7 sentences.
- Checked:
  - page.md (every sentence)
  - rule_extract.md (4.2, 4.3, 4.5)
  - compliance_procedure.md
  - performance.csv (all 5 rows)
  - request.md
  - context.md
- Not checked:
  - RICR text outside the extract (not_supplied)
  - Holdings data (not_supplied)

**SEATS AND GATE:** Only the local reviewer ran. No subagent or cross-vendor seat was available. The sensitivity gate is not triggered: the materials contain no personal, client or credential data.

**CLAIMS TO EVIDENCE**

| Claim | Location | Support | Status |
|---|---|---|---|
| C1 "guaranteed 6% a year" | page.md L3 | None. performance.csv shows 2021 at 4.2%, below 6%. | Contradicted by the data and prohibited by RICR 4.2. Linked to F1. |
| C2 "risk-free" | page.md L3 | None | Prohibited by RICR 4.2. Linked to F1. |
| C3 "so you can sleep at night" | page.md L3 | None | Implies freedom from risk. Interpretation. Linked to F3. |
| C4 "holds high-grade bonds" | page.md L3 | No holdings supplied | UNVERIFIED. Linked to N1. |
| C5 "five-year average 7.1%, net of fees" | page.md L5 | performance.csv, 2021–2025, net_return_pct | Recomputed (details below). Derived value verified. |
| C6 Past-performance statement | page.md L5 | RICR 4.3 | Present and verified. |
| C7 "Every page … reviewed and approved … before it goes live" | page.md L7 | compliance_procedure.md says the opposite | Contradicted. Linked to F2. |
| C8 "Compare this information…" | page.md L9 | RICR 4.5 | Verbatim match, verified. |

Recomputation of C5:
- Arithmetic mean: (4.2 + 8.1 + 6.9 + 9.4 + 6.9) / 5 = 35.5 / 5 = **7.10%**.
- Geometric (annualized) mean: the cumulative growth factor is 1.4082, which annualizes to about **7.09%**. This also rounds to 7.1%.

**FINDINGS**

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | R, C | page.md L3, "Earn a guaranteed 6% a year, risk-free." | RICR 4.2: "A communication must not state or imply that a return is guaranteed, or that an investment is free of risk." The sentence does both. The guarantee is also false on the firm's own data: 2021 returned 4.2%. | A retail investor reads the page as a promise of 6% with no risk of loss. When a year returns under 6% or a bond defaults, the investor has been misled. The regulator can read a plain breach of 4.2 on a public page. | Delete the sentence. Replace it with a description of the strategy that makes no promise or safety claim. | y/y/y/y |
| F2 | Critical | CONFIRMED | R | page.md L7, "Every page on this site is reviewed and approved by our compliance officer before it goes live." | The filed procedure says: "Posts and pages are not individually approved before they are published." Review is a monthly 10% sample taken after publication. The page describes a control that does not operate, which breaks the request's instruction "do not say anything the firm does not do." | An investor or regulator relies on the stated pre-approval. The filed procedure, which the regulator holds, shows the statement is false. That turns a marketing page into a misstatement about the firm's own controls. | Delete the sentence. If a statement about review is wanted, describe the filed process accurately, or say nothing. | y/y/y/y |
| F3 | High | PROBABLE | R | page.md L3, "so you can sleep at night" | Read together with "high-grade bonds," this implies the investment carries no meaningful risk. RICR 4.2 also prohibits *implying* that an investment is free of risk. This is a sibling of F1 and survives even if F1's words are removed. | The guarantee is deleted but this phrase stays. The page still implies safety and remains exposed under 4.2's "or imply" clause. | Remove the phrase, or pair any description of the strategy with a plain statement that the value can fall and investors can lose money. | y/n/y/y |

Siblings searched for F1 and F3 (risk and guarantee language): every sentence on the page. Found L3 "sleep at night," recorded as F3. L5 and L9 are clean.

Siblings searched for F2 (statements about firm practice): every sentence on the page. Found L3 "holds high-grade bonds," recorded as N1 because it cannot be checked. L5's "net of fees" is supported by the csv column name.

None of these is a security finding. They are regulatory and customer-harm findings with no system trust boundary.

**NEEDS VALIDATION**
- **N1.** "Steady Harbor holds high-grade bonds" (L3). Unresolved fact: whether the portfolio's mandate or current holdings are restricted to high-grade bonds. If they are not, this is another statement of something the firm does not do.
- **N2.** The 7.1% figure gives no period and no averaging method (L5). Unresolved fact: whether the full RICR, beyond the extract, requires a stated period or standardized annualized periods. The number itself reproduces under both methods.

**REFUTED**
- *"7.1% is miscalculated."* The arithmetic mean is exactly 7.10% and the geometric mean is about 7.09%. Both round to 7.1%.
- *"Missing the 4.3 statements."* L5 says "net of fees" and "Past performance does not predict future results," which satisfies 4.3.
- *"Missing the 4.5 sentence."* L9 matches the required sentence verbatim.

**WHAT HOLDS UP:** The performance line is net of fees, reproduces from the supplied data, and carries the required past-performance statement. The RICR 4.5 sentence is present verbatim.

**UNVERIFIED CLAIMS:**
- "High-grade bonds." Confirm it against the investment mandate or holdings report.
- That the csv figures are net of *all* fees. Confirm against the fee schedule and the performance calculation method.

**QUESTIONS FOR THE AUTHOR**
1. What document shows the portfolio holds only high-grade bonds?
2. Is there any pre-publication approval process other than the filed one? If there is, the filed procedure is out of date and must be refiled. The page cannot simply assert the process.

**DECISION-MAKER SUMMARY:** Do not publish. The page states a guaranteed, risk-free 6% return, which RICR 4.2 forbids and the firm's own 2021 result contradicts. It also claims a pre-publication compliance approval that the filed procedure explicitly denies. Publishing as written exposes the firm to a regulatory breach and a misstatement about its own controls. Removing the guarantee sentence, the "sleep at night" phrase and the approval sentence clears every confirmed finding.

**OWNER SUMMARY:** The page promises a guaranteed, risk-free return, which the rules forbid and which past results show is not true. It also says every page is approved by compliance before it goes live, but the firm's filed procedure says pages are only spot-checked after publication. Take out those statements and confirm the bond-holdings description before the page goes public.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "full RICR text beyond extract", "status": "not_seen", "matters": true},
    {"item": "portfolio holdings / mandate", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "local-reviewer", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "no personal, client or credential data"},
  "coverage": {
    "checked": [
      {"unit": "page.md", "kind": "document"},
      {"unit": "compliance_procedure.md", "kind": "document"},
      {"unit": "performance.csv", "kind": "data"},
      {"unit": "rule_extract.md", "kind": "document"},
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"}
    ],
    "not_checked": [
      {"unit": "full RICR", "reason": "not_supplied"},
      {"unit": "holdings data", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "R",
     "location": "page.md L3: \"Earn a guaranteed 6% a year, risk-free.\"",
     "scenario": "Public page states a guaranteed return and no risk, breaching RICR 4.2 (\"must not state or imply that a return is guaranteed, or that an investment is free of risk\"); the firm's own data shows 2021 at 4.2%, below the 'guaranteed' 6%.",
     "fix": "Delete the sentence; describe the strategy without any guarantee or safety claim.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "every sentence of page.md for guarantee/safety wording", "found": "L3 'sleep at night' (F3)"}},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "R",
     "location": "page.md L7: \"Every page on this site is reviewed and approved by our compliance officer before it goes live.\"",
     "scenario": "Filed procedure states 'Posts and pages are not individually approved before they are published' (monthly 10% post-publication sample); the page asserts a control that does not operate, readable against the filing by the regulator.",
     "fix": "Delete the sentence, or describe the filed sampling process accurately.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "every page.md sentence asserting a firm practice", "found": "L3 'holds high-grade bonds' (unverifiable, N1)"}},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "R",
     "location": "page.md L3: \"so you can sleep at night\"",
     "scenario": "Even with F1 removed, the phrase implies the investment is free of risk, which RICR 4.2's 'or imply' clause prohibits.",
     "fix": "Remove the phrase or pair the strategy description with a plain statement that investors can lose money.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "every sentence of page.md for implied-safety wording", "found": "no other instance"}},
    {"id": "N1", "status": "needs_validation", "track": "R", "location": "page.md L3: \"Steady Harbor holds high-grade bonds\"",
     "suspicion": "May describe holdings the portfolio does not have.",
     "unresolved_fact": "Whether the mandate or current holdings are limited to high-grade bonds."},
    {"id": "N2", "status": "needs_validation", "track": "R", "location": "page.md L5",
     "suspicion": "Performance figure gives no period or averaging method.",
     "unresolved_fact": "Whether the full RICR requires stated periods or standardized annualized returns."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "7.1% five-year average is miscalculated.", "evidence": "Arithmetic mean 35.5/5 = 7.10%; geometric mean ~7.09%; both round to 7.1%."},
    {"id": "C2", "candidate": "RICR 4.3 statements missing.", "evidence": "L5 shows 'net of fees' and the past-performance sentence."},
    {"id": "C3", "candidate": "RICR 4.5 sentence missing.", "evidence": "L9 matches the required sentence verbatim."}
  ]
}
```