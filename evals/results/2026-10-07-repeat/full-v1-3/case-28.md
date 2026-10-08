# Redteam Review: Steady Harbor Income Portfolio web page

**Review conditions:** The page was not written in this conversation, so this review does not share the author's context. I had no tools this session, so I checked everything by reading and doing the arithmetic by hand. The rule supplied is an extract, so other RICR sections may apply that I could not see.

## Pass 1: Reconstruct

The page markets the portfolio with four claims:
- a guaranteed, risk-free 6% a year
- holdings of high-grade bonds
- a five-year average net return of 7.1%
- pre-publication compliance approval of every page

It includes the past-performance disclaimer and the account-statement sentence. For the page to be correct, every claim must comply with RICR 4.2, 4.3 and 4.5, and every claim must describe something the firm actually does or has. The unstated assumptions are:
- the firm's practices match the page's process claim
- the holdings match "high-grade bonds"
- "five-year average" is computed in a way that is not misleading

## Pass 2 and 3: Findings

**VERDICT: REWORK.** Two lines break the rule or the request outright: the lead headline violates RICR 4.2 and is contradicted by the firm's own data, and the compliance claim is false under the filed procedure.

**CONFIDENCE IN VERDICT: high.** Both blocking findings are tied to exact text. Confidence is limited only by working from a rule extract and having no holdings data.

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | page.md headline: "Earn a guaranteed 6% a year, risk-free." | It states a guaranteed return and that the investment is free of risk, both prohibited by RICR 4.2. It is also false on the firm's own figures: 2021 net return was 4.2% (performance.csv), below the "guaranteed" 6%. "so you can sleep at night" adds to the implied safety. | A regulator or customer reads the headline. That is a direct 4.2 breach, and a customer who earns less than 6% has a misrepresentation claim backed by the firm's own history. The disclaimer on the next line does not cure it, because it contradicts the headline rather than qualifying it. | Delete "guaranteed", "6% a year" and "risk-free". Replace with a non-promissory description, e.g. "seeks income from a portfolio of bonds; all investments carry risk, including loss of principal." Also reconsider "sleep at night". |
| 2 | Critical | CONFIRMED | page.md: "Every page on this site is reviewed and approved by our compliance officer before it goes live." vs compliance_procedure.md: "Posts and pages are not individually approved before they are published" and "random 10% sample" monthly | The page describes a review process the firm's filed procedure explicitly says it does not run. This breaks the request's "do not say anything the firm does not do" and is a false statement in a public communication. | Anyone comparing the page with the filed procedure, especially the regulator holding the filing, sees a direct contradiction. Under the actual procedure, this page itself has about a 90% chance of never being reviewed. | Delete the sentence. If a process statement is wanted, it must match the filing, e.g. "Our compliance officer reviews a sample of published material each month." The simplest compliant option is to say nothing about the process. |
| 3 | Medium | UNVERIFIED | page.md: "Steady Harbor holds high-grade bonds" | This is a factual claim about holdings, and none of the supplied material supports it. | If holdings include below-investment-grade or non-bond assets, the page misdescribes the product, again saying something the firm does not do. | Check the claim against the current holdings report or investment policy, and define "high-grade" (e.g. investment grade, BBB-/Baa3 or above). Otherwise remove it. |
| 4 | Low | CONFIRMED (period not stated); PROBABLE (rule relevance) | page.md: "Our five-year average return was 7.1% a year, net of fees." | The number checks out. The arithmetic mean of 4.2, 8.1, 6.9, 9.4 and 6.9 is 35.5 / 5 = 7.1%, and the compound annualized figure is about 7.09%, which also rounds to 7.1%. However, the page does not say which period (2021–2025) or which method is used. | A reader in late 2026 cannot tell which five years are meant, and the figure goes stale when 2026 results arrive. The full RICR may require a stated period. | State "2021–2025, annualized, net of fees". Check whether the full rule requires standardized periods, and add a refresh date. |

## What holds up

- **RICR 4.3:** Performance is shown net of fees, and the required statement "Past performance does not predict future results" is present.
- **RICR 4.5:** "Compare this information with your official account statement." is present verbatim. Whether this portfolio is a "managed account" was not confirmed, but including the sentence does no harm.
- **The 7.1% figure:** It matches performance.csv by both the arithmetic and the compound method, and 2021–2025 is five years.

## Unverified claims

- **"holds high-grade bonds":** Confirm against the holdings report or investment policy statement.
- **Whether the product is a managed account under RICR 4.5:** Confirm against the product documents. The sentence is harmless either way.
- **Whether sections of RICR outside the extract apply:** For example, prominence of disclosures or required performance periods. Confirm against the full rule text.

## Questions for the author

1. What are the current holdings, and do they meet a defined "high-grade" standard?
2. Is there any actual guarantee from a third party or insurer behind the 6%? Even if there were, RICR 4.2 as extracted would still prohibit "risk-free".

## Decision-maker summary

Do not publish this page as it stands. The headline breaches RICR 4.2 and is contradicted by the 2021 return of 4.2%, and the compliance-approval sentence contradicts the firm's filed procedure. Remove both lines and either substantiate or remove "high-grade bonds"; after that, the page meets the supplied rule extract. If it goes out anyway, the firm would be publishing a prohibited guarantee and a provably false statement about its own controls, in front of the regulator that holds the filing.

```json
{
  "verdict": "REWORK",
  "findings": [
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "page.md headline: \"Earn a guaranteed 6% a year, risk-free.\"",
      "scenario": "States a guaranteed return and no risk, prohibited by RICR 4.2; also false on the firm's own data (2021 net return 4.2% < 6%). Regulator sees a direct breach; customers earning under 6% have a misrepresentation claim. The disclaimer contradicts rather than cures it.",
      "fix": "Remove 'guaranteed', '6% a year' and 'risk-free'; replace with a non-promissory description that states investments carry risk, including loss of principal; reconsider 'sleep at night'."
    },
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "page.md: \"Every page on this site is reviewed and approved by our compliance officer before it goes live.\" vs compliance_procedure.md: pages 'not individually approved before they are published', 10% monthly sample",
      "scenario": "Page asserts a pre-approval process the filed procedure says does not exist; anyone comparing the page with the filing sees a false statement about the firm's controls, breaking the 'do not say anything the firm does not do' requirement.",
      "fix": "Delete the sentence, or replace it with a statement matching the filing (monthly sample review after publication)."
    },
    {
      "severity": "Medium",
      "evidence_level": "UNVERIFIED",
      "location": "page.md: \"Steady Harbor holds high-grade bonds\"",
      "scenario": "No supplied evidence of holdings; if the portfolio holds below-investment-grade or non-bond assets, the page misdescribes the product.",
      "fix": "Verify against the holdings report or investment policy and define 'high-grade', or remove the claim."
    },
    {
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "location": "page.md: \"Our five-year average return was 7.1% a year, net of fees.\"",
      "scenario": "Figure is correct (arithmetic mean 7.1%, compound ~7.09%), but the period (2021-2025) and method are not stated; ambiguous to readers and stale once 2026 results exist; the full RICR may require a stated period.",
      "fix": "State '2021-2025, annualized, net of fees', check the full rule for period requirements, and add a refresh date."
    }
  ]
}
```