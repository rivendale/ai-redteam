VERDICT: **REWORK.** The memo uses about 3,000 runs per month. The supplied evidence shows 30,210 to 32,760. At $0.06 per run, Stepwise would cost about $1,903 per month against the VM's $400, so the move would cost about $18,000 a year more, not save $2,640.

CONFIDENCE: **medium.** The core finding is plain arithmetic on the supplied CSV and holds at high confidence. Three things limit the rest:
- I had no tools, so I could check no external facts (Stepwise pricing, the 99.9% SLA, the VM bill).
- No subagent or second seat was available, so this is a single-reviewer pass. I did not author the memo.
- What a "run" means in the CSV is not defined.

INPUTS LEDGER:
- **Seen:** `request.md`, `context.md`, `memo.md`, `evidence/run_counts.csv`.
- **Not seen:**
  - Stepwise's price list, SLA, and retry and history documentation (matters: the price is load-bearing).
  - The VM's actual bill (matters: $400 is the baseline the whole comparison rests on).
  - The batch scripts and the existing retry code (matters for the port effort and the "removes retry code" claim).
  - A definition of the CSV's `runs` column (matters: see NV1).

COVERAGE:
- **Scope:** the whole memo, checked against the request and the CSV.
- **Checked:**
  - `memo.md`: every section (Recommendation, Why, Alternatives, Plan, Risks).
  - `evidence/run_counts.csv`: all six rows, summed and averaged by hand.
  - `request.md` and `context.md`.
- **Not checked:** external pricing, SLA and feature claims (no tools).

SEATS AND GATE: one reviewer ran (this session, no tools, no subagent). Cross-vendor seats were not requested and not run. Sensitivity gate passed: the material is operational cost data, with no personal or confidential records.

### FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | **Critical** | CONFIRMED | A/C | `memo.md:7-8` ("about 3,000 runs per month… $180 per month… saving of $220") vs `evidence/run_counts.csv:2-7` | The run count is off by about 10x from the evidence the request required. The CSV sums to 190,320 runs over 6 months, an average of 31,720 per month. 31,720 × $0.06 = $1,903.20 per month. The latest month is 32,760 × $0.06 = $1,965.60. Net effect: about **+$1,503 per month (≈ +$18,038 per year)**, not −$220 per month. The recommendation reverses. | The team approves the move on the memo's figures. The first full Stepwise invoice is about $1,900 against a $400 VM, and the VM has already been decommissioned (F2). | Recompute from the CSV and state the run definition (NV1). Re-decide on the corrected numbers. On these numbers Stepwise is the most expensive option. | a✓ b✓ c✓ d✓ |
| F2 | Medium | CONFIRMED (plan text) / PROBABLE (impact) | A | `memo.md:19` ("Decommission the VM the same day") | There is no rollback window for a job that feeds next-morning reports. Two weeks of parallel running (line 18) does not cover month-end, rare inputs, or Stepwise's own first-week incidents. | A first-week failure on Stepwise (a quota limit, a missing secret, a timeout) means no reports that morning, and the fallback VM no longer exists. | Keep the VM stopped but restorable, or keep a snapshot, for at least one month-end cycle. Define a rollback trigger. | a✓ b✗ c✗ d✗ |
| F3 | Medium | CONFIRMED | A | `memo.md:12-14` | The alternatives are listed but never compared. Option 3 (a container job at about $60 per month) is cheaper than both the VM and Stepwise even on the memo's own numbers, and it is dismissed without a reason. With corrected numbers it is the strongest option on cost. | A decision-maker sees three options and one recommendation with no comparison table, and approves the costliest one. | Add a side-by-side table: monthly cost, effort, on-call burden, retry behaviour, rollback. Justify the choice against option 3. | a✓ b✓ c✗ d✓ |
| F4 | Low | CONFIRMED | A | `memo.md:7` vs CSV | Per-run pricing scales with volume, and runs grew 8.4% in six months (30,210 → 32,760). The memo treats usage as flat. | At this growth rate the Stepwise bill keeps rising while the VM cost is fixed. | Project costs at current growth for 12 months. | a✓ b✓ c✗ d✗ |
| F5 | Low | CONFIRMED | A | `memo.md:21-22` | The only risk listed is a vendor outage. Missing: cost overrun (F1), migration defects, secrets and network access from a managed service, lock-in, and the exit path. 99.9% availability still allows about 43 minutes of downtime a month, which may land inside the nightly window. | An unlisted risk materialises with no mitigation owner. | Add a risk table with mitigations. Check the SLA's terms against the batch window. | a✓ b✓ c✗ d✗ |

