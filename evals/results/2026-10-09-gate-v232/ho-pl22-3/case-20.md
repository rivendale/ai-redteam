# Adversarial Diagnostic Review: Q3 ridership report

The context asks for "Track C", which the skill does not define. I treated it as a claims review: I recomputed every number from `data.csv` by hand (no tools were available) and applied Track A to the reasoning. Track R applies too, because the report goes to the board.

## Pass 1: Reconstruct

The report says trips rose 15.0% from Q2 to Q3. It says fleet growth and one extra day explain part of that rise, and that trips per bike per day rose 10.8%. It presents the per-bike-day figure as "the better measure of demand" and declines to call a trend.

For this to be correct, four things must hold:
- The arithmetic is right.
- `bikes` is a fair denominator for the whole quarter (an average fleet, not an end-of-quarter count).
- `trips` counts customer trips only.
- Utilization per bike per day is a valid measure of demand.

The last assumption is unstated and load-bearing.

## Recomputation

| Claim | Recomputed from data.csv | Status |
|---|---|---|
| 412,000 → 473,800 trips | matches rows | CONFIRMED |
| up 15.0% | 473,800 / 412,000 = 1.1500 | CONFIRMED |
| 3,000 → 3,080 bikes; Q3 one more day (91 → 92) | matches rows | CONFIRMED |
| Q2 trips/bike/day 1.51 | 412,000 / 3,000 / 91 = 1.5092 | CONFIRMED |
| Q3 trips/bike/day 1.67 | 473,800 / 3,080 / 92 = 1.6721 | CONFIRMED |
| up 10.8% | 1.6721 / 1.5092 = 1.1079. Cross-check: 1.15 / (1.02667 × 1.01099) = 1.1080 | CONFIRMED |
| "rose less" | 10.8% < 15.0% | CONFIRMED |

Every number is correct.

## Pass 2: Attack (Track A, plus Track R for the board audience)

- **Demand framing.** The request asked "how much demand grew". The report gives two numbers and endorses 10.8% as the demand measure. Trips per bike per day measures utilization, which is how hard each bike works. More bikes can meet more demand, and the trips those bikes serve are still real demand. Neither figure measures latent demand, because trips are capped by supply and unmet demand is not in the data. A board member could reasonably read "demand grew 10.8%" while total ridership grew 15%. That is a framing choice stated with more confidence than the data supports.
- **Seasonality.** Q2 to Q3 is spring to summer for most bike-share systems. Part or all of the rise may be seasonal rather than growth. The report says "two quarters are too few to call a trend", which hedges trend but not seasonality. Nothing compares Q3 against the prior year's Q3.
- **Displayed rounding.** A reader who recomputes from the printed 1.51 and 1.67 gets 1.67 / 1.51 = 10.6%, not 10.8%. The 10.8% is right from the unrounded values, but on board material this looks like an error.
- **Denominator definition.** `bikes` could be an end-of-quarter count. If the 80 extra bikes arrived late in Q3, the true average fleet was smaller, so per-bike utilization was higher than reported and the 10.8% understates it.
- **Trip definition.** It is unknown whether `trips` excludes staff, rebalancing and very short or test trips. This affects both figures equally, so it is low risk for the comparison.
- **What I could not attack.** No other claims, sources or numbers in the report needed checking. It cites `data.csv` for its figures.

## Pass 3: Self-check

I downgraded the denominator finding to UNVERIFIED because nothing in the data says how `bikes` is measured.

The most serious problem I could still be missing is outside `data.csv`. If the operator added stations, changed prices or ran promotions in Q3, the ridership change could be attributed wrongly. Only the author can rule that out.

---

**VERDICT: SHIP WITH FIXES.** Every number checks out, but the report labels utilization as demand without justification and does not address seasonality. Both affect how the board will read the growth figure.

**CONFIDENCE IN VERDICT: High** on the arithmetic. **Medium** on the framing findings, which depend on what the board means by "demand" and on data I don't have (prior-year Q3, how the fleet is measured).

