VERDICT: **SHIP WITH FIXES**. The recommendation follows from the supplied benchmark and the arithmetic reproduces, but the memo's claim that the load balancer protects against bursts does not hold, and several statements about how the test was run are not backed by anything supplied.

CONFIDENCE: **medium**. Limits:
- No tools in this session, so nothing was run or opened.
- Single reviewer. I did not write the memo, but no independent seats ran.
- The bench configuration, production metrics and load balancer config were not supplied.

INPUTS LEDGER:
- Seen: `request.md`, `context.md`, `memo.md`, `evidence/bench.csv`.
- Not seen (matters): the benchmark harness and run settings. Every "how the test was run" claim depends on it, and so does whether `p95_ms` is session-store latency or end-to-end request latency.
- Not seen (matters): production traffic data behind "busiest minute of the last quarter". The request states 200 rps, so the gap is lower risk.
- Not seen (matters for one finding): the load balancer rate-limit config.
- Not seen (minor): Redis pricing source and session read/write mix.

COVERAGE:
- Checked: every figure in the memo against `bench.csv`; the 4×, 8× and 16× ratios; the threshold bracket; each alternative; the trigger; the "does not claim" section; fit to the original request.
- Not checked: the bench harness, production metrics, LB config, Redis pricing, and the migration-effort estimate.

SEATS AND GATE: Local reviewer only, with no subagent or cross-vendor seats available. Sensitivity gate passed: there is no personal, credential or confidential data, only aggregate benchmark numbers.

## Pass 1: Reconstruct

The memo recommends keeping sessions in Postgres and not adding Redis. It rests on a benchmark showing p95 of 12 ms at 4× the measured peak and below the 50 ms target up to at least 8× peak. It sets a re-evaluation trigger and estimates a one-week migration if Redis is ever needed.

For this to be correct, four things must hold:
- The benchmark must represent production: same schema, same instance class, realistic keys and data volume, and shared-cluster contention.
- `p95_ms` must measure the same thing as the 50 ms target.
- Growth must be slow enough for the trigger to fire before the target is breached.
- Someone must actually watch the trigger.

Tracks: A (decision), with a light D (burden of "watch").

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED | A | memo.md, "What this does not claim": "the load balancer limit of 2,000 requests per second per client address is the protection there" | A per-client limit does not cap total load. Even one client at the limit sits in the untested gap where the target breaks: linear interpolation of 31 ms at 1,600 rps and 118 ms at 3,200 rps puts 50 ms at about 1,950 rps. | A burst of 5,000 rps spread over 3 or more addresses passes the limit entirely, and the bench shows 118 ms p95 with errors at 3,200 rps. Even a single client at 2,000 rps on top of normal traffic lands at or above the target. | Restate this as an unmitigated risk, or name a real aggregate control (global rate limit, WAF rule). If the limit is kept as the argument, bench 2,000 and 2,400 rps to close the gap. | a✓ b✓ c✗ d✗ |
| F2 | Low | CONFIRMED | A/D | memo.md, "What would change this decision" | The trigger has no owner, alert or data source. "Do nothing and watch" depends on someone noticing p95 above 40 ms or traffic above 1,000 rps. | Traffic grows past 1,000 rps with no alert configured. The first signal is the 50 ms breach, at which point the one-week migration starts late. Headroom is about 5× before the trigger, so this is not urgent. | Name the metric (dashboard or alert), its threshold and an owner in the memo. Verify the alert fires by temporarily lowering its threshold. | a✓ b✓ c✗ d✗ |

## NEEDS VALIDATION

- **S1 – what `p95_ms` measures.** The question is whether `p95_ms` in `bench.csv` is session-store operation latency or end-to-end request latency, and which of those the 50 ms target refers to. If the bench measured only session queries, the remaining request work eats into the headroom, and the 8–16× multiplier is overstated.
- **S2 – test realism.** Nothing supplied backs the claim of "real schema, production instance class, 10-minute runs". Synthetic keys and short runs can also hide table growth, bloat, vacuum effects and cache misses. Settled by the harness config, plus the row count and table size during the run versus production.
- **S3 – shared cluster.** The bench may have run on an isolated instance. If production sessions share the Postgres cluster with application queries, contention would lower the real threshold. Settled by the bench environment description.
- **S4 – read replica dismissal.** "Session writes dominate" has no supporting numbers. This is not load-bearing for the chosen option, but it is an unsupported claim in an alternatives section. Settled by the production read/write ratio on the sessions table.

## REFUTED

- **C1 – "the 8 to 16× figure overstates headroom".** Refuted. The memo states it as a bracket: the target is first exceeded somewhere between 1,600 and 3,200 rps, which is correct per the CSV. The interpolated breach point of about 1,950 rps (about 9.7×) falls inside the stated range.
- **C2 – "the table misreports the CSV".** Refuted. All 5 rows match exactly.

## WHAT HOLDS UP

- **Arithmetic:** 800/200 = 4, 1,600/200 = 8 and 3,200/200 = 16 all reproduce, and 12 ms < 50 ms is true.
- **Answers the actual question:** the memo uses the specified evidence, peak and target. There is no drift.
- **Alternatives:** doing nothing is considered fairly, and Redis's added failure mode is a real cost.
- **Trigger thresholds:** 40 ms and 1,000 rps both sit with margin below the measured breach.
- **Reversibility:** matches the context (about a week).
- **Limitations:** the memo states its limits, which is good practice. F1 concerns the mitigation it then claims, not the honesty of the section.

