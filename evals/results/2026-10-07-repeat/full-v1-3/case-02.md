# Redteam review: Redis-for-sessions decision memo

**Review mode:** This session has no tools and no subagent. The memo was not written in this conversation, so the reviewer does not share the author's reasoning. But nothing could be run or opened, so every check below is arithmetic against the CSV or a reading of the memo text.

## Pass 1: Reconstruct

The memo recommends keeping sessions in the existing Postgres cluster and not adding Redis. Its basis is a load test showing p95 of 6 ms at today's 200 rps peak and staying under 50 ms up to at least 1,600 rps. It rejects Redis as cost and failure surface without benefit, and rejects a read replica because writes dominate. It sets a re-evaluation trigger and puts bot bursts out of scope, relying on a load-balancer per-address limit.

Load-bearing assumptions:
1. The bench's p95 is the same quantity as the 50 ms target.
2. One bench "request" equals one production request's session load.
3. A 10-minute run on an otherwise idle setup predicts sustained production behavior on a shared cluster.
4. The load-balancer limit actually bounds abusive load.
5. Migrating later takes about a week, which is shorter than the time between the trigger firing and the target being breached.

## Pass 2: Attack (Track A)

- **Facts.** The CSV and the memo table match exactly. The multiples (4×, 8×, 16×) are correct, and so is "first exceeded between 1,600 and 3,200." The test-condition claims (real schema, production instance class, 10-minute runs), the $95/month figure, "writes dominate" and "one week" are all unsourced.
- **Logic.** The conclusion follows *if* assumptions 1 and 2 hold. Neither is established in the memo.
- **Counter-case.** "Postgres is the shared primary; session churn adds write load, bloat and vacuum pressure to the database everything else depends on. Redis isolates that for $95." The memo never weighs isolation from other workloads, which is the strongest pro-Redis argument. At 200 rps, though, the counter-case is weak, and the decision is reversible within about a week.
- **Pre-mortem: three likely reasons this fails.**
  1. Session table bloat or autovacuum stalls appear over days, not in a 10-minute run.
  2. A distributed bot burst ignores the per-address limit.
  3. p95 regresses because session queries contend with the rest of the app's workload, which the isolated bench never had.

## Pass 3: Self-check

- I dropped "the busiest minute hides sub-second spikes." The 8× headroom absorbs that.
- I downgraded the bloat concern to PROBABLE. It is a known behavior for high-churn Postgres tables, but I have not seen this table's churn.
- The most serious thing that could still be missed is finding 1, the metric mismatch. It hides in the undefined word "latency."

---

**VERDICT: SHIP WITH FIXES.** The recommendation is very likely right at 200 rps and is cheap to reverse. However, the memo compares a number to a target without showing they measure the same thing, and its stated bot-burst protection does not bound the load.

**CONFIDENCE IN VERDICT: medium.** It is limited by:
- no tool access, so the bench setup could not be inspected;
- an unknown relationship between bench p95 and the 50 ms target;
- unknown other workload on the cluster.

