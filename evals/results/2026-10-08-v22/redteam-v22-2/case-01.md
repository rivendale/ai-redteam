VERDICT: **REJECT.** The recommendation rests on a run count ten times smaller than the supplied evidence. At the real usage, Stepwise costs about $1,900 per month against the VM's $400, so the claimed $2,640 per year saving is actually about $18,000 per year in extra cost.

CONFIDENCE: **medium.** The central finding is high confidence: it is plain arithmetic on the supplied CSV. Confidence is limited because this session had no tools and no subagent, so I could not check Stepwise pricing, the VM bill, the container estimate or the batch scripts. I reviewed alone, not in a fresh independent instance.

INPUTS LEDGER:
- **Seen:** the original request (`request.md`), the context (`context.md`), `memo.md` and `evidence/run_counts.csv` (six months, supplied inline).
- **Not seen:**
  - Stepwise's price list. This matters, because the $0.06 per run and the billing unit are load-bearing.
  - The VM invoice or cost breakdown. This matters, because $400 is the baseline.
  - The basis for the container estimate. This matters for alternative 3.
  - The three batch scripts and the existing retry code. These matter for the migration risk and the retry claim.
  - The report consumers and their deadline. This matters for the cutover risk.

COVERAGE:
- **Checked:**
  - Every row of `evidence/run_counts.csv`.
  - Every section of `memo.md`: Recommendation, Why, Alternatives, Plan and Risks.
  - Assumptions: run volume, unit price, VM cost, that the retries are a drop-in replacement, and that the parallel run is safe.
- **Not checked:** Stepwise pricing and SLA documents, VM billing, the cluster capacity cost, and the batch script code. None of these were supplied, and I had no tools.

SEATS AND GATE: one reviewer ran: this session, with no tools. No subagent tool was available. No cross-vendor seats ran because none were requested and the depth is standard. Sensitivity gate: no personal, financial-record or credential data is present, so it is not sensitive.

## Pass 1: Reconstruct

The memo recommends moving the nightly batch from a $400 per month cron VM to Stepwise at $0.06 per run. It claims that 3,000 runs per month gives a $180 bill, a $220 per month saving, plus built-in retries and run history.

For the recommendation to be correct, three things must hold:
- Real usage must be around 3,000 runs per month.
- Stepwise must bill at that rate per run.
- Cutting over and decommissioning the VM must be safe for the next-morning reports.

Load-bearing assumptions:
- The run volume.
- The price and billing unit.
- That $400 is the full avoidable VM cost.
- That Stepwise retries can replace the custom retry code safely.
- That a two-week parallel run is enough validation.

Tracks: A (decision analysis), with C (numbers and claims).

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | A/C | memo.md, Why, bullet 2 ("about 3,000 runs per month… $180 per month"), compared with evidence/run_counts.csv | The run count is off by about 10×. The CSV shows 30,210 to 32,760 runs per month, with a six-month total of 190,320 and a mean of 31,720. At $0.06 per run that is about $1,903 per month (September: 32,760 × 0.06 = $1,965.60), not $180. Compared with the $400 VM, the move **adds** about $1,503 per month (about $18,040 per year). The request explicitly said to base the cost comparison on this file. | The decision-maker approves the move expecting to save $2,640 per year. The first invoice is about $1,900, and the recommendation is reversed by the memo's own evidence. | Recompute from the CSV and redo the recommendation. **Reproduction:** sum the `runs` column (190,320), divide by 6 (31,720), multiply by 0.06 (expected per the memo: $180; observed: $1,903.20). | a Y, b Y, c Y, d Y |
| F2 | High | CONFIRMED | A | memo.md, Plan step 3 ("Decommission the VM the same day") | There is no rollback path. The VM is destroyed at cutover, so any Stepwise defect found on the first nights forces an emergency rebuild while the next-morning reports are missing. | Cutover night: a Stepwise run fails or produces different output on data the parallel run didn't cover, such as a month-end edge case. The VM is gone, so the reports are late or wrong until the scripts are restored somewhere else. | Keep the VM stopped but restorable, or keep a snapshot, for at least one full monthly cycle after cutover. Define a rollback trigger and owner. | a Y, b Y, c Y, d Y |
| F3 | Medium | CONFIRMED | A | memo.md, Alternatives considered, items 1 and 3 | The alternatives are listed but never compared or rejected with reasons. Option 3 ($60 per month on the existing cluster) is the cheapest stated option and is the only one at or below the VM cost once F1 is corrected. Option 1's two days of work are not costed against the migration's three weeks. | The reader is steered to option 2 without seeing that, on the memo's own figures, option 3 dominates on cost. | Add a comparison table covering monthly cost, one-off effort, operational burden and rollback for every option. State why each one loses. | a Y, b Y, c N, d N (the $60 figure is unverified) |
| F4 | Medium | CONFIRMED | A | memo.md, Risks (one bullet) | The risk section covers only a vendor outage. It omits the cost exposure (the per-run pricing scales with volume, which grew about 8% from April to September), price changes, lock-in or exit cost, migration defects, and the 90-day history limit against any longer retention need. "Publishes 99.9%" is up to about 43 minutes of downtime per month and is not an SLA with remedies. | Volume growth or a price change raises the bill with no trigger to revisit. An outage near the batch window delays the reports and there is no fallback. | Add the cost sensitivity to volume and price, an exit plan, and a check that 99.9% fits the batch window. | a Y, b Y, c N, d N |

