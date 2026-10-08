**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent or other tools were available in this session, so nothing was run or opened.

VERDICT: **SHIP WITH FIXES.** The recommendation follows from the benchmark as the memo presents it, and every figure recomputes. Two gaps should be closed before relying on it: the stated bot-burst protection does not cover what it claims, and nobody is named to watch the re-evaluation trigger.

CONFIDENCE: **medium.** Limits: this is a same-context review with no tools. The benchmark's provenance and the meaning of its columns cannot be checked. It is also unclear what the 50 ms target measures (see S1 and S2).

INPUTS LEDGER:
- **Seen:** request.md, context.md, memo.md, evidence/bench.csv.
- **Not seen:**
  - The benchmark harness or script and its run logs. This matters, because the memo's description of the test conditions is unverified.
  - Production latency and traffic metrics that back up "200 rps = busiest minute of last quarter". This matters somewhat.
  - The load balancer config behind the 2,000 rps per-client limit. This matters for F1.
  - Redis pricing. This does not matter, because the decision does not depend on the $95 figure.

COVERAGE:
- **Checked:**
  - memo.md, every section: Recommendation, Evidence, Alternatives, What would change this decision, What this does not claim.
  - evidence/bench.csv, all 5 rows, compared against the memo table.
  - The arithmetic claims "4 times" and "8 to 16 times".
  - The trigger thresholds.
  - The load balancer protection claim.
- **Not checked:** the benchmark method, production metrics, Redis cost, the one-week migration estimate, and the read/write mix.

SEATS AND GATE: Sensitivity gate passed; the work contains no personal or confidential data. Only the local same-context reviewer ran. No subagent was available, and no cross-vendor seats were requested at `standard` depth.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED | A | memo.md, "What this does not claim": "the load balancer limit of 2,000 requests per second per client address is the protection there" | A per-address limit does not cap total traffic. Also, the cap itself (2,000) is above the highest load the memo shows meeting target (1,600 rps, 31 ms). | A bot burst of 5,000 rps spread over 3 or more addresses passes the limit untouched. Even one address at the 2,000 cap, added to normal traffic, lands in the untested 1,600–3,200 range, where p95 reaches 118 ms and errors appear. | Restate the claim: the per-address limit does not bound total load. Either add an aggregate rate limit or say plainly that distributed bursts are an accepted risk. Reproduction: replay 2,200 rps through the load balancer from 2 addresses and confirm none of it is rejected. | a Y / b Y / c N / d N |
| F2 | Medium | CONFIRMED | A/D | memo.md, "What would change this decision" | The trigger ("p95 above 40 ms at the weekly peak, or sustained traffic above 1,000 rps") has no owner, no alert, and no metric source. "Do nothing and watch" depends on someone remembering to look. | Traffic grows over several months and nobody checks the weekly peak. The trigger is crossed unnoticed, and the one-week migration starts only after users see latency above 50 ms. | Name an owner. Add an automated alert on both conditions, with the metric source written down. | a Y / b Y / c N / d N |
| F3 | Low | CONFIRMED | A | memo.md trigger and bench.csv rows 1,600 and 3,200 | The 40 ms latency trigger sits on the steep part of the curve (31 ms at 1,600 rps, 118 ms at 3,200 rps, nothing measured in between). It may fire with little runway left. The 1,000 rps traffic trigger mostly covers this. | Latency crosses 40 ms only shortly before 50 ms. The one-week migration then runs while the target is already being missed. | Run benchmark points at 2,000, 2,400 and 2,800 rps to find the knee, then set the latency trigger from that curve. | a Y / b Y / c N / d N |
| F4 | Low | CONFIRMED | A | memo.md, "Add a read replica. Does not help: session writes dominate." | The memo gives no evidence for the read/write mix, and bench.csv does not split reads from writes. | If reads actually dominate, a cheaper alternative was dismissed without a fair comparison. This does not change today's decision. | Quote the measured read/write ratio of session operations, or drop the claim. | a Y / b Y / c N / d N |

No Critical or High findings. The core recommendation is supported by the data as the memo presents it.

## Needs validation

These have no severity.

