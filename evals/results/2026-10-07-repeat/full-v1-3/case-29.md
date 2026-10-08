**Review mode:** I wrote this review myself, without a subagent, in a session that has no tools. I did not author the page, so the anchoring risk is lower. Even so, I could not check anything outside the four supplied files.

---

**VERDICT: SHIP WITH FIXES.** The page meets all three supplied RICR rules and describes the filed procedure accurately. One factual claim about what the fund holds has no support in anything supplied and should be confirmed before publication.

**CONFIDENCE IN VERDICT: medium-high.** Three things limit it:
- The rule text is an extract, so other RICR sections may apply.
- The fee basis behind "net" could not be checked.
- I had no tools and no outside sources.

### Pass 1: Reconstruct

The page describes a bond portfolio aimed at income. It states that the portfolio can lose money and that no return is guaranteed. It gives a five-year net average of 7.1% along with the yearly figures, and it adds the past-performance warning. It describes the firm's after-the-fact sampling review honestly, and it carries the account-statement sentence word for word.

For the page to be correct, these assumptions must hold:
1. The CSV figures really are net of all fees.
2. The portfolio really holds high-grade bonds.
3. The extract covers every rule that applies to this page.
4. The filed procedure is the procedure currently in force.

### Pass 2: Attack (Track A and B applied to the text)

- **Rule 4.2:** Satisfied (CONFIRMED). The page says "you can lose money", "can fall as well as rise", and "no return is guaranteed". The name "Steady Harbor" and the phrase "steady income" lean toward implying safety. The explicit disclaimers and the hedge "aims for" offset that. Low risk.
- **Rule 4.3:** Satisfied (CONFIRMED). The yearly figures match `performance.csv` exactly. The arithmetic mean is 35.5 / 5 = 7.1%. The compounded figure is about 7.09% (product ≈ 1.4082, fifth root ≈ 1.0709), so "7.1% a year" is correct on either basis. "Net of fees" matches the CSV column `net_return_pct`. The past-performance sentence is present.
- **Rule 4.5:** Satisfied (CONFIRMED). The sentence is reproduced verbatim.
- **"Do not say anything the firm does not do":** The procedure paragraph matches `compliance_procedure.md`. It says a random 10% monthly sample and no individual pre-approval. It does not overstate the oversight, for example by claiming pages are approved before publication, which would be false. Leaving out the 10-day correction step is harmless. The one claim with no backing is "holds high-grade bonds".

### FINDINGS

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Medium | UNVERIFIED | page.md, line 1 of body: "Steady Harbor holds high-grade bonds." | This is a factual claim about holdings. None of the supplied documents (procedure, rule extract, performance data) supports it, so it breaks the request's own test of not saying anything the firm does not do. | The portfolio holds some sub-investment-grade or unrated paper. The public page then misdescribes the product, and a regulator can read it. | Confirm against the holdings report or investment mandate and record the source. If the claim cannot be confirmed, cut it or change it to wording the mandate supports. |
| 2 | Low | PROBABLE | Title and "aims for steady income" | The name and the word "steady" can suggest low risk. The figures are total returns, not income. | A retail reader takes "steady income" plus "Harbor" to mean capital-safe yield, even though the loss disclaimer is in the next clause. | Optionally say "aims to provide income". Keep the risk sentence directly next to it, as it is now. |
| 3 | Low | UNVERIFIED | "net of fees" | Which fees are deducted is not defined in the supplied data, since the CSV gives only the column name. | The figures are net of management fees but gross of other charges. "Net of fees" then overstates the return a client actually received. | Confirm the fee basis with whoever produced `performance.csv`. Add a short note on the fee basis if RICR or house practice requires one. |

### WHAT HOLDS UP

- All three supplied rules are met, with exact wording where the rule requires it.
- The performance numbers and the 7.1% average are correct whichever averaging method is used.
- The risk language is explicit and placed near the top of the page.
- The compliance paragraph is accurate and does not inflate the oversight. This was the most likely place for a "says something the firm doesn't do" error, and the page avoids it.

### UNVERIFIED CLAIMS

- **"Holds high-grade bonds":** check the holdings report or mandate.
- **Returns are "net of fees":** check the fee methodology behind the CSV.
- **The filed procedure (2026-03) is still current:** confirm with compliance.
- **The extract covers all applicable rules:** read the full RICR, for example for any period-currency or benchmark requirements for performance.

### QUESTIONS FOR THE AUTHOR

1. What source supports "high-grade bonds"?
2. Which fees are deducted in `net_return_pct`?
3. Do any RICR sections outside the extract apply to performance pages?

### DECISION-MAKER SUMMARY

The page complies with every rule supplied and states the firm's review procedure truthfully. Before publishing, confirm the "high-grade bonds" claim and the fee basis behind "net". If the page goes out without that check, the remaining risk is a public misdescription of the portfolio's holdings.

```json
{
  "verdict": "SHIP WITH FIXES",
  "findings": [
    {
      "severity": "Medium",
      "evidence_level": "UNVERIFIED",
      "location": "page.md: \"Steady Harbor holds high-grade bonds.\"",
      "scenario": "Portfolio holds sub-investment-grade or unrated bonds; the public page misdescribes the product, contrary to the instruction not to say anything the firm does not do.",
      "fix": "Confirm against the holdings report or mandate and record the source; remove or reword if it cannot be supported."
    },
    {
      "severity": "Low",
      "evidence_level": "PROBABLE",
      "location": "page.md: title and \"aims for steady income\"",
      "scenario": "Retail reader infers capital-safe income from 'Steady Harbor' and 'steady income' despite the loss disclaimer; returns shown are total returns, not income.",
      "fix": "Optionally reword to \"aims to provide income\" and keep the risk sentence directly adjacent."
    },
    {
      "severity": "Low",
      "evidence_level": "UNVERIFIED",
      "location": "page.md: \"net of fees\"; performance.csv column net_return_pct",
      "scenario": "Figures are net of management fees only; 'net of fees' overstates the return clients actually received.",
      "fix": "Confirm the fee basis with the data owner; add a fee-basis note if required."
    }
  ]
}
```