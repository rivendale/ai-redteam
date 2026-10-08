# Redteam review: Steady Harbor Income Portfolio web page

**VERDICT: REWORK.** The page breaks RICR 4.2 in its headline. It also claims a pre-publication approval step that the firm's filed procedure says does not happen.

**CONFIDENCE: high.** Both Critical findings rest on exact quotes from the supplied documents. Three things limit confidence:
- This session has no tools.
- I reviewed it myself with no fresh subagent. The work was not written in this conversation, so the anchoring risk is lower, but it is still a single-reviewer read.
- The rule text is only an extract, and no holdings data was supplied.

**INPUTS LEDGER**
- **Seen:** `request.md`, `context.md`, `page.md`, `compliance_procedure.md`, `rule_extract.md`, `performance.csv`.
- **Not seen:**
  - **The full RICR.** Paragraphs 4.1, 4.4 and any others are missing. This matters: other requirements may apply.
  - **Portfolio holdings or mandate.** This matters because the claim "holds high-grade bonds" cannot be checked.
  - **Whether this is a managed account.** This does not matter much: the 4.5 sentence is present either way.
  - **The filed version of the procedure.** I was given only the markdown copy. This does not matter much.

**SEATS AND GATE**
- **Sensitivity:** the page contains no personal data, credentials or client records. It is public marketing text, so the gate passed.
- **Seats:** only a same-context, local review ran. No subagent was available, and no cross-vendor seats were requested.

## Pass 1: Reconstruct

The page markets an income portfolio and makes several claims:
- a guaranteed, risk-free 6% a year;
- holdings in high-grade bonds;
- a five-year average net return of 7.1%;
- every page is approved by compliance before it goes live.

For the page to be correct, three things must hold:
1. It must comply with RICR 4.2, 4.3 and 4.5.
2. Every operational claim must match what the firm actually does.
3. The performance figure must reproduce from `performance.csv`.

The page assumes, without saying so, that the extract is the whole of the applicable rule. Tracks: **R** (primary) and **C**.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | R | `page.md` line 3: "**Earn a guaranteed 6% a year, risk-free.**" | RICR 4.2 says a communication "must not state or imply that a return is guaranteed, or that an investment is free of risk." The headline does both. It also contradicts the firm's own data: 2021 returned 4.2%, below the "guaranteed" 6%. | A regulator or customer reads the published headline. That is a direct rule breach, a misleading promise, and exposure if a customer loses money or earns under 6%. | Remove "guaranteed" and "risk-free." Do not state any assured return. Also review "so you can sleep at night" (see #4). | confirmed. The text is verbatim, and no reading of 4.2 permits it. |
| 2 | Critical | CONFIRMED | R | `page.md` line 7: "**Every page on this site is reviewed and approved by our compliance officer before it goes live.**" | This is an invented control. The filed procedure says: "Posts and pages are not individually approved before they are published," and only "a random 10% sample" is reviewed monthly, after publication. It breaks the request's instruction to "not say anything the firm does not do." | The public and the regulator compare the page with the filed procedure. A misstatement about the firm's own compliance controls is serious exposure, and it misleads customers about oversight. | Delete the sentence. If anything is said, describe the filed procedure accurately (monthly post-publication sample review). Better still, say nothing. | confirmed. The two documents contradict each other directly. |
| 3 | Medium | UNVERIFIED | R/C | `page.md` line 3: "Steady Harbor holds high-grade bonds" | No holdings, mandate or credit-quality data was supplied, so the claim cannot be substantiated from the inputs. | If the portfolio holds sub-investment-grade or non-bond assets, the page misdescribes the product. | Check the claim against the current holdings or the investment mandate before publishing. Keep a record of the substantiation. | n/a |
| 4 | Medium | PROBABLE | R | `page.md` line 3: "so you can sleep at night" | Placed next to "guaranteed" and "risk-free," this phrase reinforces an implication of safety that 4.2 also bars ("or imply"). Even after #1 is fixed, it may still imply that the investment is free of risk. | A reviewer reads the remaining phrase as implying no risk, which is a 4.2 breach by implication. | Remove it, or replace it with neutral, factual language about the strategy and its risks. | n/a |
| 5 | Low | CONFIRMED | C/R | `page.md` line 5: "Our five-year average return was 7.1% a year" | The method and period are not named. The figure reproduces either way: the arithmetic mean of 4.2, 8.1, 6.9, 9.4 and 6.9 is 35.5/5 = 7.10%, and the geometric (annualized) figure is about 7.09%. | A reader cannot tell which years are covered or how the figure was calculated. The full RICR may require this; that is unverified. | State "2021–2025, annualized, net of fees." Consider showing the year-by-year figures. | n/a |

