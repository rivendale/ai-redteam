# Recommendation: roll out the edge cache to all regions

Prepared for the platform review, week 42.

## What the pilot showed
In the three-region pilot the edge cache cut **p95 page latency by 38%** (410 ms to 254 ms) [bench/pilot_p95.csv].
Faster pages lift conversion, so we expect the cache to pay for itself within one quarter.

## Cost
The cache costs **$4,200 a month** for the three pilot regions ($1,400 each) [pricing.md]. Rolling it out to all 9 regions costs
**$12,600 a month**, or **$151,200 a year**.

## Recommendation
Roll the cache out to all 9 regions this quarter.
