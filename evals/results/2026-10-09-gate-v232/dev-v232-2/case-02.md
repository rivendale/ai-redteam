**Note:** No tools were available in this session, so nothing was opened, run or fetched. The review covers only the text supplied. I did not write the memo, so there is no same-context anchoring, but this is a single-reviewer, no-tools pass.

VERDICT: **SHIP WITH FIXES.** The recommendation follows from the supplied benchmark and the arithmetic reproduces. The weak points are a flawed "protection" argument for bursts, an unowned re-evaluation trigger, and test conditions that are asserted but not evidenced.

CONFIDENCE: **medium.** It is limited by having no tools, by test conditions that the CSV does not record, and by an ambiguity about what the 50 ms target measures.

INPUTS LEDGER:
- **Seen:** request.md, context.md, evidence/bench.csv (5 rows), memo.md.
- **Not seen:** the benchmark harness and its config (schema, instance class, run length, key distribution); production traffic data behind "busiest minute of the last quarter"; load balancer config; Redis pricing source. **These matter**: the memo's headroom claim depends on the bench measuring the same unit of load as the 200 rps peak, and only the harness would show that.

COVERAGE:
- **Scope:** the whole memo plus its cited evidence.
- **Checked:** request.md, context.md, bench.csv, memo.md (Recommendation, Evidence table and both bullets, Alternatives, Trigger, "What this does not claim"), headroom arithmetic, trigger placement against measured curve.
- **Not checked:** benchmark harness (not_supplied), production traffic logs (not_supplied), LB config (not_supplied), Redis price (no_tools).

SEATS AND GATE:
- **Sensitivity:** no personal, financial or credential data found, so the gate passed.
- **Reviewers:** one local reviewer ran. No subagent or cross-vendor seats were available, and none was requested.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | PROBABLE | A | memo.md, "What this does not claim": "the load balancer limit of 2,000 requests per second per client address is the protection there" | The cited limit does not protect the 50 ms target. A single client at the limit (2,000 rps) plus peak traffic (200) gives 2,200 rps. That is above 1,600 rps, the highest tested point that meets the target. A burst spread over many addresses is not capped by a per-address limit at all. | A bot sends 2,000 rps from one address during peak. Total load is about 2,200 rps. Straight-line interpolation between 1,600 (31 ms) and 3,200 (118 ms) gives about 64 ms, so p95 likely exceeds 50 ms. This is PROBABLE because the curve between the tested points is unmeasured. | Run the bench at 2,000 and 2,400 rps. Either show p95 stays under 50 ms, or reword this section to say the per-address limit alone permits load past the target and name the real mitigation, if one exists. | a Y, b N, c N, d N |
| F2 | Low | CONFIRMED | D | memo.md, "What would change this decision" | The trigger (p95 > 40 ms at weekly peak, or > 1,000 rps sustained) has no owner, alert or dashboard. It relies on someone remembering to look each week. | Traffic grows over months and nobody checks. The first sign of a breach is user-facing latency. The week-long migration then starts while the target is already missed. | Name an owner and an automated alert for each trigger condition, and add both to the memo. | a Y, b Y, c N, d N |
| F3 | Low | CONFIRMED | A | memo.md, Alternatives: "Add a read replica. Does not help: session writes dominate." | The read/write mix is asserted with no data. bench.csv has no read/write split. | If reads actually dominate, a replica may be a cheaper headroom option than Redis when the trigger fires. The decision today is unaffected. | Cite the read/write ratio from production metrics, or mark the claim as an assumption. | a Y, b Y, c N, d N |

## NEEDS VALIDATION

- **S1. Unit of load.** Is one benchmark "request" the same as one production request at the 200 rps peak? If each app request makes several session operations, or the bench only drives session queries, the 8–16× headroom shrinks proportionally. *Settled by:* the harness code and a per-request count of session operations in production.
- **S2. What the 50 ms target measures.** Is the target end-to-end request latency or session-store latency? The memo compares session-store p95 directly against it. If it is end-to-end, session latency is only part of the budget. *Settled by:* the owner of the latency target.
- **S3. Shared cluster load.** Was the bench run on an isolated Postgres instance or alongside production workload? "The existing Postgres cluster" serves other traffic, which competes for the same resources. *Settled by:* the harness setup notes.
- **S4. Test conditions.** The memo says the test used the real schema, the production instance class and 10-minute runs. bench.csv records none of this. *Settled by:* the harness config or run logs.
- **S5. Sub-minute bursts.** The peak is the "busiest minute", so bursts within a second could run well above 200 rps. *Settled by:* per-second peak from production metrics.
- **S6. Error units.** The `errors=14` value at 3,200 rps has no unit (count or percent) and no denominator. *Settled by:* the harness output definition.

## REFUTED

- **Wrong multiples:** 800/200 = 4×, 1,600/200 = 8× and 3,200/200 = 16× all recompute correctly, and the table matches the CSV row for row.
- **Trigger fires too late:** 1,000 rps is below 1,600 rps (31 ms), and 40 ms is below 50 ms, so the trigger fires before the measured breach.
- **Drift from the request:** the memo answers the question asked (Redis, yes or no), uses the named evidence and the stated peak and target, and gives a recommendation.

## WHAT HOLDS UP

- The core logic is sound. At the stated peak, p95 is 6 ms against a 50 ms target, with measured compliance up to 8× peak.
- "Do nothing" is a fair alternative, and the decision is reversible within about a week, consistent with the context.
- The memo states its own limits: synthetic keys and no burst model.

## UNVERIFIED CLAIMS

