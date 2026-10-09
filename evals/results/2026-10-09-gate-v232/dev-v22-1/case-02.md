Same-context review, with anchoring risk; re-run in a fresh session for anything high-stakes. No tools were available in this session. The memo was not written in this conversation, but no fresh subagent or second reviewer ran.

**VERDICT: SHIP.** The recommendation follows from the supplied benchmark, every figure in the memo reproduces from `evidence/bench.csv`, and no Critical or High finding survived review.

**CONFIDENCE: medium.** It is limited by three things:
- I could not open anything beyond the text supplied.
- The benchmark's setup claims (schema, instance class, run length) are not recorded in the CSV.
- It is not stated whether the 50 ms target applies end to end or to the session store alone.

**INPUTS LEDGER**
- **Seen:** `request.md`, `context.md`, `evidence/bench.csv` (5 rows), `memo.md`.
- **Not seen:**
  - Load-test harness, config or run logs. These matter: the setup claims depend on them.
  - Traffic data behind "200 rps peak". This matters a little; the figure is given in the request.
  - Redis pricing source. Does not matter; the decision does not hinge on $95.
  - Load balancer config. Matters for the bot-burst claim only.
  - Session read/write mix. Matters for the read-replica dismissal only.

**COVERAGE**
- **Checked:**
  - Every number in the memo against the CSV.
  - The 4×, 8× and 16× ratios.
  - The "first exceeded" interval.
  - The alternatives section.
  - The trigger and reversibility claims.
  - The bot-burst and synthetic-keys limitations.
  - Fit to the original request.
- **Not checked:** the harness and environment (not supplied), the LB rate-limit configuration, and the Redis price.

**SEATS AND GATE:** Only the local reviewer ran. No sensitive data is present (synthetic benchmark figures). Cross-vendor seats were not requested and were not needed at standard depth.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | PROBABLE | A | memo.md, "What this does not claim": "the load balancer limit of 2,000 requests per second per client address is the protection there" | A per-client-address limit does not cap aggregate load. | A burst spread over 3+ addresses passes the per-address limit and reaches 5,000 rps, above the 3,200 rps row where errors start (14). Even one client at its 2,000 rps limit plus 200 rps of normal traffic gives about 2,200 rps. That sits between the 31 ms and 118 ms rows, so the 50 ms target is plausibly breached. | Restate the limit as protection against a single-source burst only. Either name an aggregate limit, or record bot bursts as an accepted risk with the trigger as the response. To check: run the benchmark at 2,200 rps and at 5,000 rps. | a✓ b✗ c✗ d✗ |
| F2 | Low | CONFIRMED | D | memo.md, "What would change this decision" | The trigger has no owner and no alert. "Do nothing and watch" depends on someone checking the weekly p95 and the traffic level. | Traffic grows past 1,000 rps over a few months. No one is watching, the trigger is never acted on, and the one-week migration starts only after the target is missed. | Name an owner and attach an automated alert on p95 > 40 ms and on sustained traffic > 1,000 rps. | a✓ b✓ c✗ d✗ |

## NEEDS VALIDATION
- **S1, end-to-end versus store latency.** The memo compares session-store p95 directly with "the latency target is 50 ms p95".
  - If the target applies to the whole request, the store's share of the budget matters. The 1,600 rps row (31 ms) would leave only 19 ms for everything else, so the "8 to 16 times" headroom is overstated. At 200 rps (6 ms) the decision still holds.
  - **Settling fact:** whether the 50 ms target applies end to end or to session operations only, and what the benchmark timed.
- **S2, benchmark setup.** The memo says the test used the "sessions table, the real schema, the production instance class, 10-minute runs".
  - **Settling fact:** the harness config or run log. The CSV records none of this.
- **S3, read-replica dismissal.** The memo says "session writes dominate".
  - **Settling fact:** the measured read/write ratio for session operations.
- **S4, cost.** The memo gives "Roughly $95 per month".
  - **Settling fact:** the provider price page for the intended node size, checked on the decision date. Low impact either way.

## REFUTED
- **C1, "headroom figures are miscalculated".**
  - 800/200 = 4×, and 1,600/200 = 8×.
  - 3,200/200 = 16×.
  - 31 ms is under 50 ms and 118 ms is over it, so the target is first exceeded between 1,600 and 3,200 rps.
  - All figures reproduce.
- **C2, "memo table misstates the CSV".** All 5 rows match exactly: rps, p95 and errors.
- **C3, "drift from the request".** The request asked whether to add Redis, using `bench.csv`, against 200 rps and 50 ms p95. The memo answers exactly that with that evidence.
- **C4, "busiest-minute peak hides sub-minute bursts".**
  - It is real in principle.
  - An 8× margin before the target is reached absorbs any plausible sub-minute spike at the current scale.
  - It is not material to the decision.

## WHAT HOLDS UP
- **The core inference.** At the measured peak (200 rps), p95 is 6 ms, against a 50 ms target, with zero errors. The first errors and the first target breach both occur only at 8 to 16 times today's peak.
- **Fair alternatives.** "Do nothing" is a real option and was chosen. Redis is not strawmanned: the memo names its cost and the operational risk it adds.
- **Reversibility.** The memo says moving later takes about one week. That is consistent with the context.
- **Honest scope.** The memo discloses its limitations (synthetic keys, no bot-burst model) instead of hiding them.

