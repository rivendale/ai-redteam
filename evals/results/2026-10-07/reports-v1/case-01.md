# Redteam Review: Stepwise Migration Decision Memo

The memo was not written in this conversation, so this is an independent review. I had no tools: I checked the arithmetic by hand against the supplied CSV and could not verify any external facts.

## Pass 1: Reconstruct

The memo recommends moving the nightly batch from a $400/month cron VM to Stepwise this quarter. Its main argument is cost. It claims about 3,000 runs/month at $0.06/run, which gives $180/month and a saving of $2,640/year. Secondary benefits are built-in retries, 90-day run history, and less patching and on-call work.

For the memo to be right, these must hold:
1. The run count is about 3,000/month.
2. $0.06/run is the full Stepwise bill, with no per-step, storage or egress charges.
3. The VM really costs $400/month all-in.
4. Retrying steps is safe, meaning the steps are idempotent.
5. The cutover can be done without a fallback.
6. The rejected alternatives are actually worse.

Assumption 1 is false according to the memo's own evidence file.

---

**VERDICT: REJECT.** The required evidence file shows about 31,700 runs/month, not 3,000. At the memo's own price, Stepwise costs about $1,903/month, so the move would *raise* costs by about $18,000/year instead of saving $2,640.

**CONFIDENCE IN VERDICT: high.** The main finding is plain arithmetic on the supplied CSV. Confidence is limited by:
- the unverified pricing and VM figures;
- the unknown definition of a "run" in the CSV. Thirty thousand runs a month is odd for a single nightly job, which suggests per-item or per-step runs. That would not rescue the memo, because Stepwise bills per workflow run.

## FINDINGS

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | memo.md "Why", bullet 2: "about **3,000 runs per month**… **$180 per month**" vs evidence/run_counts.csv | The run count is about 10x too low. The CSV sums to 190,320 runs over 6 months, an average of 31,720/month (range 30,210 to 32,760). At $0.06/run that is $1,903/month on average, and $1,966 for 2026-09. The original request explicitly required the cost to be based on this file. | The org migrates expecting to save $220/month. The real bill is about $1,900/month, an extra ~$1,500/month (~$18k/year) over the VM. The $2,640/year "saving" becomes a large loss. | Recompute from the CSV: 31,720 × $0.06 ≈ $1,903/month vs $400. Explain where "3,000" came from. Confirm the CSV's "run" matches Stepwise's billable unit. |
| 2 | High | CONFIRMED (trend) / PROBABLE (impact) | evidence/run_counts.csv; memo has no growth analysis | Runs grew from 30,210 to 32,760 in six months (~8%). Per-run pricing scales with that growth. The VM's cost is roughly flat. | Volume keeps rising and the Stepwise bill grows with it, which widens the gap from Finding 1. | Project 12-month cost at the observed growth rate for each option. |
| 3 | High | CONFIRMED | memo.md "Alternatives": option 3, "about $60 per month" | The memo prices the container option below Stepwise even on its own wrong numbers ($60 vs $180), then drops it without explanation. Option 1 is also not costed as a real alternative. | Decision-makers pick the more expensive option because a cheaper, apparently viable option was listed but never evaluated. With corrected numbers, options 1 and 3 both clearly beat Stepwise. | Compare all three options on cost, labor, retries and observability, and state why any cheaper option is rejected. |
| 4 | High | CONFIRMED | memo.md "Plan", step 3: "**Decommission the VM the same day**" | The plan removes the rollback path at cutover, even though the batch feeds next-morning reports. | Stepwise fails on its first or second production night: a quota, timeout, secret or network issue the parallel run did not exercise. The VM is gone, so the morning reports are missing or stale with no fast fallback. | Keep the VM, stopped but restorable, for 2 to 4 weeks after cutover. Define rollback criteria and a tested rollback procedure. |
| 5 | Medium | PROBABLE | memo.md "Why", bullet 3: "retries failed steps on its own… removes our hand-written retry code" | Automatic step retries are only safe if the steps are idempotent. The memo does not say whether the three scripts are. | A step that appends rows or sends output fails partway and is retried. Reports then show duplicate or double-counted data. | Audit each script for idempotency before relying on platform retries, and add a test that re-runs a failed step. |
| 6 | Medium | PROBABLE | memo.md "Plan", step 2: "run both systems in parallel" | The plan does not say whether the parallel Stepwise run writes to production sinks. | Both systems write to the same report tables or outputs, causing duplicates or conflicts during week 2. | Run Stepwise in shadow mode with separate outputs, then compare. |
| 7 | Medium | CONFIRMED (omission) | memo.md cost section vs "Alternatives" option 1 | Labor is counted asymmetrically. Option 1's two days of work are counted, but the 3-week Stepwise migration's labor is not. | The comparison understates the cost of the recommended option. | Add the migration's engineering cost to the Stepwise option. |
| 8 | Medium | CONFIRMED (omission) | memo.md "Risks" lists only vendor outage | The risk section is thin. It omits lock-in and exit cost, per-run timeouts and limits, secrets handling, data egress, and cost overrun. 99.9% availability allows about 43 minutes of downtime a month, which can fall entirely in the nightly window. | An outage or limit during the nightly run delays the morning reports, and nobody planned for it. | Add those risks, each with a mitigation, plus a cost alert threshold. |
| 9 | Low | PROBABLE | memo.md "Why", bullet 1: "a person on call for stuck jobs" | The memo implies Stepwise removes the on-call need. Someone still has to respond when a managed run fails before morning reports. | Ownership of failed runs becomes unclear after migration. | State who is on call after cutover and what the alerting path is. |

