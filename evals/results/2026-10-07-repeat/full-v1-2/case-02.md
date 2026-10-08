VERDICT: **SHIP WITH FIXES.** For the question asked (200 rps peak, 50 ms p95), the CSV supports "keep Postgres, don't add Redis yet." But the memo's section on what it does not claim names a protection (the load balancer cap) that its own data shows does not protect.

CONFIDENCE IN VERDICT: **medium.** This review is independent: the work was not produced in this conversation. But I had no tools, so I could only check the memo against the CSV. I could not check the test setup, the cluster topology, or the load balancer config.

## Pass 1: Reconstruct

The memo claims that Postgres-backed sessions meet the 50 ms p95 target with large headroom. The CSV shows 12 ms at 4× peak, and the target is first exceeded somewhere between 8× and 16× peak. It recommends doing nothing, with a re-evaluation trigger.

Load-bearing assumptions:
1. The bench conditions represent production: real schema, production instance class, and the same contention.
2. The CSV's "requests_per_sec" and "p95_ms" are the same units as the 200 rps peak and the 50 ms target.
3. Abnormal traffic (bots, bursts) is capped below the failure region.
4. The trigger fires early enough to allow a one-week migration.

## Pass 2: Attack (Track A)

**Facts.** The memo's table matches `bench.csv` exactly. The ratios are correct: 800/200 = 4, 1600/200 = 8, 3200/200 = 16. The crossing point is also right: 31 ms at 1,600 rps and 118 ms at 3,200 rps. Some claims are not in the evidence:
- "real schema, production instance class, 10-minute runs"
- "busiest minute of the last quarter"
- "$95 per month"
- "session writes dominate"
- "one week"

**Logic.** The headroom conclusion follows from the data. The bot-burst rebuttal does not (finding 1).

**Counter-case.** The strongest argument for Redis is not average-load capacity. It is isolation: Redis keeps session traffic, especially abusive traffic, from loading the primary database. The memo's only answer to that is the load balancer cap, and that answer fails.

**Pre-mortem.**
1. One or more abusive clients push session load past 1,600 rps and degrade the shared Postgres cluster.
2. Production contention from non-session queries makes real headroom much smaller than the isolated bench showed.
3. Growth crosses the knee between two weekly checks, and the one-week migration lands after the incident.