## Pass 3: Self-check

- The verdict matches the findings: two Critical findings are open, so the verdict cannot be SHIP or SHIP WITH FIXES.
- No finding assumes the worst case beyond what the quoted text shows.
- **Most serious problem that may still be missed:** requirements in the RICR paragraphs that were not supplied, such as a risk-disclosure section, fee disclosure, or performance-period rules. These would hide in the unseen 4.1 and 4.4.

## What holds up

- **RICR 4.3:** performance is shown "net of fees," and the required statement "Past performance does not predict future results." is present verbatim.
- **RICR 4.5:** "Compare this information with your official account statement." is present verbatim.
- **The 7.1% figure:** it reproduces from `performance.csv` by both the arithmetic and the annualized method. The five years 2021–2025 match "five-year."

## Unverified claims

- **"Holds high-grade bonds":** confirm against the holdings report or the mandate.
- **Completeness of the rule extract:** confirm against the full RICR text.
- **Whether the account is "managed":** this matters only for whether 4.5 applies, and the sentence is present anyway.

## Questions for the author

1. What evidence supports "high-grade bonds"?
2. Does the full RICR contain further requirements, such as risk disclosure or performance-period rules, that this page must meet?

## Summaries

**DECISION-MAKER SUMMARY:** Do not publish. The headline breaches RICR 4.2, and the approval claim contradicts the filed procedure. Fix #1, #2 and #4, substantiate #3, and re-review. Publishing as written would mean making a prohibited guarantee and misrepresenting the firm's compliance controls to the public and the regulator.

**OWNER SUMMARY:** The page should not go live yet. It promises a guaranteed, risk-free return, which the rules forbid, and it says every page is approved by compliance before publishing, which is not how the firm actually works. Remove both claims, confirm what the portfolio actually holds, and have the page checked again.

```json
{
  "verdict": "REWORK",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "full RICR text (beyond 4.2, 4.3, 4.5)", "status": "not_seen", "matters": true},
    {"item": "portfolio holdings / mandate", "status": "not_seen", "matters": true},
    {"item": "page.md, compliance_procedure.md, rule_extract.md, performance.csv", "status": "seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "public marketing text; no personal or confidential data"},
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "R", "location": "page.md line 3: 'Earn a guaranteed 6% a year, risk-free.'",
     "scenario": "Published headline states a guaranteed return and no risk, breaching RICR 4.2; contradicted by the 2021 net return of 4.2%.",
     "fix": "Remove 'guaranteed' and 'risk-free'; state no assured return.", "status": "confirmed"},
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "R", "location": "page.md line 7: 'Every page on this site is reviewed and approved by our compliance officer before it goes live.'",
     "scenario": "Filed procedure says pages are not individually approved before publication, only a 10% monthly post-publication sample; the page describes a control that does not operate.",
     "fix": "Delete the sentence, or describe the filed procedure accurately.", "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "track": "R", "location": "page.md line 3: 'holds high-grade bonds'",
     "scenario": "No holdings data supplied; if holdings are not high-grade, the page misdescribes the product.",
     "fix": "Substantiate against current holdings or the mandate, and record the evidence.", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "R", "location": "page.md line 3: 'so you can sleep at night'",
     "scenario": "Implies freedom from risk, which RICR 4.2 bars by implication, even after the explicit claims are removed.",
     "fix": "Remove it or replace it with neutral, factual risk language.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "C", "location": "page.md line 5: 'five-year average return was 7.1% a year'",
     "scenario": "Period and method not stated; the figure reproduces (arithmetic 7.10%, geometric about 7.09%), but readers cannot tell how it was derived.",
     "fix": "State '2021-2025, annualized, net of fees'; optionally show the yearly figures.", "status": "n/a"}
  ]
}
```