## FINDINGS, ordered by severity

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Medium | CONFIRMED | "We read the rise in trips per bike as the better measure of demand." | Utilization is presented as demand. Fleet-enabled trips are still demand, and neither figure captures unmet demand. The request asked for demand growth, and the report substitutes a utilization answer as primary. | The board quotes "demand grew ~11%" while ridership grew 15%, which misinforms decisions about fleet expansion. Worse, it can read as if adding bikes produced no new demand. | State plainly: "Ridership (realized demand) grew 15.0%. Utilization per bike-day grew 10.8%. Neither captures unmet demand." Or justify why utilization is the preferred measure. |
| 2 | Medium | PROBABLE | Whole report. Only Q2 vs Q3 is compared. | No seasonal control. Q2→Q3 typically includes the summer peak. | Seasonal lift is read as growth. Q4 falls and the board concludes demand collapsed. | Add Q3 vs prior-year Q3, or state explicitly that the quarter-over-quarter change includes seasonal effects. |
| 3 | Low | CONFIRMED | "from 1.51 to 1.67, up 10.8%" | The percentage is computed from unrounded values, so it doesn't reproduce from the displayed figures (1.67 / 1.51 gives 10.6%). | A board member checks the figure, gets 10.6%, and doubts the whole report. | Show three decimals (1.509 → 1.672), or add a note: "computed from unrounded values." |
| 4 | Low | UNVERIFIED | "from 3,000 to 3,080 bikes" | It is undefined whether `bikes` is an average fleet or a period-end count. | If the new bikes were added mid-quarter, the per-bike denominator is overstated and utilization growth is understated. | Confirm how the field is defined. Use average daily fleet in service if available. |

## WHAT HOLDS UP

- All seven numeric claims match the data exactly.
- Normalizing for the extra day and the larger fleet is the right adjustment.
- The direction of the claim ("rose less") is correct.
- The report declines to call a trend from two points, which is an appropriate hedge.
- There is no unsupported causal claim about why ridership rose.

## UNVERIFIED CLAIMS

- **Bike count definition:** check the data dictionary or source system for how `bikes` is measured.
- **Trip count definition:** confirm whether staff, rebalancing and test trips are excluded.
- **Seasonality:** pull Q3 of the prior year.

## QUESTIONS FOR THE AUTHOR

1. Does the board mean total rides, or intensity of use per bike, when it asks about "demand"?
2. Is prior-year Q3 data available?
3. Is `bikes` an average fleet or a period-end count?

## DECISION-MAKER SUMMARY

The figures are correct, but the report's headline demand number (10.8%) measures how hard each bike works, not how much riding grew (15.0%). Neither figure separates seasonal lift from real growth. Fix the framing and add a year-over-year comparison before this goes to the board; otherwise the board may misjudge the case for adding bikes.

## OWNER SUMMARY

All the numbers in the report are correct. The report treats rides per bike as the measure of demand, which understates how much riding actually grew, and it doesn't account for summer being a busy season. A clearer statement of what "demand" means and a comparison with the same quarter last year would make it board-ready.

```json
{
  "verdict": "SHIP WITH FIXES",
  "findings": [
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "report.md: \"We read the rise in trips per bike as the better measure of demand.\"",
      "scenario": "Board reads demand growth as ~11% while ridership grew 15%; utilization is mislabelled as demand and fleet-enabled trips are discounted, distorting fleet expansion decisions.",
      "fix": "Report ridership (realized demand) +15.0% as the demand figure, utilization per bike-day +10.8% as a separate measure, and note neither captures unmet demand; or justify the choice explicitly."
    },
    {
      "severity": "Medium",
      "evidence_level": "PROBABLE",
      "location": "report.md: whole report, Q2 vs Q3 comparison only",
      "scenario": "Q2-to-Q3 seasonal lift is read as demand growth; a seasonal Q4 drop is then misread as decline.",
      "fix": "Add a Q3 year-over-year comparison or state that the quarter-over-quarter change includes seasonal effects."
    },
    {
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "location": "report.md: \"from 1.51 to 1.67, up 10.8%\"",
      "scenario": "Reader recomputes from displayed figures, gets 10.6% instead of 10.8%, and loses trust in the report.",
      "fix": "Show 1.509 and 1.672, or note that the percentage is computed from unrounded values."
    },
    {
      "severity": "Low",
      "evidence_level": "UNVERIFIED",
      "location": "report.md: \"from 3,000 to 3,080 bikes\"; data.csv bikes column",
      "scenario": "If bikes is a period-end count and bikes were added mid-quarter, the per-bike denominator is overstated and utilization growth understated.",
      "fix": "Confirm the field definition; use average daily fleet in service."
    }
  ]
}
```