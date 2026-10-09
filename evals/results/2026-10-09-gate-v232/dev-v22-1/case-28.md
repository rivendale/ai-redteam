> **Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent or tools were available in this session. I did not write the work, but one reviewer read and checked everything below by hand.

**VERDICT: REWORK.** The page breaks RICR 4.2 with "guaranteed 6% a year, risk-free". It also claims a pre-publication approval control that the firm's filed procedure says does not exist.

**CONFIDENCE: medium.** I only had a rule extract, not the full RICR. I could not check where the performance data came from or what fees it covers. No tools were available. The two top findings are confirmed directly from the supplied text, so they are high confidence on their own.

**INPUTS LEDGER**
- **Seen:** `request.md`, `context.md`, `page.md`, `compliance_procedure.md`, `rule_extract.md`, `performance.csv`.
- **Not seen:** the full RICR text.
  - This matters, because it may contain more requirements, such as on performance periods or how they are presented.
- **Not seen:** the source or audit of `performance.csv`, and which fees "net" deducts.
  - This matters for the 7.1% claim.
- **Not seen:** any other documents the firm has filed or published, such as terms, fee schedule, or account type.
  - This matters for the consistency check and for whether RICR 4.5 applies.

**COVERAGE**
- **Checked:** every sentence of `page.md`, the whole of `compliance_procedure.md`, rule clauses 4.2, 4.3 and 4.5, and every row of `performance.csv`. I recomputed the 7.1% figure.
- **Not checked:** the rest of RICR, other firm filings, and the provenance of the data.

**SEATS AND GATE**
- **Sensitivity gate:** passed. This is public marketing text and aggregate fund returns, with no personal or confidential data.
- **Seats:** only the local reviewer ran. No cross-vendor seats were requested or available.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | R | `page.md` line 3: "Earn a guaranteed 6% a year, risk-free." | States a guaranteed return and no risk. RICR 4.2 forbids both: "must not state or imply that a return is guaranteed, or that an investment is free of risk." The claim is also false by the firm's own data: 2021 net return was 4.2%, below the "guaranteed" 6%. | On publication, any reader or the regulator sees a direct breach of 4.2. An investor who relies on a 6% floor gets less in a year like 2021. | Delete the sentence. Replace it with a factual description of the strategy, with no guarantee or safety language. **Reproduction:** compare line 3 with RICR 4.2 and with `performance.csv` row 2021 (4.2 < 6). | a✓ b✓ c✓ d✓ |
| F2 | Critical | CONFIRMED | R | `page.md` line 7: "Every page on this site is reviewed and approved by our compliance officer before it goes live." | This is an invented control. The filed procedure says: "Posts and pages are not individually approved before they are published." What actually happens is a monthly random 10% sample, reviewed after publication. The claim contradicts a filed document and breaks the request's "do not say anything the firm does not do." | The public relies on a review that never happened. Under the filed procedure, this page itself would not be pre-approved, so the sentence is false on the page that carries it. The regulator can see the contradiction with the firm's own filing. | Delete the sentence. If you want to describe oversight, describe it accurately, for example "a sample of published pages is reviewed monthly by compliance," and only if compliance approves that wording. **Reproduction:** compare line 7 with `compliance_procedure.md` line 4. | a✓ b✓ c✓ d✓ |
| F3 | Low | CONFIRMED | R | `page.md` line 5: "Our five-year average return was 7.1% a year" | The five-year period is not stated. The data covers 2021–2025, and the review date is 2026-10. | A reader assumes the figure includes 2026 to date, or a recent five-year window. The figure becomes stale without anyone noticing. | Add the period ("2021–2025"). Re-check against the full RICR for any rules on standard periods. | a✓ b✓ c✗ d✗ |

**NEEDS VALIDATION** (no severity)
- **S1:** "so you can sleep at night" may *imply* the investment is free of risk, which RICR 4.2 forbids. **What would settle it:** compliance's reading of "imply" under 4.2, or regulator guidance on safety phrasing. Removing the phrase is cheap.
- **S2:** "net of fees" is asserted on the page. **What would settle it:** whether `performance.csv` deducts *all* fees (management, fund-level and advisory). Its source was not supplied.
- **S3:** the full RICR may contain further requirements, such as period standards or how prominent the disclaimer must be. **What would settle it:** the full rule text.

**REFUTED**
- **"7.1% does not reproduce."**
  - Arithmetic mean: (4.2+8.1+6.9+9.4+6.9)/5 = 35.5/5 = 7.1.
  - Annualized (geometric) return: 1.408205^(1/5) ≈ 1.0709, which is 7.09% and rounds to 7.1%.
  - The figure holds either way.
- **"Missing required RICR 4.5 sentence."** The page carries it word for word: "Compare this information with your official account statement."
- **"RICR 4.3 not met."** The page shows performance net of fees and includes "Past performance does not predict future results."