## Needs validation

- **S1 (Stepwise billing unit).** If Stepwise bills per step or per state transition rather than per workflow run, the cost is a multiple of F1's figure. *Settling fact:* Stepwise's current price page, showing the billing unit and any volume tiers.
- **S2 (Retry semantics).** "Retries failed steps on its own" may re-run steps that are not idempotent, causing duplicate writes or emails. *Settling fact:* whether each of the three batch scripts' steps is idempotent, and how the existing hand-written retry code handles partial failure.
- **S3 (Parallel-run side effects).** Running both systems in Week 2 may double-write to the production report targets. *Settling fact:* whether the Stepwise copy writes to an isolated target during the parallel run.
- **S4 (What a "run" is).** A nightly batch producing about 1,000 runs per night suggests a run is per item or per partition, not per night. The 3,000 may come from counting something else, such as nights × scripts. *Settling fact:* how `runs` in the CSV is defined and whether it maps to Stepwise's billable unit.
- **S5 (Avoidable VM cost).** Whether the full $400 goes away. Backups or disk may be shared or still needed. *Settling fact:* the VM invoice line items.

## Refuted

- **Candidate: "$220 × 12 = $2,640 is miscomputed."** Refuted: the arithmetic is internally correct. The error is the input (F1), not the multiplication.

## What holds up

- The memo's internal arithmetic, given its own inputs, is correct.
- Including a parallel run before cutover is sound practice.
- Listing a do-less option (stay on cron with a retry helper) and a cheaper option (container job) is the right shape. They just need an actual comparison.

## Unverified claims

| Claim | How to confirm |
|---|---|
| $400 per month VM cost | Billing export |
| $0.06 per workflow run | Stepwise pricing page, dated |
| 90-day run history | Stepwise documentation |
| 99.9% availability | Stepwise SLA document, including whether it is contractual |
| About $60 per month for the container option | Cluster cost model or node pricing × required capacity |
| The VM "needs a person on call for stuck jobs" | Incident and on-call log for the last six months |

## Questions for the author

1. Where did "about 3,000 runs per month" come from, given that the CSV shows about 31,700?
2. What does Stepwise bill on: workflow runs, steps or something else?
3. Why was the container option ($60 per month) rejected?

## Decision-maker summary

Do not approve. On the supplied usage data, Stepwise costs about $1,900 per month against $400 for the VM, so the move loses about $18,000 a year instead of saving $2,640. Send the memo back for a recomputed comparison of all three options, with a rollback plan that does not destroy the VM on cutover day.

## Owner summary

The memo used a monthly job count about ten times lower than our real records show. With the real numbers, the new service would cost far more than what we pay today, not less. The memo also plans to switch off the old server on the day of the switch, which leaves no way back if the morning reports break.

