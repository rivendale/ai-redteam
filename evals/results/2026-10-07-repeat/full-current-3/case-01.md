# Redteam review: Stepwise migration decision memo

**Review conditions:** Same-context review with no subagent and no tools, so there is some anchoring risk. Re-run in a fresh session for anything high-stakes. Every figure below was recomputed by hand from the supplied CSV.

**VERDICT: REWORK.** The memo's cost case uses 3,000 runs per month, but the evidence file it was asked to use shows about 31,700. At $0.06 per run, Stepwise costs more than the VM, so the recommendation reverses.

**CONFIDENCE: medium.** The arithmetic is certain. Confidence is limited by:
- not knowing what a "run" means in the CSV (this batch only, or all workflows);
- unverified pricing for both Stepwise and the VM;
- the review being same-context with no tools.

**INPUTS LEDGER:**
- **Seen:** request.md, context.md, memo.md and evidence/run_counts.csv (six rows, 2026-04 to 2026-09).
- **Not seen: Stepwise pricing page or terms.** This matters: the $0.06 per-run price and its billing unit (run or step) carry the whole conclusion.
- **Not seen: VM invoice or cost breakdown.** This matters: the $400 per month is asserted, not evidenced.
- **Not seen: cluster capacity and cost data behind the $60 per month.** This matters: it would show whether Alternative 3 dominates.
- **Not seen: definition of a "run" in the CSV.** This matters a great deal (see Question 1).
- **Not seen: the three batch scripts and the existing retry code.** This matters moderately, for the retry and idempotency claims.