## UNVERIFIED CLAIMS
- **Test environment details.** Confirm them from the harness config or logs.
- **"Session writes dominate".** Confirm with a query of the operation mix.
- **$95/month.** Confirm on the provider price page.
- **The 2,000 rps per-address LB limit.** Confirm in the LB config.
- **The one-week migration estimate.** Confirm by counting the call sites of the session module.

## QUESTIONS FOR THE AUTHOR
1. Is the 50 ms p95 target end to end, or for session operations?
2. Is there an aggregate (not per-address) rate limit, and who owns the trigger alert?

## DECISION-MAKER SUMMARY
Keeping sessions in Postgres is supported: the benchmark shows 6 ms p95 at today's peak and no breach until 8 to 16 times that load. Before filing the memo:
- Name an owner and an alert for the trigger.
- Correct the claim that a per-address LB limit protects against bot bursts.

The residual risk is a distributed burst or unmonitored growth, and either one is recoverable within the one-week migration window.

## OWNER SUMMARY
The recommendation to keep things as they are is sound: our test shows the current database handles today's busiest traffic many times over, well inside the speed target. Two small gaps should be closed. Someone should be named to watch the warning signs. The note that says the load balancer protects against a bot flood should be softened, because that limit only stops a flood coming from one address.

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
    {"item": "load-test harness config and run logs", "status": "not_seen", "matters": true},
    {"item": "load balancer rate-limit config", "status": "not_seen", "matters": false},
    {"item": "session read/write mix data", "status": "not_seen", "matters": false},
    {"item": "Redis pricing source", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Synthetic benchmark figures and an internal architecture memo; no personal or confidential data."},
  "coverage": {
    "checked": [
      {"unit": "evidence/bench.csv", "kind": "data"},
      {"unit": "memo.md", "kind": "file"},
      {"unit": "memo.md#Evidence", "kind": "section"},
      {"unit": "memo.md#Alternatives", "kind": "section"},
      {"unit": "memo.md#What would change this decision", "kind": "section"},
      {"unit": "memo.md#What this does not claim", "kind": "section"},
      {"unit": "4x / 8x / 16x headroom ratios", "kind": "claim"},
      {"unit": "50 ms first exceeded between 1,600 and 3,200 rps", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "load-test harness and environment", "reason": "not supplied"},
      {"unit": "load balancer configuration", "reason": "not supplied"},
      {"unit": "Redis managed-node price", "reason": "no tools to open a price page"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "A",
     "location": "memo.md, What this does not claim: 'the load balancer limit of 2,000 requests per second per client address is the protection there'",
     "scenario": "A bot burst spread across 3 or more client addresses passes the per-address limit and reaches 5,000 rps, above the 3,200 rps row where errors appear; even one client at 2,000 rps plus 200 rps normal traffic (about 2,200 rps) plausibly exceeds the 50 ms p95 target.",
     "fix": "State that the limit protects only against single-source bursts; name an aggregate limit or record distributed bursts as an accepted risk.",
     "answers": {"a": true, "b": false, "c": false, "d": false},
     "reproduction": "Run the benchmark at 2,200 rps and 5,000 rps; expect p95 above 50 ms and errors at 5,000 rps."},
    {"id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "D",
     "location": "memo.md, What would change this decision",
     "scenario": "Traffic grows past 1,000 rps over months; with no named owner or automated alert, the trigger goes unnoticed and the one-week migration starts only after the latency target is missed.",
     "fix": "Name an owner and add automated alerts on p95 > 40 ms at weekly peak and on sustained traffic > 1,000 rps.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "A", "location": "memo.md, Evidence, second bullet",
     "suspicion": "Session-store p95 is compared directly with what may be an end-to-end 50 ms target, overstating headroom.",
     "unresolved_fact": "Whether the 50 ms p95 target applies end to end or to session operations, and what the benchmark timed."},
    {"id": "S2", "status": "needs_validation", "track": "C", "location": "memo.md, Evidence, first sentence",
     "suspicion": "Test environment details (real schema, production instance class, 10-minute runs) are asserted but not recorded in bench.csv.",
     "unresolved_fact": "The load-test harness configuration or run logs."},
    {"id": "S3", "status": "needs_validation", "track": "A", "location": "memo.md, Alternatives: 'session writes dominate'",
     "suspicion": "The read-replica dismissal rests on an unmeasured read/write mix.",
     "unresolved_fact": "Measured ratio of session reads to writes."},
    {"id": "S4", "status": "needs_validation", "track": "C", "location": "memo.md, Alternatives: 'Roughly $95 per month'",
     "suspicion": "Price figure unsourced and may be stale.",
     "unresolved_fact": "Current provider price for the intended node size."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Headroom ratios are miscalculated.", "evidence": "800/200=4, 1600/200=8, 3200/200=16; 31 ms < 50 ms < 118 ms, so the first breach is between 1,600 and 3,200 rps."},
    {"id": "C2", "candidate": "Memo table misstates bench.csv.", "evidence": "All five rows match the CSV exactly on rps, p95 and errors."},
    {"id": "C3", "candidate": "Memo drifts from the request.", "evidence": "It answers the Redis question using bench.csv against the stated 200 rps peak and 50 ms p95 target."},
    {"id": "C4", "candidate": "Busiest-minute peak hides sub-minute bursts that invalidate the decision.", "evidence": "An 8x margin before the target is reached absorbs any plausible sub-minute spike at current scale."}
  ]
}
```