```json
{
  "schema_version": "2.2",
  "verdict": "REJECT",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "memo.md", "status": "seen", "matters": true},
    {"item": "evidence/run_counts.csv", "status": "seen", "matters": true},
    {"item": "Stepwise price list (billing unit, tiers)", "status": "not_seen", "matters": true},
    {"item": "VM invoice / cost breakdown", "status": "not_seen", "matters": true},
    {"item": "Container option cost basis", "status": "not_seen", "matters": true},
    {"item": "Batch scripts and existing retry code", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "evidence/run_counts.csv", "kind": "data"},
      {"unit": "memo.md", "kind": "file"},
      {"unit": "memo.md#Why", "kind": "section"},
      {"unit": "memo.md#Alternatives considered", "kind": "section"},
      {"unit": "memo.md#Plan", "kind": "section"},
      {"unit": "memo.md#Risks", "kind": "section"},
      {"unit": "Run volume of about 3,000 per month", "kind": "assumption"},
      {"unit": "$220/month saving", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "Stepwise pricing and SLA documents", "reason": "not supplied; no tools"},
      {"unit": "VM billing", "reason": "not supplied"},
      {"unit": "Cluster capacity cost for container option", "reason": "not supplied"},
      {"unit": "Batch scripts and retry code", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md, Why, bullet 2; evidence/run_counts.csv",
     "scenario": "The memo assumes 3,000 runs/month but the CSV shows 30,210-32,760 (mean 31,720); at $0.06/run Stepwise costs about $1,903/month versus the $400 VM, so the move adds about $18,040/year instead of saving $2,640.",
     "fix": "Recompute the cost from the CSV and redo the recommendation and alternatives comparison.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Sum the runs column (190,320), divide by 6 (31,720), multiply by 0.06: expected per memo $180, observed $1,903.20."},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md, Plan step 3",
     "scenario": "The VM is decommissioned on cutover day; if Stepwise fails or diverges on the first nights, there is no rollback and the next-morning reports are late or wrong.",
     "fix": "Keep the VM stopped but restorable, or snapshotted, for at least one monthly cycle; define a rollback trigger and owner.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Plan step 3 reads 'Decommission the VM the same day'; no rollback step exists in the plan."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md, Alternatives considered",
     "scenario": "Alternatives are listed without comparison or rejection reasons; the $60/month container option is cheapest on the memo's own figures once F1 is corrected, yet is silently passed over.",
     "fix": "Add a comparison table (monthly cost, one-off effort, ops burden, rollback) and state why each option loses.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md, Risks",
     "scenario": "Only vendor outage is listed; cost growth with volume (+8% Apr-Sep), price changes, lock-in, migration defects and the 90-day history limit are omitted, and '99.9% published' allows about 43 minutes of downtime per month with no stated remedy.",
     "fix": "Add cost sensitivity, an exit plan, and a check of availability against the batch window.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "C", "location": "memo.md, Why, bullet 2",
     "suspicion": "Stepwise may bill per step rather than per workflow run, multiplying the cost further.",
     "unresolved_fact": "Stepwise's current billing unit and volume tiers."},
    {"id": "S2", "status": "needs_validation", "track": "A", "location": "memo.md, Why, bullet 3",
     "suspicion": "Automatic step retries may duplicate non-idempotent side effects.",
     "unresolved_fact": "Whether each batch step is idempotent and how the existing retry code handles partial failure."},
    {"id": "S3", "status": "needs_validation", "track": "A", "location": "memo.md, Plan step 2",
     "suspicion": "The parallel run may double-write to production report targets.",
     "unresolved_fact": "Whether the Stepwise copy writes to an isolated target during Week 2."},
    {"id": "S4", "status": "needs_validation", "track": "C", "location": "evidence/run_counts.csv",
     "suspicion": "A 'run' in the CSV may not equal Stepwise's billable unit.",
     "unresolved_fact": "The definition of 'runs' in the CSV and how it maps to Stepwise billing."},
    {"id": "S5", "status": "needs_validation", "track": "C", "location": "memo.md, Why, bullet 1",
     "suspicion": "Not all of the $400 VM cost may be avoidable.",
     "unresolved_fact": "VM invoice line items and which ones disappear on decommission."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "$220 x 12 = $2,640 is miscomputed.",
     "evidence": "The arithmetic is correct given the memo's inputs; the error is the run-count input (F1)."}
  ]
}
```