**Sibling search (F1):** I checked every other figure in the memo for the same root cause (an unsourced or misread input):
- **$220/month and $2,640/year (`memo.md:8`):** derived from the wrong count, so wrong by inheritance. The $2,640 "stakes" figure in `context.md` repeats the same error.
- **$400 (line 6) and $60 (line 14):** neither has a source. See NV2 and NV3.

No other figure in the memo is drawn from the CSV. This is not a security finding.

### NEEDS VALIDATION
- **NV1.** Does one CSV "run" equal one billable Stepwise workflow run? A nightly batch implies about 30 runs per month, so 31,000 suggests per-item or per-step runs. **Settled by:** the CSV's source query, and how Stepwise counts runs for the ported definitions.
- **NV2.** Is the VM really $400 per month all-in? **Settled by:** the actual billing line items.
- **NV3.** Is option 3 really about $60 per month of node capacity? **Settled by:** cluster cost data.
- **NV4.** Is Stepwise's price still $0.06 per run, and are there step, storage or egress charges on top? **Settled by:** the current price page, dated.
- **NV5.** Do Stepwise's retries and 90-day history actually replace the hand-written retry code (idempotency, partial failures)? **Settled by:** Stepwise docs plus the existing retry code.

### REFUTED
- **"$0.06 × 3,000 ≠ $180."** Refuted: the arithmetic is right (3,000 × 0.06 = 180). The error is in the input, not the multiplication.

### WHAT HOLDS UP
- The structure is sound: recommendation, rationale, alternatives, phased plan, risks.
- A parallel-run week is planned.
- The operational argument (no patching, fewer stuck-job pages) is a legitimate non-cost benefit, though it is unquantified.

### UNVERIFIED CLAIMS
- VM $400 per month: confirm against the bill.
- Stepwise $0.06 per run: confirm against the dated price page.
- 99.9% availability: confirm against the SLA text.
- Automatic retries and 90-day history: confirm against the docs.
- Container option at about $60 per month: confirm against cluster costs.
- "Removes our hand-written retry code": confirm against the code.

### QUESTIONS FOR THE AUTHOR
1. Where did "about 3,000 runs per month" come from, given that the CSV shows about 31,700?
2. What does one CSV row's `runs` count measure, and how would Stepwise bill it?
3. Why was the container option rejected?

### DECISION-MAKER SUMMARY
Do not approve the move. Using the required usage data, Stepwise costs about $1,900 per month against $400 for the VM, a loss of roughly $18,000 a year rather than a $2,640 saving. Ask for a corrected memo that compares all three options on real numbers. That comparison should give the container option real consideration, and the plan should keep a rollback path for the VM.

