# Redteam review: decision memo, "keep sessions in Postgres; do not add Redis yet"

**VERDICT: SHIP.** The recommendation follows from the supplied load test. The arithmetic and the CSV-to-table transcription are correct, and the only confirmed defect is a Medium overstatement in the caveats section that does not change the decision.

**CONFIDENCE: medium.** Three things limit it:
- I had no tools, so I could not open anything beyond the supplied text or check the test's provenance.
- I am a single reviewer with no independent seat. This was not a same-context review, since the memo was not written in this conversation.
- The CSV does not show what the latency measures, so whether it is comparable to the 50 ms target is unconfirmed (S1).

**INPUTS LEDGER**

| Item | Status | Does the gap matter? |
|---|---|---|
| `request.md` | seen | — |
| `context.md` | seen | — |
| `memo.md` | seen | — |
| `evidence/bench.csv` | seen | — |
| Load-test harness, config and run logs | not supplied | Yes. The memo's description of the test cannot be checked, and it is unclear what the p95 measures (S1, S2). |
| Traffic data behind "busiest minute of the last quarter" | not supplied | Minor. The 4x margin absorbs a sub-minute spike. |
| Read/write mix of session traffic | not supplied | Minor. It only supports the dismissal of read replicas (S3). |
| Redis pricing source ($95/month) | not supplied | No. It does not drive the decision. |
| Load balancer configuration | not supplied | Minor. The rate is taken from the memo itself (F1). |

**COVERAGE**
- **Scope:** the whole memo plus `bench.csv`.
- **Checked:**
  - The memo's table against the CSV, row by row.
  - The 4x, 8x and 16x multiples.
  - The 50 ms crossing point.
  - The trigger thresholds against the curve.
  - The alternatives, the reversibility claim and the bot-burst caveat.
- **Not checked:** the test's environment claims and the cost figure. There were no tools and no source.