## WHAT HOLDS UP

- Run history and managed retries are plausible operational benefits, as long as the steps are idempotent.
- The plan is phased, with a port, a parallel run and a cutover, which is a sound structure apart from the same-day decommission.
- The memo does list alternatives, including staying put, even though it evaluates them poorly.

## UNVERIFIED CLAIMS

| Claim | How to confirm |
|---|---|
| VM costs $400/month (instance, disk, backups) | Cloud billing export for the last 6 months |
| Stepwise bills $0.06 per workflow run, with no other charges | Current Stepwise pricing page or quote; check per-step, storage, log-retention and egress charges |
| Stepwise keeps run history for 90 days | Stepwise documentation |
| Stepwise publishes 99.9% availability | Stepwise SLA, including its credit terms and exclusions |
| Container option costs about $60/month | Cluster capacity and cost estimate from the platform team |
| "Run" in the CSV means the same unit Stepwise bills | Data source or definition of run_counts.csv |

## QUESTIONS FOR THE AUTHOR

1. Where did "about 3,000 runs per month" come from, given that the CSV shows 30,000 to 33,000?
2. What does one "run" in the CSV represent, and is it Stepwise's billable unit?
3. Why was the $60/month container option rejected?
4. Are the three batch scripts idempotent under step retry?

## DECISION-MAKER SUMMARY

Do not approve this move. On the memo's own price and the usage data it was told to use, Stepwise costs about $1,900/month against $400 for the VM, a loss of roughly $18k/year rather than a $2,640 saving. Ask for a corrected memo that properly evaluates the cron-plus-retry and container options, and that keeps a rollback path for any cutover.

```json
{
  "verdict": "REJECT",
  "findings": [
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "memo.md Why bullet 2 ('about 3,000 runs per month... $180 per month') vs evidence/run_counts.csv",
      "scenario": "CSV averages 31,720 runs/month (30,210-32,760); at $0.06/run Stepwise costs ~$1,903/month vs $400 VM, an increase of ~$18k/year instead of a $2,640/year saving",
      "fix": "Recompute cost from the CSV (31,720 x $0.06), explain the source of '3,000', and confirm the CSV run unit matches Stepwise's billable unit"
    },
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "location": "evidence/run_counts.csv trend; memo has no growth analysis",
      "scenario": "Runs grew ~8% in six months (30,210 to 32,760); per-run billing scales with growth while VM cost is flat, widening the loss",
      "fix": "Project 12-month cost for each option using the observed growth rate"
    },
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "location": "memo.md Alternatives option 3 ('about $60 per month')",
      "scenario": "A cheaper listed option ($60 vs $180 even on the memo's numbers) is dropped without reasoning, leading to selection of the costlier option",
      "fix": "Evaluate all three options side by side on cost, labor, retries and observability, with explicit rejection reasons"
    },
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "location": "memo.md Plan step 3 ('Decommission the VM the same day')",
      "scenario": "Stepwise fails on its first production nights; with the VM gone there is no fast rollback and next-morning reports are missed",
      "fix": "Keep the VM restorable for 2-4 weeks after cutover with defined rollback criteria and a tested rollback procedure"
    },
    {
      "severity": "Medium",
      "evidence_level": "PROBABLE",
      "location": "memo.md Why bullet 3 (automatic step retries replace hand-written retry code)",
      "scenario": "A non-idempotent step fails midway and is auto-retried, producing duplicate or double-counted report data",
      "fix": "Audit each script for idempotency and test re-running a failed step before relying on platform retries"
    },
    {
      "severity": "Medium",
      "evidence_level": "PROBABLE",
      "location": "memo.md Plan step 2 (run both systems in parallel)",
      "scenario": "Both systems write to production report sinks during the parallel week, causing duplicates or conflicts",
      "fix": "Run Stepwise in shadow mode with separate outputs and diff against the cron outputs"
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "memo.md cost section vs Alternatives option 1 (labor counted only for option 1)",
      "scenario": "The 3-week migration labor is omitted while option 1's 2 days are counted, understating the recommended option's cost",
      "fix": "Add migration engineering cost to the Stepwise option"
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "memo.md Risks (only vendor outage listed)",
      "scenario": "Lock-in, per-run limits/timeouts, secrets, egress and cost overrun are unaddressed; 99.9% allows ~43 min/month of downtime, which could hit the nightly window and delay reports",
      "fix": "Add these risks with mitigations and a cost alert threshold"
    },
    {
      "severity": "Low",
      "evidence_level": "PROBABLE",
      "location": "memo.md Why bullet 1 ('a person on call for stuck jobs')",
      "scenario": "The memo implies on-call is eliminated, but failed managed runs still need a responder before morning reports, so ownership becomes unclear",
      "fix": "Name the post-cutover on-call owner and the alerting path"
    }
  ]
}
```
