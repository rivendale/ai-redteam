# Adversarial Diagnostic Review: Q3 Ridership Report

The requested "Track C" does not exist in the skill. I applied its intent (recompute every number from data.csv and check each claim) under Track A's Facts and Logic checks. I had no tools, so all arithmetic below was done by hand from the two rows shown.

## Pass 1: Reconstruct

The report says trips grew 15.0% from Q2 to Q3. After adjusting for a larger fleet and one extra day, trips per bike per day grew 10.8%. It presents the 10.8% figure as "the better measure of demand" and warns that two quarters are too few to call a trend.

For this to be correct, four things must hold:
- The arithmetic matches data.csv.
- Trips per bike per day is a valid measure of demand.
- `bikes` is a fleet measure comparable across quarters (an average, not a point-in-time count).
- The Q2→Q3 change reflects demand rather than seasonality.

The fourth assumption is unstated.

## Recomputation

| Claim | Recomputed | Result |
|---|---|---|
| Trips 412,000 → 473,800 | Matches data.csv | ✔ |
| Up 15.0% | 473,800 / 412,000 = 1.1500 | ✔ |
| Fleet 3,000 → 3,080 | Matches (+2.67%, not stated in report) | ✔ |
| Q3 has one more day | 92 vs 91; also matches the calendar (Apr–Jun = 91, Jul–Sep = 92) | ✔ |
| Q2 trips/bike/day 1.51 | 412,000 / (3,000 × 91) = 412,000 / 273,000 = 1.5092 | ✔ |
| Q3 trips/bike/day 1.67 | 473,800 / (3,080 × 92) = 473,800 / 283,360 = 1.6721 | ✔ |
| Up 10.8% | 1.6721 / 1.5092 = 1.1080 | ✔ (from unrounded values; 1.67 / 1.51 would give 10.6%) |
| "rose less" than trips | 10.8% < 15.0% | ✔ |
| Not in report: trips per day | 4,527.5 → 5,150.0 = +13.75% | — |

Every number in the report is arithmetically correct.

## Verdict

**VERDICT: SHIP WITH FIXES.** The numbers are right, but the report gives the board a utilization figure labelled as demand growth and ignores seasonality.

**CONFIDENCE IN VERDICT: medium.** Two things limit it: I don't know how `bikes` is defined, and there is no prior-year data to check how much of the change is seasonal.

## Findings

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | High | CONFIRMED (logic) | report.md L5: "We read the rise in trips per bike as the better measure of demand." | Trips per bike per day measures fleet **utilization**, not demand. Dividing by fleet size removes real riders whenever new bikes are actually used. Utilization rose while the fleet grew, which suggests demand outpaced supply, the opposite of "demand grew less." Trips are also realized ridership; if the system is capacity-limited, real demand is higher still. | The board reads "demand grew 10.8%." It underweights growth and may under-invest in fleet expansion even though rising utilization is a sign of a capacity shortfall. | Report calendar-adjusted demand as trips per day (+13.75%) and label 10.8% as utilization. If the 10.8% framing is kept, justify it explicitly. |
| 2 | High | PROBABLE (domain knowledge; data has no prior year) | report.md L3 and L5 | Q2 (Apr–Jun) → Q3 (Jul–Sep) is a seasonal comparison. Bike-share ridership typically peaks in summer, and neither figure is adjusted for season. The "two quarters" caveat addresses trend, not seasonality. | The board takes the 15% or 10.8% as underlying growth when much or all of it may be seasonal. Q4 then "drops" and looks like a decline. | Add a Q3-over-Q3 (year-on-year) comparison, or state plainly that the quarter-on-quarter figure includes seasonal effects and is not a growth rate. Settle by pulling last year's Q2 and Q3. |
| 3 | Medium | UNVERIFIED | data.csv column `bikes`; report.md L5 | The report doesn't say whether `bikes` is an average active fleet or an end-of-quarter count. If it is end of quarter, the 80 bikes added in Q3 were not available all quarter. That makes the per-bike denominator too large and the 10.8% too low. | The utilization figure is biased. The size of the bias depends on when bikes were added. | Confirm the definition with the data owner. Use average available bikes, or bike-days, as the denominator. |
| 4 | Low | CONFIRMED | report.md L5: "rise in trips per bike" | Says "trips per bike" right after defining "trips per bike per day." They are different metrics. | A reader recomputes trips per bike (137.3 → 153.8, +12.0%) and finds the figure doesn't match. | Use the full metric name consistently. |

