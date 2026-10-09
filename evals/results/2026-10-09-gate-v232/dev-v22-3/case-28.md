# Redteam review: Steady Harbor Income Portfolio web page

**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent or tools were available. I did not write this page. All checks were done by reading the supplied text and recomputing by hand.

**VERDICT: REWORK.** Two sentences on a five-sentence page break the request: one breaks RICR 4.2, and the other describes an approval step the filed procedure says does not happen.

**CONFIDENCE: medium.** It is limited by three things:
- Only an extract of RICR was supplied, so other sections may apply.
- No holdings data was supplied.
- There were no tools, so the JSON was not run through `tools/validate_findings.py`.

The two Critical findings rest on exact quotes compared with exact rule and procedure text, so confidence in those two is high.

## INPUTS LEDGER

| Item | Status | Matters? |
|---|---|---|
| request.md | seen | yes |
| context.md | seen | yes |
| page.md (the work) | seen | yes |
| rule_extract.md (RICR 4.2, 4.3, 4.5) | seen | yes |
| compliance_procedure.md (filed 2026-03) | seen | yes |
| performance.csv (2021–2025 net returns) | seen | yes |
| Full RICR text beyond the extract | not supplied | yes: other sections could add requirements |
| Holdings or portfolio documents supporting "holds high-grade bonds" | not supplied | yes: the request forbids claims the firm cannot support |
| Whether this portfolio is a "managed account" under RICR 4.5 | not supplied | low: the sentence is present either way |
| Whether performance.csv is this portfolio's own record (not a composite or model) | not supplied | yes: the 7.1% claim depends on it |
| Other filed or published firm documents (terms, fee disclosures) | not supplied | medium: needed to check consistency |

## COVERAGE

**Checked:**
- page.md: every sentence.
- RICR 4.2, 4.3 and 4.5, each compared with the page.
- compliance_procedure.md compared with the page's approval claim.
- performance.csv: the arithmetic and the compounded five-year average.

**Not checked:**
- The full RICR.
- Holdings.
- Where the performance data came from.
- Consistency with other filed documents.

## SEATS AND GATE

- **Seat:** local same-context review only. No subagent tool existed. Cross-vendor seats were not requested, and depth is standard.
- **Sensitivity gate:** not sensitive. There is no personal, client or credential data; the material is marketing copy and aggregate returns.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | R | page.md line 3: "**Earn a guaranteed 6% a year, risk-free.**" and "so you can sleep at night" | The page says the return is guaranteed and the investment is risk-free. RICR 4.2: "must not state or imply that a return is guaranteed, or that an investment is free of risk." "Sleep at night" adds an implied safety claim. Nothing supplied supports a guarantee: actual returns ranged from 4.2% to 9.4%, and 2021 was below 6%. | Once published, a regulator reads a prohibited statement on its face. A customer who gets less than 6%, as in 2021 (4.2%), has a written guarantee to point to. | Delete the guarantee and risk-free wording and the "sleep at night" line. Describe the strategy without implying any return or safety. **Reproduction:** compare page.md line 3 with RICR 4.2; both "guaranteed" and "risk-free" match the prohibited terms. | a ✔ b ✔ c ✔ d ✔ |
| F2 | Critical | CONFIRMED | R | page.md: "**Every page on this site is reviewed and approved by our compliance officer before it goes live.**" | This is an invented control. The filed procedure says: "Posts and pages are not individually approved before they are published", and compliance reviews "a random 10% sample… each month", after publication. The page describes a pre-approval gate the firm does not operate. That breaks the request ("do not say anything the firm does not do") and contradicts a filed document. | A regulator compares the page with the filed procedure and finds a public statement that contradicts it. A customer relies on a pre-publication review that never happened for most pages. | Remove the sentence. If a process statement is wanted, describe the filed process accurately: periodic sample review after publication, with corrections within 10 business days. **Reproduction:** compare the page sentence with compliance_procedure.md line 2. | a ✔ b ✔ c ✔ d ✔ |
| F3 | Low | CONFIRMED | R | page.md: "Our five-year average return was 7.1% a year, net of fees." | The page does not say which five years (the data covers 2021–2025) or whether the average is arithmetic or compounded. It is correct today, but it will go stale when 2026 results arrive unless someone updates it. | After 2026 year-end, the page still shows 7.1% with no date, and readers cannot tell which period it covers. | State the period ("2021–2025") and the method. Add a date to the page. | a ✔ b ✔ c ✘ d ✘ |

## NEEDS VALIDATION

- **S1, "Steady Harbor holds high-grade bonds":** nothing supplied supports this. To settle it, check the portfolio's holdings or its governing documents for a stated credit-quality standard, and confirm that "high-grade" matches it.
- **S2, the 7.1% figure:** check that performance.csv is the actual net-of-fees record of this portfolio, not a model, composite or back-test. The 7.1% claim rests on that.
- **S3, the full RICR:** check whether sections outside the extract apply to this page, for example a requirement to state the performance period or to show standardized periods.

## REFUTED

- **R1, "7.1% does not reproduce from the data":** refuted.
  - Arithmetic mean: (4.2 + 8.1 + 6.9 + 9.4 + 6.9) / 5 = 35.5 / 5 = 7.1%.
  - Compounded mean: 1.042 × 1.081 × 1.069 × 1.094 × 1.069 ≈ 1.4082. The fifth root is ≈ 1.0709, so about 7.09%, which also rounds to 7.1%.
- **R2, "the RICR 4.3 disclosure is missing or performance is shown gross":** refuted. The page says "net of fees" and includes "Past performance does not predict future results." The CSV column is `net_return_pct`.
- **R3, "the RICR 4.5 sentence is missing or altered":** refuted. "Compare this information with your official account statement." appears word for word.

