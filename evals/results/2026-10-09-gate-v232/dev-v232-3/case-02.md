> Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes. (No subagent or tools were available in this session. The memo was not written in this conversation, so I saw none of the author's reasoning.)

**VERDICT: SHIP WITH FIXES.** The recommendation follows from the supplied data with a wide margin: 8 to 16 times headroom against the stated peak. One supporting claim about bot-burst protection is contradicted by the memo's own numbers and should be corrected.

**CONFIDENCE: medium.** Three things limit it:
- This is a same-context review with no tools.
- The bench metadata the memo cites is not in `bench.csv`.
- It is unclear whether the bench latency is comparable to the 50 ms target.

**INPUTS LEDGER**
- **Seen:** `request.md`, `context.md`, `evidence/bench.csv`, `memo.md`.
- **Not seen:**
  - **Bench run configuration** (schema, instance class, run length, whether other cluster load was present, what "a request" means). This matters because the comparison against the target depends on it.
  - **Traffic data behind "busiest minute of the last quarter".** This matters only slightly, given the margin.
  - **Load balancer configuration.** This matters for F1 only.
  - **Redis pricing source.** This does not matter to the verdict.

**COVERAGE**
- **Scope:** the whole memo plus its evidence file.
- **Checked:**
  - all four documents
  - every row of the memo table against the CSV
  - every multiple and ratio
  - each alternative
  - the trigger
  - the "does not claim" section
- **Not checked:** the bench config, traffic logs and LB config (`not_supplied`).

**SEATS AND GATE:** Only a local same-context review ran. No cross-vendor seats were used because none were requested and the stakes are standard. Sensitivity gate: there is no personal, credential or confidential data.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED (from the memo's own figures) | A | memo.md, "What this does not claim": "the load balancer limit of 2,000 requests per second per client address is the protection there" | A per-address limit does not cap total load. The cap itself (2,000 rps) is also above the highest load that met the target in testing (1,600 rps at 31 ms). The target breaks somewhere between 1,600 and 3,200 rps. | A burst spread across many addresses passes the per-address limit entirely. Even a single address running at its 2,000 rps cap, plus normal traffic, may push p95 past 50 ms. The 14 errors appear at 3,200 rps. | Remove the word "protection" or qualify it. State that bot-burst resilience is out of scope for this decision. Optionally add a total-load rate limit, or a bench point at about 2,200 rps. | a✓ b✓ c✗ d✗ |
| F2 | Low | CONFIRMED (the claim has no supporting evidence) | A | memo.md, Alternatives: "Add a read replica. Does not help: session writes dominate." | The read/write mix is asserted without evidence. `bench.csv` has no read/write split. | If reads actually dominate, a cheap option was dismissed on a wrong premise. The impact is small because the chosen option is to do nothing. | Cite the measured read:write ratio, or soften the sentence to "not evaluated". | a✓ b✓ c✗ d✗ |
| F3 | Low | CONFIRMED | A/D | memo.md, "What would change this decision" | The trigger has no owner, alert or definition. "Weekly peak" implies someone checks manually every week, and "sustained" is undefined. | Nobody watches the metric. Traffic crosses the 1,000 rps trigger unnoticed, and the one-week migration starts late. Latency is non-linear above 1,600 rps (31 ms rising to 118 ms). | Make the trigger an automated alert with a named owner. Define "sustained" (for example, 1,000 rps over 15 minutes). | a✓ b✓ c✗ d✗ |

## NEEDS VALIDATION
- **S1: what the bench latency measures.** Does the bench `p95_ms` measure end-to-end request latency, or only the session-store call? And is one bench "request" equal to one production request, or one session operation? If it is store-only latency, or production requests make several session calls, the 50 ms comparison needs adjusting.
- **S2: bench conditions.** The memo says the bench used the real schema, the production instance class and 10-minute runs, but none of that is recorded in the CSV. Was the shared Postgres cluster carrying its normal production load during the test? An isolated bench understates contention.
- **S3: sub-minute peaks.** The 200 rps figure is the busiest minute, an average. What was the per-second peak? Given 8 times headroom, this is unlikely to change the decision.
- **S4: units of the `errors` column.** Is it a count or a rate? This does not affect the decision.

## REFUTED
- **"The memo table misstates the CSV."** Every row matches: 200/6/0, 400/8/0, 800/12/0, 1600/31/0, 3200/118/14.
- **"The multiples are wrong."** 800/200 = 4, 1,600/200 = 8 and 3,200/200 = 16. The target is first crossed between 1,600 rps (31 ms) and 3,200 rps (118 ms), as stated.
- **"The memo drifts from the request."** It answers the question asked, uses the named file, and applies the stated peak and target.
- **"Synthetic keys are a hidden limitation."** The memo discloses this.

## WHAT HOLDS UP
- The core reasoning holds. At 4 times the stated peak, p95 is 12 ms against a 50 ms target, and there are no errors up to 1,600 rps.
- The "do nothing" option is fairly compared.
- The decision is reversible, with an explicit exit trigger.
- The 1,000 rps traffic trigger sits safely below the observed knee in the latency curve.
- The limitations are disclosed honestly.

## UNVERIFIED CLAIMS
- **"Roughly $95 per month"** for managed Redis. Confirm with a current provider quote.
- **The "one week" migration estimate.** Confirm by scoping the session module and the data migration.
- **The bench metadata** (S2). Confirm with the bench config or run logs.
- **The LB limit of 2,000 rps per address.** Confirm by reading the LB config.
- **"Session writes dominate."** Confirm with query statistics (F2).

## QUESTIONS FOR THE AUTHOR
1. Is the bench p95 end-to-end latency, and does one bench request equal one production request? (S1)
2. Did the bench run alongside normal cluster load? (S2)

## DECISION-MAKER SUMMARY
Keeping sessions in Postgres is well supported: the evidence shows 8 to 16 times headroom against the 50 ms target. Before circulating the memo, fix the bot-burst sentence, and turn the trigger into an automated alert with an owner. If S1 shows the bench measured only the session-store call, recheck the margin; otherwise the risk of proceeding is low and reversible.

## OWNER SUMMARY
The advice not to add a new session store yet is sound: the current database handles many times today's busiest traffic well within the speed goal. One sentence overstates how well we are protected against a flood of automated traffic and should be corrected. Someone should also be named to watch the warning signs, so that a switch, if ever needed, starts on time.

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
    {"item": "bench run configuration (schema, instance class, run length, concurrent load, request definition)", "status": "not_seen", "matters": true},
    {"item": "traffic data behind the 200 rps busiest-minute peak", "status": "not_seen", "matters": false},
    {"item": "load balancer rate-limit configuration", "status": "not_seen", "matters": true},
    {"item": "Redis pricing source", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "evidence/bench.csv", "kind": "data"},
      {"unit": "memo.md", "kind": "document"},
      {"unit": "memo.md#Evidence", "kind": "section"},
      {"unit": "memo.md#Alternatives", "kind": "section"},
      {"unit": "memo.md#What would change this decision", "kind": "section"},
      {"unit": "memo.md#What this does not claim", "kind": "section"},
      {"unit": "multiples 4x, 8x, 16x against the 200 rps peak", "kind": "claim"},
      {"unit": "bench latency is comparable to the 50 ms p95 target", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "bench run configuration", "reason": "not_supplied"},
      {"unit": "traffic logs", "reason": "not_supplied"},
      {"unit": "load balancer configuration", "reason": "not_supplied"},
      {"unit": "Redis pricing", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md, What this does not claim: 'the load balancer limit of 2,000 requests per second per client address is the protection there'",
     "scenario": "A burst spread across many client addresses passes the per-address limit. A single address at its 2,000 rps cap already exceeds the highest tested load that met the target (1,600 rps at 31 ms), so p95 may exceed 50 ms.",
     "fix": "Remove or qualify the 'protection' claim, state that bot-burst resilience is out of scope, and optionally add a total-load rate limit or a bench point near 2,200 rps.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md, Alternatives: 'Add a read replica. Does not help: session writes dominate.'",
     "scenario": "No read/write split is supplied, so if reads dominate, a cheap alternative was dismissed on an unsupported premise.",
     "fix": "Cite the measured read:write ratio, or reword to 'not evaluated'.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md, What would change this decision: trigger definition",
     "scenario": "The trigger has no owner or alert and 'sustained' is undefined, so traffic can cross 1,000 rps unnoticed and the one-week migration starts late while latency climbs steeply above 1,600 rps.",
     "fix": "Make the trigger an automated alert with a named owner and define 'sustained' (for example, 1,000 rps over 15 minutes).",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "A", "location": "evidence/bench.csv: p95_ms column",
     "suspicion": "Bench latency may measure only the session-store call, or bench requests may not map one-to-one to production requests, making the comparison with the 50 ms target invalid.",
     "unresolved_fact": "Whether p95_ms is end-to-end request latency and how many session operations a production request performs."},
    {"id": "S2", "status": "needs_validation", "track": "A", "location": "memo.md, Evidence: 'sessions table, the real schema, the production instance class, 10-minute runs'",
     "suspicion": "Bench conditions are asserted but not recorded, and an isolated bench may understate contention on a shared cluster.",
     "unresolved_fact": "The bench run configuration and whether normal production load ran on the cluster during the test."},
    {"id": "S3", "status": "needs_validation", "track": "A", "location": "memo.md, Evidence: 'the busiest minute of the last quarter'",
     "suspicion": "Per-second peaks may exceed the 200 rps busiest-minute average.",
     "unresolved_fact": "The maximum per-second request rate during the last quarter."},
    {"id": "S4", "status": "needs_validation", "track": "A", "location": "evidence/bench.csv: errors column",
     "suspicion": "The units of the errors column are unstated.",
     "unresolved_fact": "Whether errors is a count or a rate."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The memo table misstates the CSV.", "evidence": "All five rows match bench.csv exactly."},
    {"id": "C2", "candidate": "The headroom multiples are wrong.", "evidence": "800/200=4, 1600/200=8, 3200/200=16, and the 50 ms target is first crossed between 1,600 rps (31 ms) and 3,200 rps (118 ms)."},
    {"id": "C3", "candidate": "The memo drifts from the request.", "evidence": "It answers the Redis question using the named bench file, the stated 200 rps peak and the 50 ms p95 target."},
    {"id": "C4", "candidate": "The use of synthetic keys is a hidden limitation.", "evidence": "It is disclosed in 'What this does not claim'."}
  ]
}
```