**SEATS AND GATE:**
- Single local reviewer (this session).
- No subagent or cross-vendor seats were available.
- Sensitivity gate passed: there is no personal, credential or client data, only aggregate run counts and list prices.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | A, C | memo.md "Why" bullet 2: "Our batch is about **3,000 runs per month**, so the bill is **$180 per month**" | The run count does not come from evidence/run_counts.csv, even though the request names that file. The CSV sums to 190,320 runs over six months, an average of 31,720 per month and 32,760 in the latest month. At $0.06 that is about $1,903 per month on average and $1,966 in September. That is $1,503 per month **more** than the VM, about $18,000 per year in extra cost, not $2,640 per year saved. The figure is 10x too low. | Leadership approves the move expecting a $220 per month saving. The first Stepwise invoice is about $1,900, roughly 4.75 times the current cost. The VM is already gone (see #3), so reverting costs more time and money. | Recompute from the CSV: mean 31,720 runs × $0.06 = $1,903.20 per month. Restate the recommendation on that basis. If only part of the CSV runs belong to this batch, say which column or filter isolates them and cite it. | Confirmed. The strongest defense is that the CSV counts all workflows and 3,000 is this batch's share. The memo never says so or cites a source for 3,000. The request makes the CSV the basis for cost. The context calls the file "the monthly workflow run counts" for the decision. |
| 2 | High | CONFIRMED (logic) / UNVERIFIED (inputs) | A | memo.md "Alternatives considered" item 3: "about $60 per month of extra node capacity" | The cheapest option the memo lists ($60 per month, against $400 for the VM and about $1,900 for Stepwise once corrected) is named and then dropped without a reason. The memo also never weighs "do nothing" (Alternative 1 costs two days) against the migration effort, which is about 3 weeks of engineering under its own plan. | The decision-maker picks the most expensive option because the alternatives were listed but never compared. | Add a comparison table covering monthly cost, one-time effort, operational burden, rollback and failure modes. Either recommend the container job or state concretely why it is unsuitable. | Confirmed. Even with the memo's own (wrong) $180 figure, $60 is cheaper and goes unaddressed. |
| 3 | High | PROBABLE | A | memo.md "Plan" step 3: "**Decommission the VM the same day**" | There is no rollback window. The batch feeds next-morning reports, and decommissioning also removes the VM's backups and the known-good runtime. Problems that only show at month-end, under load or in rare data paths would not appear in a one-week parallel run. | Night 3 after cutover, a Stepwise definition mishandles an edge case or the vendor has an incident. There is nothing to fall back to, and the morning reports are missing or wrong. | Keep the VM stopped but restorable (snapshot plus disabled cron) for at least one full month-end cycle. Define explicit go/no-go criteria for cutover and a rollback runbook. | Confirmed. The parallel week reduces the risk but does not cover what happens after cutover. The quoted line is exact. |
| 4 | Medium | UNVERIFIED | C | memo.md "Why": "Stepwise bills **$0.06 per workflow run**"; "The VM costs **$400 per month**" | Neither price is sourced or dated. If Stepwise bills per step or per state transition, and the batch has three scripts, the cost could be about 3x higher again. | The real invoice exceeds even the corrected estimate. | Cite the Stepwise pricing page with its retrieval date and billing unit, and the VM invoice line items. | n/a |
| 5 | Medium | PROBABLE | A, B | memo.md "Risks" (one line) | The risk section lists only vendor outage. It omits network and credential access from a managed service to the batch's data sources, data egress, lock-in, migration effort, and the on-call need that remains (Stepwise failures still page someone). At 99.9% availability, roughly 43 minutes of downtime per month are allowed, which can coincide with the nightly window. | Cutover stalls on firewall or IAM work not in the plan, or an outage during the batch window delays reports with no SLA remedy. | Add each risk with owner, likelihood and mitigation. Check the Stepwise SLA credits against the cost of a missed morning report. | n/a |
| 6 | Medium | PROBABLE | B | memo.md "Plan" step 2: "run both systems in parallel and compare outputs" | It is not specified whether the parallel Stepwise run writes to production targets. Two systems writing the same outputs can duplicate or conflict. | Week-2 reports contain doubled or overwritten rows. | Point the Stepwise run at a shadow output and diff it. State this in the plan. | n/a |
| 7 | Medium | UNVERIFIED | B | memo.md "Why" bullet 3: "retries failed steps on its own … removes our hand-written retry code" | Automatic retries are only safe if the steps are idempotent. Retry policy, limits and backoff are unverified. | A partially completed step is retried and writes duplicate data. | Confirm the retry semantics in the Stepwise docs. Check each of the three scripts for idempotency before deleting the retry code. | n/a |
| 8 | Low | PROBABLE | A | memo.md "Why" bullet 1 vs the CSV | The CSV shows 8.4% growth from April to September (30,210 to 32,760). Per-run pricing scales with that growth; a flat VM does not. The memo treats volume as static. | The cost gap widens over time. | Project 12 months of cost using the observed growth trend. | n/a |

## WHAT HOLDS UP
- The memo's structure is sound: recommendation, rationale, alternatives, phased plan with a parallel run, and risks.
- The internal arithmetic is consistent with its own inputs: 3,000 × $0.06 = $180, $400 − $180 = $220, and $220 × 12 = $2,640.
- Listing three alternatives, including "stay and improve", is the right shape for the analysis.

## UNVERIFIED CLAIMS
- **$0.06 per run.** Check the Stepwise pricing page and confirm the billing unit.
- **$400 per month VM.** Check the cloud invoice.
- **$60 per month for container capacity.** Check the cluster cost model.
- **99.9% availability and 90-day history.** Check the Stepwise SLA and documentation.
- **Retries replace the hand-written code.** Check the documentation and audit the scripts for idempotency.

## QUESTIONS FOR THE AUTHOR
1. Where did 3,000 runs per month come from? Does run_counts.csv count only this batch, and what counts as a "run"? A nightly job of three scripts would be about 90 runs per month, which matches neither number.
2. Does Stepwise bill per workflow run or per step?
3. Why was the $60 per month container job rejected?

## DECISION-MAKER SUMMARY
Do not approve this move. On the usage data the memo was asked to use, Stepwise costs about $1,900 per month against $400 for the current VM, roughly $18,000 per year more instead of $2,640 saved. Ask for a revised comparison that includes the $60 per month container option and a rollback period before the VM is retired.

## OWNER SUMMARY
The memo says moving the nightly job to the new service saves money, but it used a usage figure about ten times lower than our actual records. With the real figures, the move would cost several times more than what we pay today. The memo should be redone with the correct numbers, a fair look at the cheaper container option, and a safety period before the old server is switched off.

```json
{
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "evidence/run_counts.csv", "status": "seen", "matters": true},
    {"item": "Stepwise pricing page / billing unit", "status": "not_seen", "matters": true},
    {"item": "VM invoice", "status": "not_seen", "matters": true},
    {"item": "cluster cost basis for $60/month", "status": "not_seen", "matters": true},
    {"item": "definition of 'run' in run_counts.csv", "status": "not_seen", "matters": true},
    {"item": "batch scripts and retry code", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "aggregate run counts and list prices only"},
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "A", "location": "memo.md Why bullet 2 ('about 3,000 runs per month ... $180 per month')",
      "scenario": "CSV averages 31,720 runs/month (190,320 over six months); at $0.06 that is about $1,903/month, $1,503/month more than the $400 VM (about $18,000/yr extra), so the recommendation reverses and the VM is already decommissioned when the invoice arrives.",
      "fix": "Recompute cost from evidence/run_counts.csv (31,720 x $0.06 = $1,903.20/month) and restate the recommendation; if only part of the CSV is this batch, document the filter and cite it.",
      "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "A", "location": "memo.md Alternatives item 3 ('about $60 per month')",
      "scenario": "Cheapest listed option ($60/month) is dropped without reasoning, so the decision-maker picks the most expensive option.",
      "fix": "Add a side-by-side comparison (monthly cost, one-time effort, ops burden, rollback) and justify or recommend the container job.",
      "status": "confirmed"},
    {"severity": "High", "evidence_level": "PROBABLE", "track": "A", "location": "memo.md Plan step 3 ('Decommission the VM the same day')",
      "scenario": "A post-cutover defect or vendor incident (e.g. month-end edge case) breaks next-morning reports with no fallback, because the VM and its backups are gone.",
      "fix": "Keep the VM stopped and restorable (snapshot, cron disabled) through at least one month-end; write go/no-go criteria and a rollback runbook.",
      "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "track": "C", "location": "memo.md Why ('$0.06 per workflow run'; '$400 per month')",
      "scenario": "If billing is per step rather than per run, cost rises up to about 3x further.",
      "fix": "Cite the dated Stepwise pricing page with its billing unit, and the VM invoice."},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "A", "location": "memo.md Risks",
      "scenario": "Unlisted risks (network/IAM access, egress, lock-in, migration effort, ongoing on-call, up to about 43 min/month downtime allowed by 99.9%) stall cutover or delay reports.",
      "fix": "Expand the risk register with owners and mitigations; compare SLA credits to the cost of a missed report."},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "B", "location": "memo.md Plan step 2 ('run both systems in parallel')",
      "scenario": "Both systems write to production outputs, producing duplicated or overwritten report data.",
      "fix": "Write Stepwise output to a shadow target and diff it against production."},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "track": "B", "location": "memo.md Why bullet 3 ('retries failed steps on its own')",
      "scenario": "Automatic retry of a non-idempotent, partially completed step writes duplicate data.",
      "fix": "Verify Stepwise retry semantics and audit the three scripts for idempotency before removing the retry code."},
    {"severity": "Low", "evidence_level": "PROBABLE", "track": "A", "location": "memo.md Why vs evidence/run_counts.csv",
      "scenario": "Runs grew 8.4% from April to September; per-run pricing scales with volume while the VM cost is flat, so the gap widens.",
      "fix": "Project 12-month cost using the observed growth trend."}
  ]
}
```