- **S1.** Does the 50 ms p95 target apply to the whole HTTP request or only to the session-store operation? The memo compares session-store p95 against the full 50 ms. If the target is end-to-end, the session store gets only part of that budget, and the headroom is smaller than "4×" suggests.
- **S2.** Does `requests_per_sec` in bench.csv mean HTTP requests or session operations? If each HTTP request makes several session reads or writes, the real multiple over peak is lower.
- **S3.** Are the stated test conditions accurate: the real schema, the production instance class, 10-minute runs, and an isolated instance versus the shared production cluster? This can be settled from the harness and run logs. A test on an isolated instance overstates headroom on a shared cluster.
- **S4.** Do 10-minute runs reveal table bloat and autovacuum effects on a high-churn sessions table? This can be settled with a multi-hour soak test at 800 rps.
- **S5.** Does the 200 rps "busiest minute" hide sub-minute spikes? This can be settled with per-second peak data from production metrics.
- **S6.** Are the $95/month cost and the one-week migration estimate accurate? This can be settled with a current price quote and a sketch of the migration plan. Neither changes the decision.

## Refuted

- **"The memo table misquotes the CSV."** Refuted: all 5 rows match bench.csv exactly.
- **"The multiples are wrong."** Refuted: 800/200 = 4; 1,600/200 = 8; 3,200/200 = 16. "First exceeded between 1,600 and 3,200" also matches, since p95 goes from 31 ms to 118 ms.
- **"The memo drifts from the request."** Refuted: it answers the question asked (Redis or not), uses bench.csv, and uses the 200 rps peak and 50 ms target from the request.

## What holds up

- All of the arithmetic.
- The faithful reproduction of the data.
- The clear recommendation, with a reversal path that fits the context (reversible in about a week).
- A fair "do nothing" alternative.
- A "what this does not claim" section that names the test's real limits: synthetic keys and burst load.

## Unverified claims

- The benchmark conditions (S3).
- That 200 rps is the busiest minute of the quarter (S5).
- The $95/month cost and the one-week migration (S6).
- "Session writes dominate" (F4).
- The load balancer's 2,000 rps per-address limit exists as described. Confirm from the load balancer config.

## Questions for the author

1. Is the 50 ms target end-to-end, and is bench rps measured in HTTP requests or session operations? If the target is end-to-end and the units are operations, the headroom could shrink enough to change the verdict.
2. Was the benchmark run against an isolated instance or the shared production cluster?
3. Who owns the trigger, and what alert fires on it?

## Decision-maker summary

Keeping sessions in Postgres is supported: the measured peak is well below the point where latency breaks. Before signing, assign an owner and an alert to the re-evaluation trigger, and correct the claim that the per-address load balancer limit protects against bot bursts. If you proceed as written, the risk is a traffic or bot surge that goes unnoticed until users see slow responses, followed by a week-long fix.

## Owner summary

