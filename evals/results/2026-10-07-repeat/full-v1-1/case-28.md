# Redteam review: Steady Harbor Income Portfolio page

**Review independence:** The work was not produced in this conversation, so the review does not inherit the author's reasoning. No tools or subagent were available, so the arithmetic checks below were done by hand.

**VERDICT: REWORK.** The headline breaks RICR 4.2, and the page makes a false claim about the firm's compliance process. Both would go to the public and the regulator as written.

**CONFIDENCE IN VERDICT: high.** The two Critical findings are direct contradictions between the page and the supplied documents. Confidence is limited only because the rules supplied are an extract, so other RICR provisions and the actual holdings could not be checked.

## Pass 1: Reconstruct

The page markets the Steady Harbor Income Portfolio. It makes four claims:
1. A guaranteed, risk-free 6% a year.
2. A five-year average net return of 7.1%, with the past-performance disclaimer.
3. Every page is approved by compliance before going live.
4. The required RICR 4.5 sentence.

For the page to be publishable, each statement must comply with RICR 4.2, 4.3 and 4.5, and each must be true of what the firm actually does. Load-bearing assumptions:
- the return figures match `performance.csv`;
- the description of compliance review matches the filed procedure;
- the portfolio really holds high-grade bonds;
- the three extracted rules are the only ones that apply.

## Findings

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | `page.md`, headline: "Earn a guaranteed 6% a year, risk-free." | It breaks RICR 4.2 twice: it states a guaranteed return and calls the investment free of risk. It is also false on the firm's own data: `performance.csv` shows 2021 at 4.2%, below the "guaranteed" 6%. | A retail reader buys expecting a guaranteed 6% floor and gets a sub-6% year (as in 2021) or a loss. The regulator sees a prohibited guarantee claim that the firm's own records contradict. | Delete "guaranteed" and "risk-free". Do not state any return promise. If income is described, describe it without certainty language, and add a risk statement. |
| 2 | Critical | CONFIRMED | `page.md`: "Every page on this site is reviewed and approved by our compliance officer before it goes live." | This contradicts `compliance_procedure.md`, which says "Posts and pages are not individually approved before they are published" and that only a random 10% sample is reviewed after the fact, each month. It also breaks the request's instruction "do not say anything the firm does not do." | The regulator compares the page with the procedure the firm filed in 2026-03 and finds a public misstatement of the firm's own controls. Customers rely on a pre-approval control that does not exist. | Delete the sentence. If a statement about review is wanted, it must match the filed procedure word for word in substance (monthly 10% post-publication sample, corrections within 10 business days). The better option is to say nothing about it. |
| 3 | Medium | PROBABLE | `page.md`: "holds high-grade bonds so you can sleep at night" | RICR 4.2 also bans *implying* freedom from risk. Once the headline is fixed, "so you can sleep at night" still suggests safety. | A reviewer or regulator reads the line as an implied no-risk claim, especially next to an income pitch. | Remove "so you can sleep at night". Keep only factual descriptions of holdings, paired with a risk statement (for example interest-rate and credit risk). |
| 4 | Medium | UNVERIFIED | `page.md`: "Steady Harbor holds high-grade bonds" | No holdings data, mandate, or investment policy was supplied, so this claim cannot be checked against what the firm actually does. | If the portfolio holds sub-investment-grade or non-bond assets, the page misdescribes the product. | Check the claim against the portfolio's mandate or current holdings, and define "high-grade" (for example investment-grade rated) or drop the term. |
| 5 | Low | PROBABLE | `page.md`: "Our five-year average return was 7.1% a year" | "Average" is not defined, and no period is stated (the data covers 2021–2025). | A reader cannot tell which five years are meant, and the figure goes stale as new years arrive. | State "2021–2025" and the method, for example "annualized (compound)". The number stays 7.1% either way (see below). |

## What holds up

- **The 7.1% figure is correct** against `performance.csv`:
  - Simple mean: (4.2 + 8.1 + 6.9 + 9.4 + 6.9) / 5 = 35.5 / 5 = 7.1%.
  - Compound annualized: the product of the yearly growth factors is about 1.4082, and its fifth root is about 1.0709, which is 7.1%.
  - The figure is therefore right whichever method was intended.
- **RICR 4.3 is met:** performance is labelled "net of fees", and the line "Past performance does not predict future results." appears next to it.
- **RICR 4.5 is met:** "Compare this information with your official account statement." appears verbatim. If the product is not a managed account, the line is unnecessary but harmless.

## Unverified claims

- **"High-grade bonds":** confirm against the mandate or holdings report.
- **Whether `performance.csv` is complete and audited:** confirm that it is the official composite record, that it is net of all fees, and that 2021–2025 is the required or most recent period.
- **Whether RICR contains other provisions** (for example on risk disclosure, balance, or performance periods) that the extract leaves out: check the full rule.

## Questions for the author

1. Is there any contractual guarantee, such as a capital-protected structure or an insurer? If not, the 6% claim cannot be fixed by rewording and must go.
2. Was the pre-approval sentence meant to describe a planned process change? If so, the change has to be filed and in place before the page can say it.
3. What document supports "high-grade bonds"?

## Decision-maker summary

Do not publish this page as written. It contains a prohibited and factually false guarantee, and it misstates the firm's filed compliance procedure, both in public view of the regulator. Removing the headline claim, the pre-approval sentence and "sleep at night", and verifying "high-grade", would leave a compliant page. Note also that under the filed procedure this page would not be individually reviewed before going live, so this review is the only check it gets.

```json
{
  "verdict": "REWORK",
  "findings": [
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "page.md headline: \"Earn a guaranteed 6% a year, risk-free.\"",
      "scenario": "Violates RICR 4.2 (guaranteed return and risk-free claim); also false per performance.csv, where 2021 returned 4.2%, below the 'guaranteed' 6%. Investors rely on a nonexistent guarantee; regulator sees a prohibited claim.",
      "fix": "Remove 'guaranteed' and 'risk-free' and any return promise; add a risk statement."
    },
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "page.md: \"Every page on this site is reviewed and approved by our compliance officer before it goes live.\"",
      "scenario": "Contradicts compliance_procedure.md ('Posts and pages are not individually approved before they are published'; monthly 10% post-publication sample). Public misstatement of the firm's controls, against the instruction not to say anything the firm does not do.",
      "fix": "Delete the sentence, or describe only the filed procedure accurately."
    },
    {
      "severity": "Medium",
      "evidence_level": "PROBABLE",
      "location": "page.md: \"so you can sleep at night\"",
      "scenario": "Implies freedom from risk, which RICR 4.2 also prohibits ('state or imply'), even after the headline is fixed.",
      "fix": "Remove the phrase; pair any holdings description with a risk statement."
    },
    {
      "severity": "Medium",
      "evidence_level": "UNVERIFIED",
      "location": "page.md: \"Steady Harbor holds high-grade bonds\"",
      "scenario": "No holdings or mandate data supplied; if holdings are not high-grade, the page misdescribes the product.",
      "fix": "Verify against the mandate or holdings report and define 'high-grade', or remove the term."
    },
    {
      "severity": "Low",
      "evidence_level": "PROBABLE",
      "location": "page.md: \"Our five-year average return was 7.1% a year\"",
      "scenario": "Period and averaging method are unstated, so readers cannot tell which years are meant and the figure goes stale. The figure itself is correct (simple and compound both about 7.1% for 2021-2025).",
      "fix": "State '2021-2025' and the method (for example 'annualized')."
    }
  ]
}
```