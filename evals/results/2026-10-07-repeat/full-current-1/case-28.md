# Redteam review: Steady Harbor Income Portfolio web page

**VERDICT: REWORK.** The page breaks RICR 4.2 in its headline, and it claims a pre-publication approval control that the firm's own filed procedure says does not exist.

**CONFIDENCE: high.** Both Critical findings rest on exact quotes compared against exact rule and procedure text. Two things limit confidence:
- This is a same-context review with no subagent and no tools. It carries anchoring risk, so re-run it in a fresh session before publication.
- I saw only an extract of the rule, not the full RICR.

**INPUTS LEDGER**
- **Seen:** request.md, context.md, page.md, rule_extract.md (4.2, 4.3, 4.5), compliance_procedure.md, performance.csv.
- **Not seen: the full RICR text.** This matters. Other paragraphs, such as 4.1, 4.4 or definitions, may add requirements like stating the performance period. Anything outside the extract is UNVERIFIED.
- **Not seen: holdings or portfolio documentation.** This matters for the "high-grade bonds" claim.
- **Not seen: whether the portfolio is a "managed account" under 4.5.** This matters little. The required sentence is present either way.
- **Not seen: the firm's other filed or published documents** (terms, filings). This matters for the consistency check, which I could not do beyond the procedure.

**SEATS AND GATE**
- Seats: single same-context reviewer. No subagent or cross-vendor seats were available.
- Sensitivity gate: passed. There is no personal data, credentials or client records, only public-facing marketing text and aggregate returns.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | R | page.md line 3: "**Earn a guaranteed 6% a year, risk-free.**" and "so you can sleep at night" | States both a guaranteed return and freedom from risk. RICR 4.2 prohibits each, quote: "must not state or imply that a return is guaranteed, or that an investment is free of risk". The firm's own data contradicts the guarantee: 2021 net return was 4.2%, below 6% (performance.csv). "Sleep at night" reinforces the implied safety. | The page is published, and the regulator or a customer reads it. That is a direct rule breach. A retail investor buys expecting a floor of 6% and no loss of principal. In any year below 6%, or any bond loss, the firm faces a misrepresentation claim and regulatory action. | Delete the guarantee and the risk-free claim, and remove or soften "sleep at night". Replace them with a factual description and a plain risk statement, for example that bond values and income can fall and investors can lose money. | confirmed. No reading of "guaranteed" or "risk-free" survives 4.2. |
| 2 | Critical | CONFIRMED | R | page.md line 7: "**Every page on this site is reviewed and approved by our compliance officer before it goes live.**" | This is an invented control. The filed procedure says the opposite, quote: "Posts and pages are not individually approved before they are published", and review is a monthly random 10% sample after publication. It also violates the request: "do not say anything the firm does not do." | A regulator compares the page with the filed procedure and finds a false statement about compliance controls. That is worse than saying nothing. It also gives customers false assurance about every other page. | Delete the sentence. If a statement about review is wanted, describe the filed procedure accurately, or say nothing. | confirmed. The filed procedure explicitly excludes pre-publication approval, and nothing supplied shows a newer practice. |
| 3 | Medium | UNVERIFIED | R/C | page.md line 3: "Steady Harbor holds high-grade bonds" | This is a factual claim about holdings, and no holdings, mandate or credit-quality data was supplied. | The portfolio holds sub-investment-grade or unrated paper, or its mandate permits it. The claim is then a misstatement that also implies low risk. | Check against the portfolio's mandate and current holdings. Define "high-grade", for example by a minimum rating, or remove the claim. | n/a (Medium) |
| 4 | Low | CONFIRMED | R/C | page.md line 5: "Our five-year average return was 7.1% a year, net of fees." | The figure reproduces. The arithmetic mean is (4.2+8.1+6.9+9.4+6.9)/5 = 35.5/5 = 7.10%. The geometric annualized figure is (1.042·1.081·1.069·1.094·1.069)^(1/5) − 1 ≈ 7.09%, which also rounds to 7.1%. However, the page names neither the period (2021–2025) nor the averaging method. | A reader in late 2026 assumes the five years run through the current date. Or a later update silently switches method, and a sub-7% year turns the rounding. | State the period ("2021–2025") and say "annualized". Check the full RICR for any period or method requirement. | n/a (Low) |