## Findings

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | High | CONFIRMED (arithmetic on the memo's own numbers) | "What this does not claim": "the load balancer limit of 2,000 requests per second per client address is the protection there" | The per-client cap (2,000 rps) is above the highest load tested within target (1,600 rps at 31 ms). Two capped clients (4,000 rps) exceed the 3,200 rps point, where p95 was 118 ms with 14 errors. The cap is per address, so it does nothing against a distributed burst. | One client at the cap plus 200 rps of organic traffic gives about 2,200 rps. That is in the untested 1,600 to 3,200 band where p95 climbs past 50 ms (PROBABLE). Two clients at the cap, or a 5,000 rps botnet, give a load the bench showed failing (CONFIRMED). | Remove the "is the protection" claim, or back it with a global or session-endpoint rate limit set below about 1,600 rps. Add bench points at 2,000 and 2,400 rps. List burst isolation as an open risk in the alternatives section. |
| 2 | Medium | UNVERIFIED | Evidence section: "sessions table, the real schema, the production instance class" | It is not stated whether the bench ran against an idle instance or under the cluster's normal mixed workload. The recommendation is to keep sessions in the existing, shared cluster. | Other application queries compete for CPU, I/O, and connections. The knee moves well below 1,600 rps, and the "8 to 16×" headroom claim overstates real margin. | State the bench conditions. Re-run with the production query mix replayed alongside, or compare against production `pg_stat_statements` latency for session queries at peak. |
| 3 | Medium | UNVERIFIED | Evidence bullets comparing "12 ms against a 50 ms target" | It is unclear whether `p95_ms` is session-store latency or end-to-end request latency, and whether one request equals one session operation. If the 50 ms target is end-to-end, session p95 uses only part of the budget, so "against a 50 ms target" compares unlike quantities. | A request does 2 or 3 session reads and writes plus application work. At 800 rps the session cost alone could be about 24 to 36 ms, and the end-to-end p95 misses 50 ms well before the memo's predicted crossing. | State what the bench measured and the session operations per request. If the bench measured the store only, add measured non-session latency to it before comparing with the target. |
| 4 | Medium | PROBABLE | "What would change this decision": "p95 above 40 ms at the weekly peak" | The curve is steep: 31 ms at 1,600 rps, 118 ms at 3,200 rps. There are no points in between, so 40 ms may sit just before the cliff. A weekly check combined with a one-week migration leaves little or no lead time. | Traffic reaches the band between the 40 ms point and the 50 ms point mid-week, or during a launch. The breach comes before the next weekly review, or during the migration. | Add bench points between 1,600 and 3,200 rps to locate the knee. Use a continuous alert, not a weekly review, and set the traffic trigger with the one-week lead time in mind. |
| 5 | Low | UNVERIFIED | "Add a read replica. Does not help: session writes dominate." | No read/write ratio is given. Session workloads are often read-heavy. | It only matters if the decision is revisited. A dismissed option may be the cheaper fix. | Cite the measured read/write ratio for session queries. |
| 6 | Low | PROBABLE | "measured peak is 200 requests per second (the busiest minute...)" | A per-minute average hides sub-second bursts. The peak second may be well above 200 rps. | Short spikes exceed the steady-state 10-minute bench conditions. The headroom still likely absorbs this. | Report the p99 per-second rate from load balancer logs. |
| 7 | Low | CONFIRMED (stated in memo) | "The test used synthetic keys" | Synthetic key distribution may give unrealistic index and cache locality. The memo acknowledges this. | Real session-ID access patterns raise p95 somewhat. | Replay a sample of production session IDs in one bench run. |

## What holds up

- The table is transcribed faithfully from the CSV, and all ratios and crossing points are computed correctly.
- For the question actually asked, 4× to 8× headroom within target is a sound basis for "not yet."
- Doing nothing is considered, there is an explicit trigger, the costs of Redis (a new failure mode, a second place sessions can be lost) are fair, and reversibility is addressed.
- The memo has no drift: it answers the question that was asked.

## Unverified claims

| Claim | How to confirm |
|---|---|
| Real schema, production instance class, 10-minute runs | Bench config and logs |
| 200 rps is the busiest minute of the quarter | Load balancer or APM query |
| $95 per month for a managed Redis node | Provider pricing page for the intended tier |
| Session writes dominate | `pg_stat_statements` read/write ratio for session queries |
| One-week migration estimate | Size the session module; check the TTL on session rows |
| Load balancer per-client limit is 2,000 rps | LB config; also check whether any global limit exists |

## Questions for the author

1. Is there a global or endpoint-level rate limit below about 1,600 rps? If not, the burst risk is open.
2. Does `p95_ms` measure the session store or the end-to-end request, and how many session operations happen per request?
3. Was the bench run on an isolated instance or under the production query mix?

## Decision-maker summary

Keeping sessions in Postgres is supported for current traffic, and the decision is cheap to reverse. Before signing, correct the bot-burst section: the per-client cap of 2,000 rps sits above the measured knee, and two capped clients reach the load that failed in testing. Also confirm that the bench measured what the 50 ms target measures. If you proceed without these fixes, the remaining risk is a burst or shared-cluster contention degrading the primary database, not ordinary growth.

```json
{
  "verdict": "SHIP WITH FIXES",
  "findings": [
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "location": "memo.md, 'What this does not claim': load balancer limit of 2,000 requests per second per client address is the protection",
      "scenario": "The per-client cap (2,000 rps) exceeds the highest in-target tested load (1,600 rps, 31 ms). One capped client plus 200 rps of organic traffic sits in the untested 1,600-3,200 band where p95 rises toward 118 ms. Two capped clients (4,000 rps) or a distributed 5,000 rps burst exceed 3,200 rps, where the bench showed 118 ms p95 and 14 errors. A per-address limit does not bound a distributed burst.",
      "fix": "Withdraw the protection claim or add a global or session-endpoint rate limit below about 1,600 rps. Bench at 2,000 and 2,400 rps. Record burst isolation as an open risk."
    },
    {
      "severity": "Medium",
      "evidence_level": "UNVERIFIED",
      "location": "memo.md, Evidence: sessions table, real schema, production instance class",
      "scenario": "If the bench ran on an idle instance, production contention from other queries on the shared cluster lowers the knee well below 1,600 rps, and the stated 8-16x headroom is overstated.",
      "fix": "State the bench conditions. Re-run with the production query mix, or compare against production pg_stat_statements session-query latency at peak."
    },
    {
      "severity": "Medium",
      "evidence_level": "UNVERIFIED",
      "location": "memo.md, Evidence bullets: 12 ms against a 50 ms target",
      "scenario": "If p95_ms is session-store latency and the 50 ms target is end-to-end, or one request performs multiple session operations, end-to-end p95 misses 50 ms well below the predicted crossing.",
      "fix": "State what the bench measured and the session operations per request. Add non-session latency before comparing with the target."
    },
    {
      "severity": "Medium",
      "evidence_level": "PROBABLE",
      "location": "memo.md, 'What would change this decision': p95 above 40 ms at the weekly peak",
      "scenario": "The latency curve is steep between 1,600 rps (31 ms) and 3,200 rps (118 ms) with no points in between. Crossing 40 ms may come just before crossing 50 ms, so a weekly check plus a one-week migration leaves no lead time.",
      "fix": "Add bench points between 1,600 and 3,200 rps to locate the knee. Use a continuous alert and size the traffic trigger with the one-week lead time in mind."
    },
    {
      "severity": "Low",
      "evidence_level": "UNVERIFIED",
      "location": "memo.md, Alternatives: read replica does not help because session writes dominate",
      "scenario": "If session traffic is read-heavy, a cheaper alternative was dismissed without evidence when the decision is revisited.",
      "fix": "Cite the measured read/write ratio for session queries."
    },
    {
      "severity": "Low",
      "evidence_level": "PROBABLE",
      "location": "memo.md, Evidence: 200 rps is the busiest minute of the last quarter",
      "scenario": "Per-minute averaging hides sub-second spikes that exceed 200 rps and the steady-state bench conditions.",
      "fix": "Report the peak or p99 per-second rate from load balancer logs."
    },
    {
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "location": "memo.md, 'What this does not claim': the test used synthetic keys",
      "scenario": "Synthetic key distribution gives unrealistic index and cache locality, so real p95 is somewhat higher.",
      "fix": "Replay a sample of production session IDs in a bench run."
    }
  ]
}
```