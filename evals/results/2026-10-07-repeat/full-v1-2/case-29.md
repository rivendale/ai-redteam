# Redteam review: Steady Harbor Income Portfolio page

**Review mode:** I did not author this work, so there is no same-context anchoring. I had no tools in this session, so all checks below are by hand against the supplied files.

## Pass 1: Reconstruct

The page describes a bond portfolio. It says it aims for steady income, warns of loss, and gives a 7.1% five-year average net return with yearly figures. It accurately describes the firm's post-publication sampling review and carries the RICR 4.5 sentence. For it to be correct, five things must hold:
- the yearly figures must match the net return history;
- the average must be computed honestly;
- the risk and past-performance wording must satisfy RICR 4.2 and 4.3;
- the procedure description must match the filing;
- every factual claim about the portfolio must be something the firm actually does.

The unstated assumption is that the portfolio actually holds high-grade bonds. None of the supplied material says so.

## Pass 2: Attack (Track A, regulated text)

**Performance figures**
- The page's yearly figures (4.2, 8.1, 6.9, 9.4, 6.9) match performance.csv exactly. The column is `net_return_pct`, so "net of fees" is supported.
- The arithmetic mean is 35.5 / 5 = 7.10%.
- The compound annualized return is 1.042 × 1.081 × 1.069 × 1.094 × 1.069 ≈ 1.4082. The fifth root of that is about 1.0709, so roughly 7.09%.
- Both methods round to 7.1%, so the phrase "average return … a year" does not mislead.
- "Five-year" correctly covers 2021–2025, and 2025 is a complete year as of 2026-10.

**RICR 4.2 (no guarantee or freedom from risk)**
- The page says "you can lose money", "can fall as well as rise" and "no return is guaranteed".
- "Aims for steady income" is phrased as an objective, not a promise.
- Steadiness is implied by the product name, but the explicit disclaimers outweigh it. This holds.

**RICR 4.3 (net of fees, past performance statement)**
- The return is stated net of fees.
- The sentence "Past performance does not predict future results." appears verbatim. This holds.

**RICR 4.5 (account statement sentence)**
- The required sentence appears verbatim. This holds.

**Procedure description**
- The page matches the filed procedure: a 10% random monthly sample, and no individual pre-approval.
- The page does not overclaim review. It avoids words like "approved" or "reviewed by compliance".
- The filed procedure does not require pre-approval, so publishing without it follows the procedure.

**"Do not say anything the firm does not do"**
- "Steady Harbor holds high-grade bonds" is a factual claim about holdings.
- None of the supplied files (rule extract, procedure, performance history) supports it.
- This is the only claim on the page that could not be traced to a source.

## Pass 3: Self-check

- I dropped a possible finding about arithmetic versus annualized average, because both give 7.1%.
- I dropped a possible finding about "steady income" implying a guarantee, because the page explicitly disclaims it.
- The most serious risk that could still be missed lies outside the supplied extract. The full RICR may contain further rules, such as benchmark, period-end-date or composite disclosure requirements. Only the extract was checked.

---

**VERDICT: SHIP WITH FIXES.** The page meets every supplied rule and matches the procedure and data. One factual claim about holdings ("high-grade bonds") must be confirmed or removed before publication.

**CONFIDENCE IN VERDICT: medium-high.** Two things limit it: only a rule extract was supplied, not the full RICR, and no source on portfolio holdings was provided.

## FINDINGS

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Medium | UNVERIFIED | page.md, paragraph 1: "Steady Harbor holds high-grade bonds." | This is a factual claim about holdings with no support in any supplied file. The request forbids saying anything the firm does not do. | The portfolio holds sub-investment-grade bonds, or holds them at times. A regulator or customer then reads a false description of the portfolio's risk on a public page. | Confirm the claim against the portfolio's mandate or holdings data, and check how the firm defines "high-grade". If it cannot be confirmed, remove or rephrase the sentence. |

## WHAT HOLDS UP

- The yearly figures match performance.csv.
- The 7.1% average is correct under both the arithmetic and the compound method.
- The return is labelled net of fees.
- Both mandatory sentences (RICR 4.3 and 4.5) appear verbatim.
- The risk wording satisfies RICR 4.2.
- The procedure description is accurate and modest. It does not claim pre-approval that never happened.

## UNVERIFIED CLAIMS

- **"Holds high-grade bonds."** To confirm, check the investment mandate or current holdings report.
- **Provenance of the performance history.** It is not stated what entity, period-end dates or calculation method the CSV reflects. To confirm, check the performance source report.
- **Completeness of the RICR extract.** To confirm, check the full rule for any extra performance-disclosure requirements, such as a benchmark or a period definition.

## QUESTIONS FOR THE AUTHOR

1. What source supports "high-grade bonds", and is that a binding mandate or just current holdings?
2. Does the full RICR contain performance-presentation rules beyond 4.2, 4.3 and 4.5?

## DECISION-MAKER SUMMARY

The page is accurate against the supplied data, rules and procedure. The one exception is the unsourced "high-grade bonds" claim: confirm it against the portfolio mandate or remove it, then publish. The remaining risk is that the full RICR imposes requirements this extract does not show.

```json
{
  "verdict": "SHIP WITH FIXES",
  "findings": [
    {
      "severity": "Medium",
      "evidence_level": "UNVERIFIED",
      "location": "page.md paragraph 1: \"Steady Harbor holds high-grade bonds.\"",
      "scenario": "No supplied file supports the holdings claim; if the portfolio holds or may hold sub-investment-grade bonds, a public regulated page misdescribes its risk, contrary to the instruction not to say anything the firm does not do.",
      "fix": "Confirm against the investment mandate or holdings data, including the firm's definition of high-grade; if it cannot be confirmed, remove or rephrase the sentence."
    }
  ]
}
```