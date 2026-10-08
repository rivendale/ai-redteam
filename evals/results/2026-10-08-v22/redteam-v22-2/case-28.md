**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** I had no tools, so nothing was fetched or run. Every figure below was recomputed by hand from the supplied files.

**VERDICT: REWORK.** The page breaks RICR 4.2 in its headline. It also claims a pre-publication approval control that the firm's filed procedure says does not exist.

**CONFIDENCE: medium.** Limited by: same-context review, no tools, and only an extract of the rule (other RICR paragraphs not seen). Holdings data behind "high-grade bonds" was not supplied.

**INPUTS LEDGER**
- **Seen:**
  - request.md
  - context.md
  - page.md
  - rule_extract.md (4.2, 4.3, 4.5)
  - compliance_procedure.md (filed 2026-03)
  - performance.csv (2021–2025)
- **Not seen:**
  - Full RICR text. This matters: other paragraphs may impose requirements, such as stating the performance period or calculation method.
  - Portfolio holdings or credit-quality data. This matters for the "high-grade bonds" claim.
  - The firm's other published documents (terms, filings beyond the procedure). This matters for the consistency check.

**COVERAGE**
- **Checked:**
  - page.md, every sentence
  - rule_extract.md 4.2, 4.3, 4.5 against the page
  - compliance_procedure.md against the page's control claim
  - performance.csv: recomputed the 7.1% figure
- **Not checked:**
  - The full RICR
  - Holdings data
  - Other filed or published documents
  - How the page will be versioned or archived once published

**SEATS AND GATE:** Local same-context reviewer only. No subagent or cross-vendor seats were available. Sensitivity gate: not sensitive. The material is a public marketing page and a public rule extract, with no personal data.

**FINDINGS**

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | R | page.md line 3: "Earn a guaranteed 6% a year, risk-free." | The page states a guaranteed return and no risk. RICR 4.2 prohibits both: "must not state or imply that a return is guaranteed, or that an investment is free of risk." The claim is also false on the firm's own data: 2021 net return was 4.2%, below the "guaranteed" 6%. "So you can sleep at night" reinforces the implied safety. | The page is published. A regulator reads the headline and finds a direct 4.2 breach. A customer buys expecting 6% with no loss and gets 4.2% (as in 2021) or a loss, then has a misrepresentation claim. | Delete "guaranteed", "risk-free" and "sleep at night". Do not state a target return as a promise. Add a plain risk statement (bond prices can fall; you can lose money). **Reproduction:** search page.md for "guarantee" and "risk-free"; expect 0 hits, observe 1 each. Positive control: the same search on this unedited page returns the hits. | a Y, b Y, c Y, d Y |
| F2 | Critical | CONFIRMED | R | page.md line 7: "Every page on this site is reviewed and approved by our compliance officer before it goes live." | This is an invented control that contradicts the filed procedure. compliance_procedure.md says: "Posts and pages are not individually approved before they are published." Review is a monthly random 10% sample after publication. It also breaks the request's instruction "do not say anything the firm does not do". | The regulator compares the page to the procedure the firm filed in 2026-03 and finds the firm publicly describing a control it has told the regulator it does not run. This is a misstatement to the public and an inconsistency with a filed document. If a bad page later surfaces, the false claim aggravates it. | Delete the sentence. If anything is said, describe the actual practice: pages are reviewed by sampling after publication. Better still, say nothing about internal review. **Reproduction:** compare page.md line 7 with compliance_procedure.md line 4. The statements are mutually exclusive. | a Y, b Y, c Y, d Y |

**NEEDS VALIDATION**
- **S1, "Steady Harbor holds high-grade bonds" (page.md line 3).** The settling fact is the portfolio's holdings and credit ratings over the period. If it holds sub-investment-grade or unrated paper, the claim is untrue and adds to F1's implied safety.
- **S2, performance presentation (page.md line 5).** The settling fact is whether the full RICR requires the period (2021–2025) and the calculation method to be stated. The page says "five-year average" without naming the years or saying arithmetic versus annualized.

**REFUTED**
- **C1: "The 7.1% figure is wrong."**
  - Arithmetic mean: (4.2+8.1+6.9+9.4+6.9)/5 = 35.5/5 = 7.1%.
  - Geometric (annualized): 1.042×1.081×1.069×1.094×1.069 ≈ 1.4082, and the fifth root is ≈ 1.0709, so ≈ 7.09%, which rounds to 7.1%.
  - Both methods reproduce the figure.
- **C2: "Performance is not net of fees."** The CSV column is `net_return_pct`, and the page says "net of fees". This is consistent with 4.3.

