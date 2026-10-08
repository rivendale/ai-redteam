VERDICT: **REWORK**. The page breaks RICR 4.2 in its headline, and it describes a pre-publication approval control that the firm's own filed procedure says does not exist.

CONFIDENCE: **medium.** Both blocking findings rest on exact quotes, so the confidence limit is not about them. It is limited by three things: no tools were available, so the arithmetic was done by hand; this is a same-context review with no subagent available, so there is anchoring risk and anything high-stakes should be re-run in a fresh session; and only an extract of the rule was supplied.

INPUTS LEDGER:
- **Seen:** request.md, context.md, page.md, compliance_procedure.md (filed 2026-03), performance.csv, rule_extract.md (RICR 4.2, 4.3, 4.5).
- **Not seen:** the full RICR. Sections such as 4.1 and 4.4 are absent. This matters, because other requirements may apply to the page.
- **Not seen:** the portfolio's holdings or investment policy. This matters for the "high-grade bonds" claim.
- **Not seen:** the account type, i.e. whether this is a managed account under 4.5. This matters less, because the 4.5 sentence is present either way.
- **Not seen:** the methodology behind performance.csv (actual account, composite or model). This matters for 4.3 and for the "our return" wording.

COVERAGE:
- **Checked:**
  - page.md: every sentence.
  - performance.csv: all five rows, with the average recomputed.
  - rule_extract.md: 4.2, 4.3 and 4.5, each tested against the page.
  - compliance_procedure.md: tested against the page's control claim.
- **Not checked:**
  - RICR sections that were not supplied.
  - Whether the holdings claim is true.
  - The performance methodology.
  - Any other published firm documents, such as terms or filings beyond the procedure.

SEATS AND GATE: one reviewer ran, a same-context local review. No cross-vendor seats were requested and depth is standard. The sensitivity gate passed: there is no personal, client or confidential data, only public marketing text and aggregate returns.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | R | page.md:3 "**Earn a guaranteed 6% a year, risk-free.**" (also "so you can sleep at night") | It states a guaranteed return and freedom from risk, which RICR 4.2 prohibits in exact terms: "must not state or imply that a return is guaranteed, or that an investment is free of risk." The firm's own data contradicts the guarantee: 2021 returned 4.2%, below 6%. | The page is published. A regulator reading it finds a direct 4.2 breach in the headline. A retail customer invests relying on a 6% floor, receives a 4.2%-type year, and complains or claims mis-selling. | Delete the guarantee and the risk-free claim. Replace them with neutral wording, for example "seeks income from bonds; the value of your investment can fall." Drop "sleep at night", which implies no risk. **Reproduction:** compare page.md:3 word for word with RICR 4.2; "guaranteed" and "risk-free" match the prohibited terms. | Y/Y/Y/Y |
| F2 | Critical | CONFIRMED | R | page.md:7 "**Every page on this site is reviewed and approved by our compliance officer before it goes live.**" | This is an invented control. The filed procedure says: "Posts and pages are not individually approved before they are published," and that compliance reviews "a random 10% sample" after publication, each month. The request said "do not say anything the firm does not do." | A regulator compares the page with the filed procedure and finds a false statement about the firm's own controls. That is a misleading-communication problem in its own right, and it also undercuts trust in every other claim. Any customer relying on "pre-approved" is misled. | Delete the sentence. If a statement about review is wanted, describe the filed process accurately, for example "marketing is subject to periodic compliance review", or say nothing. **Reproduction:** read page.md:7 against compliance_procedure.md lines 3–4; they contradict each other directly. | Y/Y/Y/Y |

## NEEDS VALIDATION
- **S1 (page.md:3, "Steady Harbor holds high-grade bonds"):** this is a factual statement about holdings, and no holdings data was supplied. To settle it, check the current portfolio holdings and investment policy and confirm they are high-grade bonds.
- **S2 (page.md:5, "Our five-year average return"):** to settle it, find out whether performance.csv shows actual account or composite returns, and confirm that the full RICR has no further requirements, such as period or benchmark disclosure, that were left out of the extract.
- **S3 (page.md:9):** to settle it, confirm the portfolio is a "managed account" under 4.5. The required sentence is present either way, so this only affects whether 4.5 applies.

## REFUTED
- **R1. "7.1% does not reproduce."** The arithmetic mean is (4.2+8.1+6.9+9.4+6.9)/5 = 35.5/5 = 7.1%. The geometric (annualized) return is 1.042×1.081×1.069×1.094×1.069 ≈ 1.4082, which gives a fifth root of about 1.0709, or about 7.1%. The figure holds under either method. 2021–2025 is five years.
- **R2. "Missing 4.3 disclosures."** The page says "net of fees" and carries "Past performance does not predict future results." verbatim.
- **R3. "Missing 4.5 sentence."** "Compare this information with your official account statement." appears verbatim at page.md:9.