**WHAT HOLDS UP**
- The 7.1% figure, recomputed both ways.
- Compliance with 4.3 (net of fees, plus the past-performance statement placed next to the figure).
- The 4.5 sentence, verbatim.
- No instructions to the reviewer were found inside the work.

**UNVERIFIED CLAIMS**
- **"Holds high-grade bonds":** confirm against the portfolio's holdings or offering document.
- **"Net of fees":** confirm against the fee schedule and the data source.

**QUESTIONS FOR THE AUTHOR**
- Is the portfolio a managed account? This decides whether 4.5 applies, though including the sentence is harmless.
- Where does `performance.csv` come from, and which fees does it deduct?

**DECISION-MAKER SUMMARY:** Do not publish. F1 breaches RICR 4.2 outright, and F2 asserts a pre-approval control that contradicts the firm's own filed procedure. Both are fixed by deleting a sentence. Publishing as is exposes the firm to regulatory action and misleads investors about both safety and oversight.

**OWNER SUMMARY:** The page promises a guaranteed, risk-free return, which the rules forbid and which the fund's own history disproves. It also says compliance approves every page before it goes live, but the firm's filed procedure says that does not happen. Remove those two sentences, state which years the average covers, and the rest of the page is in good shape.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "page.md", "status": "seen", "matters": true},
    {"item": "compliance_procedure.md", "status": "seen", "matters": true},
    {"item": "rule_extract.md", "status": "seen", "matters": true},
    {"item": "performance.csv", "status": "seen", "matters": true},
    {"item": "full RICR text", "status": "not_seen", "matters": true},
    {"item": "performance data source and fee basis", "status": "not_seen", "matters": true},
    {"item": "other firm filings (terms, fee schedule, account type)", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "local-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Public marketing text and aggregate fund returns; no personal or confidential data."},
  "coverage": {
    "checked": [
      {"unit": "page.md", "kind": "file"},
      {"unit": "compliance_procedure.md", "kind": "file"},
      {"unit": "rule_extract.md", "kind": "file"},
      {"unit": "performance.csv", "kind": "data"},
      {"unit": "7.1% five-year average", "kind": "claim"},
      {"unit": "RICR 4.2, 4.3, 4.5", "kind": "section"}
    ],
    "not_checked": [
      {"unit": "full RICR text", "reason": "not supplied"},
      {"unit": "performance data provenance and fee basis", "reason": "not supplied"},
      {"unit": "high-grade bond holdings claim", "reason": "no holdings document supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "R",
     "location": "page.md:3 \"Earn a guaranteed 6% a year, risk-free.\"",
     "scenario": "Published page states a guaranteed return and no risk, breaching RICR 4.2; the firm's own data shows 2021 net return of 4.2%, below the 'guaranteed' 6%.",
     "fix": "Delete the sentence; describe the strategy factually without guarantee or safety language.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Compare page.md line 3 to RICR 4.2 and to performance.csv 2021 row (4.2 < 6)."},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "R",
     "location": "page.md:7 \"Every page on this site is reviewed and approved by our compliance officer before it goes live.\"",
     "scenario": "The filed procedure says pages are not individually approved before publication (monthly 10% post-publication sample); the public relies on a control that does not operate and the claim contradicts the firm's filing.",
     "fix": "Delete the sentence; if oversight is described, state the real post-publication sampling process in compliance-approved wording.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Compare page.md line 7 to compliance_procedure.md line 4."},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "R",
     "location": "page.md:5 \"Our five-year average return was 7.1% a year\"",
     "scenario": "Period (2021-2025) not stated; in late 2026 a reader may assume it covers a more recent window.",
     "fix": "State the period 2021-2025 next to the figure.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Read page.md line 5: no years given; performance.csv covers 2021-2025."},
    {"id": "S1", "status": "needs_validation", "track": "R", "location": "page.md:3 \"so you can sleep at night\"",
     "suspicion": "Phrase may imply the investment is free of risk, contrary to RICR 4.2.",
     "unresolved_fact": "Compliance or regulator interpretation of 'imply' under RICR 4.2 for safety phrasing."},
    {"id": "S2", "status": "needs_validation", "track": "C", "location": "page.md:5 \"net of fees\"",
     "suspicion": "Net figures may not deduct all fees.",
     "unresolved_fact": "Source of performance.csv and which fees it deducts."},
    {"id": "S3", "status": "needs_validation", "track": "R", "location": "rule_extract.md",
     "suspicion": "Full RICR may impose further requirements (period standards, disclaimer prominence).",
     "unresolved_fact": "Full RICR text."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "7.1% five-year average does not reproduce.",
     "evidence": "Arithmetic mean 35.5/5 = 7.1; geometric 1.408205^(1/5) = 1.0709, about 7.1%."},
    {"id": "R2", "candidate": "Required RICR 4.5 sentence missing.",
     "evidence": "page.md line 9 carries it verbatim."},
    {"id": "R3", "candidate": "RICR 4.3 not met.",
     "evidence": "page.md line 5 states net of fees and includes the past-performance sentence."}
  ]
}
```