**WHAT HOLDS UP**
- RICR 4.3: performance is shown net of fees, and the page carries "Past performance does not predict future results." verbatim.
- RICR 4.5: "Compare this information with your official account statement." is present verbatim.
- The 7.1% five-year figure reproduces from performance.csv.

**UNVERIFIED CLAIMS**
- "Holds high-grade bonds": confirm against holdings and ratings data (S1).
- Completeness against the full RICR: only three paragraphs were supplied. Check the remaining rule text for further required statements.

**QUESTIONS FOR THE AUTHOR**
1. Where did "guaranteed 6%" come from? Is there any contractual guarantee? (No answer would cure 4.2, but it tells us whether the error is wording or substance.)
2. What are the portfolio's holdings and credit quality?
3. Does the full RICR require stating the performance period and method?

**DECISION-MAKER SUMMARY:** Do not publish. The headline breaches RICR 4.2, and the approval sentence contradicts the firm's own filed procedure (F1, F2). Both fixes are deletions, after which the page is close to publishable. Publishing as is exposes the firm to regulatory action for prohibited claims and for a public statement inconsistent with its filing. Note also that under the filed procedure this page may never be reviewed at all (10% sample), so this pre-publication check is the only control it will get.

**OWNER SUMMARY:** The page promises a guaranteed, risk-free return, which the rules forbid and which the fund's own history disproves. It also says every page is approved by compliance before going live, but the firm's filed procedure says that does not happen. Remove both statements before publishing; the rest of the page meets the rules supplied.

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
    {"item": "Full RICR text", "status": "not_seen", "matters": true},
    {"item": "Portfolio holdings and credit-quality data", "status": "not_seen", "matters": true},
    {"item": "Other filed or published firm documents", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "same-context-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Public marketing page and public rule extract; no personal or confidential data."},
  "coverage": {
    "checked": [
      {"unit": "page.md", "kind": "file"},
      {"unit": "rule_extract.md", "kind": "file"},
      {"unit": "compliance_procedure.md", "kind": "file"},
      {"unit": "performance.csv", "kind": "data"},
      {"unit": "page.md: 7.1% five-year net average", "kind": "claim"},
      {"unit": "page.md: guaranteed 6% risk-free", "kind": "claim"},
      {"unit": "page.md: every page approved before going live", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "Full RICR text", "reason": "only an extract supplied"},
      {"unit": "page.md: holds high-grade bonds", "reason": "holdings data not supplied"},
      {"unit": "Other filed or published firm documents", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "R",
     "location": "page.md:3 \"Earn a guaranteed 6% a year, risk-free.\"",
     "scenario": "Published page states a guaranteed return and no risk, breaching RICR 4.2; the firm's own data shows 2021 net return of 4.2%, below the promised 6%, so a customer relying on it is misled and the regulator finds a direct breach.",
     "fix": "Remove 'guaranteed', 'risk-free' and 'sleep at night'; add a plain statement that the investment can lose value.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Search page.md for 'guarantee' and 'risk-free'; expected 0 hits, observed 1 each."},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "R",
     "location": "page.md:7 \"Every page on this site is reviewed and approved by our compliance officer before it goes live.\"",
     "scenario": "The filed procedure (compliance_procedure.md:4) says pages are not individually approved before publication and only a 10% monthly sample is reviewed afterwards; the regulator compares the page with the filing and finds a public description of a control that does not operate.",
     "fix": "Delete the sentence; if anything is said, describe the actual post-publication sampling practice.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Compare page.md:7 with compliance_procedure.md:4 ('Posts and pages are not individually approved before they are published'); the statements contradict."},
    {"id": "S1", "status": "needs_validation", "track": "R", "location": "page.md:3 \"Steady Harbor holds high-grade bonds\"",
     "suspicion": "The credit-quality claim may be untrue or overstated, reinforcing the implied safety.",
     "unresolved_fact": "The portfolio's actual holdings and their credit ratings over the period."},
    {"id": "S2", "status": "needs_validation", "track": "R", "location": "page.md:5 \"Our five-year average return was 7.1% a year, net of fees.\"",
     "suspicion": "The period (2021-2025) and calculation method are not stated, which the full rule may require.",
     "unresolved_fact": "Whether the full RICR requires the performance period and calculation method to be disclosed."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The 7.1% five-year average does not reproduce from the data.",
     "evidence": "Arithmetic mean 35.5/5 = 7.1%; geometric annualized (1.042*1.081*1.069*1.094*1.069)^(1/5) - 1 is about 7.09%, also rounding to 7.1%."},
    {"id": "C2", "candidate": "Performance is not shown net of fees (RICR 4.3).",
     "evidence": "performance.csv column is net_return_pct and page.md:5 says 'net of fees'."}
  ]
}
```