VERDICT: **REJECT.** Priced on the request's own data, Stepwise costs about $1,900/month, so the memo's $2,640/year saving becomes a loss of about $18,000/year.

CONFIDENCE: **medium-high** on the cost finding, which is arithmetic on the supplied CSV. **Low** on vendor and VM figures, which I could not check without tools. This is a single-reviewer, no-tools review; no subagent or second seat was available. The memo was not written in this conversation, so anchoring risk is low.

INPUTS LEDGER:
- **Seen:** request.md, context.md, memo.md, evidence/run_counts.csv.
- **Not seen:** the following gaps matter.
  - Stepwise pricing page, including whether it bills per workflow run or per step.
  - The VM invoice behind the $400.
  - Stepwise's SLA and retry and retention docs.
  - Any definition of what the CSV counts: batch runs only, or all workflows and steps.
  - Report timing (the time downstream reports need the batch output).
  - The cluster capacity behind the $60 container option.

SEATS AND GATE:
- **Seats:** a single local reviewer ran. No cross-vendor seats were run because none were requested and the review had no tools.
- **Sensitivity gate:** passed. The material contains no personal, financial-record or confidential customer data, only internal cost figures.

FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | A/C | memo.md "Why", bullet 2 ("about 3,000 runs per month… $180") vs evidence/run_counts.csv | The memo uses 3,000 runs/month. The CSV it was told to use shows 30,210 to 32,760 runs/month (six-month total 190,320, average 31,720). At $0.06 that is $1,903/month on average and $1,966 for 2026-09, against the VM's $400. That is about $1,500/month ($18,000/year) **more**, not $220/month less. Break-even is 6,667 runs/month, and actual usage is about 4.8× that. | The team approves on the memo, cuts over, decommissions the VM, and the first Stepwise invoice is about 5× the VM cost. | Recompute from the CSV and state which figure feeds the price. If the author believes the CSV overcounts billable runs (for example it counts steps or other workflows), show that mapping against Stepwise's billing unit. | Confirmed. The strongest defense is that the CSV may not measure billable batch runs. The memo never cites or reconciles the CSV, though, and the request required it to. The 3,000 figure looks like a dropped digit. |
| 2 | High | CONFIRMED | A | memo.md "Why" bullet 2 vs request.md | The request was drift-checked against the memo: it says "Base the cost comparison on our real usage, which is in evidence/run_counts.csv". The memo does not reference the file at all, which is drift from the request. | Decision-makers assume the comparison used real data, but it did not. | Cite the CSV, show the calculation, and use the latest month and the trend, not a round number. | Confirmed |
| 3 | High | CONFIRMED | A/B | memo.md Plan step 3 ("Decommission the VM the same day") | There is no rollback window for a job that feeds next-morning reports. One week of parallel running does not cover month-end or rare paths. | A defect or Stepwise incident in the first nights after cutover leaves reports missing, and there is no VM to fall back to. | Keep the VM stopped but restorable (snapshot) for 2 to 4 weeks after cutover, and define rollback criteria. | Confirmed. Saving one day of VM cost does not justify losing the fallback. |
| 4 | High | PROBABLE | A | memo.md "Alternatives considered" item 3 | The container option ($60/month) beats both other options on the memo's own numbers: it saves $340/month ($4,080/year), more than the claimed Stepwise saving even at 3,000 runs. It is listed and then never evaluated. | The organization picks a costlier option because the cheapest credible one was never compared. | Compare all three options on cost, ops burden, retries and history. With corrected Stepwise pricing, the container option is the likely recommendation. | Confirmed as a gap. It is PROBABLE as a recommendation because the $60 figure is unverified. |
| 5 | Medium | CONFIRMED | A | run_counts.csv trend; memo "Why" | Runs grew 8.4% over six months (30,210 to 32,760). Stepwise cost is linear in runs, but VM cost is flat. The memo models neither. | Cost gap widens each year. | Add a 12-month projection at the observed growth rate. | n/a |
| 6 | Medium | PROBABLE | A/C | run_counts.csv vs "nightly batch" | About 1,000 runs per day is unusual for a "nightly batch". The CSV may count something other than what the memo describes (per-item runs, several workflows, or steps). | Even after the price is corrected, the unit may still be wrong, in either direction. | The author should confirm what a "run" is in the CSV and in Stepwise's billing. | n/a |
| 7 | Medium | UNVERIFIED | C | memo.md "Why" bullets 1 and 3; "Risks" | The $400 VM cost, the $0.06/run price, automatic retries, 90-day history and 99.9% availability are all asserted without sources. | A wrong price or billing unit changes the outcome again. 99.9% allows about 43 minutes of downtime per month, which could fall on the nightly window. | Attach the VM invoice and the Stepwise pricing and SLA pages, dated, and quote them. | n/a |
| 8 | Medium | PROBABLE | A | memo.md "Risks" | Risks lists only vendor outage. It omits migration effort, which is about 3 weeks of engineering and is not netted against savings. It also omits lock-in and exit cost, whether 90-day history meets any retention need, and the fact that Stepwise still needs someone watching failures. "Removes on-call" is implied but not shown. | Hidden costs erode or erase savings, and on-call burden persists. | Add a costed risk and exit section. | n/a |

