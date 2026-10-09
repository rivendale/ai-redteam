VERDICT: **SHIP.** The page meets RICR 4.2, 4.3 and 4.5, its figures reproduce from `performance.csv`, and its description of the review process matches the filed procedure. One factual claim about holdings should be confirmed before publication.

CONFIDENCE: **medium.** This was a single reviewer with no tools and no subagent; the work was not written in this session. Only an extract of the rule was supplied. Nothing documents what the portfolio holds.

INPUTS LEDGER:
- **Seen:** `request.md`, `context.md`, `page.md`, `compliance_procedure.md`, `performance.csv`, `rule_extract.md`.
- **Not seen:** the full RICR text. It matters somewhat, because other paragraphs might impose more duties.
- **Not seen:** any holdings or mandate document. This matters for the claim "holds high-grade bonds".
- **Not seen:** whether the product is a managed account. This does not matter, because carrying the 4.5 sentence anyway does no harm.

COVERAGE:
- **Scope:** the whole page, checked against the rule extract, the procedure and the performance data.
- **Checked:**
  - all four supplied files plus `request.md` and `context.md`;
  - each sentence of `page.md`;
  - RICR 4.2, 4.3 and 4.5;
  - the arithmetic of the returns.
- **Not checked:** RICR paragraphs beyond the extract (not supplied), and the portfolio's holdings (not supplied).

SEATS AND GATE:
- **Sensitivity:** none found. The material is public marketing text and aggregate returns.
- **Seats:** only a local same-session reviewer ran. No subagent tool was available, and no cross-vendor seat was requested.

FINDINGS: none confirmed.

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| — | — | — | — | — | No confirmed findings | — | — | — |

NEEDS VALIDATION:
- **S1** (`page.md` line 3, "Steady Harbor holds high-grade bonds"): no supplied document shows what the portfolio holds. The request says "do not say anything the firm does not do".
  - **What settles it:** the portfolio's mandate or current holdings report, showing investment-grade bonds only.

REFUTED:
- **"Steady" and "steady income" imply a guaranteed return (4.2).** The same paragraph says "you can lose money", "the value… can fall as well as rise" and "no return is guaranteed". "Aims for" states an objective, not a promise.
- **The 7.1% average is wrong or overstated.**
  - The simple average is (4.2 + 8.1 + 6.9 + 9.4 + 6.9) / 5 = 35.5 / 5 = 7.1.
  - The compound rate is 1.042 × 1.081 × 1.069 × 1.094 × 1.069 ≈ 1.4082, and 1.4082^(1/5) ≈ 1.0709, which also rounds to 7.1%.
  - Both methods give the same rounded figure, so the unstated method does not mislead.
- **The page describes a control that does not operate.** The page says a random 10% monthly sample is reviewed and pages are not approved individually before publication. That matches `compliance_procedure.md` exactly, and the page admits the absence of pre-approval rather than claiming it.
- **Performance is shown without fees deducted or without the required sentence (4.3).** The page says "net of fees", the CSV column is `net_return_pct`, and "Past performance does not predict future results." is verbatim.
- **The required 4.5 sentence is missing or altered.** "Compare this information with your official account statement." is verbatim.
- **The yearly figures are mis-transcribed.** All five match the CSV.

WHAT HOLDS UP:
- The risk disclosure.
- Net-of-fees performance that reproduces from the data.
- Both mandatory sentences, quoted verbatim.
- A description of the review procedure that is honest and matches the filed procedure, with no invented pre-approval gate.

UNVERIFIED CLAIMS:
- "Holds high-grade bonds": confirm against the mandate or the latest holdings report.
- Compliance with RICR paragraphs outside the extract: confirm against the full rule.

QUESTIONS FOR THE AUTHOR:
1. Which document supports "high-grade bonds"?
2. Does any RICR paragraph outside the extract apply, such as rules on the performance period or benchmarks?

DECISION-MAKER SUMMARY: The page complies with the rule paragraphs supplied and does not overstate the firm's review process. Confirm the "high-grade bonds" claim against the holdings before publishing. If you publish without that check, an inaccurate claim about holdings could break the "say nothing the firm does not do" requirement.

OWNER SUMMARY: The page is accurate and follows the rules we were given. Its return figures add up and its required warnings are worded exactly as required. Before it goes live, someone should confirm that the portfolio really holds only high-grade bonds, as the page says.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "full RICR text", "status": "not_seen", "matters": true},
    {"item": "portfolio holdings or mandate", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "page.md", "kind": "document"},
      {"unit": "compliance_procedure.md", "kind": "document"},
      {"unit": "performance.csv", "kind": "data"},
      {"unit": "rule_extract.md", "kind": "document"},
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "page.md: 7.1% average and yearly figures", "kind": "claim"},
      {"unit": "page.md: review procedure description", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "full RICR text", "reason": "not_supplied"},
      {"unit": "portfolio holdings", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "S1", "status": "needs_validation", "track": "R", "location": "page.md:3",
     "suspicion": "The claim that the portfolio holds high-grade bonds has no supporting document.",
     "unresolved_fact": "Whether the mandate or holdings report shows investment-grade bonds only."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Steady/steady income implies a guarantee (RICR 4.2).", "evidence": "The same paragraph states you can lose money and no return is guaranteed; 'aims for' is an objective."},
    {"id": "C2", "candidate": "The 7.1% average is wrong.", "evidence": "The arithmetic mean is 35.5/5 = 7.1; the geometric mean is ~7.09%, which rounds to 7.1%."},
    {"id": "C3", "candidate": "The page describes a review control that does not operate.", "evidence": "The page wording matches compliance_procedure.md (10% monthly sample, no pre-approval)."},
    {"id": "C4", "candidate": "The 4.3 or 4.5 required statements are missing or altered.", "evidence": "Both sentences appear verbatim; the figures are stated net of fees and match performance.csv."}
  ]
}
```