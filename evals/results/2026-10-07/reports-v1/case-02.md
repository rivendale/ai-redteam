**Review setup:** The memo was not written in this conversation, so this review does not inherit the author's reasoning. No tools were available, so every check below was done by reading the memo against `evidence/bench.csv` and the request.

VERDICT: **SHIP WITH FIXES.** The main recommendation (keep sessions in Postgres) is supported by the data with large margin, but one stated safeguard does not hold, and the benchmark's setup is asserted rather than shown.

CONFIDENCE IN VERDICT: **Medium-high.** What limits it:
- I could not see how the benchmark was run.
- I could not check whether one request equals one session operation.
- I could not check the price or migration-time estimates.

## Pass 1: Reconstruct

The memo recommends keeping sessions in Postgres. Its case is that measured p95 latency is 12 ms at 4× the current peak and 31 ms at 8×, against a 50 ms target. It treats Redis as unneeded cost plus a new failure mode, and sets triggers (p95 above 40 ms at the weekly peak, or sustained traffic above 1,000 rps) for revisiting.

For the memo to be correct, these must be true:
1. The benchmark represents production: same schema, instance class, realistic payloads, and the shared-cluster load that exists at peak.
2. "Requests per second" in the benchmark matches "requests per second" in the 200 rps peak figure.
3. The minute-level peak does not hide sub-minute bursts near the knee.
4. Long-running effects that a 10-minute run cannot show stay small.
5. Moving to Redis later really is a one-week contained change.

**Arithmetic check:** Every number in the memo's table matches the CSV. The multiples (4×, 8×, 16×) are correct, and so is the claim that the 50 ms target is first crossed between 1,600 and 3,200 rps. **CONFIRMED.**

## Findings

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Medium | CONFIRMED (logic) | "What this does not claim": "the load balancer limit of 2,000 requests per second per client address is the protection there" | A per-address limit does not cap total traffic. A single client is allowed 2,000 rps, which is already above the last tested point that met the target (1,600 rps). | A bot burst spread over many addresses, or one client at 2,000 rps plus normal traffic, pushes total load toward the 3,200 rps row (118 ms p95, errors). Because sessions live on the shared Postgres cluster, every other workload on that cluster slows down too. | Remove the claim, or state the real exposure. Add an aggregate rate limit or a bot-burst plan. Note that this is an argument for isolating sessions (Redis or a separate instance) that the Alternatives section never weighs. |
| 2 | Medium | UNVERIFIED | Evidence: "sessions table, the real schema, the production instance class, 10-minute runs" | The CSV has no run metadata. It does not show whether the benchmark ran on an isolated instance or alongside the app's normal peak queries. | At real peak, session queries compete with the rest of the app's database load, so p95 at 200–800 rps is worse than measured and the knee arrives earlier than 1,600 rps. | Attach the run configuration. Repeat the 800 and 1,600 rps runs against a cluster that is also carrying a replay of production queries. |
| 3 | Medium | PROBABLE | "10-minute runs"; "session writes dominate" | Session tables are write-heavy with short-lived rows, which builds up dead rows that Postgres must clean up (bloat and autovacuum load). A 10-minute run cannot show this. | After weeks of churn, index bloat and autovacuum contention raise p95 at ordinary traffic levels, and the benchmark never predicted it. | Run a soak test of 24 hours or more at 400–800 rps. Watch dead-row counts and the p95 trend, and check the expired-session cleanup job. |
| 4 | Medium | UNVERIFIED | "Our measured peak is 200 requests per second" compared with the benchmark's `requests_per_sec` | It is unclear whether one HTTP request equals one session operation. If each request does a read plus a write or a refresh, real session load is about 2–3× the peak figure. | The actual margin is around 1.5–2× instead of 4×, so the trigger fires much later than intended. | State what one benchmark "request" was, and map the 200 rps HTTP peak to session operations per second. |
| 5 | Low | PROBABLE | "busiest minute of the last quarter"; trigger "sustained traffic above 1,000 requests per second" | A one-minute average hides spikes within the minute. A "sustained" trigger at 1,000 rps also allows short peaks above 1,600 rps before it fires. | Short bursts land near the knee and cause brief periods over the target, while neither trigger fires. | Base triggers on per-second or 10-second peaks. The p95-at-weekly-peak trigger partly covers this, so keep it as the main one. |
| 6 | Low | UNVERIFIED | Alternatives: "$95 per month"; "Does not help: session writes dominate"; "we estimate one week" | The cost, the read/write ratio, and the migration estimate are given without sources. | If the claim that writes dominate is wrong, a read replica or caching was dismissed unfairly. If the migration takes longer, the triggers fire too late. | Cite the pricing tier and the measured read/write ratio. Size the migration estimate against the session module. |
| 7 | Low | CONFIRMED | bench.csv `errors` column (14 at 3,200 rps) | The memo does not say whether 14 is a count or a rate, or what kind of errors they were. | A reader cannot tell whether failure at the knee looks like timeouts, connection-pool exhaustion, or deadlocks. Each of these leads to a different fix. | Label the units and error types in the evidence. |