## WHAT HOLDS UP

- **RICR 4.3 is met.** Performance is shown "net of fees". The required sentence "Past performance does not predict future results." appears word for word, next to the figure.
- **The 7.1% figure is correct.** It reproduces from performance.csv by both arithmetic and geometric methods.
- **RICR 4.5 is met.** "Compare this information with your official account statement." appears verbatim.
- **No personal data** appears on the page.

## UNVERIFIED CLAIMS

- **"High-grade bonds."** Settle it with the investment mandate and a current holdings report.
- **Compliance with the RICR beyond the three extracted paragraphs.** Settle it with the full rule text.
- **Consistency with the firm's other published documents** (terms, filings, fee disclosures). Settle it with those documents.

## QUESTIONS FOR THE AUTHOR

1. Where did "guaranteed 6%" come from? Is there any actual guarantee, insurance or contractual floor? If there isn't, the claim must go.
2. Has the firm changed its review practice since the March 2026 filing? If it now pre-approves every page, the procedure filing needs updating before the page can say so. Until then the sentence must go.
3. What is the portfolio's credit-quality mandate?

## DECISION-MAKER SUMMARY

Do not publish. The headline promises a guaranteed, risk-free return, which the rule forbids outright. The page also claims every page is pre-approved, which contradicts the firm's own filed procedure. Both are quick deletions, but publishing as is invites regulatory action and customer claims.

Note that under the filed procedure this page would only have about a 10% chance of being caught in the monthly sample. That makes this pre-publication review the main safeguard.

## OWNER SUMMARY

The page promises investors a guaranteed 6% return with no risk. The rules forbid that, and the firm's own results show a year below 6%. The page also says every page is checked by compliance before going live, which is not how the firm actually works. Both statements need to be removed before anyone publishes the page.

```json
{
  "verdict": "REWORK",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "full RICR text (only extract 4.2, 4.3, 4.5 supplied)", "status": "not_seen", "matters": true},
    {"item": "portfolio holdings / mandate", "status": "not_seen", "matters": true},
    {"item": "other filed or published firm documents", "status": "not_seen", "matters": true},
    {"item": "managed-account status under 4.5", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "public marketing text and aggregate returns only"},
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "R", "location": "page.md:3 \"Earn a guaranteed 6% a year, risk-free.\"",
     "scenario": "Published page states a guaranteed return and no risk, breaching RICR 4.2; 2021 net return of 4.2% already contradicts the guarantee, exposing the firm to regulatory action and misrepresentation claims.",
     "fix": "Delete the guarantee and risk-free claim (and 'sleep at night'); add a plain statement that investors can lose money.", "status": "confirmed"},
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "R", "location": "page.md:7 \"Every page on this site is reviewed and approved by our compliance officer before it goes live.\"",
     "scenario": "Filed procedure says pages are not individually approved before publication (monthly 10% post-publication sample); regulator finds a false statement about compliance controls.",
     "fix": "Delete the sentence, or accurately describe the filed procedure.", "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "track": "R", "location": "page.md:3 \"Steady Harbor holds high-grade bonds\"",
     "scenario": "If the mandate or holdings include sub-investment-grade or unrated bonds, the claim misstates the portfolio and implies low risk.",
     "fix": "Verify against mandate and current holdings; define 'high-grade' or remove.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "R", "location": "page.md:5 \"Our five-year average return was 7.1% a year, net of fees.\"",
     "scenario": "Figure reproduces (arithmetic 7.10%, geometric ~7.09%) but period and method are unstated; readers may assume it runs to the current date.",
     "fix": "State '2021-2025, annualized'; check the full RICR for period requirements.", "status": "n/a"}
  ]
}
```