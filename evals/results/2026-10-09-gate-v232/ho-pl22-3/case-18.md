# Adversarial review: battery supplier memo

**VERDICT: REJECT.** The memo recommends the supplier with the highest five-year total cost of ownership, because it compares purchase price and calls that total cost of ownership.

**CONFIDENCE IN VERDICT: high.** The arithmetic below uses only the memo and suppliers.csv. One input is unverified: the memo's own "once a day" usage figure. The ranking survives any rate above about 0.55 cycles a day.

## Pass 1: Reconstruct

The memo claims Zesto has the lowest five-year total cost of ownership, at "$335 per battery", and recommends Zesto for a 3,080-bike fleet. For that to be correct, purchase price alone would have to decide five-year cost. That would only hold if every battery lasted the full five years or replacement cost nothing.

The load-bearing assumptions are:
- **Usage:** each bike uses one cycle a day. The memo states this; neither the request nor the CSV supplies it.
- **Cycle life:** the CSV figures are comparable across suppliers.
- **Replacement:** a battery is replaced when it reaches its cycle life.
- **Labour:** swap labour applies to each battery installed.

## Pass 2: Attack (Track A)

### Recomputation from suppliers.csv at the memo's one cycle a day

Five years is about 1,825 cycles; 1,826 with a leap day, which changes no count. "Batteries per bike" means batteries bought per bike over five years.

| Supplier | Cycle life | Batteries per bike | Cost per bike: batteries + $15 labour each | Fleet of 3,080 |
|---|---|---|---|---|
| Volta | 2,000 | 1 | $410 + $15 = **$425** | **$1,309,000** |
| Amperia | 1,000 | 2 | $760 + $30 = **$790** | **$2,433,200** |
| Zesto | 600 | 4 (3.04 needed) | $1,340 + $60 = **$1,400** | **$4,312,000** |

Volta wins under every reasonable treatment:
- **Without labour:** Volta $1.26M, Amperia $2.34M, Zesto $4.13M.
- **Pro-rated to cost per cycle:** Volta $0.21, Amperia $0.40, Zesto $0.58.
- **Zesto given only 3 batteries:** Zesto is still $1,050 per bike against Volta's $425.

Choosing Zesto over Volta costs about **$3.0M** over five years.

### How sensitive the ranking is to usage (cycles per bike over five years)

| Cycles over 5 years | Rate | Cheapest supplier |
|---|---|---|
| 600 or fewer | under about 0.33 a day | Zesto ($350) |
| 601 to 1,000 | about 0.33 to 0.55 a day | Amperia ($395, against Volta $425) |
| more than 1,000 | above about 0.55 a day | Volta, and Volta stays cheapest at 2 cycles a day ($850 against $1,580 and $2,450) |

So Zesto is only right if bikes average under about one cycle every three days. That contradicts the memo's own assumption.

### Other checks

- **Facts:** the memo's prices match the CSV. The total cost of ownership figure is not a total cost of ownership; it is the unit price relabelled.
- **Logic:** "lowest price, therefore lowest total cost" is a non-sequitur. The memo itself states daily use, but never applies it to the 600-cycle life.
- **Drift:** the request asked for a five-year comparison. The memo answers "which battery is cheapest to buy," which is an easier question.
- **Counter-case:** the strongest case for the opposite conclusion (Volta) is just the request's own method applied to the data. The memo does not survive it.
- **Pre-mortem: why this decision fails in a year:**
  1. Zesto packs wear out around month 20, and the replacement budget runs about 3× over.
  2. Swap labour and bike downtime from about 9,200 extra swaps (3 per bike × 3,080) were never planned.
  3. The cycle-life figures were not comparable, and real-world life is worse still.
- **Missing information:** the memo does not cover:
  - measured cycles per bike per day from fleet telemetry;
  - the test standard behind each cycle-life figure (depth of discharge, end-of-life capacity threshold);
  - warranty terms;
  - price escalation over five years;
  - disposal and recycling cost;
  - residual value (a Volta pack has about 175 cycles left at year 5);
  - discount rate;
  - supplier financial and supply risk over a five-year lock-in.