## UNVERIFIED CLAIMS

- **Bench conditions** ("real schema, production instance class, 10-minute runs"): confirm from the harness config.
- **"Busiest minute of the last quarter" = 200 rps:** confirm from the metrics query, including that the query returns non-zero data for a known busy period.
- **About $95 per month for managed Redis:** confirm against the provider's pricing page.
- **LB limit of 2,000 rps per client address:** confirm from the LB config.
- **One-week migration estimate:** confirm by the scope of the session module.

## QUESTIONS FOR THE AUTHOR

1. Is `p95_ms` end-to-end request latency or session-query latency?
2. Was the bench run against the shared production-class cluster, under realistic table size?
3. What aggregate control, if any, limits total traffic during a distributed burst?

## DECISION-MAKER SUMMARY

Keeping sessions in Postgres is supported by the benchmark at today's 200 rps, and the decision is cheap to reverse. Before signing:
- Fix the load balancer claim, which does not stop a multi-address burst.
- Attach an owner and an alert to the trigger.
- Confirm the benchmark measured the same latency as the 50 ms target.

If you proceed as is, the main risk is a traffic burst or unnoticed growth that degrades latency before anyone acts.

## OWNER SUMMARY

The recommendation to keep using the current database for sessions is reasonable, and the numbers check out. The memo overstates how well the system is protected against sudden traffic spikes, and it does not say who will watch for the signal to revisit the decision. Fix those two points and confirm how the test was measured, then the decision is safe to adopt.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "evidence/bench.csv", "status": "seen", "matters": true},
    {"item": "memo.md", "status": "seen", "matters": true},
    {"item": "benchmark harness and run configuration", "status": "not_seen", "matters": true},
    {"item": "production traffic metrics for the 200 rps peak", "status": "not_seen", "matters": true},
    {"item": "load balancer rate-limit configuration", "status": "not_seen", "matters": true},
    {"item": "Redis pricing source", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "local-reviewer", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Aggregate benchmark figures only; no personal, credential or confidential data."},
  "coverage": {
    "checked": [
      {"unit": "evidence/bench.csv", "kind": "data"},
      {"unit": "memo.md", "kind": "file"},
      {"unit": "memo.md#Evidence", "kind": "section"},
      {"unit": "memo.md#Alternatives", "kind": "section"},
      {"unit": "memo.md#What would change this decision", "kind": "section"},
      {"unit": "memo.md#What this does not claim", "kind": "section"},
      {"unit": "4x / 8x / 16x ratios and 50 ms threshold bracket", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "benchmark harness", "reason": "not supplied"},
      {"unit": "production traffic metrics", "reason": "not supplied"},
      {"unit": "load balancer config", "reason": "not supplied"},
      {"unit": "Redis price and migration-effort estimate", "reason": "no tools; not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md, 'What this does not claim': load balancer limit of 2,000 rps per client address",
     "scenario": "A 5,000 rps burst spread across 3 or more client addresses passes a per-client limit; the bench shows 118 ms p95 with errors at 3,200 rps, and even one client at 2,000 rps sits near the interpolated 50 ms breach (~1,950 rps).",
     "fix": "Restate as an unmitigated risk or name an aggregate control (global rate limit or WAF); bench 2,000 and 2,400 rps if the per-client limit is kept as an argument.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md, 'What would change this decision'",
     "scenario": "Traffic grows past 1,000 rps with no alert or owner; the first signal is the 50 ms breach, and the one-week migration starts late.",
     "fix": "Name the metric, alert threshold and owner; verify the alert fires by temporarily lowering its threshold.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "A", "location": "evidence/bench.csv column p95_ms",
     "suspicion": "Bench p95 may be session-query latency while the 50 ms target is end-to-end request latency, which would overstate headroom.",
     "unresolved_fact": "What p95_ms measures in the harness, and what the 50 ms target measures."},
    {"id": "S2", "status": "needs_validation", "track": "A", "location": "memo.md, Evidence: 'sessions table, the real schema, the production instance class, 10-minute runs'",
     "suspicion": "Synthetic keys and short runs may hide table growth, bloat and cache misses.",
     "unresolved_fact": "Harness config, and table size and row count during the run versus production."},
    {"id": "S3", "status": "needs_validation", "track": "A", "location": "memo.md, Recommendation: 'existing Postgres cluster'",
     "suspicion": "The bench may have run without the contention of other workloads on the shared cluster.",
     "unresolved_fact": "Whether the bench ran on the shared cluster under production-like concurrent load."},
    {"id": "S4", "status": "needs_validation", "track": "A", "location": "memo.md, Alternatives: 'session writes dominate'",
     "suspicion": "The read-replica dismissal rests on an unsupported read/write mix.",
     "unresolved_fact": "Production read/write ratio on the sessions table."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The 8 to 16x headroom figure is overstated.",
     "evidence": "It is stated as a bracket; the CSV shows 31 ms at 1,600 and 118 ms at 3,200 rps, and the interpolated breach of ~1,950 rps (~9.7x) lies inside it."},
    {"id": "C2", "candidate": "The memo table misreports bench.csv.",
     "evidence": "All five rows match the CSV exactly."}
  ]
}
```