## Findings, ordered by severity

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | High | UNVERIFIED | Evidence bullets, "12 ms against a 50 ms target"; request "latency target is 50 ms p95" | The bench p95 appears to be session-store latency. The 50 ms target is most plausibly end-to-end request latency. The memo compares them directly. | Other request work already costs about 40 ms p95. The session store then has a budget of about 10 ms, which is exceeded somewhere between 400 and 800 rps rather than above 1,600, and the "8–16×" headroom collapses to about 2–4×. | State what the bench measured (DB query time or full HTTP request) and what the target measures. If they differ, derive the session-store budget from a production latency breakdown and restate the headroom. |
| 2 | Medium | CONFIRMED (arithmetic) | "What this does not claim": "load balancer limit of 2,000 requests per second per client address is the protection there" | The limit is per address, so a burst spread across many addresses is not bounded at all. Even a single address at the limit (2,000) plus today's 200 rps is 2,200 rps, above the last passing test point (1,600 at 31 ms). The curve reaches 118 ms by 3,200. | A 5,000 rps burst from 50 addresses passes the limiter untouched. Even one client at 2,000 rps pushes the store into the untested region where p95 rises steeply. | Reword so it does not claim protection. Either add an aggregate rate limit, or test at 2,200 and 5,000 rps and state the result. |
| 3 | Medium | PROBABLE | Evidence: "10-minute runs"; "synthetic keys" | Short runs on synthetic keys do not exercise sustained session churn. That churn means dead tuples, table and index bloat, and autovacuum competing for I/O. | After weeks of production churn the sessions table bloats. p95 drifts up, or vacuum spikes coincide with peak, at traffic well below 1,600 rps. | Report sessions-table dead-tuple and bloat stats and autovacuum settings. Run a multi-hour soak at 400–800 rps with realistic key distribution and TTL expiry. |
| 4 | Medium | UNVERIFIED | Recommendation: "existing Postgres cluster"; Evidence: test conditions | No evidence the bench ran alongside the cluster's normal non-session workload. The memo also ignores the counter-case that sessions add load to a shared, critical database. | At peak, application queries and session writes contend. Real p95 exceeds the bench figure, and session load degrades unrelated features. | State whether the bench ran against an otherwise idle instance. Either re-run with background production-like load, or measure the session queries' share of current DB load. |
| 5 | Low | UNVERIFIED | Evidence: "requests per second" | The memo does not say how many session operations one production request performs (for example, a read plus a write or a touch). | Each production request does 3 session operations. 200 rps of traffic is then about 600 bench "requests," and headroom shrinks threefold. | State the session-operation-to-request ratio from code or production metrics. |
| 6 | Low | UNVERIFIED | Alternatives: "Read replica… session writes dominate" | No read/write mix is given anywhere in the evidence. | If reads dominate (common: read on every request, write on login or occasional touch), a replica or app-side cache is a cheaper option that was dismissed incorrectly. | Cite the measured read/write ratio for session queries. |
| 7 | Low | UNVERIFIED | Trigger section: "p95 above 40 ms at the weekly peak"; "we estimate one week" | The trigger metric is undefined (same ambiguity as finding 1) and has no named owner or alert. The one-week migration estimate is unsupported. | Nobody watches the metric, or it measures a different latency. Traffic grows faster than the one-week lead time, and the target is breached before Redis ships. | Define the exact metric and dashboard, assign an alert owner, and justify the one-week estimate with a scope list. The traffic trigger of 1,000 rps itself leaves reasonable margin below 1,600. |
| 8 | Low | CONFIRMED | bench.csv `errors` column, 3200 row: `14` | The units are unlabeled (count, per second, or percent?), and the memo does not interpret them. | Readers can't tell whether failure at 3,200 is marginal or severe, which affects how sharp the cliff is. | Label the units and give the error type. |

## What holds up

- The CSV is transcribed faithfully.
- All the multiples and the breach interval are computed correctly.
- The memo honestly scopes what it does not claim.
- It includes "do nothing" as an option.
- It sets concrete, numeric triggers.
- The core judgment (no Redis needed at 200 rps when the decision is reversible within a week) survives the counter-case under the memo's own assumptions.

## Unverified claims

- **Bench used the real schema, the production instance class and 10-minute runs.** Confirm with the bench config or script and the instance type.
- **Measured peak of 200 rps, the busiest minute of last quarter.** Confirm with a production metrics query.
- **Redis costs about $95/month.** Confirm with the provider's price for the specific node size and HA option.
- **Session writes dominate.** Confirm with a query read/write ratio.
- **Migration is "one module, one data migration," about one week.** Confirm by code-search for session access points.
- **The load balancer enforces a 2,000 rps per-address limit.** Confirm with the LB config.

## Questions for the author