## What holds up

- Every number in the memo matches the CSV, and the multiples are computed correctly.
- The direction of the conclusion is sound. At 200 rps the measured p95 is 6 ms against a 50 ms target. Even if findings 2 and 4 cut the margin by 2–3×, the current peak still meets the target.
- The alternatives include doing nothing. The memo states its limits. It sets concrete triggers, and it correctly notes the decision is reversible (consistent with the one-week reversibility in the context).
- It names the operational cost of Redis (a new failure mode, a second place to lose sessions) instead of treating Redis as free.

## Unverified claims

- **Benchmark setup (schema, instance class, isolation, synthetic keys and payload size):** confirm with the run config and scripts.
- **"Session writes dominate":** confirm with `pg_stat_statements` or application metrics.
- **$95 per month:** confirm with the provider's price sheet for the intended tier.
- **One-week migration:** confirm with a sizing of the session module and its call sites.
- **Load balancer limit of 2,000 rps per address:** confirm with the load balancer config, and check whether any aggregate limit exists.

## Questions for the author

1. Does one benchmark "request" equal one HTTP request at the 200 rps peak, or one session operation?
2. Did the benchmark share the cluster with production-like load, or run on an isolated instance?
3. Is there any aggregate rate limit or bot-burst plan beyond the per-address limit?

## Decision-maker summary

Keeping sessions in Postgres is well supported for current traffic; proceed. Before relying on the memo, fix the bot-burst claim, because the per-address limit does not stop a distributed or single-client burst from overloading the shared cluster, and document the benchmark setup. The remaining risks are a smaller real margin than stated and slow degradation from table bloat, and the p95 trigger should catch both while the change can still be reversed.

```json
{
  "verdict": "SHIP WITH FIXES",
  "findings": [
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "memo.md 'What this does not claim': load balancer limit of 2,000 rps per client address", "scenario": "Per-address limit does not cap aggregate load; a multi-address burst, or one client at 2,000 rps (above the 1,600 rps last-good point) plus organic traffic, drives the shared Postgres cluster toward 118 ms p95 with errors and degrades unrelated workloads", "fix": "Remove the claim or state the exposure; add an aggregate limit or burst plan; weigh session isolation as an alternative"},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "location": "memo.md Evidence: 'sessions table, the real schema, the production instance class, 10-minute runs'", "scenario": "If the benchmark ran on an isolated instance, contention with normal app queries at peak raises p95 and moves the knee below 1,600 rps", "fix": "Attach the run config; re-run at 800 and 1,600 rps alongside a replay of production queries"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "location": "memo.md '10-minute runs' / 'session writes dominate'", "scenario": "High-churn short-lived session rows cause bloat and autovacuum contention over weeks, raising p95 in a way a 10-minute test cannot show", "fix": "Soak test of 24h or more at 400-800 rps; monitor dead rows, p95 trend, and the cleanup job"},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "location": "memo.md peak of 200 rps vs bench.csv requests_per_sec", "scenario": "If each HTTP request does multiple session operations, real session load is 2-3x the stated figure and the margin shrinks from 4x to about 1.5-2x", "fix": "Define the benchmark unit and map HTTP rps to session operations per second"},
    {"severity": "Low", "evidence_level": "PROBABLE", "location": "memo.md 'busiest minute of the last quarter'; trigger 'sustained traffic above 1,000 rps'", "scenario": "Sub-minute bursts reach the knee while the minute average and the sustained-traffic trigger stay below threshold", "fix": "Base triggers on per-second or 10-second peaks; treat the p95 trigger as primary"},
    {"severity": "Low", "evidence_level": "UNVERIFIED", "location": "memo.md Alternatives: $95/month, 'session writes dominate', one-week migration estimate", "scenario": "If writes do not dominate, a read replica or cache was wrongly dismissed; if migration takes longer, the triggers fire too late", "fix": "Cite pricing, the measured read/write ratio, and a migration sizing"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "location": "bench.csv errors column (14 at 3,200 rps)", "scenario": "Unclear units and error type hide whether the failure mode is timeouts, pool exhaustion, or deadlocks, which need different fixes", "fix": "Label the units and error types"}
  ]
}
```
