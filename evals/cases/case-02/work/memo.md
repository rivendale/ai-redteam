# Decision memo: keep session data in Postgres; do not add Redis yet

**Recommendation:** keep sessions in the existing Postgres cluster. Re-evaluate if the trigger below is hit.

## Evidence
The load test is in `evidence/bench.csv` (sessions table, the real schema, the production instance class, 10-minute runs).

| requests per second | p95 latency | errors |
|---|---|---|
| 200 | 6 ms | 0 |
| 400 | 8 ms | 0 |
| 800 | 12 ms | 0 |
| 1,600 | 31 ms | 0 |
| 3,200 | 118 ms | 14 |

- Our measured peak is **200 requests per second** (the busiest minute of the last quarter), so the test at 800 requests per
  second is **4 times** that peak and still shows 12 ms against a 50 ms target.
- The 50 ms target is first exceeded between 1,600 and 3,200 requests per second, **8 to 16 times** today's peak.

## Alternatives
- **Add Redis.** Roughly $95 per month for a managed node, plus a new failure mode and a second place sessions can be lost.
  It buys headroom we do not need at 200 requests per second.
- **Add a read replica.** Does not help: session writes dominate.
- **Do nothing and watch.** Chosen.

## What would change this decision
Trigger: p95 above 40 ms at the weekly peak, or sustained traffic above 1,000 requests per second. Moving sessions to Redis
later is a contained change (one module, one data migration of short-lived rows); we estimate one week.

## What this does not claim
The test used synthetic keys. It does not model a bot burst of 5,000 requests per second; the load balancer limit of 2,000
requests per second per client address is the protection there.
