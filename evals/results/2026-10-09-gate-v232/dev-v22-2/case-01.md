**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent and no tools were available. I recomputed the numbers by hand. Nothing external (pricing, availability, invoices) could be opened.

VERDICT: **REWORK**. The cost case uses about 3,000 runs a month, but the supplied usage file shows about 31,700. At the memo's own price, Stepwise costs roughly $1,900 a month, not $180, so the recommendation flips from saving $2,640 a year to losing about $18,000 a year.

CONFIDENCE: **medium**. The central arithmetic error is certain, since it uses only the memo and the CSV. Confidence is limited by the same-context review, no tools, and missing inputs: Stepwise's actual pricing, the VM bill, and what one "run" in the CSV means.

INPUTS LEDGER:
- Seen: request.md, context.md, memo.md, evidence/run_counts.csv.
- Not seen: Stepwise pricing page (the $0.06 per run figure and the billing unit). This **matters**, because the cost conclusion depends on it.
- Not seen: VM invoice or cost breakdown (the $400 a month). This **matters**, as the baseline for any saving.
- Not seen: Stepwise SLA and retention terms (99.9% availability, 90-day history). This matters for the risk section.
- Not seen: the three batch scripts and the existing retry code. These matter only for the porting effort estimate.
- Not seen: cluster pricing behind the "$60/month" figure. This **matters**, because it may be the cheapest option.

COVERAGE:
- Checked: memo.md sections (Recommendation, Why, Alternatives, Plan, Risks), every row of run_counts.csv, every figure in the memo.
- Not checked: vendor claims, the VM cost source, the cluster cost source, and the scripts. None of these were supplied.

SEATS AND GATE: Only the local same-context reviewer ran. No cross-vendor seats were run, because the user did not ask for them and no tools were available. Sensitivity gate passed: the inputs contain no personal, financial-record, credential or client data.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | **Critical** | CONFIRMED | A/C | memo.md, Why, bullet 2: "Our batch is about **3,000 runs per month**, so the bill is **$180 per month**" | The memo's run count is about 10× below the evidence the request said to use. The CSV ranges from 30,210 to 32,760 runs a month. The six months sum to 190,320, an average of 31,720. | If the memo is approved, the Stepwise bill at the memo's own $0.06 per run is 31,720 × 0.06 = **$1,903.20 a month** (latest month: 32,760 × 0.06 = $1,965.60). That is about $1,503 a month more than the $400 VM, roughly **$18,000 a year in added cost** instead of a $2,640 saving. The recommendation reverses. | Recompute from the CSV: sum the `runs` column (190,320), divide by 6 (31,720), multiply by 0.06 (1,903.20), then compare with 400. Rewrite the cost section and recommendation using the CSV, and cite the CSV in the memo. | a✓ b✓ c✓ d✓ |
| F2 | Medium | CONFIRMED (text); failure PROBABLE | A | memo.md, Plan step 3: "**Decommission the VM the same day**" | The plan removes the rollback path at cutover. The batch feeds next-morning reports, and the plan sets no criteria for leaving the parallel run. | Stepwise fails or produces different output on the first nights after cutover. With the VM gone, there is no quick fallback, and next-morning reports are late or wrong until the old setup is rebuilt. | Keep the VM, stopped or snapshotted, for at least two weeks after cutover. Define pass criteria for the parallel run, for example N consecutive nights with identical output. | a✓ b✗ c✗ d✗ |
| F3 | Medium | CONFIRMED | A | memo.md, Alternatives 3: "about $60 per month of extra node capacity" | The cheapest listed option gets one line and no comparison. On the corrected numbers it beats both the VM and Stepwise on cost, but the memo never weighs it. | The decision-maker picks between the VM and Stepwise without seeing that a $60 a month option exists that may also remove the VM patching burden. | Add a comparison table covering cost, ops burden, retry and history, and migration effort for all three options plus doing nothing. Source the $60 figure. | a✓ b✓ c✗ d✓ |
| F4 | Low | CONFIRMED | A | memo.md, Risks | The risk section names only vendor outage. It omits migration effort, the cost of running both systems in parallel during Plan week 2, cost growth (runs rose from 30,210 to 32,760 over six months, about 8%), and lock-in. 99.9% availability allows about 43 minutes of downtime a month, which could land in the nightly window. | Costs and failure modes the memo does not list show up after approval. | Add these risks with an estimate for each, including parallel-run cost: about 7,400 runs × $0.06 ≈ $444 for one week. | a✓ b✓ c✗ d✗ |

## NEEDS VALIDATION
- **S1.** Is a CSV "run" the same unit Stepwise bills for? About 31,000 runs a month for one *nightly* batch is about 1,000 a night. That suggests the CSV counts per item or per step, or that Stepwise's unit differs. *Settle by:* Stepwise's pricing definition of a billable workflow run, mapped to how the CSV was produced. If the units differ, F1's corrected figure changes, but the memo's 3,000 still has no source.
- **S2.** Is the VM really $400 a month? *Settle by:* the cloud invoice lines for the instance, disk and backups.
- **S3.** Is $0.06 per run the current price, and are there tiers or volume discounts? *Settle by:* the Stepwise pricing page dated on or after the decision date.
- **S4.** Do the unpriced labour savings (patching, on-call for stuck jobs) offset the roughly $18k a year gap? *Settle by:* hours per month spent on VM patching and stuck-job pages, multiplied by the loaded hourly cost.

## REFUTED
- **"Alternative 1 is a strawman."** Refuted. The memo gives it a concrete cost (two days of work) and correctly notes it leaves the $400 unchanged. That is a fair statement of the option.

