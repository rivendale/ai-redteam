# Redteam review: Steady Harbor Income Portfolio web page

**VERDICT: REWORK.** The page breaks RICR 4.2 in its headline, and it claims a pre-publication approval step that the firm's own filed procedure says does not happen.

**CONFIDENCE: medium.** I had no tools and no fresh subagent, so this is a single-reviewer pass. The work was not written in this conversation, so the author's reasoning did not anchor me. The supplied rule is only an extract, so other RICR paragraphs could add requirements I cannot see. The two blocking findings rest on exact quotes and do not depend on anything missing.

**INPUTS LEDGER**
- **Seen:** request.md, context.md, page.md, compliance_procedure.md, performance.csv, rule_extract.md.
- **Not seen:**
  - The full RICR text. This matters, because paragraphs other than 4.2, 4.3 and 4.5 may impose further requirements.
  - The portfolio's holdings. This matters for the "high-grade bonds" claim.
  - The fee schedule and how "net of fees" was computed. This matters for the 7.1% figure.
  - Whether the portfolio is a "managed account" under RICR. This does not matter, because the 4.5 sentence is present either way.

**COVERAGE**
- **Scope:** the whole page, checked against the request, the rule extract, the filed procedure and the performance data.
- **Checked:**
  - Every sentence of page.md.
  - RICR 4.2, 4.3 and 4.5.
  - The filed procedure.
  - performance.csv. I recomputed the average by hand.
- **Not checked:**
  - RICR paragraphs outside the extract (not supplied).
  - Holdings and fee data (not supplied).

**SEATS AND GATE**
- **Gate:** no personal or confidential data. The page is public-facing and the procedure is a filed document.
- **Seats:** only the local reviewer ran. No subagent or cross-vendor seat was available in this session, so none were refused on sensitivity grounds.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | R | page.md, headline: "**Earn a guaranteed 6% a year, risk-free.**" | This states a guaranteed return and freedom from risk. RICR 4.2: "must not state or imply that a return is guaranteed, or that an investment is free of risk." The firm's own data also contradicts it: 2021 net return was 4.2%, below the "guaranteed" 6%. | The page goes live, and a regulator or a customer reads a prohibited guarantee. A customer who earns under 6% in any year (as in 2021) has a documented misrepresentation claim. | Delete the sentence. Replace it with a neutral description of the strategy, with no return promise and no safety claim. | y/y/y/y |
| F2 | Critical | CONFIRMED | R | page.md: "**Every page on this site is reviewed and approved by our compliance officer before it goes live.**" | This invents a control. The filed procedure says: "Posts and pages are not individually approved before they are published", and review is a monthly 10% sample after publication. The request explicitly said "do not say anything the firm does not do." | A regulator compares the page with the filed procedure and finds a public misstatement of the firm's own compliance controls. This sentence itself would be published without approval, which disproves it the day it goes live. | Delete the sentence, or replace it with an accurate description consistent with the filing. Deleting is safer: the page does not need to describe internal review. | y/y/y/y |
| F3 | Medium | PROBABLE | R | page.md: "so you can sleep at night" | Even after "risk-free" is removed, this phrase still implies safety. RICR 4.2 forbids *implying* that an investment is free of risk. | A reader takes "sleep at night" as an assurance of no loss. A bond portfolio can still lose value through rate and credit risk. | Remove the phrase, or pair any reference to the strategy with a plain statement that the value can fall. | y/n/y/n |

**Severity rationale for F3.** Whether this phrase alone would be read as "free of risk" is a judgment call, so I rated it PROBABLE and not likely enough to rate High.

**Siblings searched (F1, F2).**
- **F1:** I searched every sentence of the page for guarantee, safety or no-loss language. Found "sleep at night" (F3). "high-grade bonds" describes holdings rather than promising safety, so I did not raise it under 4.2; see needs-validation below.
- **F2:** I searched for any other statement about the firm's processes or controls. Found none.
- Neither finding is a security finding.

## NEEDS VALIDATION
- **"holds high-grade bonds":** whether the portfolio's actual holdings meet a defined "high-grade" standard. This is settled by the holdings report and the firm's definition of the term.
- **Other RICR requirements:** whether paragraphs outside the extract require more, such as naming the performance period, the calculation method or a benchmark. This is settled by the full rule text.
- **"net of fees":** whether the CSV figures are actually net of all fees. This is settled by the fee schedule and the performance calculation workpapers.

## REFUTED
- **"7.1% average does not reproduce."** It does. The arithmetic mean of 4.2, 8.1, 6.9, 9.4 and 6.9 is 35.5 / 5 = 7.1. The compounded annualized figure is (1.042 × 1.081 × 1.069 × 1.094 × 1.069)^(1/5) − 1 ≈ 1.4082^0.2 − 1 ≈ 7.09%, which also rounds to 7.1. The figure holds under either method.
- **"Missing RICR 4.3 or 4.5 statements."** Both are present. The page says "net of fees" and carries "Past performance does not predict future results." The 4.5 sentence appears verbatim.

