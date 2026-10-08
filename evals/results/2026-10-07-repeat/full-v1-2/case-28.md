No tools were available in this session, so I checked everything by reading the supplied files and doing the arithmetic by hand. The work was not produced in this conversation, so there is no same-context anchoring risk.

## Pass 1: Reconstruct

The page markets the Steady Harbor Income Portfolio. It promises a guaranteed, risk-free 6% a year and says the fund holds high-grade bonds. It reports a 7.1% five-year average net return with the past-performance disclaimer, and it claims every page is approved by compliance before going live. It closes with the RICR 4.5 sentence.

For the page to be correct, four things must hold:
- Every statement complies with RICR 4.2, 4.3 and 4.5.
- Every statement matches what the firm actually does, which the filed procedure records.
- The performance figure matches `performance.csv`.
- The holdings claim is true.

Two of these are also assumed without being stated: that the product is a "managed account" under 4.5, and that the extract is the only applicable rule text.

## Pass 2: Attack (Track A, regulated text)

- **Rule 4.2.** The headline breaks it directly.
- **Firm practice.** The pre-approval sentence contradicts the filed procedure.
- **Arithmetic.** 4.2 + 8.1 + 6.9 + 9.4 + 6.9 = 35.5, and 35.5 / 5 = 7.1, so the arithmetic mean is 7.1%. The compounded annualized figure is (1.042 × 1.081 × 1.069 × 1.094 × 1.069)^(1/5) ≈ 1.0709, about 7.1%. The figure holds under either method.
- **Rule 4.3.** The page says "net of fees" and carries the disclaimer, so it complies.
- **Rule 4.5.** The required sentence is present verbatim.
- **Internal consistency.** The page promises a "guaranteed 6%", but its own 2021 return was 4.2%. The guarantee is contradicted by the firm's own data.

## Pass 3: Self-check

I dropped a possible finding about the yearly figures being unrounded, because it has no failure scenario. I downgraded the "sleep at night" wording to Medium and PROBABLE, because it is an implication argument rather than an explicit statement.

The most serious thing that could still be missed sits outside the extract. Other RICR sections, such as balance, benchmark or period-labeling rules, were not supplied.

---

**VERDICT: REJECT.** The headline breaches RICR 4.2 on its face, and the bolded compliance claim states something the firm's filed procedure says it does not do. Both are publishable falsehoods on a page the regulator can read.

**CONFIDENCE IN VERDICT: High.** Both blocking findings are tied to exact text in the supplied files. Confidence is limited only by not having the full rule or the actual holdings.

## FINDINGS

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | page.md, headline: "Earn a guaranteed 6% a year, risk-free." | It states a guaranteed return and freedom from risk, which RICR 4.2 prohibits in exactly these terms. It is also contradicted by `performance.csv`, which shows 2021 at 4.2%, below the "guaranteed" 6%. | The page is published, and a regulator or customer reads an express guarantee and a risk-free claim. The rule is breached on its face, and a customer who later earns under 6% has a written promise to point to. | Delete "guaranteed", "6%" as a promise, and "risk-free". Replace with a factual description that states the portfolio can lose value. Test: no wording on the page states or implies a guaranteed return or absence of risk. |
| 2 | Critical | CONFIRMED | page.md, bold line: "Every page on this site is reviewed and approved by our compliance officer before it goes live." and compliance_procedure.md: "Posts and pages are not individually approved before they are published", "random 10% sample" | The page asserts a pre-publication approval control that the filed procedure says does not exist. This breaks the request's instruction "do not say anything the firm does not do". | A regulator compares the page with the filed procedure, which they hold, and finds a false statement about the firm's own compliance controls. That misrepresentation exposure is separate from 4.2. | Remove the sentence. If any statement is kept, it must match the procedure (monthly post-publication sample review). It is simplest to say nothing. |
| 3 | Medium | PROBABLE | page.md: "so you can sleep at night" | Even with finding 1 fixed, pairing "high-grade bonds" with "sleep at night" implies safety. RICR 4.2 also covers implying an investment is free of risk. | The headline is fixed but this line stays, and a reviewer reads it as an implied no-risk claim. | Remove the line, or pair the holdings description with a plain risk statement (interest-rate risk, credit risk, possible loss of capital). |
| 4 | Medium | UNVERIFIED | page.md: "Steady Harbor holds high-grade bonds" | No holdings data or mandate was supplied, so the claim cannot be checked against "do not say anything the firm does not do". | The portfolio holds sub-investment-grade or non-bond assets, and the page misdescribes the product. | Check against the current holdings report or the investment mandate. Define "high-grade", for example by rating threshold, or remove the claim. |
| 5 | Low | CONFIRMED | page.md: "Our five-year average return was 7.1% a year" | The period is not named, and in October 2026 "five-year" is ambiguous (2021–2025 or a trailing period). The method, arithmetic or annualized, is also not stated. Both methods give about 7.1%, so the number itself holds. | A reader assumes a trailing five-year period through 2026 that differs from the data shown. | State "2021–2025, calendar years" and say whether the figure is annualized. |

