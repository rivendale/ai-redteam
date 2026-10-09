# Redteam review: Steady Harbor Income Portfolio web page

**VERDICT: SHIP.** I found no confirmed defect. The page meets each supplied RICR paragraph, its performance figures reproduce from `performance.csv`, and its description of the review procedure matches the filed procedure.

**CONFIDENCE: medium.** Three things limit it:
- I had no tools, so everything was checked by reading and hand arithmetic.
- I saw only an extract of the rule, not the full RICR.
- No document backs the holdings claim ("high-grade bonds").

I am not the author of this work, but no independent subagent or cross-vendor seat ran.

**INPUTS LEDGER**
- **Seen:**
  - `request.md`
  - `context.md`
  - `page.md` (the work)
  - `rule_extract.md` (RICR 4.2, 4.3, 4.5)
  - `compliance_procedure.md` (filed 2026-03)
  - `performance.csv`
- **Not seen, and whether it matters:**
  - **Full RICR text.** It matters a little. Paragraphs outside the extract (for example 4.1 and 4.4) may impose further requirements.
  - **Portfolio holdings or investment policy.** It matters for one sentence: "holds high-grade bonds".
  - **Source records behind `performance.csv`** (audited or composite figures). It matters because the page's numbers are only as good as the CSV.
  - **Confirmation that the portfolio is a "managed account" under RICR 4.5.** It does not matter much: the page carries the sentence anyway.

**COVERAGE**
- **Checked:**
  - Every sentence of `page.md`, against RICR 4.2, 4.3 and 4.5.
  - The performance figures, against `performance.csv`, with the average recomputed.
  - The description of the procedure, against `compliance_procedure.md`.
  - The request's instruction "do not say anything the firm does not do".
- **Not checked:**
  - RICR paragraphs outside the extract.
  - The holdings claim.
  - Where the performance data came from.
  - Page elements not supplied (images, footers, links).

**SEATS AND GATE**
- **Seats:** Only this reviewer ran, with no tools. No subagent or cross-vendor seats were available in this session.
- **Sensitivity gate:** Passed. The material contains no personal, client or credential data; the page is intended for publication.

## FINDINGS

None confirmed.

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| none | | | | | | | | |

## NEEDS VALIDATION

These have no severity and do not affect the verdict.

- **S1, `page.md:3`, "Steady Harbor holds high-grade bonds."** This is a factual claim about the firm's practice, and no input supports it. It would be settled by the current holdings or the investment policy showing that the portfolio is restricted to, and actually holds, high-grade bonds.
- **S2, `page.md:6-7` and `performance.csv`, the performance figures.** The page matches the CSV, but I could not check the CSV's provenance. It would be settled by confirming that the 2021–2025 figures are net of all fees and match the firm's official or audited performance records.
- **S3, RICR beyond the extract.** The page meets 4.2, 4.3 and 4.5. Other paragraphs may set further requirements (for example on period length, benchmarks, or how current figures must be). This would be settled by reading the full RICR, or by the compliance officer confirming that the extract covers every applicable paragraph.

## REFUTED

- **C1: "The 7.1% average is wrong or misleading."**
  - Arithmetic mean: (4.2 + 8.1 + 6.9 + 9.4 + 6.9) / 5 = 35.5 / 5 = **7.1%**.
  - Compounded (annualized): 1.042 × 1.081 × 1.069 × 1.094 × 1.069 ≈ 1.4082, and 1.4082^(1/5) ≈ 1.0709, which is **7.1%**.
  - Both methods round to 7.1%, and the yearly figures match the CSV row for row.
- **C2: "'Steady income' and the name 'Steady Harbor' imply a guaranteed return (RICR 4.2)."** The page says "aims for", and in the same paragraph states "you can lose money … no return is guaranteed".
- **C3: "The page describes a control the firm does not operate (an invented pre-approval)."** The page says a random 10% monthly sample is reviewed and that "Pages are not individually approved before they are published". That matches the filed procedure nearly word for word, so no pre-approval is claimed.
- **C4: "Required statements are missing or paraphrased."**
  - "Net of fees" is present (4.3).
  - "Past performance does not predict future results." is present (4.3).
  - The 4.5 sentence appears verbatim: "Compare this information with your official account statement."

## WHAT HOLDS UP

