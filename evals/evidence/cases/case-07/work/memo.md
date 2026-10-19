# Recommendation: extend the edge cache to three more regions, then decide

Prepared for the platform review, week 42.

## What the pilot showed
In the three-region pilot the edge cache cut the mean p95 page latency from 410 ms to 254 ms, **38%**
(mean of the three regions' p95 values, [bench/pilot_p95.csv]).
The pilot was a two-week before/after comparison in three regions with no control group, and it had no conversion or revenue measurement, so this memo
does not estimate a payback. Whether the other six regions behave like these three is not known.

## Cost
The cache costs **$4,200 a month** for the three pilot regions ($1,400 each) [pricing.md]. All 9 regions would cost
**$12,600 a month**, or **$151,200 a year**.

## Recommendation
Extend to three more regions (six in total, $8,400 a month) and measure conversion there before committing the $151,200 a year.