**SEATS AND GATE:** I ran as a single local reviewer, and no cross-vendor seats were run. The sensitivity gate found nothing sensitive: the material is performance data and an internal memo, with no personal or confidential data.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED (logic, from the memo's own text); crossing point PROBABLE | A | memo.md, "What this does not claim": "the load balancer limit of 2,000 requests per second per client address is the protection there" | A limit per client address does not cap total traffic. It also does not keep a single client below the point where latency fails. | 1. Interpolating the CSV, p95 crosses 50 ms at about 1,950 requests per second (31 ms at 1,600, 118 ms at 3,200).<br>2. One address capped at 2,000 requests per second, plus the 200 of normal peak, gives about 2,200, which is past the crossing.<br>3. A 5,000 requests per second burst spread over three or more addresses is not limited at all, and the CSV shows errors at 3,200.<br>4. A reader relying on this sentence would think bot bursts are covered when they are not. | Reword it to say the per-address limit does not bound total load and that bot bursts are an open risk. Name the actual total-load control if one exists, such as a global rate limit or autoscaling. Note that Redis would not remove this risk either, so the recommendation still stands. | a=Y, b=Y, c=N, d=N |

## Needs validation (no severity)

- **S1. What the p95 measures.** Does the `bench.csv` p95 measure the session-store operation or the full request?
  - If it measures only the session read or write, comparing it against a 50 ms target for whole requests overstates the headroom.
  - **Settled by:** the harness definition of `p95_ms`.
- **S2. Whether the test environment matches production.** The memo says the test used the sessions table, the real schema, the production instance class and 10-minute runs. The CSV shows none of this.
  - It is also unknown whether the test ran against an idle instance. Production shares the "existing Postgres cluster" with other workload, which would reduce real headroom.
  - **Settled by:** the run logs or config, and the background load on the target during the test.
- **S3. "Session writes dominate."** This is asserted without a read/write ratio.
  - **Settled by:** a query of read versus write counts on the sessions table. It only affects the dismissal of read replicas.

## Refuted

- **C1. The multiples are wrong.** Refuted: 800/200 = 4, 1,600/200 = 8 and 3,200/200 = 16. All are correct.
- **C2. The table does not match the CSV.** Refuted: all five rows match exactly in rate, p95 and errors.
- **C3. The trigger is too late to migrate in time.** Refuted: the 1,000 requests per second trigger sits below the 1,600 point (31 ms) and well below the roughly 1,950 crossing. That leaves room for the estimated one-week migration unless traffic grows about 2x within a week, which the context's reversibility of about a week also covers.
- **C4. Drift from the request.** Refuted: the memo answers the question that was asked, uses the named evidence, and states both the 200 requests per second peak and the 50 ms p95 target.

## What holds up

- The core claim is sound: at the measured 200 requests per second peak, p95 is 6 ms against a 50 ms target, with 4x headroom proven at 12 ms.
- Doing nothing is a fair, cheap and reversible choice.
- Redis's costs are named honestly, as a new failure mode and a second place sessions can be lost.
- The memo has a measurable trigger, and it states its limits openly: synthetic keys, and bot bursts not modelled.

## Unverified claims

| Claim | How to confirm |
|---|---|
| Test conditions (schema, instance class, 10-minute runs) | Run config or logs |
| Peak of 200 requests per second is the busiest minute of the last quarter | Metrics query |
| Redis costs about $95 per month | Provider price page, with the date |
| Migration takes about one week | Size of the session module and its callers |
| Session writes dominate | Read/write counts on the sessions table |

## Questions for the author

1. Is `p95_ms` measured on the full request or on the session operation only?
2. Was the test target isolated from other workload on the cluster?
3. Is there a control that limits total traffic, beyond the per-address limit?

## Decision-maker summary

Keep sessions in Postgres. The load test shows comfortable headroom at today's peak, and the decision is cheap to reverse. Before relying on the memo, correct the bot-burst sentence, because the per-address limit does not protect the database from a large or distributed burst. Also confirm that the measured latency is comparable to the 50 ms target.

## Owner summary

The advice to stay on the current database for now is well supported by the test results. One sentence overstates how well the system is protected from sudden floods of automated traffic, and it should be corrected. It is also worth confirming that the test measured the same kind of response time as the target.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "memo.md", "status": "seen", "matters": true},
    {"item": "evidence/bench.csv", "status": "seen", "matters": true},
    {"item": "load-test harness, config and run logs", "status": "not_seen", "matters": true},
    {"item": "traffic metrics behind the 200 rps peak", "status": "not_seen", "matters": false},
    {"item": "session read/write mix", "status": "not_seen", "matters": false},
    {"item": "Redis pricing source", "status": "not_seen", "matters": false},
    {"item": "load balancer configuration", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "memo.md", "kind": "document"},
      {"unit": "evidence/bench.csv", "kind": "data"},
      {"unit": "memo.md:Evidence table vs bench.csv", "kind": "claim"},
      {"unit": "memo.md:4x / 8-16x multiples", "kind": "claim"},
      {"unit": "memo.md:Alternatives", "kind": "section"},
      {"unit": "memo.md:What would change this decision", "kind": "section"},
      {"unit": "memo.md:What this does not claim", "kind": "section"}
    ],
    "not_checked": [
      {"unit": "load-test harness and run logs", "reason": "not_supplied"},
      {"unit": "Redis price of $95/month", "reason": "no_tools"},
      {"unit": "traffic metrics for the 200 rps peak", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md, 'What this does not claim': 'the load balancer limit of 2,000 requests per second per client address is the protection there'",
     "scenario": "A per-address limit does not cap total traffic: a 5,000 rps burst over three or more addresses passes unthrottled, beyond the 3,200 rps point where errors appear; even one capped address at 2,000 rps plus 200 rps normal peak exceeds the interpolated ~1,950 rps where p95 crosses 50 ms.",
     "fix": "State that the per-address limit does not bound total load and that bot bursts are an open risk; name the actual total-load control if one exists. The recommendation is unaffected, since Redis would not remove this risk either.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "A", "location": "evidence/bench.csv: p95_ms",
     "suspicion": "p95_ms may measure only the session-store operation, not the full request the 50 ms target applies to.",
     "unresolved_fact": "The harness definition of p95_ms."},
    {"id": "S2", "status": "needs_validation", "track": "A", "location": "memo.md, Evidence: '(sessions table, the real schema, the production instance class, 10-minute runs)'",
     "suspicion": "Test conditions are asserted, not shown, and the test may have run against an idle instance while production shares the cluster with other workload.",
     "unresolved_fact": "Run config or logs, and background load on the test target."},
    {"id": "S3", "status": "needs_validation", "track": "A", "location": "memo.md, Alternatives: 'session writes dominate'",
     "suspicion": "The read/write ratio is asserted without data.",
     "unresolved_fact": "Read versus write counts on the sessions table."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The 4x and 8-16x multiples are miscalculated.", "evidence": "800/200=4, 1600/200=8, 3200/200=16."},
    {"id": "C2", "candidate": "The memo table misstates the CSV.", "evidence": "All five rows match exactly in rate, p95 and errors."},
    {"id": "C3", "candidate": "The 1,000 rps trigger leaves too little time to migrate.", "evidence": "1,000 rps is below the 1,600 rps (31 ms) point and the ~1,950 rps crossing; this covers the one-week migration unless traffic roughly doubles within a week."},
    {"id": "C4", "candidate": "The memo drifts from the request.", "evidence": "It answers the Redis question using bench.csv, the 200 rps peak and the 50 ms p95 target, as asked."}
  ]
}
```