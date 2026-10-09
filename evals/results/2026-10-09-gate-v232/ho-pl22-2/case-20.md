# Adversarial Diagnostic Review: Q3 ridership report

**Note on track:** The context asks for "Track C (claims review)". The prompt defines only Tracks A, B and R. I applied Track A with a full recomputation of every number from `data.csv`, which is what the context asks for. I have no tools in this session, so the recomputation below is done by hand and shown in full so it can be checked.

## Pass 1: Reconstruct

The report says trips rose 15.0% from Q2 to Q3. It then adjusts for fleet size and day count, getting trips per bike per day of 1.51 → 1.67, up 10.8%, and names that as "the better measure of demand." It cautions that two quarters cannot establish a trend.

For this to be correct and fit the request, several things must hold:
- The arithmetic must be right.
- `trips`, `bikes` and `days` must mean what the report assumes: completed trips, average fleet in service, and calendar days.
- Trips per bike per day must actually measure demand.
- A Q2→Q3 change must be a fair read of "growth" without a seasonal adjustment. This one is unstated.

## Recomputation

| Claim | Recomputed | Result |
|---|---|---|
| Q2 trips 412,000; Q3 473,800 | Matches data.csv | ✔ |
| Up 15.0% | 473,800 / 412,000 = 1.1500 (412,000 × 1.15 = 473,800 exactly) | ✔ |
| Fleet 3,000 → 3,080 | Matches | ✔ (+2.67%) |
| "Q3 has one more day" | 92 vs 91 | ✔ (also matches calendar Apr–Jun = 91, Jul–Sep = 92) |
| Q2 trips/bike/day 1.51 | 412,000 / (3,000 × 91) = 412,000 / 273,000 = 1.5092 | ✔ |
| Q3 trips/bike/day 1.67 | 473,800 / (3,080 × 92) = 473,800 / 283,360 = 1.6721 | ✔ |
| Up 10.8% | 1.6721 / 1.5092 = 1.1079 → 10.8% | ✔ (from unrounded values; the displayed 1.67/1.51 gives 10.6%) |
| Not stated: trips per day | 4,527.5 → 5,150.0 = +13.75% | omitted |

Every stated number is correct.

## Pass 2: Attack (Track A)

**Facts.** All numbers trace to `data.csv` and recompute correctly. Nothing is fabricated. The citation is present.

**Logic.** The weak step is "We read the rise in trips per bike as the better measure of demand." Trips per bike per day measures **fleet utilization**, not demand.
- If the 80 added bikes went into new areas or relieved stock-outs, they create trips. Dividing by fleet then removes real demand growth.
- If demand is supply-constrained (empty docks at peak), utilization understates demand.

The natural demand measure that removes the calendar effect without removing supply-driven trips is **trips per day: +13.75%**. The report never gives it. The board gets two numbers, 15.0% and 10.8%, and the report steers them to the lower one with no justification.

**Unstated assumption: seasonality.** Q2 to Q3 is spring into peak summer for most bike-share systems. A quarter-on-quarter rise may be mostly seasonal and say little about underlying demand growth. Comparing Q3 with the prior year's Q3 is the standard test, and `data.csv` has no such row. The report's "too few to call a trend" caveat is correct, but it does not name seasonality. That is the caveat a board most needs.

**Definitions.** The report assumes `bikes` is an average in-service fleet. If it is an end-of-quarter count, the denominator is wrong. If the 80 bikes arrived late in Q3, per-bike utilization is understated. The report also assumes `trips` excludes rebalancing and test trips. Both are unverified.

**Counter-case.** "Demand grew about 14–15%. The fleet addition was a response to demand, not a confounder, so dividing it out double-penalizes growth." This argument is at least as strong as the report's. The report does not address it.

**Pre-mortem.**
1. The board budgets on 10.8% or 15% "growth" that was mostly the summer season, and Q4 falls.
2. The board reads 10.8% as demand when it was utilization, and under-invests in fleet.
3. `bikes` turns out to be a period-end count, and the per-bike figure is restated.

**Requirement fit.** The request was "Say how much demand grew." The report gives two figures and picks the less obvious one. It does answer, but the answer rests on the contestable step above.

## Pass 3: Self-check

I dropped a possible finding on rounding (1.67/1.51 displays as 10.6%, not 10.8%). The report correctly computed from unrounded values, so it is at most a reader-confusion nit.

The seasonality finding is PROBABLE, not CONFIRMED. I do not know this system's climate or its history.

The most serious thing I might still be missing is how the data was generated: whether the trips count changed definition between quarters, for example a new app or new e-bikes counted differently. That would hide in the column definitions, which I cannot see.

---

**VERDICT: SHIP WITH FIXES.** Every number is correct, but the headline demand figure rests on a contestable metric choice and omits the seasonal caveat a board needs.

**CONFIDENCE IN VERDICT: medium.** It is limited by unknown column definitions (`bikes`, `trips`) and by having no year-ago data to test seasonality.

