**Note:** I had no tools in this session, so I could not run anything, open links or check the repo. I did recompute every figure in the memo by hand from the supplied CSV. The work was not written in this conversation, so there is no anchoring to an earlier draft. No subagent or cross-vendor seat was used.

VERDICT: **SHIP.** The recommendation follows from the supplied load test, every number reproduces, and the memo states its own limits and when to revisit the decision.

CONFIDENCE: **medium.** Three things limit it: I had no tools, the test setup is described but not supplied, and I cannot tell whether the test ran alongside the cluster's other production load.

INPUTS LEDGER:
- Seen: the original request (request.md), the context (context.md), `evidence/bench.csv` and `memo.md`.
- Not seen:
  - The load-test harness and configuration (instance, concurrency, whether other workload was running). This matters for one item under Needs Validation.
  - The traffic data behind "busiest minute of the last quarter". This matters little, given the 8× headroom.
  - The Redis pricing source. This does not matter; the price does not drive the decision.
  - Write-versus-read data for sessions. This does not matter; the replica option was rejected either way.

COVERAGE:
- Checked:
  - All 5 CSV rows against the memo table.
  - The 4×, 8× and 16× ratios.
  - The claim about where the 50 ms target is first exceeded.
  - The alternatives section.
  - The triggers and the one-week reversal estimate (against context.md).
  - The "What this does not claim" section.
  - Fit to the request.
- Not checked:
  - How faithful the test is to production (no harness supplied).
  - The $95/month figure.
  - "Session writes dominate."
  - The load-balancer limit of 2,000 requests per second per client address.

SEATS AND GATE: Only the local same-session reviewer ran. No sensitive data is present. Cross-vendor seats were not requested and the depth is standard.

FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Low | PROBABLE | A | memo.md, "What this does not claim", last sentence | The memo calls the 2,000 requests per second per-client-address limit "the protection" against a 5,000 requests per second bot burst. That limit does not stop a burst spread across many addresses. Even a single capped client (2,000) plus the measured peak (200) gives 2,200 requests per second. That falls in the untested gap between 1,600 (31 ms) and 3,200 (118 ms, 14 errors), where the curve bends sharply. | A distributed bot burst, or one client at its cap during peak, pushes p95 latency past 50 ms and causes errors. | Change the sentence to say the limit only bounds a single address. Add a test point at about 2,200–2,400 requests per second. This does not change the Redis decision: a burst of that size is an edge or rate-limiting problem, not a session-store problem. | a✔ b✘ c✘ d✘ |

NEEDS VALIDATION:
- **S1: The test may not reflect a shared production cluster.** The memo keeps sessions in the "existing Postgres cluster". If the test ran sessions alone, production p95 under mixed load could be higher than the CSV shows. What would settle it: whether the test ran with the cluster's normal concurrent workload. The weekly-peak trigger of p95 above 40 ms partly covers this risk.
- **S2: "Session writes dominate."** This is asserted without evidence. What would settle it: the session read/write ratio from production query stats. It is not load-bearing, because the replica option was rejected and Redis was not chosen.

REFUTED:
- **"Busiest minute" hides sub-second bursts.** Withdrawn. Even a 4× burst within the busiest minute (800 requests per second) measured 12 ms. The headroom covers it.
- **The 40 ms trigger leaves too little lead time before the latency knee.** Withdrawn. The traffic trigger of 1,000 requests per second fires well below the tested 1,600 requests per second (31 ms). The one-week migration fits the reversibility stated in context.md.

WHAT HOLDS UP:
- The memo table matches the CSV exactly.
- The ratios are correct: 800/200 = 4, 1,600/200 = 8 and 3,200/200 = 16.
- The target is first breached between 1,600 and 3,200 requests per second, as stated.
- It answers the question actually asked, using the requested evidence.
- It compares fair alternatives, including doing nothing.
- It gives concrete, measurable reasons to revisit the decision.
- It discloses its limits (synthetic keys, no burst modelling).

UNVERIFIED CLAIMS:
- Test conditions (real schema, production instance class, 10-minute runs). Confirm against the harness configuration.
- Redis at about $95/month. Confirm against the provider's pricing page.
- The load-balancer limit of 2,000 requests per second per client address. Confirm against the load-balancer configuration.
- A one-week migration. This is an estimate.

QUESTIONS FOR THE AUTHOR:
1. Did the load test run alongside the cluster's normal workload?
2. Is the load-balancer limit enforced per client address only, or is there also a global limit?

DECISION-MAKER SUMMARY: Approve keeping sessions in Postgres. The load test shows roughly 8× headroom over measured peak against the 50 ms target, and the decision can be reversed within a week. The remaining risk is that a burst of bot traffic, or a cluster busier than in the test, raises latency sooner than the test suggests. The memo's triggers should catch that.

OWNER SUMMARY: The memo's advice to keep using the current database for login sessions is sound and its numbers check out. Our busiest traffic is a small fraction of what the database handled comfortably in testing. One sentence about protection from sudden floods of automated traffic overstates things and should be softened, but that does not change the decision.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "evidence/bench.csv", "status": "seen", "matters": true},
    {"item": "memo.md", "status": "seen", "matters": true},
    {"item": "load test harness and configuration", "status": "not_seen", "matters": true},
    {"item": "traffic data behind the 200 rps peak", "status": "not_seen", "matters": false},
    {"item": "Redis pricing source", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "evidence/bench.csv", "kind": "data"},
      {"unit": "memo.md", "kind": "file"},
      {"unit": "memo.md#Evidence", "kind": "section"},
      {"unit": "memo.md#Alternatives", "kind": "section"},
      {"unit": "memo.md#What would change this decision", "kind": "section"},
      {"unit": "memo.md#What this does not claim", "kind": "section"},
      {"unit": "4x/8x/16x headroom ratios", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "load test harness", "reason": "not supplied"},
      {"unit": "Redis $95/month price", "reason": "no tools to open pricing"},
      {"unit": "load balancer 2,000 rps per-client limit", "reason": "config not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Low", "evidence_level": "PROBABLE", "track": "A",
     "location": "memo.md, What this does not claim, last sentence",
     "scenario": "A burst spread across many addresses bypasses the per-address limit; even one capped client (2,000) plus peak (200) gives about 2,200 rps, inside the untested 1,600-3,200 band where p95 rises from 31 ms to 118 ms with errors.",
     "fix": "Say the limit only bounds a single address; add a test point at about 2,200-2,400 rps. The Redis decision is unaffected.",
     "answers": {"a": true, "b": false, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "A", "location": "memo.md, Evidence, test description",
     "suspicion": "The test may have measured the session load alone, not on the shared production cluster.",
     "unresolved_fact": "Whether the load test ran alongside the cluster's normal concurrent workload."},
    {"id": "S2", "status": "needs_validation", "track": "A", "location": "memo.md, Alternatives, read replica",
     "suspicion": "'Session writes dominate' is asserted without evidence.",
     "unresolved_fact": "The session read/write ratio from production query stats."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Busiest-minute peak hides sub-second bursts that break the target.",
     "evidence": "800 rps (4x peak) measured 12 ms p95; the headroom absorbs plausible intra-minute bursts."},
    {"id": "C2", "candidate": "The 40 ms trigger gives too little lead time before the latency knee.",
     "evidence": "The 1,000 rps traffic trigger fires below the tested 1,600 rps (31 ms); the one-week migration matches the stated reversibility."}
  ]
}
```