## WHAT HOLDS UP
- The performance figure is correct and stated net of fees.
- The 4.3 past-performance statement is verbatim.
- The 4.5 required sentence is verbatim.

## UNVERIFIED CLAIMS
- "Holds high-grade bonds." Confirm against the holdings.
- The source and methodology of the return series. Confirm with the performance team.

## QUESTIONS FOR THE AUTHOR
1. Where does the "guaranteed 6%" figure come from? Is there any contractual guarantee at all? If not, it must go.
2. Was the approval sentence meant to describe a planned procedure change? If so, the change must be filed and operating before the page can claim it.

## DECISION-MAKER SUMMARY
Do not publish yet. F1 breaches RICR 4.2 in the headline, and F2 claims a pre-approval control that the filed procedure explicitly denies. Both are fixed by deleting or rewording two sentences. Publishing as is exposes the firm to a regulatory finding and to customer claims built on a "guarantee" its own returns already missed in 2021.

## OWNER SUMMARY
The page promises a guaranteed, risk-free return, which the rules forbid, and the fund's own history shows a year below the promised rate. It also says every page is approved by compliance before going live, but the firm's filed procedure says that does not happen. Remove those two statements and confirm the bond-holdings description, and the rest of the page is in good shape.

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
    {"item": "performance.csv", "status": "seen", "matters": true},
    {"item": "rule_extract.md", "status": "seen", "matters": true},
    {"item": "full RICR text beyond the extract", "status": "not_seen", "matters": true},
    {"item": "portfolio holdings / investment policy", "status": "not_seen", "matters": true},
    {"item": "performance methodology (actual vs composite)", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Public marketing text and aggregate returns only; no personal or client data."},
  "coverage": {
    "checked": [
      {"unit": "page.md", "kind": "file"},
      {"unit": "compliance_procedure.md", "kind": "file"},
      {"unit": "performance.csv", "kind": "data"},
      {"unit": "rule_extract.md", "kind": "file"},
      {"unit": "RICR 4.2", "kind": "section"},
      {"unit": "RICR 4.3", "kind": "section"},
      {"unit": "RICR 4.5", "kind": "section"},
      {"unit": "page.md:5 five-year average 7.1% net", "kind": "claim"},
      {"unit": "page.md:7 pre-publication approval", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "RICR sections not in extract", "reason": "not supplied"},
      {"unit": "page.md:3 high-grade bonds holdings claim", "reason": "holdings not supplied"},
      {"unit": "performance methodology", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "R",
     "location": "page.md:3",
     "scenario": "Headline 'Earn a guaranteed 6% a year, risk-free' is published; it directly breaches RICR 4.2 and is contradicted by the 4.2% 2021 return, so a regulator finds a breach and customers relying on a 6% floor are misled.",
     "fix": "Delete 'guaranteed', 'risk-free' and 'sleep at night'; replace with neutral wording that states the investment can lose value.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Compare page.md:3 against RICR 4.2 text; 'guaranteed' and 'risk-free' match the prohibited statements."},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "R",
     "location": "page.md:7",
     "scenario": "Page claims every page is approved by compliance before going live; the filed procedure says pages are not individually approved and only a 10% sample is reviewed after publication, so the firm publishes a false statement about its own controls.",
     "fix": "Delete the sentence, or describe the filed post-publication sample review accurately.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Read page.md:7 against compliance_procedure.md lines 3-4 ('not individually approved before they are published'); they contradict."},
    {"id": "S1", "status": "needs_validation", "track": "R", "location": "page.md:3",
     "suspicion": "'Steady Harbor holds high-grade bonds' may not reflect actual holdings.",
     "unresolved_fact": "Current portfolio holdings and investment policy (not supplied)."},
    {"id": "S2", "status": "needs_validation", "track": "R", "location": "page.md:5",
     "suspicion": "Performance presentation may need further RICR disclosures or may be a composite presented as 'our' return.",
     "unresolved_fact": "Performance methodology and full RICR text beyond 4.2/4.3/4.5."},
    {"id": "S3", "status": "needs_validation", "track": "R", "location": "page.md:9",
     "suspicion": "Applicability of RICR 4.5 depends on whether this is a managed account.",
     "unresolved_fact": "Whether the Steady Harbor Income Portfolio is a managed account (sentence is present regardless)."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "The 7.1% five-year average does not reproduce from performance.csv.",
     "evidence": "Arithmetic mean 35.5/5 = 7.1%; geometric (1.4082)^(1/5) is about 7.09%; both round to 7.1% over 2021-2025."},
    {"id": "R2", "candidate": "Page omits RICR 4.3 net-of-fees and past-performance statements.",
     "evidence": "page.md:5 says 'net of fees' and 'Past performance does not predict future results.' verbatim."},
    {"id": "R3", "candidate": "Page omits the RICR 4.5 required sentence.",
     "evidence": "page.md:9 carries 'Compare this information with your official account statement.' verbatim."}
  ]
}
```