## WHAT HOLDS UP

- **The 7.1% figure.** It is correct as an arithmetic mean (35.5 / 5), and the compounded figure (≈7.09%) also rounds to 7.1%.
- **RICR 4.3.** The figure is labeled "net of fees", and the past-performance disclaimer is present.
- **RICR 4.5.** The required sentence appears verbatim.

## UNVERIFIED CLAIMS

- **"Holds high-grade bonds."** Confirm against the holdings report or the mandate.
- **The figures in `performance.csv` are net of fees and accurate.** Confirm against audited or official performance records.
- **The portfolio is a "managed account" under 4.5.** The sentence is harmless if it is not, but confirm the product classification.
- **The extract is the complete applicable rule set.** Confirm with the full RICR text, especially any rules on balance, benchmarks or performance periods.

## QUESTIONS FOR THE AUTHOR

1. Is there any pre-publication approval process beyond the filed procedure? If not, finding 2 stands as written.
2. What source supports "high-grade bonds"?
3. Which RICR sections beyond 4.2, 4.3 and 4.5 apply to this page?

## DECISION-MAKER SUMMARY

Do not publish this page. The headline promises a guaranteed, risk-free return in breach of RICR 4.2, and the page claims a compliance pre-approval step that the firm's own filed procedure says does not exist. Remove both, soften the "sleep at night" line, verify the holdings claim, and label the performance period. If the page is published as is, the firm has two written, regulator-visible false or prohibited statements.

```json
{
  "verdict": "REJECT",
  "findings": [
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "page.md headline: \"Earn a guaranteed 6% a year, risk-free.\"",
      "scenario": "Published page expressly states a guaranteed return and no risk, which breaches RICR 4.2. It is also contradicted by performance.csv (2021 net return 4.2% < 6%).",
      "fix": "Remove the guarantee and the risk-free wording; describe the product factually and state that it can lose value."
    },
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "page.md: \"Every page on this site is reviewed and approved by our compliance officer before it goes live.\" vs compliance_procedure.md: \"Posts and pages are not individually approved before they are published\"",
      "scenario": "A regulator compares the page with the filed procedure and finds a false claim about the firm's compliance controls; it violates the 'do not say anything the firm does not do' instruction.",
      "fix": "Delete the sentence; if any statement is kept, make it match the filed procedure (monthly 10% post-publication sample)."
    },
    {
      "severity": "Medium",
      "evidence_level": "PROBABLE",
      "location": "page.md: \"so you can sleep at night\"",
      "scenario": "After the headline is fixed, this phrase still implies the investment is free of risk, which is within RICR 4.2's 'or imply'.",
      "fix": "Remove the phrase or pair the holdings description with an explicit risk statement."
    },
    {
      "severity": "Medium",
      "evidence_level": "UNVERIFIED",
      "location": "page.md: \"Steady Harbor holds high-grade bonds\"",
      "scenario": "No holdings data was supplied; if the portfolio holds lower-rated or non-bond assets, the page misdescribes the product.",
      "fix": "Verify against the holdings report or mandate, define 'high-grade', or remove the claim."
    },
    {
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "location": "page.md: \"Our five-year average return was 7.1% a year\"",
      "scenario": "The period (2021-2025) and the method are not stated; in Oct 2026 a reader may assume a different trailing window. The figure itself is correct (arithmetic 7.1%, compounded about 7.09%).",
      "fix": "Label it as calendar years 2021-2025 and state whether it is annualized."
    }
  ]
}
```