- Real schema, production instance class and 10-minute runs: confirm from the harness config.
- "Busiest minute of last quarter" = 200 rps: confirm from metrics.
- Redis cost of about $95/month: confirm against the provider's pricing page.
- Migration effort of one week: confirm with the module owner.
- LB per-address limit of 2,000 rps: confirm from the LB config.
- "Session writes dominate": confirm from database stats.

## QUESTIONS FOR THE AUTHOR

1. Does one bench request equal one production request in session operations?
2. Is the 50 ms target end-to-end or session-store latency?
3. Was the bench cluster isolated from other workloads?

## DECISION-MAKER SUMMARY

Keeping sessions in Postgres is supported by the benchmark, with wide headroom at today's peak. Before signing, confirm that the benchmark load unit and the 50 ms target mean what the memo assumes, and attach an owned alert to the re-evaluation trigger. If the unit assumption is wrong, the headroom could be much smaller than 8×, but the week-long reversal limits the damage.

## OWNER SUMMARY

The plan to keep using the current database for login sessions looks sound for today's traffic, with a lot of room to grow. Two things should be confirmed first: that the speed test measured the same kind of traffic we actually get, and that someone is automatically alerted if things slow down. The memo's claim that existing traffic limits protect against bot floods is weaker than it sounds and should be tested or reworded.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "evidence/bench.csv", "status": "seen", "matters": true},
    {"item": "memo.md", "status": "seen", "matters": true},
    {"item": "benchmark harness and config", "status": "not_seen", "matters": true},
    {"item": "production traffic metrics", "status": "not_seen", "matters": true},
    {"item": "load balancer config", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "evidence/bench.csv", "kind": "data"},
      {"unit": "memo.md", "kind": "document"},
      {"unit": "memo.md:Evidence headroom multiples", "kind": "claim"},
      {"unit": "memo.md:Alternatives", "kind": "section"},
      {"unit": "memo.md:What would change this decision", "kind": "section"},
      {"unit": "memo.md:What this does not claim", "kind": "section"}
    ],
    "not_checked": [
      {"unit": "benchmark harness and config", "reason": "not_supplied"},
      {"unit": "production traffic metrics", "reason": "not_supplied"},
      {"unit": "load balancer config", "reason": "not_supplied"},
      {"unit": "Redis managed-node pricing", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "A",
     "location": "memo.md, What this does not claim: 'the load balancer limit of 2,000 requests per second per client address is the protection there'",
     "scenario": "One client at the 2,000 rps per-address limit plus 200 rps peak gives about 2,200 rps, above the highest tested passing point (1,600 rps, 31 ms); interpolation toward 3,200 rps (118 ms) suggests about 64 ms p95, and multi-address bursts are not capped at all.",
     "fix": "Benchmark at 2,000 and 2,400 rps, or reword to state the per-address limit permits load beyond the target and name the actual mitigation.",
     "answers": {"a": true, "b": false, "c": false, "d": false}},
    {"id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "D",
     "location": "memo.md, What would change this decision",
     "scenario": "Traffic grows and no one checks the weekly p95; the breach is discovered by users and the one-week migration starts late.",
     "fix": "Assign an owner and automated alerts for p95 > 40 ms at weekly peak and sustained rps > 1,000.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md, Alternatives: 'Does not help: session writes dominate.'",
     "scenario": "If reads dominate, a read replica may be a cheaper headroom option when the trigger fires; the dismissal rests on no supplied data.",
     "fix": "Cite the production read/write ratio, or mark the claim as an assumption.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "A", "location": "memo.md, Evidence",
     "suspicion": "A benchmark request may not equal one production request in session operations, which would shrink the headroom.",
     "unresolved_fact": "Session operations per production request, and what the harness issues per request."},
    {"id": "S2", "status": "needs_validation", "track": "A", "location": "request.md / memo.md, Evidence",
     "suspicion": "The 50 ms p95 target may be end-to-end, not session-store latency.",
     "unresolved_fact": "The definition of the 50 ms target from its owner."},
    {"id": "S3", "status": "needs_validation", "track": "A", "location": "memo.md, Evidence",
     "suspicion": "The bench may have run on an isolated instance, unlike the shared production cluster.",
     "unresolved_fact": "Harness setup: isolated instance or concurrent production-like load."},
    {"id": "S4", "status": "needs_validation", "track": "C", "location": "memo.md, Evidence (test conditions)",
     "suspicion": "Real schema, production instance class and 10-minute runs are asserted but not recorded in bench.csv.",
     "unresolved_fact": "Harness config or run logs."},
    {"id": "S5", "status": "needs_validation", "track": "A", "location": "memo.md, Evidence first bullet",
     "suspicion": "Busiest-minute averaging hides per-second peaks.",
     "unresolved_fact": "Per-second peak rps from production metrics."},
    {"id": "S6", "status": "needs_validation", "track": "C", "location": "evidence/bench.csv errors column",
     "suspicion": "Error count has no unit or denominator.",
     "unresolved_fact": "Harness definition of the errors column."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Headroom multiples are miscomputed.",
     "evidence": "800/200=4, 1600/200=8, 3200/200=16; table matches bench.csv row for row."},
    {"id": "R2", "candidate": "Trigger fires only after the target is breached.",
     "evidence": "1,000 rps is below 1,600 rps (31 ms) and 40 ms is below 50 ms, so the trigger fires before the measured breach."},
    {"id": "R3", "candidate": "Memo drifts from the request.",
     "evidence": "It answers the Redis yes/no question using the named bench.csv, the stated 200 rps peak and the 50 ms target."}
  ]
}
```