- **Risk wording:** it is explicit and placed next to the income aim.
- **Performance:** it is net of fees, broken down year by year, dated, and reproduces from its source.
- **Mandatory sentences:** they are verbatim.
- **Description of the procedure:** it is accurate, and it avoids overstating oversight. This directly honours "do not say anything the firm does not do".

## UNVERIFIED CLAIMS

- **"Holds high-grade bonds."** Confirm against the holdings or the investment policy (S1).
- **The figures are "net of fees".** Confirm against the fee-adjusted records (S2).

## QUESTIONS FOR THE AUTHOR

1. What document supports "holds high-grade bonds"?
2. Are the CSV figures from the official, fee-net performance record?
3. Does any RICR paragraph outside the extract apply to this page?

## DECISION-MAKER SUMMARY

The page meets every supplied rule, and its numbers check out, so it can be published. Before publishing, confirm the holdings claim and the source of the performance data. If you proceed without that, the residual risk is a factual misstatement on a regulated page that this review could not see.

## OWNER SUMMARY

The page follows the rules we were given, the return figures add up correctly, and it describes our review process honestly. Before it goes live, someone should confirm that the portfolio really holds high-grade bonds and that the return figures come from our official records. Otherwise it is ready.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "page.md", "status": "seen", "matters": true},
    {"item": "rule_extract.md", "status": "seen", "matters": true},
    {"item": "compliance_procedure.md", "status": "seen", "matters": true},
    {"item": "performance.csv", "status": "seen", "matters": true},
    {"item": "full RICR text", "status": "not_seen", "matters": true},
    {"item": "portfolio holdings / investment policy", "status": "not_seen", "matters": true},
    {"item": "source records for performance.csv", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Public marketing page; no personal, client or credential data."},
  "coverage": {
    "checked": [
      {"unit": "page.md", "kind": "file"},
      {"unit": "compliance_procedure.md", "kind": "file"},
      {"unit": "performance.csv", "kind": "data"},
      {"unit": "rule_extract.md", "kind": "file"},
      {"unit": "RICR 4.2 no guarantee / no risk-free", "kind": "claim"},
      {"unit": "RICR 4.3 net of fees + past performance statement", "kind": "claim"},
      {"unit": "RICR 4.5 required sentence", "kind": "claim"},
      {"unit": "five-year average 7.1% (arithmetic and compounded)", "kind": "claim"},
      {"unit": "procedure description matches filed procedure", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "full RICR beyond extract", "reason": "not supplied"},
      {"unit": "holdings claim 'high-grade bonds'", "reason": "no holdings or policy document supplied"},
      {"unit": "provenance of performance.csv", "reason": "source records not supplied"}
    ]
  },
  "findings": [
    {"id": "S1", "status": "needs_validation", "track": "R", "location": "page.md:3",
     "suspicion": "'Steady Harbor holds high-grade bonds' is a practice claim with no supporting input.",
     "unresolved_fact": "Whether current holdings and the investment policy restrict the portfolio to high-grade bonds."},
    {"id": "S2", "status": "needs_validation", "track": "C", "location": "page.md:6-7; performance.csv",
     "suspicion": "Page matches the CSV, but the CSV's figures may not be the official net-of-fees record.",
     "unresolved_fact": "Whether 2021-2025 figures match the firm's official or audited net-of-fees performance."},
    {"id": "S3", "status": "needs_validation", "track": "R", "location": "rule_extract.md",
     "suspicion": "RICR paragraphs outside the extract may impose further requirements.",
     "unresolved_fact": "Whether the extract covers every RICR paragraph applicable to this page."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The 7.1% five-year average is wrong or misleading.",
     "evidence": "Arithmetic mean 35.5/5 = 7.1; compounded 1.4082^(1/5) ≈ 1.0709 = 7.1%; yearly figures match performance.csv."},
    {"id": "C2", "candidate": "'Steady income' implies a guaranteed return (RICR 4.2).",
     "evidence": "Page says 'aims for' and states 'you can lose money ... no return is guaranteed' in the same paragraph."},
    {"id": "C3", "candidate": "Page describes a control the firm does not operate.",
     "evidence": "Page's 10% monthly sample and 'not individually approved' match compliance_procedure.md."},
    {"id": "C4", "candidate": "A required RICR statement is missing or paraphrased.",
     "evidence": "Net of fees stated; past-performance sentence present; RICR 4.5 sentence verbatim."}
  ]
}
```