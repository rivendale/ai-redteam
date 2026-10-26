# Redteam review: Steady Harbor Income Portfolio page

**VERDICT: REWORK.** The page breaks RICR 4.2 in its headline and makes a claim about compliance approval that the firm's own filed procedure contradicts. Both are Critical, and both break the request's instruction not to say anything the firm does not do.

**CONFIDENCE: medium.**
- I had no tools, so I could not open sources, run code or check holdings. I did recompute the numbers by hand.
- The rule is an extract, so other RICR paragraphs could add requirements I could not check.
- The work was supplied as files, not written in this conversation, so anchoring risk is low.

**INPUTS LEDGER:**

| Item | Status | Does the gap matter? |
|---|---|---|
| request.md, context.md, page.md, compliance_procedure.md, performance.csv, rule_extract.md | Seen | — |
| Full RICR text (only 4.2, 4.3 and 4.5 supplied) | Not seen | Yes. Other paragraphs could add requirements, such as the performance period or benchmark. |
| Portfolio holdings or investment policy (needed to back "holds high-grade bonds") | Not seen | Yes, for that one claim. |
| Fee basis behind `net_return_pct` (which fees, gross-to-net method) | Not seen | Partly. The page says "net of fees", but only a column name supports it. |
| Whether this product is a "managed account" under 4.5 | Not seen | No. The sentence is present either way. |

**COVERAGE:**
- Scope: the whole page, checked against the rule extract and the filed procedure.
- Checked: all six supplied files; every sentence of page.md; RICR 4.2, 4.3 and 4.5; the performance arithmetic.
- Not checked: the rest of RICR (not supplied); holdings (not supplied); fee methodology (not supplied); the rest of the site (out of scope).

**SEATS AND GATE:**
- Reviewer: a single local reviewer, with no subagent and no tools.
- Sensitivity: no personal, client or credential data, so the gate passed.
- No cross-vendor seats were run (not requested; standard depth).

## Claims to evidence

| Label | Location and wording | Support | Status |
|---|---|---|---|
| C1 | page.md:3 "Earn a guaranteed 6% a year, risk-free." | None. RICR 4.2 prohibits it. performance.csv shows 2021 at 4.2%, below 6%. | Contradicted by the rule and by the firm's own data → F1 |
| C2 | page.md:3 "holds high-grade bonds" | No holdings data supplied | UNVERIFIED → S1 |
| C3 | page.md:3 "so you can sleep at night" | None | Interpretation: implies freedom from risk → F3 |
| C4 | page.md:5 "five-year average return was 7.1% a year, net of fees" | See the derivation below | Derived value; reproduces. Fee basis UNVERIFIED → S2 |
| C5 | page.md:5 "Past performance does not predict future results." | RICR 4.3 | Verified present |
| C6 | page.md:7 "Every page … reviewed and approved by our compliance officer before it goes live." | compliance_procedure.md: "Posts and pages are not individually approved before they are published", plus a 10% monthly sample after publication | Contradicted by the filed procedure → F2 |
| C7 | page.md:9 "Compare this information with your official account statement." | RICR 4.5 | Verified verbatim |

**C4 derivation:**
- Inputs: performance.csv, 2021–2025, five yearly net returns in percent.
- Arithmetic mean: (4.2 + 8.1 + 6.9 + 9.4 + 6.9) / 5 = 35.5 / 5 = **7.1%**.
- Geometric (annualized) mean: the five years compound to a factor of about 1.4082, which is about **7.09% a year**.
- Both reproduce 7.1%. There is no benchmark and no stated time window on the page.

## Findings, ordered by severity

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | R | page.md:3 | Says a return is "guaranteed" and the investment is "risk-free". RICR 4.2 prohibits both. The firm's own record (2021: 4.2%) shows 6% was not even achieved every year. | A regulator or customer reads the headline. That is a direct 4.2 breach, and an investor relies on a guarantee that does not exist and loses money or income. | Delete "guaranteed" and "risk-free". State the objective without promising it, and name the main risks (interest-rate and credit risk). | Y/Y/Y/Y |
| F2 | Critical | CONFIRMED | R | page.md:7 vs compliance_procedure.md, lines 3–4 | Describes a pre-publication approval control that the filed procedure says does not operate. Pages are sampled at 10% after publication and are not individually approved. | A regulator compares the page with the filed procedure and finds a false statement about the firm's controls. Readers are told the content was vetted when it may never be reviewed. This is the request's "do not say anything the firm does not do" breached outright. | Delete the sentence. Do not describe the review process unless the description matches the filed procedure word for word. | Y/Y/Y/Y |
| F3 | High | PROBABLE | R | page.md:3 "so you can sleep at night" | Implies freedom from risk. RICR 4.2 also covers "imply". This is a sibling of F1 that survives if only the two words "guaranteed" and "risk-free" are removed. | Someone removes the two words but keeps this phrase. The page still implies safety and still breaches 4.2. | Remove the phrase or replace it with neutral description. | Y/N/Y/Y |

No reproduction field is needed: this is Track R, not Track B. The bad text is quoted at each location.

**Sibling search for F1 and F3:**
- I searched every sentence of page.md for wording that states or implies a guarantee or safety.
- Found: "guaranteed" and "risk-free" (F1) and "sleep at night" (F3).
- "high-grade" is a factual quality claim rather than a safety promise. It is handled under S1.

**Sibling search for F2:**
- I searched page.md for any other statement about firm processes or controls.
- Found none besides line 7.

None of these are security findings.

## Needs validation (no severity)