## FINDINGS

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | memo.md: "Zesto has the lowest total cost of ownership at $335 per battery. We recommend Zesto." | Total cost of ownership is equated with unit price. The cycle_life and swap_labor_usd columns are ignored. | At one cycle a day, Zesto costs $1,400 per bike against Volta's $425. Across 3,080 bikes that is $4.31M against $1.31M, about $3.0M of avoidable spend. | Compute ceil(1,825 / cycle_life) × (price + labour) per supplier and scale to 3,080 bikes. The memo's ranking should invert. |
| 2 | High | CONFIRMED | memo.md table (price only) | The requested five-year comparison is missing entirely: no replacement count, no labour, no fleet total. This is drift from "total cost of ownership over five years" to "purchase price." | A decision-maker reads the table as the analysis and approves a five-year contract on the wrong basis. | Add batteries per bike, five-year cost per bike and fleet total, with the formula shown. |
| 3 | Medium | PROBABLE | memo.md: "Each bike uses its battery once a day." | The usage rate is unsourced, and the winner changes with it: Zesto at 600 cycles or fewer over five years, Amperia from 601 to 1,000, Volta above 1,000. | If real usage is about 0.4 cycles a day, Amperia, not Volta, is cheapest. | Source cycles per bike from fleet telemetry and show the sensitivity bands. |
| 4 | Medium | UNVERIFIED | suppliers.csv cycle_life column | The cycle-life figures may not be comparable (different depth of discharge, different end-of-life capacity threshold, different test standard). | Volta's 2,000 is rated at 70% end-of-life and Zesto's 600 at 80%, so the real gap differs from the stated one. | Get each supplier's spec sheet and test conditions, and normalise. |
| 5 | Medium | PROBABLE | memo.md (whole) | Several costs and risks are absent: warranty, price escalation, disposal, downtime per swap, residual value, discounting, and supplier risk over a five-year single-source lock-in. Given the 3× gap these are unlikely to change Volta's lead, but they are not addressed. | A supplier failure or a warranty gap goes unpriced for five years. | Add these lines, or state them explicitly as excluded with a reason. Consider a pilot or dual sourcing. |

## WHAT HOLDS UP

- The prices in the memo match suppliers.csv exactly.
- The one-cycle-a-day assumption is at least stated rather than hidden.
- There is no fabricated data.

## UNVERIFIED CLAIMS

- **"Each bike uses its battery once a day."** Confirm from fleet charge logs.
- **Cycle-life comparability.** Confirm from supplier datasheets.
- **Swap labour of $15 flat for all three suppliers.** Confirm from operations or a time study.

## QUESTIONS FOR THE AUTHOR

1. What is measured average cycles per bike per day? If it is below about 0.55, the recommendation changes again.
2. Are the cycle-life figures rated under the same end-of-life threshold and depth of discharge?
3. Was the omission of cycle life and labour deliberate? If so, on what basis?

## DECISION-MAKER SUMMARY

Do not adopt Zesto. On the memo's own usage assumption and the supplied data, Zesto is the most expensive option (about $4.3M against Volta's about $1.3M over five years), and Volta is cheapest. Before signing, confirm actual usage and that the cycle-life ratings are comparable, because below about 0.55 cycles a day Amperia becomes cheapest.

## OWNER SUMMARY

The memo picked the battery that is cheapest to buy, not the one that is cheapest to own. The cheap batteries wear out much sooner and would need replacing about four times in five years. Using the same data, a different supplier would save roughly three million dollars, so the choice should be redone after checking how often bikes are actually used.

```json
{
  "verdict": "REJECT",
  "findings": [
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "memo.md: 'Zesto has the lowest total cost of ownership at $335 per battery. We recommend Zesto.'",
      "scenario": "TCO equated with unit price; cycle_life and swap_labor_usd ignored. At 1 cycle/day over 5 years (~1,825 cycles) Zesto needs 4 batteries per bike ($1,400) vs Volta 1 ($425); fleet of 3,080 = $4,312,000 vs $1,309,000, ~$3.0M overspend.",
      "fix": "Compute ceil(1825/cycle_life) x (price + swap labor) per supplier, scale to 3,080 bikes; ranking becomes Volta < Amperia < Zesto."
    },
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "location": "memo.md price table",
      "scenario": "Requested five-year comparison is absent (no replacement count, labor, or fleet total); question drifted to purchase price and a five-year contract is approved on the wrong basis.",
      "fix": "Add batteries per bike, five-year cost per bike, and fleet total with formulas shown."
    },
    {
      "severity": "Medium",
      "evidence_level": "PROBABLE",
      "location": "memo.md: 'Each bike uses its battery once a day.'",
      "scenario": "Usage rate is unsourced and decisive: Zesto wins at <=600 five-year cycles, Amperia at 601-1,000, Volta above 1,000 (~0.55/day). At ~0.4/day Amperia is cheapest.",
      "fix": "Source cycles per bike from fleet telemetry and present sensitivity bands."
    },
    {
      "severity": "Medium",
      "evidence_level": "UNVERIFIED",
      "location": "suppliers.csv cycle_life column",
      "scenario": "Cycle lives may be rated under different end-of-life thresholds or depth of discharge, so the real gap differs from stated.",
      "fix": "Obtain each supplier's datasheet test conditions and normalise."
    },
    {
      "severity": "Medium",
      "evidence_level": "PROBABLE",
      "location": "memo.md (whole)",
      "scenario": "Warranty, price escalation, disposal, swap downtime, residual value, discounting and five-year single-supplier risk are unpriced; supplier failure or warranty gaps surface mid-contract.",
      "fix": "Add these cost lines or state them as excluded with a reason; consider pilot or dual sourcing."
    }
  ]
}
```