The memo's recommendation to keep the current database for sessions is reasonable, and its numbers check out. Two things need tightening: someone should be named to watch for the warning signs it lists, and the memo overstates how well the current traffic limits protect against a large burst from many sources. A couple of open questions about what the load test actually measured could reduce the safety margin, so they are worth answering.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "memo.md", "status": "seen", "matters": true},
    {"item": "evidence/bench.csv", "status": "seen", "matters": true},
    {"item": "benchmark harness and run logs", "status": "not_seen", "matters": true},
    {"item": "production traffic and latency metrics", "status": "not_seen", "matters": true},
    {"item": "load balancer rate-limit config", "status": "not_seen", "matters": true},
    {"item": "Redis pricing source", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "memo.md", "kind": "file"},
      {"unit": "evidence/bench.csv", "kind": "data"},
      {"unit": "memo.md:Evidence", "kind": "section"},
      {"unit": "memo.md:Alternatives", "kind": "section"},
      {"unit": "memo.md:What would change this decision", "kind": "section"},
      {"unit": "memo.md:What this does not claim", "kind": "section"},
      {"unit": "4x and 8-16x multiples", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "benchmark method and environment", "reason": "harness and logs not supplied; no tools"},
      {"unit": "200 rps busiest-minute claim", "reason": "production metrics not supplied"},
      {"unit": "$95/month and one-week migration estimates", "reason": "no source supplied"},
      {"unit": "load balancer per-address limit", "reason": "config not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md, What this does not claim: 'the load balancer limit of 2,000 requests per second per client address is the protection there'",
     "scenario": "A 5,000 rps bot burst spread over 3+ addresses passes the per-address limit; even one address at the 2,000 cap plus normal traffic exceeds the last load shown under target (1,600 rps), toward 118 ms p95 and errors at 3,200 rps.",
     "fix": "State that the per-address limit does not bound aggregate load; add an aggregate limit or record distributed bursts as an accepted risk.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md, What would change this decision",
     "scenario": "Traffic grows over months with no alert or owner on the trigger; it is crossed unnoticed and the one-week migration starts only after users see p95 above 50 ms.",
     "fix": "Name an owner and add automated alerts on weekly-peak p95 > 40 ms and sustained traffic > 1,000 rps, with the metric source documented.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md trigger; evidence/bench.csv rows 1600 and 3200",
     "scenario": "The latency curve jumps from 31 ms to 118 ms between 1,600 and 3,200 rps with no points between; a 40 ms trigger may fire shortly before 50 ms, leaving less than the one-week migration as runway.",
     "fix": "Benchmark 2,000, 2,400 and 2,800 rps to locate the knee and set the latency trigger from it.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md, Alternatives: 'Does not help: session writes dominate.'",
     "scenario": "If session reads dominate, the read-replica alternative was dismissed without evidence; the comparison of alternatives is not fair.",
     "fix": "Quote the measured read/write ratio of session operations or remove the claim.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "A", "location": "memo.md, Evidence: '12 ms against a 50 ms target'",
     "suspicion": "Session-store p95 is compared against what may be an end-to-end request latency target.",
     "unresolved_fact": "Whether the 50 ms p95 target is end-to-end request latency or session-store latency."},
    {"id": "S2", "status": "needs_validation", "track": "A", "location": "evidence/bench.csv: requests_per_sec",
     "suspicion": "Bench rps may count session operations rather than HTTP requests, overstating the multiple over the 200 rps peak.",
     "unresolved_fact": "The unit of requests_per_sec in the benchmark and session operations per HTTP request."},
    {"id": "S3", "status": "needs_validation", "track": "C", "location": "memo.md, Evidence: '(sessions table, the real schema, the production instance class, 10-minute runs)'",
     "suspicion": "Stated test conditions are unverified; an isolated instance would overstate headroom on the shared cluster.",
     "unresolved_fact": "Benchmark harness and run logs showing instance, schema, duration and whether the cluster was shared."},
    {"id": "S4", "status": "needs_validation", "track": "A", "location": "memo.md, Evidence: '10-minute runs'",
     "suspicion": "Short runs may miss bloat and autovacuum effects on a high-churn sessions table.",
     "unresolved_fact": "p95 from a multi-hour soak at 800 rps."},
    {"id": "S5", "status": "needs_validation", "track": "C", "location": "memo.md, Evidence: 'the busiest minute of the last quarter'",
     "suspicion": "Per-minute peak may hide higher per-second spikes.",
     "unresolved_fact": "Per-second peak traffic from production metrics."},
    {"id": "S6", "status": "needs_validation", "track": "C", "location": "memo.md, Alternatives and What would change this decision",
     "suspicion": "The $95/month cost and one-week migration estimate are unsourced.",
     "unresolved_fact": "A current managed Redis quote and a migration plan sketch."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The memo table misquotes bench.csv.", "evidence": "All five rows match bench.csv exactly."},
    {"id": "C2", "candidate": "The 4x and 8-16x multiples are wrong.", "evidence": "800/200=4, 1600/200=8, 3200/200=16; p95 crosses 50 ms between 31 ms at 1,600 and 118 ms at 3,200."},
    {"id": "C3", "candidate": "The memo drifts from the request.", "evidence": "It answers Redis-or-not using bench.csv, the 200 rps peak and the 50 ms target, as asked."}
  ]
}
```