**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent and no tools were available. Every check below is arithmetic against the supplied text. Nothing was executed or opened.

VERDICT: **SHIP WITH FIXES.** The load test supports the recommendation with wide margin, and the decision can be reversed in about a week. Two claims need tightening first: the bot-burst rate limit, which is set above the highest load that passed the test, and what the benchmark's p95 actually measures.

CONFIDENCE: **medium.** It is limited by the single same-context reviewer, having no tools, and no access to the test harness or run configuration behind `bench.csv`.

INPUTS LEDGER:
- **Seen:** the request (verbatim), the context, `evidence/bench.csv` and `memo.md`.
- **Not seen:** the load-test harness and config. The memo's description ("sessions table, the real schema, production instance class, 10-minute runs") rests on this, so the gap matters for confidence, though not for direction.
- **Not seen:** the traffic source behind "busiest minute of the last quarter." This matters a little.
- **Not seen:** a source for the Redis price. This matters little.
- **Not seen:** the load balancer config. This matters for finding 1.

SEATS AND GATE:
- One local reviewer ran.
- Sensitivity gate passed: the work contains no personal, financial or credential data.
- No cross-vendor seats: none were requested, and the depth is standard.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Medium | CONFIRMED (arithmetic) / PROBABLE (impact) | A | memo.md, "What this does not claim" | The memo calls the load balancer limit "the protection," but it caps each client address at 2,000 rps. That is above 1,600 rps, the highest rate that passed. It also does nothing against traffic spread across many addresses. | A bot at 2,000 rps from one address, or 5,000 rps from three or more addresses, puts load in the untested 1,600–3,200 band, or past 3,200 where p95 was 118 ms with errors. Session latency degrades for everyone. | Either remove the claim and state that burst exposure is accepted, or add an aggregate rate limit below about 1,600 rps. Test at 2,000 and 2,400 rps to find the knee. Adding Redis is not necessarily the fix. | confirmed (a defender could argue the risk is out of scope, but the memo names it as covered) |
| 2 | Medium | UNVERIFIED | A | memo.md, Evidence; bench.csv `p95_ms` | It is unstated whether `p95_ms` is end-to-end request latency or session-store latency only. The 50 ms target reads as end-to-end. | If the benchmark timed only the session query, the 12 ms at 800 rps excludes app and network time. The "4×" and "8–16×" headroom claims then overstate the margin. | State what was measured. If it was store-only, add the observed non-session latency at peak. | n/a (Medium) |
| 3 | Medium | PROBABLE | D | memo.md, "What would change this decision" | The trigger has no owner or alert. "p95 above 40 ms at the weekly peak" depends on someone checking every week. | Nobody looks. Traffic grows past 1,000 rps unnoticed, and the one-week migration starts after the target is already missed. | Name an owner. Set up automated alerts on p95 above 40 ms and on sustained rps above 1,000. | n/a |
| 4 | Low | UNVERIFIED | A | memo.md, Alternatives (read replica) | "Session writes dominate" has no supporting evidence. The bench reports no read/write mix. | Unlikely to change the decision, but the read-replica alternative is dismissed on an unsupported claim. | Cite the measured read/write ratio, or soften the wording. | n/a |
| 5 | Low | PROBABLE | A | memo.md, Evidence ("busiest minute") | A per-minute peak averages away bursts within the minute. Synthetic keys and single runs per rate hide variance and cache/index effects. | Real per-second peaks run several times 200 rps. Given the 8× margin, harm is unlikely. | Report the peak per-second rate. Note run count and data volume (number of session rows). | n/a |
| 6 | Low | UNVERIFIED | A | memo.md, bench.csv `errors` | "14 errors" has no denominator or error type. | Readers cannot tell whether 3,200 rps is degraded or failing. | Report it as an error rate (%) and give the type. | n/a |