1. Is the bench p95 session-store latency or full request latency, and which one is the 50 ms target?
2. Did the bench run alongside the cluster's normal workload, or on an otherwise idle instance?
3. How many session operations does one production request perform?

## Decision-maker summary

Keeping sessions in Postgres is very likely fine at 200 rps, and the decision is reversible within about a week, so proceed. First, confirm that the bench latency and the 50 ms target measure the same thing, because if they don't, the stated 8–16× headroom may really be 2–4×. The remaining risks are slow session-table bloat and a distributed burst that the per-address load-balancer limit does not stop.

```json
{
  "verdict": "SHIP WITH FIXES",
  "findings": [
    {
      "severity": "High",
      "evidence_level": "UNVERIFIED",
      "location": "memo.md Evidence: '12 ms against a 50 ms target'; request.md '50 ms p95'",
      "scenario": "Bench p95 is session-store latency, but the target is end-to-end; if other request work costs ~40 ms, the session budget is ~10 ms and is exceeded between 400 and 800 rps, so headroom is ~2-4x, not 8-16x.",
      "fix": "State what bench p95 and the target each measure; if they differ, derive the session-store budget from a production latency breakdown and restate headroom."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "memo.md 'What this does not claim': per-client-address limit of 2,000 rps is 'the protection there'",
      "scenario": "A distributed burst (e.g. 5,000 rps from 50 addresses) is not limited at all; even one address at 2,000 rps plus 200 baseline is 2,200 rps, above the last passing test point of 1,600 rps.",
      "fix": "Remove the protection claim, or add an aggregate rate limit, or test at 2,200 and 5,000 rps and report the results."
    },
    {
      "severity": "Medium",
      "evidence_level": "PROBABLE",
      "location": "memo.md Evidence: '10-minute runs'; 'synthetic keys'",
      "scenario": "Sustained session churn causes dead tuples, bloat and autovacuum I/O that a 10-minute synthetic run never exercises; p95 drifts up at traffic well below 1,600 rps.",
      "fix": "Report sessions-table bloat/dead-tuple stats and autovacuum settings; run a multi-hour soak at 400-800 rps with realistic keys and TTL expiry."
    },
    {
      "severity": "Medium",
      "evidence_level": "UNVERIFIED",
      "location": "memo.md Recommendation: 'existing Postgres cluster'; test conditions",
      "scenario": "The bench likely ran without the cluster's normal workload; at peak, session writes and application queries contend, raising real p95 and degrading unrelated features.",
      "fix": "State whether the bench instance was otherwise idle; re-run with background production-like load or measure the session share of current DB load."
    },
    {
      "severity": "Low",
      "evidence_level": "UNVERIFIED",
      "location": "memo.md Evidence: 'requests per second'",
      "scenario": "If each production request does 3 session operations, 200 rps of traffic equals ~600 bench requests and headroom shrinks threefold.",
      "fix": "State the session-operation-to-request ratio from code or production metrics."
    },
    {
      "severity": "Low",
      "evidence_level": "UNVERIFIED",
      "location": "memo.md Alternatives: 'session writes dominate'",
      "scenario": "If reads dominate, a replica or app-side cache is a cheaper option that was dismissed incorrectly.",
      "fix": "Cite the measured read/write ratio for session queries."
    },
    {
      "severity": "Low",
      "evidence_level": "UNVERIFIED",
      "location": "memo.md Trigger: 'p95 above 40 ms at the weekly peak'; 'we estimate one week'",
      "scenario": "The trigger metric is undefined and has no owner or alert; traffic growth outpaces the unsupported one-week migration estimate, and the target is breached before Redis ships.",
      "fix": "Define the exact metric and dashboard, assign an alert owner, and justify the migration estimate with a scope list."
    },
    {
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "location": "evidence/bench.csv errors column, 3200 row: 14",
      "scenario": "Units are unlabeled, so readers cannot tell whether failure at 3,200 rps is marginal or severe.",
      "fix": "Label the units and give the error type."
    }
  ]
}
```