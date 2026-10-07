# Redteam review: decision memo on moving the nightly batch to Stepwise

**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No tools or subagents were available in this session. Every figure below was recomputed by hand from the supplied CSV.

**VERDICT: REJECT.** The memo's central cost claim uses 3,000 runs a month, but its own evidence shows about 31,700, so Stepwise costs about 4.8× the VM and the recommendation reverses.

**CONFIDENCE: high** on the cost reversal, which comes from arithmetic on supplied data. **Medium** on the rest, which is limited by:
- no tools,
- no access to the Stepwise pricing page or the VM bill,
- same-context review.

**INPUTS LEDGER:**

| Item | Status | Matters? |
|---|---|---|
| request.md | Seen | — |
| context.md | Seen | — |
| memo.md | Seen | — |
| evidence/run_counts.csv | Seen (6 rows, 2026-04 to 2026-09) | Yes, it settles the main finding |
| Stepwise pricing page or contract (the $0.06/run figure, what counts as a "run") | Not seen | Yes, the unit of billing could change the totals |
| VM invoice (the $400/month figure) | Not seen | Medium, it sets the baseline |
| The three batch scripts and the current retry code | Not seen | Medium, they bear on porting effort and idempotency |
| Stepwise SLA document (99.9%) | Not seen | Low to medium |

**SEATS AND GATE:**
- Only the local reviewer ran. There were no subagents and no cross-vendor seats; none were requested and the depth is standard.
- The sensitivity gate passed: the work contains no personal, financial-record, credential or client data. It holds only internal cost figures, which are not sensitive.
- No text in the work addresses the reviewer or tries to give it instructions.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | A/C | memo.md "Why", bullet 2 ("about 3,000 runs per month… $180 per month… saving of $220") vs evidence/run_counts.csv | The run count is wrong by 10×. The CSV ranges from 30,210 to 32,760 runs a month: the six months total 190,320, an average of 31,720. At $0.06 a run that is $1,812.60 to $1,965.60 a month, averaging **$1,903.20**, against the VM's $400. The memo claims a $2,640 a year saving; the real effect is about **$1,503 a month (≈ $18,038 a year) of extra cost**. | The team migrates on the memo's numbers, and the first Stepwise invoice comes in at about $1,900 instead of $180. The decision was the opposite of correct. | Recompute from the CSV and restate the comparison. On these inputs, stay off Stepwise unless the pricing unit differs (see Q1). | Confirmed. Strongest defense: "run" in the CSV might not equal a billable Stepwise run. The memo gives no basis for that, though, and the request says to base the cost on this file. The finding holds. |
| 2 | High | CONFIRMED | A | memo.md "Why" vs request.md | The memo drifts from the request. The request says to "base the cost comparison on our real usage, which is in evidence/run_counts.csv"; the memo cites no figure from the file, and its 3,000 matches no row. | A reader trusts that the instruction was followed, because the memo looks finished. | Cite the CSV explicitly: monthly figures, the average and the latest month. | Confirmed. Nothing in the memo ties to the file. |
| 3 | High | CONFIRMED | A | memo.md "Alternatives considered", item 3 | The scheduled container job at about $60 a month is listed but never evaluated. On the memo's own figures it beats both other options on cost, and it costs $1,843 a month less than Stepwise at real usage. The comparison was not fair. | The cheapest viable option is skipped without any reasoning. | Compare all three options in a table covering cost, migration effort, retries and operating burden. | Confirmed. No reason for rejecting it appears anywhere. |
| 4 | High | CONFIRMED | A/B | memo.md "Plan", step 3 ("Decommission the VM the same day") | The plan has no rollback. The batch feeds next-morning reports, yet the VM is destroyed on cutover day after a one-week parallel run. | A Stepwise definition bug or an outage on night 2 leaves no fallback, and the morning reports are missing until someone rebuilds the VM. | Keep the VM, stopped or snapshotted, for 2 to 4 weeks after cutover. Define rollback criteria and test the rollback. | Confirmed. The plan text is explicit, and saving one month of VM cost does not justify the risk. |
| 5 | Medium | PROBABLE | A | memo.md "Risks" (a single bullet) | The risks are thin. The plan says 99.9% availability (≈ 43 min/month of allowed downtime) with no mitigation and no check on whether downtime clusters in the batch window. It ignores network and data access from a managed service to internal sources, lock-in, and what happens to reports when a run fails. | Stepwise is degraded during the nightly window, and the reports fail with no alerting or retry plan. | Add a failure-to-report path: alerting, manual re-run and SLA credits. Confirm Stepwise can reach the data sources. | — |
| 6 | Medium | PROBABLE | B | memo.md "Why", bullet 3 ("retries failed steps on its own… removes our hand-written retry code") | Automatic retries are only safe if the steps are idempotent. The memo does not say whether the three scripts are. | A retried step that partially wrote data writes it again, which duplicates or corrupts the inputs to the reports. | Review the scripts for idempotency before relying on platform retries. | — |
| 7 | Medium | CONFIRMED | A | evidence/run_counts.csv trend | Usage is growing: 30,210 to 32,760 is +8.4% in five months. The memo's cost is static. Per-run pricing scales with that growth; the VM's cost is flat. | The gap widens over time, which strengthens finding 1. | Project the cost forward 12 months at the observed growth rate. | — |
| 8 | Low | UNVERIFIED | C | memo.md "$400 per month", "$0.06 per workflow run", "keeps run history for 90 days", "99.9%" | Each figure is asserted with no source. Pricing and SLA claims go stale. | A pricing tier or minimum changes the numbers. | Attach the VM invoice and the Stepwise pricing and SLA pages, dated. | — |

