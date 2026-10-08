# Redteam Review: Stepwise Migration Decision Memo

**Review conditions:** This session has no tools and no subagent, so I did the review myself. I did not write the memo, so the anchoring risk is lower than in a self-review. Every number below comes from the supplied CSV and the memo text. I could not check any external pricing or availability claim.

## Pass 1: Reconstruct

The memo recommends moving the nightly batch from a $400/month cron VM to Stepwise this quarter. Its case is that Stepwise would cost $180/month (3,000 runs × $0.06), saving $2,640/year, and would remove hand-written retry code. Five things must be true for this to hold:

1. Monthly run volume is about 3,000.
2. The $0.06/run price is the full cost.
3. The $400 VM cost goes away entirely.
4. Migration cost and risk are small.
5. Stepwise is reliable enough for a job that feeds next-morning reports.

There are also unstated assumptions:

- The batch scripts are safe to retry automatically.
- Running both systems in parallel will not produce duplicate outputs.
- No rollback is needed after cutover.

## Pass 2: Attack (Track A)

The memo fails on its first assumption, using its own evidence. The request says to base the cost on `evidence/run_counts.csv`. That file shows 30,210 to 32,760 runs/month, not ~3,000:

- Six-month total: 190,320. Average: 31,720/month.
- Average cost: 31,720 × $0.06 = **$1,903.20/month**.
- Latest month: 32,760 × $0.06 = **$1,965.60/month**.

So Stepwise costs about **$1,500/month more** than the VM, not $220 less. That is about **$18,000/year extra** instead of $2,640/year saved. Volume also grew about 8% over the six months (30,210 → 32,760), so the gap widens over time. The recommendation reverses.

**Counter-case:** Stay on cron and add the retry helper (two days of work), or use the $60/month container job. Both beat Stepwise on cost by a wide margin. The memo lists them as alternatives but never compares them. With corrected numbers, the counter-case wins easily.

**Pre-mortem: three likely reasons this fails within a year**

1. The first invoice is roughly 10× the forecast.
2. A failure in the first weeks after cutover leaves no fallback, because the VM is already gone and the morning reports are missed.
3. Automatic retries re-run non-idempotent steps and duplicate data.

## Pass 3: Self-check

**Downgrades:**
- I kept the retry/idempotency and parallel-run findings at Medium and labelled them UNVERIFIED/PROBABLE, because the scripts are not visible.

**Where a serious problem might still hide:**
- The definition of a "run." Thirty thousand runs a month for a "nightly" job is about 1,000 a night.
- If the CSV counts something other than billable Stepwise runs, both the memo's figure and my correction need re-basing. Examples: per-item or per-step counts, or every workflow in the org.
- The memo's 3,000 still has no source either way, and the request explicitly required the CSV.

---

## Report

**VERDICT: REJECT.** The memo's central cost claim is off by about 10× compared with the evidence file it was told to use. Corrected, Stepwise costs about $1,500/month more than the VM, so the recommendation reverses.

**CONFIDENCE IN VERDICT: High.** The arithmetic needs only the supplied CSV and the memo's own unit price. Two things limit confidence:
- Whether the CSV's "runs" match Stepwise's billing unit.
- The fact that I could not verify any external price or SLA (no tools).

### Findings, ordered by severity

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | memo.md, Why: "about **3,000 runs per month**, so the bill is **$180 per month**" vs evidence/run_counts.csv | The run volume is about 10× too low. The CSV shows 30,210 to 32,760/month (average 31,720). The request explicitly asked for the cost to be based on this file. | The org migrates expecting $180/month and is billed about $1,903 to $1,966/month. That is about $18k/year more than the VM, against a promised $2,640/year saving. | Recompute from the CSV: 31,720 × $0.06 ≈ $1,903/month, and the latest month ≈ $1,966/month. Project forward using the ~8% six-month growth. Restate the recommendation. |
| 2 | High | CONFIRMED | memo.md, Alternatives #1 and #3 | The alternatives are listed but never costed against each other. The $60/month container job and the "two days + $400" cron option are both far cheaper than Stepwise at real volume. | The decision-maker approves the most expensive option because the comparison was never laid out. | Add a table of monthly run cost, one-time migration effort, and ops burden for all three options plus "do nothing." |
| 3 | High | CONFIRMED | memo.md, Plan step 3: "**Decommission the VM the same day**" | There is no rollback window for a job that feeds next-morning reports. | Stepwise fails, or produces wrong output, on night 1 to 7 after cutover. The VM is gone, so the reports are late or wrong with no quick fallback. | Keep the VM, stopped or on standby, for 2 to 4 weeks after cutover. Define rollback criteria and a tested rollback procedure. |
| 4 | Medium | UNVERIFIED | memo.md, Why: "Stepwise retries failed steps on its own … removes our hand-written retry code" | This assumes the batch steps are idempotent. Automatic step retries on non-idempotent writes duplicate data. | A step partially writes, then times out. Stepwise retries it and the report double-counts rows. | Audit each of the three scripts for idempotency. Configure retry limits. Add a test that forces a mid-step failure. |
| 5 | Medium | PROBABLE | memo.md, Plan step 2: "run both systems in parallel" | The plan does not say how to keep the two runs from both writing to production targets. | Both systems write the same night's output, producing duplicate or conflicting report data. | Run Stepwise against a shadow target or dry-run mode, then diff the outputs. |
| 6 | Medium | CONFIRMED | memo.md, Risks section | The risk section has one item. It omits lock-in, run-history retention (90 days may be shorter than audit needs), secrets handling, and the nightly time window. Also, 99.9% availability allows about 43 minutes of downtime a month, which could fall in the batch window. | An outage during the batch window, or a retention or audit request older than 90 days, hits a risk nobody planned for. | Expand the risks. Check the SLA's terms, including whether it offers credits only. Confirm retention requirements. |
| 7 | Medium | CONFIRMED | memo.md, Why vs Alternatives #1 | Costs are compared asymmetrically. The retry helper is costed at "two days of work," while the three-week migration and parallel run have no labour cost at all. Patching and on-call savings are asserted but not quantified, and Stepwise still needs someone on call for failed runs. | The labour cost of migrating exceeds what it saves, and this is never surfaced. | Put engineering days and ongoing ops hours on each option. |
| 8 | Low | UNVERIFIED | memo.md, Why: "$400 per month", "$0.06 per workflow run", "99.9% availability" | None of these figures is sourced. The $0.06 may exclude per-step, compute, or egress charges. | The real Stepwise unit cost is higher, which makes Finding 1 worse. | Cite the VM invoice and the Stepwise pricing page and SLA, with the date retrieved. |