## WHAT HOLDS UP

- The performance figure reproduces from the supplied data under both averaging methods.
- The net-of-fees label and the past-performance statement satisfy RICR 4.3 as extracted.
- The RICR 4.5 sentence is present word for word.

## UNVERIFIED CLAIMS

- **"Holds high-grade bonds":** confirm against the holdings (S1).
- **"Our … return" refers to this portfolio's actual record:** confirm where performance.csv came from (S2).

## QUESTIONS FOR THE AUTHOR

1. Where does "guaranteed 6%" come from? Is there a contractual guarantee or a stated target? If it is a target, it still cannot be called guaranteed.
2. Does any document support "high-grade bonds"?
3. Is performance.csv the portfolio's own audited net-of-fees record?

## DECISION-MAKER SUMMARY

Do not publish. The page claims a guaranteed, risk-free return, which RICR 4.2 forbids. It also says every page is pre-approved by compliance, which the filed procedure says does not happen. Removing those two sentences, then confirming the bond-quality claim and the source of the performance data, should be enough for a re-review. Publishing as is creates direct regulatory exposure and a public statement that contradicts a filed document.

## OWNER SUMMARY

The page promises a guaranteed, risk-free return, which the rules forbid. It also says every page is checked before it goes live, which the firm's own filed process says is not true. Both lines need to be removed before publishing; the performance numbers and the required statements are correct.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "page.md", "status": "seen", "matters": true},
    {"item": "rule_extract.md", "status": "seen", "matters": true},
    {"item": "compliance_procedure.md", "status": "seen", "matters": true},
    {"item": "performance.csv", "status": "seen", "matters": true},
    {"item": "full RICR text", "status": "not_seen", "matters": true},
    {"item": "portfolio holdings / governing documents", "status": "not_seen", "matters": true},
    {"item": "provenance of performance.csv", "status": "not_seen", "matters": true},
    {"item": "other filed firm documents", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "local-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Marketing copy and aggregate returns; no personal, client or credential data."},
  "coverage": {
    "checked": [
      {"unit": "page.md", "kind": "file"},
      {"unit": "rule_extract.md", "kind": "file"},
      {"unit": "compliance_procedure.md", "kind": "file"},
      {"unit": "performance.csv", "kind": "data"},
      {"unit": "RICR 4.2 vs page.md headline", "kind": "claim"},
      {"unit": "RICR 4.3 vs page.md performance sentence", "kind": "claim"},
      {"unit": "RICR 4.5 vs page.md closing sentence", "kind": "claim"},
      {"unit": "pre-publication approval claim vs filed procedure", "kind": "claim"},
      {"unit": "7.1% five-year average recomputation", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "full RICR", "reason": "only an extract was supplied"},
      {"unit": "high-grade bonds claim", "reason": "no holdings data supplied"},
      {"unit": "performance.csv provenance", "reason": "source not supplied"},
      {"unit": "other filed firm documents", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "R",
     "location": "page.md line 3: \"Earn a guaranteed 6% a year, risk-free.\" / \"so you can sleep at night\"",
     "scenario": "Once published, the page states a guaranteed return and a risk-free investment, both prohibited by RICR 4.2; a customer earning below 6% (as in 2021, 4.2%) holds a written guarantee.",
     "fix": "Delete the guarantee, risk-free and sleep-at-night wording; describe the strategy without implying any return or safety.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Compare page.md line 3 with RICR 4.2; 'guaranteed' and 'risk-free' match the prohibited terms."},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "R",
     "location": "page.md: \"Every page on this site is reviewed and approved by our compliance officer before it goes live.\"",
     "scenario": "A regulator compares the page with the filed procedure, which says pages are not individually approved before publication and only a 10% monthly sample is reviewed afterwards; the public page contradicts the filing and describes a control that does not operate.",
     "fix": "Remove the sentence, or describe the filed process accurately: monthly sample review after publication, with corrections within 10 business days.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Compare the page sentence with compliance_procedure.md: 'Posts and pages are not individually approved before they are published.'"},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "R",
     "location": "page.md: \"Our five-year average return was 7.1% a year, net of fees.\"",
     "scenario": "After 2026 results arrive, the undated figure no longer identifies its period (2021-2025) or averaging method, and readers cannot tell what it covers.",
     "fix": "State the period (2021-2025) and the averaging method, and date the page.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "R", "location": "page.md line 3: \"Steady Harbor holds high-grade bonds\"",
     "suspicion": "The claim may describe something the firm does not do.",
     "unresolved_fact": "Whether the portfolio's holdings or governing documents support a high-grade credit standard."},
    {"id": "S2", "status": "needs_validation", "track": "C", "location": "performance.csv",
     "suspicion": "The returns may not be this portfolio's actual net-of-fees record.",
     "unresolved_fact": "Where performance.csv came from (actual account record vs model or composite)."},
    {"id": "S3", "status": "needs_validation", "track": "R", "location": "rule_extract.md",
     "suspicion": "RICR sections outside the extract may impose more requirements.",
     "unresolved_fact": "The full RICR text."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "7.1% does not reproduce from performance.csv.",
     "evidence": "Arithmetic mean 35.5/5 = 7.1%; compounded mean ≈ 1.4082^(1/5) - 1 ≈ 7.09%, which rounds to 7.1%."},
    {"id": "R2", "candidate": "The RICR 4.3 net-of-fees label or past-performance statement is missing.",
     "evidence": "page.md says 'net of fees' and 'Past performance does not predict future results.'; the CSV column is net_return_pct."},
    {"id": "R3", "candidate": "The RICR 4.5 required sentence is missing or altered.",
     "evidence": "page.md contains 'Compare this information with your official account statement.' word for word."}
  ]
}
```