## WHAT HOLDS UP
- The memo's own multiplication is internally consistent: 3,000 × $0.06 = $180, $400 − $180 = $220, and $220 × 12 = $2,640. The error is the input, not the arithmetic.
- The 1-week parallel run comparing outputs (Plan step 2) is sound practice; it is just too short to carry a same-day decommission.
- The memo does list alternatives, including doing less (alternative 1), even though it does not evaluate them.

## UNVERIFIED CLAIMS
- **$0.06 per run, and the definition of a run:** check against the Stepwise pricing page or contract.
- **VM at $400 a month:** check against the cloud invoice.
- **90-day run history and automatic step retries:** check against the Stepwise documentation.
- **99.9% availability:** check against the published SLA, including the credit terms.

## QUESTIONS FOR THE AUTHOR
1. Where did 3,000 come from? Does a CSV "run" equal one Stepwise billable run, or would a Stepwise run cover many CSV rows? This is the only answer that could rescue the recommendation.
2. Why was the $60-a-month container option not chosen?
3. Are the three batch scripts idempotent under automatic retry?

## DECISION-MAKER SUMMARY
Do not approve this memo. The real usage in the supplied file puts Stepwise at about $1,900 a month against $400 for the VM, a loss of about $18,000 a year rather than a saving of $2,640. If you proceed anyway, you will pay roughly 4.8× more, and with the VM decommissioned on cutover day there will be no fallback if the morning reports fail. Ask for a revised memo that uses the CSV figures and seriously evaluates the $60-a-month container option.

```json
{
  "verdict": "REJECT",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "evidence/run_counts.csv", "status": "seen", "matters": true},
    {"item": "memo.md", "status": "seen", "matters": true},
    {"item": "Stepwise pricing/contract (run definition)", "status": "not_seen", "matters": true},
    {"item": "VM invoice ($400/month)", "status": "not_seen", "matters": true},
    {"item": "batch scripts and retry code", "status": "not_seen", "matters": true},
    {"item": "Stepwise SLA", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "local-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "internal cost figures only; no personal, credential or client data"},
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "A", "location": "memo.md Why bullet 2 vs evidence/run_counts.csv",
      "scenario": "Memo uses 3,000 runs/month; CSV shows 30,210-32,760 (avg 31,720). At $0.06/run Stepwise costs ~$1,903/month vs $400 VM: ~$18,038/year extra, not $2,640 saved.",
      "fix": "Recompute from CSV; recommendation reverses unless the billable-run definition differs.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "A", "location": "memo.md Why vs request.md",
      "scenario": "Request required basing cost on run_counts.csv; memo cites no figure from it.",
      "fix": "Cite CSV monthly figures, average and latest month explicitly.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "A", "location": "memo.md Alternatives item 3",
      "scenario": "Container job at ~$60/month is cheapest option but is listed and never evaluated.",
      "fix": "Compare all three options on cost, effort, retries and ops burden.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "A", "location": "memo.md Plan step 3",
      "scenario": "VM decommissioned on cutover day; a post-cutover failure leaves no fallback for next-morning reports.",
      "fix": "Retain VM (stopped/snapshotted) 2-4 weeks with tested rollback criteria.", "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "A", "location": "memo.md Risks",
      "scenario": "Only vendor outage listed, with no mitigation; failure during the batch window means missing reports; network/data access and lock-in are unaddressed.",
      "fix": "Add alerting, manual re-run path, data-access check, SLA credit terms.", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "B", "location": "memo.md Why bullet 3",
      "scenario": "Platform auto-retry of non-idempotent steps duplicates or corrupts writes.",
      "fix": "Verify idempotency of the three scripts before relying on retries.", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "A", "location": "evidence/run_counts.csv",
      "scenario": "Runs grew 8.4% Apr-Sep; per-run pricing widens the cost gap over time.",
      "fix": "Project 12-month cost at the observed growth rate.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "UNVERIFIED", "track": "C", "location": "memo.md $400, $0.06, 90 days, 99.9%",
      "scenario": "Unsourced pricing/SLA figures may be stale or tiered.",
      "fix": "Attach dated invoice and Stepwise pricing/SLA pages.", "status": "n/a"}
  ]
}
```