## WHAT HOLDS UP
- The 7.1% figure, net-of-fees framing and past-performance statement satisfy 4.3 and reproduce from the data.
- The required 4.5 sentence is present word for word.

## UNVERIFIED CLAIMS
- "high-grade bonds": confirm against the holdings.
- "net of fees": confirm against the fee schedule.

## QUESTIONS FOR THE AUTHOR
1. Where did the 6% figure come from? Is there any contractual floor? If not, the claim is false as well as prohibited.
2. What is the source for "high-grade"?

## DECISION-MAKER SUMMARY
Do not publish. F1 is a direct RICR 4.2 violation, and F2 contradicts the firm's filed procedure. Both are one-sentence deletions, after which the page is close to compliant. Publishing as is exposes the firm to regulatory action and customer claims from the first day.

## OWNER SUMMARY
The page promises a guaranteed, risk-free return, which the rules forbid and which the fund's own history shows is not true. It also says every page is approved by compliance before publication, when the firm's filed procedure says pages are only spot-checked afterwards. Remove those two sentences and soften the "sleep at night" line before the page goes live.

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
    {"item": "portfolio holdings", "status": "not_seen", "matters": true},
    {"item": "fee schedule / net-of-fees workpapers", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "local-reviewer", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "public marketing page and filed procedure; no personal or confidential data"},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "page.md", "kind": "file"},
      {"unit": "compliance_procedure.md", "kind": "document"},
      {"unit": "performance.csv", "kind": "data"},
      {"unit": "rule_extract.md", "kind": "document"},
      {"unit": "page.md: 7.1% five-year average", "kind": "claim"},
      {"unit": "page.md: pre-publication approval statement", "kind": "claim"},
      {"unit": "page.md: guaranteed 6% risk-free", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "RICR paragraphs outside the extract", "reason": "not_supplied"},
      {"unit": "portfolio holdings (high-grade claim)", "reason": "not_supplied"},
      {"unit": "fee schedule", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "R",
     "location": "page.md headline: \"Earn a guaranteed 6% a year, risk-free.\"",
     "scenario": "Published page states a guaranteed return and no risk, which RICR 4.2 prohibits; the firm's own data shows a 4.2% year (2021), so the guarantee is also false, exposing the firm to regulatory action and customer misrepresentation claims.",
     "fix": "Delete the sentence; replace with a neutral strategy description with no return promise or safety claim.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "every sentence of page.md for guarantee, safety or no-loss wording", "found": "\"so you can sleep at night\" (F3)"}},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "R",
     "location": "page.md: \"Every page on this site is reviewed and approved by our compliance officer before it goes live.\"",
     "scenario": "The filed procedure says pages are not individually approved before publication and only a monthly 10% sample is reviewed afterwards; a regulator comparing the page to the filing finds a public misstatement of the firm's controls, contrary to the request's 'do not say anything the firm does not do'.",
     "fix": "Delete the sentence, or replace it with wording consistent with the filed procedure.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "every sentence of page.md for statements about firm processes or controls", "found": "none other"}},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "R",
     "location": "page.md: \"so you can sleep at night\"",
     "scenario": "Even with 'risk-free' removed, the phrase implies the investment carries no meaningful risk, which RICR 4.2 forbids implying; bond portfolios can lose value through rate and credit risk.",
     "fix": "Remove the phrase or pair the strategy description with a plain statement that value can fall.",
     "answers": {"a": true, "b": false, "c": true, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "R", "location": "page.md: \"holds high-grade bonds\"",
     "suspicion": "Holdings claim may not be substantiated.",
     "unresolved_fact": "Whether the portfolio's holdings meet a defined high-grade standard (holdings report not supplied)."},
    {"id": "S2", "status": "needs_validation", "track": "R", "location": "page.md performance paragraph",
     "suspicion": "Full RICR may require more (named period, calculation method, benchmark).",
     "unresolved_fact": "Text of RICR paragraphs outside 4.2, 4.3, 4.5."},
    {"id": "S3", "status": "needs_validation", "track": "C", "location": "performance.csv / page.md \"net of fees\"",
     "suspicion": "Returns may not be net of all fees.",
     "unresolved_fact": "Fee schedule and performance calculation workpapers."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The 7.1% five-year average does not reproduce from performance.csv.",
     "evidence": "Arithmetic mean 35.5/5 = 7.1; compounded annualized ≈ 7.09%, rounds to 7.1."},
    {"id": "C2", "candidate": "Page omits RICR 4.3 or 4.5 required statements.",
     "evidence": "Page says 'net of fees', carries 'Past performance does not predict future results.', and the 4.5 sentence verbatim."}
  ]
}
```