## What holds up
- **No drift.** The memo answers the question that was asked, uses the named evidence, and applies the stated 200 rps and 50 ms targets.
- **The table matches the CSV** row for row.
- **All ratios recompute correctly:** 800/200 = 4×, 1,600/200 = 8×, 3,200/200 = 16×.
- **The threshold claim is correct.** The 50 ms target is first exceeded between 1,600 rps (31 ms) and 3,200 rps (118 ms).
- **The trigger has margin.** The 1,000 rps trigger sits about 1.6× below the last passing point, which suits a one-week migration lead time.
- **The alternatives are compared fairly,** including doing nothing. The memo states its limits.

## Unverified claims
- **Test fidelity:** real schema, production instance class, 10-minute runs. Confirm by checking the harness config and run logs.
- **The ~$95/month Redis cost.** Confirm against the vendor price page.
- **The one-week migration estimate.** Confirm by scoping the session module.
- **"Session writes dominate."** Confirm from DB stats.
- **The load balancer limit of 2,000 rps per address.** Confirm from the LB config.

## Questions for the author
1. Is `p95_ms` end-to-end request latency or session-store latency?
2. Is there any aggregate rate limit, or only the per-address one?
3. Who owns the trigger, and is it alerted or checked by hand?

## Decision-maker summary
Keeping sessions in Postgres is well supported: the measured peak runs at about a quarter of the load that stayed well under target. Before signing, fix the bot-burst claim, since the per-address limit is set above the highest tested safe load, and confirm what the latency figure measures. If you proceed as is, the main risk is a traffic burst degrading sessions. Redis would not be the cure for that.

## Owner summary
Not adding Redis is the right call for now: our current traffic is far below where the database starts to slow down. The memo overstates how well we are protected against sudden bot traffic, and it should say exactly what the speed test measured. Someone should also be named to watch the warning thresholds so the switch can happen in time if traffic grows.

```json
{
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "load-test harness/config", "status": "not_seen", "matters": true},
    {"item": "traffic source for 200 rps peak", "status": "not_seen", "matters": false},
    {"item": "load balancer config", "status": "not_seen", "matters": true},
    {"item": "Redis pricing source", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "findings": [
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "A", "location": "memo.md: What this does not claim",
     "scenario": "Per-address LB limit of 2,000 rps exceeds the highest passing tested rate (1,600 rps) and does not cap multi-address bursts; a 5,000 rps bot burst lands in or past the 3,200 rps band where p95 was 118 ms with errors.",
     "fix": "Drop the 'protection' claim or add an aggregate limit below ~1,600 rps; test 2,000 and 2,400 rps.", "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "track": "A", "location": "memo.md: Evidence; bench.csv p95_ms",
     "scenario": "If p95_ms is session-store latency only, end-to-end p95 against the 50 ms target is higher and the stated headroom is overstated.",
     "fix": "State the measurement scope; add non-session latency at peak if store-only.", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "D", "location": "memo.md: What would change this decision",
     "scenario": "No owner or alert for the trigger; growth past 1,000 rps goes unnoticed and the one-week migration starts too late.",
     "fix": "Name an owner and automate alerts on p95 > 40 ms and sustained rps > 1,000.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "UNVERIFIED", "track": "A", "location": "memo.md: Alternatives (read replica)",
     "scenario": "'Session writes dominate' is unsupported by the bench; the read-replica option is dismissed without evidence.",
     "fix": "Cite the measured read/write ratio or soften the claim.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "PROBABLE", "track": "A", "location": "memo.md: Evidence (busiest minute)",
     "scenario": "A per-minute peak hides per-second bursts; synthetic keys and single runs hide variance.",
     "fix": "Report the peak per-second rate, run count and session row volume.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "UNVERIFIED", "track": "A", "location": "bench.csv errors column",
     "scenario": "14 errors has no denominator or type, so readers cannot judge whether 3,200 rps is degraded or failing.",
     "fix": "Report it as an error rate and give the error type.", "status": "n/a"}
  ]
}
```