### What holds up

- The VM's operational burden (patching, someone on call for stuck jobs) is a legitimate cost to weigh.
- A parallel-run phase is the right idea, though Finding 5 explains how it needs to be set up.
- Listing alternatives, including the cluster option, is correct in structure. The options just need costing.
- The $0.06 × 3,000 = $180 and $400 − $180 = $220 arithmetic is internally correct. It is the input that is wrong.

### Unverified claims

| Claim | How to confirm |
|---|---|
| VM costs $400/month | Check the cloud invoice. |
| Stepwise costs $0.06/run with no other charges | Check the vendor pricing page or a quote. |
| Stepwise keeps 90-day history and retries automatically | Check the vendor docs. |
| Stepwise is 99.9% available | Read the SLA terms, exclusions, and remedies. |
| Retry helper takes two days | Get an engineer's estimate. |
| Container job costs about $60/month extra | Get a cluster capacity estimate. |
| CSV "runs" equal Stepwise billable runs | Map the batch structure to Stepwise's billing unit. |

### Questions for the author

1. Where did "about 3,000 runs per month" come from, given that run_counts.csv shows about 31,700?
2. Does one row of the CSV count the same unit Stepwise bills, or something finer (items or steps) or broader (all workflows)?
3. Why was the $60/month container option not chosen?

### Decision-maker summary

Do not approve this memo. Using the run counts it was told to use, Stepwise costs about $1,900/month against the VM's $400, which is roughly $18k/year more, not $2.6k saved. Have the comparison redone with all three options costed, likely favouring the container job or cron plus retries. If Stepwise is pursued anyway, keep the VM as a rollback path for several weeks after cutover.

```json
{
  "verdict": "REJECT",
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "location": "memo.md, Why: 'about 3,000 runs per month, so the bill is $180 per month' vs evidence/run_counts.csv", "scenario": "CSV shows 30,210-32,760 runs/month (avg 31,720); at $0.06 the bill is ~$1,903-$1,966/month, ~$1,500/month more than the $400 VM (~$18k/yr extra) instead of $2,640/yr saved; recommendation reverses.", "fix": "Recompute from the CSV (31,720 x $0.06 = $1,903.20/month), project ~8% growth, and restate the recommendation."},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "memo.md, Alternatives considered #1 and #3", "scenario": "Cheaper options (container job ~$60/month; cron + two-day retry helper) are listed but never costed against Stepwise, so the most expensive option is approved.", "fix": "Add a side-by-side table of run cost, migration effort and ops burden for all options including do-nothing."},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "memo.md, Plan step 3: 'Decommission the VM the same day'", "scenario": "Stepwise fails or misbehaves in the first nights after cutover; with the VM gone, next-morning reports are late or wrong with no fast rollback.", "fix": "Keep the VM on standby for 2-4 weeks after cutover with defined, tested rollback criteria."},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "location": "memo.md, Why: 'Stepwise retries failed steps on its own'", "scenario": "A non-idempotent step partially writes, times out, is auto-retried, and duplicates data in the reports.", "fix": "Audit the three scripts for idempotency, cap retries, and test a forced mid-step failure."},
    {"severity": "Medium", "evidence_level": "PROBABLE", "location": "memo.md, Plan step 2: 'run both systems in parallel'", "scenario": "Both systems write production outputs on the same night, producing duplicate or conflicting report data.", "fix": "Point Stepwise at a shadow target or dry-run mode and diff the outputs."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "memo.md, Risks section", "scenario": "Only vendor outage is listed; 99.9% availability allows ~43 min/month of downtime, which could fall in the nightly window; lock-in, 90-day retention vs audit needs, and secrets handling are unaddressed.", "fix": "Expand the risk section, check the SLA terms and remedies, and confirm retention requirements."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "memo.md, Why vs Alternatives #1", "scenario": "The retry helper is costed in engineering days while the three-week migration has no labour cost and the claimed patching/on-call savings are unquantified, so the comparison is skewed toward Stepwise.", "fix": "Put engineering days and ongoing ops hours on every option."},
    {"severity": "Low", "evidence_level": "UNVERIFIED", "location": "memo.md, Why: '$400 per month', '$0.06 per workflow run'; Risks: '99.9% availability'", "scenario": "Unsourced figures; the Stepwise price may exclude step, compute or egress charges, making the cost gap larger.", "fix": "Cite the VM invoice and the vendor pricing page and SLA with retrieval date."}
  ]
}
```