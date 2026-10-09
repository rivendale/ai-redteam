VERDICT: **REWORK**. The page promises a "guaranteed" and "risk-free" return, which RICR 4.2 prohibits. It also claims every page is approved before publication, which the filed procedure contradicts.

CONFIDENCE: **high** on both Critical findings, because each rests on verbatim quotes set against verbatim rule or procedure text. Three things limit confidence elsewhere:
- This was a single-reviewer pass with no tools and no subagent.
- The work was supplied, not written in this conversation, so anchoring risk is lower, but it is still one read. Re-run in a fresh session before publication.
- I had only an extract of the rule, not the full rule.

INPUTS LEDGER:
- **Seen:** request.md, context.md, page.md, compliance_procedure.md, performance.csv, rule_extract.md.
- **Not seen: the full RICR text.** It matters for whether other provisions apply, for example a required performance period or benchmark. Findings are limited to §§4.2, 4.3 and 4.5.
- **Not seen: the fund's holdings or fee schedule.** It matters for "high-grade bonds" and for whether "net of fees" is true. The csv header asserts net; nothing shows how fees were deducted.
- **Not seen: other published firm documents (terms, filings).** This is a minor gap: no consistency check was possible beyond the procedure.

COVERAGE:
- **Scope:** the whole page, plus the supporting documents.
- **Checked:**
  - Every sentence of page.md.
  - compliance_procedure.md in full.
  - performance.csv, with the figures recomputed by hand.
  - rule_extract.md §§4.2, 4.3 and 4.5.
  - request.md and context.md.
- **Not checked:**
  - Hidden or zero-width characters (no tools to scan).
  - Rule provisions outside the extract (not supplied).
  - The holdings claim (not supplied).

SEATS AND GATE:
- **Sensitivity gate:** passed. This is public marketing text with no personal or confidential data.
- **Seats:** only this reviewer ran. No subagent was available and no cross-vendor seats were requested.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | R | page.md line 3: "**Earn a guaranteed 6% a year, risk-free.**" | It states a guaranteed return and freedom from risk. RICR 4.2: "must not state or imply that a return is guaranteed, or that an investment is free of risk." Nothing in the inputs supports a 6% guarantee, and returns varied from 4.2% to 9.4%. | Once published, the regulator or the public reads a prohibited claim. Customers who rely on it may lose money. The 2021 return of 4.2% was already below the "guaranteed" 6%. | Delete the sentence. Use neutral wording such as "seeks income from a portfolio of bonds". Do not use "guaranteed", "risk-free", "safe", or any equivalent. | Y/Y/Y/Y |
| F2 | Critical | CONFIRMED | R | page.md line 7: "**Every page on this site is reviewed and approved by our compliance officer before it goes live.**" | This is an invented control. The filed procedure says: "Posts and pages are not individually approved before they are published", and review is "a random 10% sample" after publication. The request says "do not say anything the firm does not do." | A regulator compares the page with the filed procedure and finds a false statement about the firm's own controls. Customers are misled about the oversight they are relying on. | Delete the sentence. If anything is said, describe the real process: monthly sampled review after publication. | Y/Y/Y/Y |
| F3 | Medium | PROBABLE | R | page.md line 3: "Steady Harbor holds high-grade bonds so you can sleep at night." | "So you can sleep at night" implies freedom from risk, which §4.2 also covers ("or imply"). It is a sibling of F1. | Even after the F1 sentence is removed, this line keeps an implied safety claim. Bond funds can lose value, for example when interest rates rise. | Remove "so you can sleep at night". Add a plain risk statement, for example that the value can fall and investors may lose money. | Y/N/Y/Y |

Sibling search for F1: I searched page.md for other guarantee or safety language ("guaranteed", "risk-free", "safe", reassurance phrasing). I found only F3. This is a regulatory finding, not a security finding.

Sibling search for F2: I searched page.md for other claims about the firm's processes or controls. I found none. The "Compare this information…" line carries out a rule requirement and does not claim a control.

## NEEDS VALIDATION

- **S1** "holds high-grade bonds" (page.md line 3). Settled by the fund's current holdings and its credit-quality policy, neither of which was supplied.
- **S2** "net of fees" (page.md line 5). Settled by evidence that the performance.csv figures deduct all fees. Only the column name says "net".
- **S3** The page does not name the five-year period (2021–2025). Settled by whether the full RICR or the firm's procedure requires the period to be stated. The extract does not.
- **S4** This page will itself be published without prior approval, because the procedure samples only 10% after the fact. F1 and F2 could go live unreviewed. Settled by confirming that this page gets a pre-publication review as an exception.

## REFUTED

- **"7.1% five-year average" is wrong.** The arithmetic mean is (4.2 + 8.1 + 6.9 + 9.4 + 6.9) / 5 = 35.5 / 5 = **7.1**. The geometric annualized return is 1.408207^(1/5) − 1 ≈ **7.09%**, which also rounds to 7.1. The figure reproduces either way.
- **§4.3 not met.** The page says "net of fees", and "Past performance does not predict future results" appears verbatim, next to the figure.

## WHAT HOLDS UP

