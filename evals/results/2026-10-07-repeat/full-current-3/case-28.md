**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No tools or subagent were available in this session, so I checked everything below by reading the supplied text and doing the arithmetic by hand.

VERDICT: **REWORK.** The page breaks RICR 4.2 in its headline and describes a pre-publication approval control that the firm's filed procedure says does not exist.

CONFIDENCE: **medium.** Both Critical findings are tied to exact quotes, so they are solid. Confidence is limited because this is a same-context review with no tools, and only an extract of the RICR was supplied.

INPUTS LEDGER:
- **Seen:** request.md, context.md, page.md, compliance_procedure.md, performance.csv, rule_extract.md.
- **Not seen: the full RICR text.** This matters. Other paragraphs could impose more requirements, such as prominence, benchmark rules or period disclosure, and the extract cannot rule that out.
- **Not seen: any record of the portfolio's holdings or mandate.** This matters for the "high-grade bonds" claim (finding 4).
- **Not seen: whether Steady Harbor is a "managed account" under 4.5.** This does not matter. The required sentence is present either way.
- **Note:** compliance_procedure.md was listed under "work under review", but it is a filed source document. I treated it as an input, not as text to be published.

SEATS AND GATE:
- **Seats:** a single same-context reviewer ran. No subagent or cross-vendor seats were available.
- **Gate:** no personal, client or confidential data was found, so the sensitivity gate passed.

FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | R | page.md headline: "Earn a guaranteed 6% a year, risk-free." | This states a guaranteed return and freedom from risk. RICR 4.2 prohibits both. The firm's own record also contradicts it: 2021 net return was 4.2%, below the "guaranteed" 6%. | When the page is published, the regulator reads a direct 4.2 breach. A customer relies on the guarantee, the 6% is not met (as already happened in 2021), and the customer is harmed. | Delete the guarantee and "risk-free". Replace them with a neutral description of the strategy and a plain statement that the value can fall and returns are not guaranteed. | confirmed. No reading of "guaranteed … risk-free" avoids 4.2. |
| 2 | Critical | CONFIRMED | R | page.md: "Every page on this site is reviewed and approved by our compliance officer before it goes live." vs compliance_procedure.md: "Posts and pages are not individually approved before they are published." | This is an invented control. The page claims every page is approved before publication. The filed procedure is a monthly review of a 10% sample, done after publication. The request also says "do not say anything the firm does not do". | Publishing a false statement about compliance controls that contradicts a filed document exposes the firm to a misleading-communication finding. Customers would also trust page content on the basis of a review that never happened. | Remove the sentence. If a statement is wanted, describe the filed process accurately (monthly sampled review after publication), or say nothing. | confirmed. The two texts directly contradict each other. |
| 3 | Medium | PROBABLE | R | page.md: "so you can sleep at night" | This implies safety or absence of worry, and it sits right next to the guarantee language. Even once finding 1 is fixed, it can still be read as implying freedom from risk under 4.2. | A regulator reads the phrase as an implied no-risk claim. | Remove it, or replace it with a factual description of the strategy. | n/a |
| 4 | Medium | UNVERIFIED | R/C | page.md: "Steady Harbor holds high-grade bonds" | No supplied input supports this holdings claim. Under the request's "do not say anything the firm does not do", it needs a source. | If the portfolio holds lower-grade or non-bond assets, the page misstates what the portfolio holds. | Check the claim against the portfolio mandate or holdings report, cite the definition of "high-grade", or remove the claim. | n/a |
| 5 | Low | CONFIRMED | C | page.md: "five-year average return was 7.1% a year" | The figure reproduces (details below), but the page does not state the period (2021–2025) or the method (arithmetic or annualized). | A reader cannot tell what period the figure covers. It also goes stale after 2026 results come in. | Add "2021–2025, annualized" or equivalent and an as-of date. Check the full RICR for any period-disclosure rule. | n/a |

Arithmetic behind finding 5, which reproduces the 7.1% either way:
- The arithmetic mean is (4.2+8.1+6.9+9.4+6.9)/5 = 35.5/5 = 7.10%.
- The compounded annualized figure is (1.042·1.081·1.069·1.094·1.069)^(1/5) − 1 ≈ 7.09%.

WHAT HOLDS UP:
- **The 7.1% figure:** it is net of fees as 4.3 requires, and it reproduces from performance.csv under both methods.
- **The past-performance sentence:** it is present and matches 4.3.
- **The 4.5 sentence:** "Compare this information with your official account statement." is present verbatim.

UNVERIFIED CLAIMS:
- **"high-grade bonds":** check it against the mandate or holdings report.
- **Completeness against the full RICR:** obtain the full rule text and check for requirements beyond 4.2, 4.3 and 4.5.

QUESTIONS FOR THE AUTHOR:
1. What source supports "high-grade bonds"?
2. Has the full RICR been checked, beyond the extract?
3. Was the 7.1% calculated as an arithmetic or a compounded average?

DECISION-MAKER SUMMARY: Do not publish. The headline promises a guaranteed, risk-free return, which the rule prohibits and the 2021 result disproves, and the page claims a pre-publication approval step that the filed procedure says does not exist. Remove both, tone down "sleep at night", source the bond-quality claim, and then re-review.

OWNER SUMMARY: The page should not go live as written. It promises investors a guaranteed, risk-free return, which the rules forbid and which the fund has not always delivered. It also says every page is checked by compliance before posting, which is not how the firm actually works.

```json
{
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "full RICR text (only extract supplied)", "status": "not_seen", "matters": true},
    {"item": "portfolio holdings/mandate", "status": "not_seen", "matters": true},
    {"item": "managed-account status", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "R", "location": "page.md headline: \"Earn a guaranteed 6% a year, risk-free.\"", "scenario": "States a guaranteed return and no risk, prohibited by RICR 4.2; also contradicted by the 2021 net return of 4.2%. Regulator finds a breach; customers rely on a false guarantee.", "fix": "Remove the guarantee and risk-free wording; state that returns are not guaranteed and value can fall.", "status": "confirmed"},
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "R", "location": "page.md: \"Every page on this site is reviewed and approved by our compliance officer before it goes live.\" vs compliance_procedure.md: \"Posts and pages are not individually approved before they are published.\"", "scenario": "Page describes a pre-publication approval control that the filed procedure says does not operate; misleading statement contradicting a filed document.", "fix": "Delete the sentence, or describe the actual monthly 10% sampled review after publication.", "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "R", "location": "page.md: \"so you can sleep at night\"", "scenario": "Implies freedom from risk under RICR 4.2 even after the guarantee is removed.", "fix": "Remove or replace with a factual description of the strategy.", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "track": "R", "location": "page.md: \"Steady Harbor holds high-grade bonds\"", "scenario": "No supplied source supports the holdings claim; if untrue, the page misstates what the portfolio holds, against the request's instruction.", "fix": "Verify against the mandate or holdings report and cite it, or remove the claim.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "C", "location": "page.md: \"five-year average return was 7.1% a year\"", "scenario": "The figure reproduces (arithmetic 7.10%, compounded about 7.09%), but no period or method is stated, so readers cannot tell what it covers and it goes stale.", "fix": "State 2021-2025, the method and an as-of date.", "status": "n/a"}
  ]
}
```