- **S1:** page.md:3 "holds high-grade bonds". What settles it: the current holdings or the investment policy showing the credit-quality limits the portfolio actually follows.
- **S2:** page.md:5 "net of fees". What settles it: the methodology behind `net_return_pct`, including which fees were deducted and whether they are actual or model fees.
- **S3:** whether RICR paragraphs not supplied (for example 4.1 and 4.4) add requirements, such as a stated period, a benchmark, or which kind of average to use. What settles it: the full rule text.

## Refuted

- **R1:** "The 7.1% figure is wrong." It reproduces exactly as an arithmetic mean (35.5 / 5) and to within rounding as a geometric mean (7.09%).
- **R2:** "The page fails RICR 4.3." It states net of fees and carries the past-performance statement.
- **R3:** "The page fails RICR 4.5." The required sentence is present verbatim at page.md:9.

## What holds up

- The 7.1% figure matches the supplied data.
- The 4.3 disclosures (net of fees, past-performance statement) are present.
- The 4.5 sentence is present verbatim.

## Unverified claims

- "holds high-grade bonds": confirm against holdings (S1).
- "net of fees": confirm against the fee methodology (S2).

## Questions for the author

1. Can you supply the holdings or investment policy that support "high-grade bonds"?
2. Does the full RICR have rules on performance periods or benchmarks?
3. Given the filed procedure, does anyone review this page before it goes live, or would it only be caught if it lands in the 10% sample?

## Decision-maker summary

Do not publish. The headline promises a guaranteed, risk-free return, which the rule prohibits and the firm's own 2021 return disproves. The page also claims a pre-publication approval step that the filed procedure says does not exist. Under that procedure the page might never be sampled, so these breaches could stay live and visible to the regulator.

## Owner summary

The page promises a guaranteed, risk-free return, which the rules forbid and the firm's own history contradicts. It also says every page is approved before going live, but the firm's official procedure says that does not happen. Remove those statements and confirm the bond-quality claim before anything is published.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "page.md", "status": "seen", "matters": true},
    {"item": "compliance_procedure.md", "status": "seen", "matters": true},
    {"item": "performance.csv", "status": "seen", "matters": true},
    {"item": "rule_extract.md", "status": "seen", "matters": true},
    {"item": "full RICR text", "status": "not_seen", "matters": true},
    {"item": "portfolio holdings / investment policy", "status": "not_seen", "matters": true},
    {"item": "net return fee methodology", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "local-reviewer", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "page.md", "kind": "document"},
      {"unit": "compliance_procedure.md", "kind": "document"},
      {"unit": "rule_extract.md", "kind": "document"},
      {"unit": "performance.csv", "kind": "data"},
      {"unit": "C4: 7.1% five-year net average", "kind": "claim"},
      {"unit": "C6: pre-publication approval", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "full RICR text", "reason": "not_supplied"},
      {"unit": "portfolio holdings", "reason": "not_supplied"},
      {"unit": "fee methodology", "reason": "not_supplied"},
      {"unit": "other site pages", "reason": "out_of_scope"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "R",
     "location": "page.md:3 \"Earn a guaranteed 6% a year, risk-free.\"",
     "scenario": "A regulator or customer reads the headline; it states a guaranteed return and no risk, breaching RICR 4.2, and the firm's own 2021 net return of 4.2% shows 6% was not achieved every year.",
     "fix": "Remove 'guaranteed' and 'risk-free'; state the objective without promising it and name the main risks.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "every sentence of page.md for stated or implied guarantee or safety wording",
                           "found": "'sleep at night' (F3); no others"}},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "R",
     "location": "page.md:7 vs compliance_procedure.md:3-4",
     "scenario": "The page claims every page is approved before going live; the filed procedure says pages are not individually approved and only a 10% post-publication sample is reviewed. A regulator finds a false description of the firm's controls.",
     "fix": "Delete the sentence; describe review only if it matches the filed procedure exactly.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "page.md for any other statement about firm processes or controls",
                           "found": "none"}},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "R",
     "location": "page.md:3 \"so you can sleep at night\"",
     "scenario": "If only 'guaranteed' and 'risk-free' are removed, this phrase still implies the investment is free of risk, which RICR 4.2 also prohibits.",
     "fix": "Remove the phrase or replace it with neutral, factual description.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "page.md for implied-safety wording",
                           "found": "F1 wording only; 'high-grade' handled as S1"}},
    {"id": "S1", "status": "needs_validation", "track": "R", "location": "page.md:3 \"holds high-grade bonds\"",
     "suspicion": "Holdings claim has no supporting evidence.",
     "unresolved_fact": "Current holdings or investment policy showing the credit-quality limits actually applied."},
    {"id": "S2", "status": "needs_validation", "track": "R", "location": "page.md:5 \"net of fees\"",
     "suspicion": "Net-of-fees basis rests only on a CSV column name.",
     "unresolved_fact": "Fee methodology behind net_return_pct (fees deducted; actual vs model)."},
    {"id": "S3", "status": "needs_validation", "track": "R", "location": "rule_extract.md (extract only)",
     "suspicion": "Unsupplied RICR paragraphs may impose further performance-presentation requirements.",
     "unresolved_fact": "Full RICR text."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "The 7.1% five-year average is wrong.",
     "evidence": "Arithmetic mean (4.2+8.1+6.9+9.4+6.9)/5 = 7.1; geometric mean is about 7.09%."},
    {"id": "R2", "candidate": "The page omits RICR 4.3 disclosures.",
     "evidence": "page.md:5 states net of fees and 'Past performance does not predict future results.'"},
    {"id": "R3", "candidate": "The page omits the RICR 4.5 sentence.",
     "evidence": "page.md:9 carries it verbatim."}
  ]
}
```