WHAT HOLDS UP:
- **Plan structure.** Porting, then parallel running with output comparison, then cutover is sound apart from the same-day decommission.
- **Alternatives list.** It names the right alternatives, including doing less (the retry helper only).
- **Arithmetic.** It is internally consistent ($0.06 × 3,000 = $180, and $220 × 12 = $2,640). The input is what is wrong.

UNVERIFIED CLAIMS:
- **VM $400/month:** check the cloud invoice.
- **Stepwise $0.06/run, billing unit, retries, 90-day history, 99.9% SLA:** check the vendor's pricing and SLA pages as of today.
- **Container $60/month:** check the cluster node pricing and current headroom.
- **CSV semantics:** check the source query or dashboard that produced it.

QUESTIONS FOR THE AUTHOR:
1. Where did 3,000 runs/month come from, and why not the CSV?
2. What does one row-count "run" in the CSV correspond to in Stepwise's billing unit?
3. Why was the $60/month container option not recommended?

DECISION-MAKER SUMMARY:
- Do not approve. The memo's usage figure is about 10× lower than the usage data it was told to use. Corrected, Stepwise costs about $1,900/month versus $400 for the VM.
- Ask for a revised comparison that includes the $60/month container option, which looks cheapest.
- If you proceed anyway, expect about $18,000/year in extra cost, plus no fallback if the cutover breaks next-morning reports.

OWNER SUMMARY: The memo says moving the nightly job to the new service saves money. Our own usage records show the job runs about ten times more often than the memo assumed, which would make the new service several times more expensive than today. The memo should be redone with the real numbers, with a closer look at running the job on our existing cluster, and the old server should be kept as a fallback for a few weeks after any switch.

```json
{
  "verdict": "REJECT",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "evidence/run_counts.csv", "status": "seen", "matters": true},
    {"item": "memo.md", "status": "seen", "matters": true},
    {"item": "Stepwise pricing/SLA documentation", "status": "not_seen", "matters": true},
    {"item": "VM invoice", "status": "not_seen", "matters": true},
    {"item": "definition of 'run' in run_counts.csv", "status": "not_seen", "matters": true},
    {"item": "cluster capacity/pricing for container option", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "internal cost figures only; no personal or confidential customer data"},
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "A", "location": "memo.md Why bullet 2 vs evidence/run_counts.csv",
     "scenario": "Memo prices 3,000 runs/month; CSV shows 30,210-32,760 (avg 31,720). At $0.06 that is ~$1,903/month vs $400 VM: ~$18,000/yr more, not $2,640/yr saved. Break-even is 6,667 runs/month.",
     "fix": "Recompute from the CSV and reconcile CSV run count with Stepwise's billing unit.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "A", "location": "memo.md Why bullet 2 vs request.md",
     "scenario": "Request required basing cost on run_counts.csv; memo never cites it, so readers wrongly assume real data was used.",
     "fix": "Cite the CSV and show the calculation using latest month and trend.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "A", "location": "memo.md Plan step 3",
     "scenario": "VM decommissioned on cutover day; a post-cutover defect or Stepwise outage breaks next-morning reports with no fallback.",
     "fix": "Keep a restorable VM snapshot for 2-4 weeks and define rollback criteria.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "PROBABLE", "track": "A", "location": "memo.md Alternatives item 3",
     "scenario": "Container option at $60/month saves $340/month, more than the claimed Stepwise saving, but is never evaluated; a costlier option gets chosen.",
     "fix": "Compare all three options on cost, ops burden, retries and history.", "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "A", "location": "evidence/run_counts.csv trend; memo Why",
     "scenario": "Runs grew 8.4% in six months; per-run pricing makes the gap widen yearly.",
     "fix": "Add a 12-month projection at observed growth."},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "C", "location": "run_counts.csv vs 'nightly batch'",
     "scenario": "~1,000 runs/day is unusual for a nightly batch; the unit counted may differ from Stepwise's billing unit in either direction.",
     "fix": "Confirm what a CSV run is and how Stepwise bills it."},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "track": "C", "location": "memo.md Why bullets 1 and 3; Risks",
     "scenario": "$400 VM cost, $0.06/run, retries, 90-day history and 99.9% SLA are unsourced; a wrong price or unit changes the outcome; 99.9% allows ~43 min/month downtime possibly in the nightly window.",
     "fix": "Attach dated invoice and vendor pricing/SLA quotes."},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "A", "location": "memo.md Risks",
     "scenario": "Migration effort, lock-in/exit cost, retention needs and remaining on-call burden are omitted, eroding claimed savings.",
     "fix": "Add a costed risk and exit section."}
  ]
}
```