## WHAT HOLDS UP
- The structure is sound: recommendation, rationale, three alternatives, a staged plan with a parallel run, and a risk section.
- Running both systems in parallel and comparing outputs (Plan week 2) is the right validation step.
- The $220 a month and $2,640 a year figures are internally consistent with the memo's own inputs (400 − 180 = 220, and 220 × 12 = 2,640). The error is in the input, not the subtraction.

## UNVERIFIED CLAIMS
- $0.06 per workflow run: check the Stepwise pricing page.
- VM at $400 a month: check the invoice.
- Stepwise retries failed steps and keeps 90 days of run history: check the Stepwise documentation.
- Stepwise publishes 99.9% availability: check the SLA text and its remedies.
- Container option at about $60 a month: check cluster node pricing against the batch's resource profile.
- Retry helper takes two days of work: get an engineering estimate.

## QUESTIONS FOR THE AUTHOR
1. Where did "about 3,000 runs per month" come from, given that run_counts.csv shows about 31,700?
2. What does one row count in run_counts.csv represent, and does it match Stepwise's billing unit?
3. Why was the $60 a month container option not recommended?

## DECISION-MAKER SUMMARY
Do not approve. The memo's cost case uses one-tenth of the run volume in the supplied usage data, and with the real volume Stepwise costs about $1,900 a month against $400 for the VM. Ask for a corrected memo that compares all three options from the CSV. If you proceed anyway, expect about $18k a year of added cost and no fallback for next-morning reports, because the plan shuts off the old server on cutover day.

## OWNER SUMMARY
The proposal to move the nightly job to a new service is based on a usage figure ten times smaller than our real usage. With the real figure, the move would cost much more each year instead of saving money. The proposal should be redone with the correct numbers, should compare the cheaper container option properly, and should keep the old server available for a while after the switch.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "memo.md", "status": "seen", "matters": true},
    {"item": "evidence/run_counts.csv", "status": "seen", "matters": true},
    {"item": "Stepwise pricing page ($0.06/run, billing unit)", "status": "not_seen", "matters": true},
    {"item": "VM invoice ($400/month)", "status": "not_seen", "matters": true},
    {"item": "Stepwise SLA and retention terms", "status": "not_seen", "matters": true},
    {"item": "Cluster pricing for container option ($60/month)", "status": "not_seen", "matters": true},
    {"item": "Batch scripts and existing retry code", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "memo.md", "kind": "file"},
      {"unit": "memo.md#Why", "kind": "section"},
      {"unit": "memo.md#Alternatives considered", "kind": "section"},
      {"unit": "memo.md#Plan", "kind": "section"},
      {"unit": "memo.md#Risks", "kind": "section"},
      {"unit": "evidence/run_counts.csv", "kind": "data"},
      {"unit": "Batch runs about 3,000 per month", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "Stepwise pricing, SLA, retry and history features", "reason": "not supplied; no tools"},
      {"unit": "VM cost of $400/month", "reason": "not supplied"},
      {"unit": "Container option cost of $60/month", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md, Why, bullet 2 ('about 3,000 runs per month ... $180 per month')",
     "scenario": "run_counts.csv averages 31,720 runs/month (sum 190,320 over 6 months); at $0.06/run Stepwise costs $1,903.20/month versus the $400 VM, an added cost of about $18,000/year instead of the claimed $2,640/year saving, so the recommendation reverses.",
     "fix": "Recompute cost from run_counts.csv, cite it, and rewrite the recommendation.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Sum the CSV runs column (190,320), divide by 6 (31,720), multiply by 0.06 (1,903.20), compare with 400; the memo claims 180."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "A",
     "location": "memo.md, Plan step 3 ('Decommission the VM the same day')",
     "scenario": "Stepwise fails or diverges in the first nights after cutover; with the VM gone there is no fallback and next-morning reports are late or wrong.",
     "fix": "Retain the VM (stopped or snapshotted) for at least two weeks after cutover and define parallel-run pass criteria.",
     "answers": {"a": true, "b": false, "c": false, "d": false}},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md, Alternatives considered, item 3",
     "scenario": "The $60/month container option, cheapest on corrected numbers, is listed but never compared, so the decision-maker chooses between two costlier options.",
     "fix": "Add a comparison table (cost, ops burden, retries and history, migration effort) for all options including doing nothing.",
     "answers": {"a": true, "b": true, "c": false, "d": true}},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md, Risks",
     "scenario": "Unlisted risks (parallel-run cost of about $444/week, about 8% run growth over six months, lock-in, about 43 minutes/month allowed downtime possibly in the nightly window) appear after approval.",
     "fix": "Add these risks with estimates.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "C", "location": "evidence/run_counts.csv",
     "suspicion": "About 1,000 runs/night for one nightly batch suggests the CSV unit may differ from Stepwise's billable run.",
     "unresolved_fact": "Stepwise's definition of a billable workflow run versus what a CSV row counts."},
    {"id": "S2", "status": "needs_validation", "track": "C", "location": "memo.md, Why, bullet 1",
     "suspicion": "The VM cost of $400/month is unsourced.",
     "unresolved_fact": "Invoice lines for the instance, disk and backups."},
    {"id": "S3", "status": "needs_validation", "track": "C", "location": "memo.md, Why, bullet 2",
     "suspicion": "The $0.06/run price may be stale or tiered.",
     "unresolved_fact": "Current Stepwise pricing page."},
    {"id": "S4", "status": "needs_validation", "track": "A", "location": "memo.md, Why, bullet 1",
     "suspicion": "Unpriced labour savings (patching, on-call) might offset part of the cost gap.",
     "unresolved_fact": "Monthly hours spent on VM upkeep and stuck jobs, times loaded hourly cost."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Alternative 1 (stay on cron) is a strawman.",
     "evidence": "The memo gives it a concrete cost (two days of work) and correctly states it leaves the $400 unchanged."}
  ]
}
```