## What holds up

- All stated numbers and percentages recompute exactly from data.csv.
- The 10.8% is computed from unrounded values, which is correct.
- The day count matches the calendar.
- Normalizing for days at all is appropriate.
- The "too few to call a trend" caveat is honest.
- The data source is cited.

## Unverified claims

- **Definitions of `trips` and `bikes`.** Ask the data owner whether `trips` counts unique rides, excludes rebalancing trips, and so on, and whether `bikes` is an average or a quarter-end count.
- **That data.csv is the complete and final Q3 figure.** Confirm against the source system's extract date.
- **Size of the seasonal effect.** Settle with prior-year quarterly data.

## Questions for the author

1. Why is trips per bike per day "the better measure of demand" instead of trips per day? Would you report it as utilization?
2. Is `bikes` an average fleet or a quarter-end count?
3. Is prior-year Q3 data available for a year-on-year comparison?

## Decision-maker summary

The numbers are correct, but the headline demand figure (10.8%) is a utilization measure. The cleaner calendar-adjusted demand growth is 13.75%, and neither figure separates out summer seasonality. Before the report goes to the board, relabel the metrics and add a year-on-year comparison or an explicit seasonality caveat. If it ships as is, the board may misjudge both growth and fleet needs.

## Owner summary

The arithmetic in the report is correct. However, it describes how busy each bike was as if that were a measure of how many people wanted to ride, which understates demand. It also compares spring to summer without allowing for the usual summer rise, so the wording should be fixed and last year's same-quarter figures added before the board sees it.

```json
{
  "verdict": "SHIP WITH FIXES",
  "findings": [
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "location": "report.md L5: 'We read the rise in trips per bike as the better measure of demand.'",
      "scenario": "Trips per bike per day is fleet utilization, not demand; dividing by fleet removes real riders served by new bikes, and rising utilization alongside fleet growth signals demand outpacing supply. Board reads 'demand grew 10.8%' and may under-invest in capacity.",
      "fix": "Report calendar-adjusted demand as trips per day (4,527.5 -> 5,150.0, +13.75%); label 10.8% as utilization, or justify the choice explicitly."
    },
    {
      "severity": "High",
      "evidence_level": "PROBABLE",
      "location": "report.md L3 and L5 (Q2 -> Q3 comparison)",
      "scenario": "Q2 to Q3 spans spring to summer; bike-share ridership is typically seasonal, so the 15% / 10.8% rise may be largely seasonal. Board takes it as underlying growth, and a Q4 drop then looks like decline.",
      "fix": "Add a Q3 year-on-year comparison, or state that quarter-on-quarter figures include seasonal effects; pull prior-year Q2/Q3 data to settle."
    },
    {
      "severity": "Medium",
      "evidence_level": "UNVERIFIED",
      "location": "data.csv column 'bikes'; report.md L5",
      "scenario": "If 'bikes' is a quarter-end count, bikes added during Q3 inflate the denominator and bias trips per bike per day downward.",
      "fix": "Confirm the definition with the data owner; use average available bikes or bike-days as the denominator."
    },
    {
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "location": "report.md L5: 'rise in trips per bike'",
      "scenario": "Label drops 'per day'; trips per bike alone is +12.0%, so a reader recomputing gets a mismatch.",
      "fix": "Use the full metric name 'trips per bike per day' consistently."
    }
  ]
}
```