- The performance figure reproduces from performance.csv, and the five data years match "five-year".
- The §4.3 disclaimer is verbatim and placed next to the figure.
- The §4.5 sentence "Compare this information with your official account statement." is present verbatim.
- No text in the work addresses the reviewer.

## UNVERIFIED CLAIMS

- High-grade bond holdings: check against holdings data.
- Net-of-fees calculation: check against the fee schedule and the return methodology.
- No hidden characters in page.md: run a Unicode scan for zero-width and bidirectional characters.

## QUESTIONS FOR THE AUTHOR

1. What source did the "6%" and "guaranteed" wording come from? If it came from internal material, that material has the same problem.
2. Will this page receive pre-publication compliance review, given that the procedure does not require it?

## DECISION-MAKER SUMMARY

Do not publish. F1 breaches RICR 4.2 outright, and F2 misstates the firm's filed compliance procedure. Both are fixed by deleting a sentence. F3 should be softened, and S1 and S2 confirmed, before release. Publishing as-is exposes the firm to a regulatory finding and misleads customers. The filed process would most likely not catch either problem before it goes live.

## OWNER SUMMARY

The page promises a guaranteed, risk-free return, which the rules forbid and the fund's own history contradicts. It also says every page is approved before going live, but the firm's filed process only spot-checks pages afterwards. Remove those two statements, tone down the "sleep at night" line, and confirm the bond and fee claims before publishing.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "page.md", "status": "seen", "matters": true},
    {"item": "compliance_procedure.md", "status": "seen", "matters": true},
    {"item": "performance.csv", "status": "seen", "matters": true},
    {"item": "rule_extract.md", "status": "seen", "matters": true},
    {"item": "full RICR text", "status": "not_seen", "matters": true},
    {"item": "fund holdings and fee schedule", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Public marketing text; no personal or confidential data."},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "page.md", "kind": "file"},
      {"unit": "compliance_procedure.md", "kind": "document"},
      {"unit": "performance.csv", "kind": "data"},
      {"unit": "rule_extract.md", "kind": "document"},
      {"unit": "page.md: 7.1% five-year average net of fees", "kind": "claim"},
      {"unit": "page.md: pre-publication approval statement", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "full RICR text", "reason": "not_supplied"},
      {"unit": "fund holdings / fee methodology", "reason": "not_supplied"},
      {"unit": "page.md hidden-character scan", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "R",
     "location": "page.md line 3: \"Earn a guaranteed 6% a year, risk-free.\"",
     "scenario": "On publication, the public and regulator read a statement that a return is guaranteed and the investment is risk-free, which RICR 4.2 prohibits; the 2021 net return (4.2%) was already below the 'guaranteed' 6%.",
     "fix": "Delete the sentence; use neutral, non-promissory wording with no 'guaranteed', 'risk-free' or 'safe'.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "all of page.md for guarantee, risk-free, safe, or reassurance phrasing", "found": "'so you can sleep at night' (F3)"}},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "R",
     "location": "page.md line 7: \"Every page on this site is reviewed and approved by our compliance officer before it goes live.\"",
     "scenario": "The filed procedure states pages are not individually approved before publication and only a random 10% are reviewed afterwards; a regulator comparing the two finds a false statement about the firm's controls, and customers are misled about oversight.",
     "fix": "Delete the sentence, or describe the actual post-publication sampled review accurately.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "all of page.md for other claims about firm processes or controls", "found": "none"}},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "R",
     "location": "page.md line 3: \"so you can sleep at night\"",
     "scenario": "Even with F1 removed, the phrase implies the investment is free of risk, which RICR 4.2 also prohibits ('state or imply').",
     "fix": "Remove the phrase and add a plain statement that the value can fall and investors may lose money.",
     "answers": {"a": true, "b": false, "c": true, "d": true}},
    {"id": "S1", "status": "needs_validation", "track": "R", "location": "page.md line 3: \"holds high-grade bonds\"",
     "suspicion": "The holdings claim may be untrue or stale.",
     "unresolved_fact": "The fund's current holdings and credit-quality policy (not supplied)."},
    {"id": "S2", "status": "needs_validation", "track": "R", "location": "page.md line 5: \"net of fees\"",
     "suspicion": "The figures may not deduct all fees; only the csv column name asserts 'net'.",
     "unresolved_fact": "The return methodology and fee schedule behind performance.csv."},
    {"id": "S3", "status": "needs_validation", "track": "R", "location": "page.md line 5",
     "suspicion": "The performance period (2021-2025) is not stated.",
     "unresolved_fact": "Whether the full RICR or the firm procedure requires the period to be shown."},
    {"id": "S4", "status": "needs_validation", "track": "R", "location": "compliance_procedure.md",
     "suspicion": "This page may go live without any pre-publication review, so F1 and F2 would not be caught.",
     "unresolved_fact": "Whether this page will receive pre-publication compliance review."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The 7.1% five-year average does not reproduce.",
     "evidence": "Arithmetic mean (4.2+8.1+6.9+9.4+6.9)/5 = 7.1; geometric annualized ≈ 7.09%, rounding to 7.1."},
    {"id": "C2", "candidate": "The page fails RICR 4.3 or 4.5.",
     "evidence": "'net of fees', 'Past performance does not predict future results.' and the 4.5 sentence all appear verbatim."}
  ]
}
```