### OWNER SUMMARY
The memo's cost math used a usage figure about ten times lower than our actual records, so the claimed saving is really a large extra cost. The plan also shuts down the old server on cutover day with no way back. It should be redone with the real numbers before anyone decides.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "memo.md", "status": "seen", "matters": true},
    {"item": "evidence/run_counts.csv", "status": "seen", "matters": true},
    {"item": "Stepwise pricing/SLA/docs", "status": "not_seen", "matters": true},
    {"item": "VM billing records", "status": "not_seen", "matters": true},
    {"item": "batch scripts and retry code", "status": "not_seen", "matters": false},
    {"item": "definition of CSV runs column", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-single-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "memo.md", "kind": "document"},
      {"unit": "evidence/run_counts.csv", "kind": "data"},
      {"unit": "memo.md:Why", "kind": "section"},
      {"unit": "memo.md:Alternatives considered", "kind": "section"},
      {"unit": "memo.md:Plan", "kind": "section"},
      {"unit": "memo.md:Risks", "kind": "section"}
    ],
    "not_checked": [
      {"unit": "Stepwise pricing, SLA, retry and history claims", "reason": "no_tools"},
      {"unit": "VM cost and container node cost", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md:7-8 vs evidence/run_counts.csv:2-7",
     "scenario": "Memo uses ~3,000 runs/month; CSV averages 31,720 (190,320/6). At $0.06/run Stepwise costs ~$1,903/month vs $400 VM, about +$18,038/year instead of a $2,640 saving; the recommendation reverses.",
     "fix": "Recompute from the CSV, define what a run is, and re-decide; Stepwise is the costliest option on corrected numbers.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "every figure in memo.md and the stakes figure in context.md",
                           "found": "$220/month and $2,640/year in memo.md:8 inherit the error; $400 and $60 are unsourced (NV2, NV3)"}},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "A",
     "location": "memo.md:19",
     "scenario": "VM decommissioned on cutover day; a first-week Stepwise failure leaves no fallback and next-morning reports are missed.",
     "fix": "Keep the VM restorable through at least one month-end cycle with a defined rollback trigger.",
     "answers": {"a": true, "b": false, "c": false, "d": false}},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md:12-14",
     "scenario": "Alternatives are listed but not compared; the ~$60/month container option beats both others on cost and is dismissed without a reason.",
     "fix": "Add a side-by-side comparison of cost, effort, on-call, retries and rollback, and justify the choice against option 3.",
     "answers": {"a": true, "b": true, "c": false, "d": true}},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md:7 vs evidence/run_counts.csv",
     "scenario": "Runs grew 8.4% in six months; per-run billing rises with volume while the VM cost is fixed, which the memo ignores.",
     "fix": "Project 12-month cost at the observed growth rate.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md:21-22",
     "scenario": "Only vendor outage is listed; 99.9% allows ~43 min/month of downtime, which could hit the nightly window. Cost overrun, migration, secrets, lock-in and exit are not covered.",
     "fix": "Add a risk table with mitigations and check the SLA terms against the batch window.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "NV1", "status": "needs_validation", "track": "C", "location": "evidence/run_counts.csv",
     "suspicion": "A nightly batch implies ~30 runs/month; 31,000 suggests per-item or per-step counts.",
     "unresolved_fact": "Whether one CSV run equals one billable Stepwise workflow run."},
    {"id": "NV2", "status": "needs_validation", "track": "C", "location": "memo.md:6",
     "suspicion": "The $400/month VM cost is unsourced.", "unresolved_fact": "Actual VM billing line items."},
    {"id": "NV3", "status": "needs_validation", "track": "C", "location": "memo.md:14",
     "suspicion": "The ~$60/month container cost is unsourced.", "unresolved_fact": "Cluster node cost data."},
    {"id": "NV4", "status": "needs_validation", "track": "C", "location": "memo.md:7",
     "suspicion": "$0.06/run may be stale or omit step, storage or egress charges.", "unresolved_fact": "Current dated Stepwise price page."},
    {"id": "NV5", "status": "needs_validation", "track": "C", "location": "memo.md:9",
     "suspicion": "Managed retries may not replace the custom retry logic (idempotency, partial failure).",
     "unresolved_fact": "Stepwise retry semantics vs the existing retry code."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "3,000 x $0.06 does not equal $180.",
     "evidence": "3,000 x 0.06 = 180; the multiplication is correct, the input count is wrong (F1)."}
  ]
}
```

I had no tools, so I did not run this block through `tools/validate_findings.py`.