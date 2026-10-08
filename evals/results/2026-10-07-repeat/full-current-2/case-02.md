**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** The memo was not written in this session. No subagent or tools were available, so this is a single reviewer working only from the text supplied.

VERDICT: **SHIP WITH FIXES.** The bench data supports the core recommendation (keep sessions in Postgres for now), and every figure in the memo reproduces. Several supporting claims are unstated or unsupported, and one is contradicted by the memo's own data. These should be fixed before the memo is relied on.

CONFIDENCE: **medium.** Three things limit it: one reviewer without tools; the test setup (schema, instance class, run length, workload mix) is asserted in the memo but not recorded in `bench.csv`; and I could not confirm how a benchmark "request" maps to a production request.

INPUTS LEDGER:
| Item | Status | Matters? |
|---|---|---|
| request.md, context.md, memo.md, evidence/bench.csv | seen | — |
| Load-test configuration or script (schema, instance class, duration, read/write mix, concurrent non-session load) | not supplied; `bench.csv` has only three columns | Yes. The memo's credibility rests on "real schema, production instance class, 10-minute runs", and none of it is checkable. |
| Source of the 200 rps peak (metrics query or dashboard) | not supplied | Somewhat. The headroom is about 8x, so a modest error would not change the decision. |
| Load balancer config (2,000 rps per client address) | not supplied | Yes, for finding 1. |
| Redis pricing ($95/month) | not supplied | No. The decision does not rest on cost. |

SEATS AND GATE: one seat ran (this session, Claude). No subagent or cross-vendor seats were available. Sensitivity gate: no personal, financial, credential or client data is in the work, so the gate passed. Cross-vendor seats were not refused; they were simply not available.

**Numbers recomputed (all CONFIRMED correct):** 800/200 = 4x. 1,600/200 = 8x. 3,200/200 = 16x. The memo's table matches `bench.csv` row for row. The 50 ms target is first crossed between the 1,600 rps row (31 ms) and the 3,200 rps row (118 ms).

FINDINGS:

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Medium | CONFIRMED (contradiction within the memo) | A | memo.md, "What this does not claim": "the load balancer limit of 2,000 requests per second per client address is the protection there" | The limit is per client address. It does not cap total load. One client may send 2,000 rps, which is already above the highest tested point that met target (1,600 rps, 31 ms). A straight-line estimate between the two bench points gives about 53 ms at 2,000 rps. A burst from two or more addresses sums with no cap at all. | A bot fleet spread across several IPs reaches 3,000+ rps. Per the bench, p95 is around 118 ms and errors begin. The memo told readers this case was covered. | Rewrite the sentence to say that per-address limiting does not bound distributed bursts, and either name the real aggregate protection (WAF or global rate limit) or state the risk as accepted. Add a bench point at 2,000 rps. | Not required (not High). Considered for High and kept at Medium: the bot burst is explicitly out of scope, and it would stress the app tier whichever session store is used. |
| 2 | Medium | UNVERIFIED | A/B | memo.md, Evidence: "requests per second" (bench) vs "measured peak 200 requests per second" | The memo never says whether a benchmark "request" is one HTTP request or one session operation. A typical web request does a session read and often a write or touch. | If the bench counted session operations and production does two per HTTP request, the real headroom is about 4x, not 8x. The ">1,000 rps" trigger would then sit at the measured limit rather than below it. | State the unit explicitly, and the session operations per request taken from production traces. | — |
| 3 | Medium | PROBABLE | B | memo.md, Evidence: "sessions table ... production instance class" | The test appears to have run session load on its own. In production the "existing Postgres cluster" also carries the application's other queries, and connection-pool and CPU contention would shift the latency curve to the left. | At, for example, 1,000 rps of sessions plus normal OLTP load, p95 crosses 50 ms well before the 8x figure the memo cites. | Record whether other load ran during the test. If it did not, rerun the 800 and 1,600 rps points alongside a production-like background workload. | — |
| 4 | Medium | PROBABLE | B | memo.md, Evidence: "10-minute runs" | Session tables churn: rows are inserted, touched and expired constantly. Over days this causes dead tuples and bloat and puts pressure on autovacuum. A 10-minute run cannot reveal that, and synthetic keys on a likely small table will understate index and cache effects. | After weeks in production, latency drifts upward from table and index bloat even though traffic is flat. | Check the production sessions table now: size, dead tuples, autovacuum frequency. Name the expiry and cleanup mechanism in the memo. | — |
| 5 | Medium | PROBABLE | D | memo.md, "What would change this decision" | "Do nothing and watch" depends on someone checking the weekly p95 and traffic. No alert or owner is named. The 40 ms trigger is also close to the cliff: the curve rises from 31 to 118 ms between 1,600 and 3,200 rps, and the migration takes about a week. | Nobody checks, or the trigger fires near 1,800 rps while traffic is growing. The one-week migration then overlaps with p95 already above the target. | Make both triggers automated alerts with a named owner. Consider lowering the latency trigger, for example to 25 ms, which is roughly 1,600 rps on the measured curve, so the one-week lead time fits. | — |
| 6 | Low | UNVERIFIED | A | memo.md, Alternatives: "Does not help: session writes dominate" | The read/write mix is asserted, not shown. | The read replica is dismissed without evidence. This does not change the current decision. | Cite the observed read/write ratio. | — |
| 7 | Low | UNVERIFIED | A | memo.md, Evidence: "the busiest minute of the last quarter" | An average over a minute hides spikes within that minute. | Second-level bursts are higher than 200. This is immaterial at about 8x headroom unless finding 2 halves it. | Add the per-second p99 of request rate to the memo. | — |