## Findings

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | High | CONFIRMED | report.md: "We read the rise in trips per bike as the better measure of demand." | Trips per bike per day is fleet utilization, not demand. Dividing by fleet removes trips the new bikes enabled. The day-adjusted demand figure (trips/day +13.75%) is omitted. | The board takes 10.8% as demand growth when the defensible day-adjusted figure is 13.75%. This leads to under-investment in fleet or misjudged targets. | Report trips/day (+13.75%) as the demand measure. Present trips/bike/day as utilization. If keeping 10.8% as headline, state why the fleet growth did not create demand. |
| 2 | High | PROBABLE | report.md: whole report; "Two quarters are too few to call a trend." | No seasonality caveat. Q2→Q3 growth in bike share is plausibly mostly seasonal. | The board treats a summer peak as structural growth, and Q4/Q1 decline is read as a collapse. | Add a seasonality caveat. Compare Q3 against the prior year's Q3 (requires data not in data.csv), or state that no YoY comparison is possible. |
| 3 | Medium | UNVERIFIED | data.csv columns `bikes`, `trips` | The report assumes `bikes` is an average in-service fleet and `trips` is defined the same way in both quarters. | If `bikes` is an end-of-quarter count, or the trip definition changed, the 10.8% (and possibly the 15.0%) is wrong. | Confirm the column definitions with the data owner and state them in the report. |
| 4 | Low | CONFIRMED | report.md: "from 1.51 to 1.67, up 10.8%" | Recomputing from the displayed rounded values gives 10.6%, not 10.8%. | A board member checks 1.67/1.51 and believes the report has an error. | Show two more decimals (1.509 → 1.672) or footnote that the % uses unrounded values. |

## What holds up

- All six stated figures recompute exactly from `data.csv`, including the 15.0% (exact) and the 10.8% (from unrounded values).
- The day counts match calendar quarters.
- The "too few quarters for a trend" caveat is correct.
- Adjusting for fleet and days is the right instinct. The problem is which adjusted figure gets labelled "demand."

## Unverified claims

- **That `bikes` is an average in-service fleet.** Confirm the column definition with the data owner.
- **That trips are counted consistently in both quarters.** Confirm with the data owner or the system changelog.
- **That trips per bike is "the better measure of demand."** The report gives no support. Confirm with a stated rationale, or with evidence that the added bikes did not open new stations or areas.

## Questions for the author

1. Is `bikes` an average in-service fleet or a period-end count, and when did the 80 bikes enter service?
2. Why trips per bike rather than trips per day as the demand measure? Did the new bikes open new stations or areas?
3. Is Q3 of the prior year available for a year-over-year comparison?

## Decision-maker summary

The numbers are right, but the report calls a utilization figure (+10.8%) "demand." It also omits the plain day-adjusted demand growth (+13.75%) and does not warn that summer seasonality may explain much of the rise. Fix the headline measure and add the seasonality caveat before the board sees it. If it ships as is, the board may plan on a growth figure that is both mislabelled and seasonal.

## Owner summary

All the figures in the report are calculated correctly from the data. However, the report labels a measure of how hard each bike is used as "demand." It also leaves out the simpler figure showing daily trips grew by about 14%. It should also warn that the summer season likely accounts for much of the increase before it goes to the board.

```json
{
  "verdict": "SHIP WITH FIXES",
  "findings": [
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "location": "report.md: \"We read the rise in trips per bike as the better measure of demand.\"",
      "scenario": "Trips per bike per day (+10.8%) measures fleet utilization, not demand; dividing by fleet strips out trips the 80 new bikes enabled. The day-adjusted demand figure, trips per day 4,527.5 -> 5,150.0 (+13.75%), is omitted. Board reads 10.8% as demand growth and under-invests or sets wrong targets.",
      "fix": "Headline trips per day (+13.75%) as demand growth; present trips per bike per day as utilization; justify explicitly if keeping 10.8% as the demand figure."
    },
    {
      "severity": "High",
      "evidence_level": "PROBABLE",
      "location": "report.md: whole report; \"Two quarters are too few to call a trend.\"",
      "scenario": "Q2->Q3 is spring into peak summer for bike share; the rise may be largely seasonal. Board treats it as structural growth and misreads the Q4 decline.",
      "fix": "Add an explicit seasonality caveat; compare Q3 with the prior year's Q3, or state that no year-over-year data is available."
    },
    {
      "severity": "Medium",
      "evidence_level": "UNVERIFIED",
      "location": "data.csv columns `bikes` and `trips`",
      "scenario": "If `bikes` is a period-end count rather than average in-service fleet, or the trip definition changed between quarters, the 10.8% (and possibly the 15.0%) is wrong.",
      "fix": "Confirm column definitions and when the 80 bikes entered service with the data owner; state the definitions in the report."
    },
    {
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "location": "report.md: \"from 1.51 to 1.67, up 10.8%\"",
      "scenario": "Recomputing from the displayed rounded values gives 1.67/1.51 = 10.6%, so a board member checking the arithmetic thinks the report is wrong; the true figure from unrounded values (1.5092 -> 1.6721) is 10.8%.",
      "fix": "Show three decimals (1.509 -> 1.672) or footnote that the percentage uses unrounded values."
    }
  ]
}
```