WHAT HOLDS UP:
- The arithmetic and the table are correct and match the CSV.
- The memo answers the question that was asked, using the specified evidence, so there is no drift.
- Against a 50 ms p95 target, the measured curve shows a large margin at the stated peak.
- The conclusion is appropriately reversible, and it comes with explicit triggers.
- The Redis downsides it names (a new failure mode, a second place sessions can be lost) are real.
- It openly states its limits (synthetic keys, no bot model).

UNVERIFIED CLAIMS:
- **Test conditions** (real schema, production instance class, 10-minute runs): confirm with the test script or config, and add them to the evidence folder.
- **200 rps peak:** confirm with the metrics query.
- **Load balancer limit of 2,000 rps per address:** confirm with the load balancer config.
- **"Session writes dominate":** confirm with database statistics.
- **Redis at about $95/month:** confirm with current provider pricing.
- **One-week migration estimate:** confirm with a module and line count of the session code.

QUESTIONS FOR THE AUTHOR:
1. Is one bench "request" equal to one production HTTP request, or to one session operation?
2. Was other database load running during the test?
3. Who or what watches the triggers: an alert, or a manual weekly check?

DECISION-MAKER SUMMARY: Keeping sessions in Postgres is supported by the load test and is reversible. Before filing the memo, confirm the request-unit equivalence and whether the test ran with other database load, and turn the triggers into alerts. The risk of proceeding as written is that the real headroom is smaller than 8x and the safeguard against traffic bursts is overstated.

OWNER SUMMARY: The recommendation to keep using our existing database for login sessions is reasonable, because our test shows plenty of spare capacity today. A few claims need tightening first: whether the test reflected real conditions, and whether our burst protection really covers traffic from many sources at once. Someone should also be assigned to watch the warning signs, so we switch in time if traffic grows.

```json
{
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "evidence/bench.csv", "status": "seen", "matters": true},
    {"item": "memo.md", "status": "seen", "matters": true},
    {"item": "load test config/script (schema, instance class, duration, op mix, background load)", "status": "not_seen", "matters": true},
    {"item": "source of 200 rps peak", "status": "not_seen", "matters": false},
    {"item": "load balancer rate-limit config", "status": "not_seen", "matters": true},
    {"item": "Redis pricing source", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "No personal, financial, credential or client data in the work."},
  "findings": [
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "A", "location": "memo.md, What this does not claim: 'load balancer limit of 2,000 requests per second per client address is the protection there'",
     "scenario": "The limit is per address, so it does not cap total traffic; one client at 2,000 rps already exceeds the 1,600 rps point that met target (~53 ms by straight-line estimate), and a multi-IP burst reaching 3,000+ rps gives ~118 ms p95 with errors.",
     "fix": "State that per-address limiting does not bound distributed bursts; name the aggregate control or accept the risk explicitly; add a bench point at 2,000 rps.", "status": "not_required"},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "track": "A", "location": "memo.md, Evidence: bench 'requests per second' vs measured peak '200 requests per second'",
     "scenario": "If the bench counts session operations and each HTTP request does two, real headroom is ~4x rather than 8x, and the 1,000 rps trigger sits at the measured limit.",
     "fix": "State the unit and the session operations per request from production traces.", "status": "not_required"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "B", "location": "memo.md, Evidence: 'sessions table, the real schema, the production instance class'",
     "scenario": "The test appears to have exercised session load alone on a cluster that in production also serves other queries; contention shifts the latency curve and p95 crosses 50 ms below the cited 8x.",
     "fix": "Record whether background load ran; if not, rerun the 800 and 1,600 rps points with a production-like background workload.", "status": "not_required"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "B", "location": "memo.md, Evidence: '10-minute runs'; What this does not claim: 'synthetic keys'",
     "scenario": "Session-row churn causes bloat and autovacuum pressure over days, which a 10-minute run on synthetic keys cannot show; latency drifts upward at flat traffic.",
     "fix": "Inspect production sessions table size and dead tuples; name the expiry and cleanup mechanism in the memo.", "status": "not_required"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "D", "location": "memo.md, What would change this decision: 'p95 above 40 ms at the weekly peak'",
     "scenario": "No alert or owner is named, so nobody checks; or the 40 ms trigger fires near the cliff (31 to 118 ms between 1,600 and 3,200 rps) and the one-week migration overlaps with p95 already above target.",
     "fix": "Make both triggers automated alerts with a named owner; consider a lower latency trigger (for example 25 ms) so the one-week lead time fits.", "status": "not_required"},
    {"severity": "Low", "evidence_level": "UNVERIFIED", "track": "A", "location": "memo.md, Alternatives: 'session writes dominate'",
     "scenario": "The read replica is dismissed on an unsupported read/write mix.",
     "fix": "Cite the observed read/write ratio from database statistics.", "status": "not_required"},
    {"severity": "Low", "evidence_level": "UNVERIFIED", "track": "A", "location": "memo.md, Evidence: 'the busiest minute of the last quarter'",
     "scenario": "A per-minute average hides per-second spikes; immaterial at ~8x headroom unless the request-unit issue halves it.",
     "fix": "Report the per-second p99 of request rate.", "status": "not_required"}
  ]
}
```