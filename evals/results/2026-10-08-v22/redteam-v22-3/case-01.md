# Red-team review: decision memo on moving the nightly batch to Stepwise

**Review conditions:** single reviewer, no tools, no subagent. I did not write the memo, but no independent second reviewer ran. Re-run with a fresh reviewer before relying on this for anything high-stakes. I recomputed every figure by hand from the supplied CSV.

**VERDICT: REWORK.** The memo's central cost figure ignores the usage data the request told it to use. That data shows about 31,700 runs a month, not 3,000, so Stepwise costs about $1,900 a month instead of $180. The claimed $2,640 yearly saving becomes an extra cost of about $18,000 a year.

**CONFIDENCE: medium.**
- The main finding is solid: it is plain arithmetic on the supplied file.
- Confidence is limited by:
  - no tools;
  - a single reviewer;
  - vendor prices and the VM cost not being verifiable;
  - uncertainty over whether the CSV counts only this batch's runs.

**INPUTS LEDGER:**
- **Seen:**
  - `request.md`
  - `context.md`
  - `memo.md`
  - `evidence/run_counts.csv`
- **Not seen:**
  - **Stepwise pricing page or contract.** This matters because the $0.06 rate drives the conclusion.
  - **VM billing for the $400 a month.** This matters because it is the baseline.
  - **The three batch scripts.** This matters for porting effort and for whether retries are safe.
  - **The definition of a "run" in the CSV versus a Stepwise billable "workflow run".** This matters a great deal.
  - **Stepwise SLA text.** This matters only a little.

**COVERAGE:**
- **Checked:**
  - `evidence/run_counts.csv` (all 6 rows, summed and averaged)
  - memo sections: Recommendation, Why, Alternatives, Plan, Risks
  - claims: $400 a month, $0.06 per run, 3,000 runs, $180, $220 and $2,640, retries and 90-day history, 99.9%
- **Not checked:**
  - vendor pricing, SLA and features (not supplied, no tools)
  - batch scripts (not supplied)
  - VM invoice (not supplied)

**SEATS AND GATE:**
- Seats: one local reviewer ran. No subagent was available. No cross-vendor seat was used: none was requested, and the depth is standard.
- Sensitivity gate: passed. The inputs hold no personal, financial-record or credential data.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | A, C | memo.md "Why", bullet 2: "about **3,000 runs per month**, so the bill is **$180 per month**" | The run count is off by about 10x against `evidence/run_counts.csv`. The memo did not base the cost on the real usage, as the request required. | The CSV sums to 190,320 runs over 6 months, a mean of 31,720 a month, with the latest month at 32,760. At $0.06 per run, Stepwise costs $1,903 a month on average ($1,966 for the latest month), against the VM's $400. Acting on the memo raises cost by about $1,503 a month (about $18,040 a year) instead of saving $2,640. | Recompute from the CSV: 31,720 × $0.06 = $1,903.20 a month. Redo the comparison and the recommendation. Reproduce: sum the `runs` column (190,320), divide by 6, multiply by 0.06, and compare with $180. | a Y, b Y, c Y, d Y |
| F2 | High | CONFIRMED | A | memo.md "Plan", step 3: "**Decommission the VM the same day**" | There is no rollback path at cut-over for a job that feeds next-morning reports. | Stepwise fails on its first production night because of a credential, network-access or schedule time-zone problem. The VM is already gone, so the reports are late or missing, and restoring cron means rebuilding the VM. | Keep the VM, stopped but restorable or snapshotted, for 2 to 4 weeks after cut-over. Define rollback criteria in advance. | a Y, b Y, c Y, d Y |
| F3 | Medium | CONFIRMED | A | memo.md "Alternatives", item 3 | The cheapest option is listed, at about $60 a month, but the memo never evaluates or rejects it. The Stepwise recommendation has no stated reason to beat it. | Even on the memo's own figures, the container job ($60) is cheaper than Stepwise ($180). On the corrected figures it is about 30x cheaper. The decision-maker gets no basis for choosing between the options. | Add a comparison of the three options with like-for-like costs, operating burden, retries and history, and migration effort. | a Y, b Y, c N, d N |
| F4 | Low | PROBABLE | A | memo.md "Risks" | There is a single risk, and the 99.9% figure is not tied to the batch. | 99.9% allows about 43 minutes of downtime a month, and one outage during the nightly window misses the reports. The section also omits other risks: price changes at growing volume (runs rose 8.4% from April to September), billing for retries, giving the managed service access to data sources, and lock-in. | Expand the risks section. Model cost at the observed growth rate. State the impact of an outage during the batch window. | a Y, b N, c N, d N |

## NEEDS VALIDATION

- **S1, the run definition (Track C, `run_counts.csv`).** About 1,050 runs a night is a lot for "three batch scripts".
  - Unresolved fact: does the CSV count Stepwise-billable workflow runs for this batch only, or every job or step on the VM? If it counts something else, F1's magnitude changes, but the memo's 3,000 figure is still unsupported by any supplied evidence.
- **S2, retry billing (memo "Why", bullet 3).** Unresolved fact: does Stepwise bill retried steps or runs as extra runs?
- **S3, idempotency (memo "Why", bullet 3).** The memo says Stepwise's automatic retries "remove our hand-written retry code".
  - Unresolved fact: are the three scripts' steps idempotent? If they are not, an automatic retry could write output twice.
- **S4, on-call burden (memo "Why", bullet 1).** Unresolved fact: who handles stuck or failed Stepwise runs? The memo implies on-call duty goes away, but a managed service still needs someone to respond to failures.

## REFUTED

- **C1: "$180 is miscomputed."** Refuted: 3,000 × $0.06 = $180 and $400 − $180 = $220, × 12 = $2,640. The arithmetic is internally correct. The fault is the input, which is F1.

## WHAT HOLDS UP

- The memo's internal arithmetic is correct.
- Week 2 of the plan, running both systems in parallel and comparing outputs, is sound practice.
- Listing a do-less option and a cheaper option is the right structure, even though they were not evaluated.
- I found no injected instructions in the work.

## UNVERIFIED CLAIMS

| Claim | How to confirm |
|---|---|
| VM costs $400 a month | Billing export |
| Stepwise charges $0.06 per workflow run, with no volume tiers or per-step charges | Current pricing page or quote, dated |
| 90-day run history and automatic step retries | Stepwise documentation |
| 99.9% availability | SLA text, including the credit terms |
| Two days of work for the retry helper; about $60 a month for container capacity | Engineering estimate and a cluster cost check |

## QUESTIONS FOR THE AUTHOR

1. Where does "about 3,000 runs per month" come from, and how does it relate to the 30,000 to 33,000 in `run_counts.csv`?
2. Does one CSV "run" equal one Stepwise billable run?
3. Why was the scheduled container job (about $60 a month) not chosen?

## DECISION-MAKER SUMMARY

Do not approve the move on this memo. Using the supplied usage data, Stepwise costs about $1,900 a month against the VM's $400, which is about $18,000 a year more, not $2,640 a year saved. The cheaper container-job option was never evaluated. If you proceed anyway, you take on that extra cost plus a same-day VM shutdown with no fallback for the next-morning reports.

## OWNER SUMMARY

The memo's savings estimate rests on a usage figure about ten times lower than our actual records. With the real numbers, the proposed service would cost several times more than the current setup. The memo should be redone with the correct usage, a fair look at the cheaper container option, and a safer cut-over that keeps the old machine available for a few weeks.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "memo.md", "status": "seen", "matters": true},
    {"item": "evidence/run_counts.csv", "status": "seen", "matters": true},
    {"item": "Stepwise pricing page or contract", "status": "not_seen", "matters": true},
    {"item": "VM billing records", "status": "not_seen", "matters": true},
    {"item": "Definition of a run in run_counts.csv", "status": "not_seen", "matters": true},
    {"item": "Batch scripts", "status": "not_seen", "matters": true},
    {"item": "Stepwise SLA text", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "evidence/run_counts.csv", "kind": "data"},
      {"unit": "memo.md", "kind": "file"},
      {"unit": "memo.md#Why", "kind": "section"},
      {"unit": "memo.md#Alternatives considered", "kind": "section"},
      {"unit": "memo.md#Plan", "kind": "section"},
      {"unit": "memo.md#Risks", "kind": "section"},
      {"unit": "3,000 runs per month, $180 per month, $2,640 per year", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "Stepwise price, retries, 90-day history, 99.9% SLA", "reason": "not supplied; no tools to open vendor sources"},
      {"unit": "VM cost of $400 per month", "reason": "billing not supplied"},
      {"unit": "batch scripts", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md Why, bullet 2: 'about 3,000 runs per month, so the bill is $180 per month'",
     "scenario": "run_counts.csv sums to 190,320 runs over 6 months (mean 31,720 per month; latest 32,760). At $0.06 per run Stepwise costs about $1,903 per month against the VM's $400, so moving raises cost by about $18,040 per year instead of saving $2,640.",
     "fix": "Recompute the cost from run_counts.csv (31,720 x 0.06 = $1,903.20 per month) and redo the recommendation.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Sum the runs column of evidence/run_counts.csv (190,320), divide by 6 (31,720), multiply by 0.06 ($1,903.20); expected $180 per memo, observed $1,903.20."},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md Plan, step 3: 'Decommission the VM the same day'",
     "scenario": "If Stepwise fails on its first production night (credentials, network access, schedule time zone), the VM is already gone and the next-morning reports are missed with no quick fallback.",
     "fix": "Keep the VM stopped but restorable, or snapshotted, for 2 to 4 weeks after cut-over, with predefined rollback criteria.",
     "answers": {"a": true, "b": true, "c": true, "d": true}},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md Alternatives considered, item 3",
     "scenario": "The scheduled container job (about $60 per month) is cheaper than Stepwise even on the memo's own figures, yet it is never evaluated or rejected, leaving the decision-maker without a basis to choose.",
     "fix": "Add a like-for-like comparison of the three options covering cost, operating burden, retries and history, and migration effort.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "PROBABLE", "track": "A",
     "location": "memo.md Risks",
     "scenario": "Only vendor outage is listed. 99.9% allows about 43 minutes of downtime per month, and one outage in the nightly window misses the reports. Growth in runs (+8.4% from April to September), retry billing, data-source access and lock-in are not considered.",
     "fix": "Expand the risks section, model cost at the observed growth rate, and state the impact of an outage during the batch window.",
     "answers": {"a": true, "b": false, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "C", "location": "evidence/run_counts.csv",
     "suspicion": "About 1,050 runs per night may count jobs or steps beyond this batch, which would change the size of F1.",
     "unresolved_fact": "Whether a CSV run equals one Stepwise billable workflow run for this batch only."},
    {"id": "S2", "status": "needs_validation", "track": "C", "location": "memo.md Why, bullet 3",
     "suspicion": "Automatic retries may be billed as extra runs.",
     "unresolved_fact": "Whether Stepwise bills retried steps or runs."},
    {"id": "S3", "status": "needs_validation", "track": "A", "location": "memo.md Why, bullet 3",
     "suspicion": "Automatic retries of non-idempotent steps could duplicate writes.",
     "unresolved_fact": "Whether the three batch scripts' steps are idempotent."},
    {"id": "S4", "status": "needs_validation", "track": "A", "location": "memo.md Why, bullet 1",
     "suspicion": "On-call duty for failed runs may not actually go away.",
     "unresolved_fact": "Who responds to failed or stuck Stepwise runs."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The $180 and $2,640 figures are miscomputed.",
     "evidence": "3,000 x 0.06 = 180; (400 - 180) x 12 = 2,640. The arithmetic is internally correct; the input is wrong (F1)."}
  ]
}
```

The output note asks for a severity on every finding. Under the skill's schema 2.2, `needs_validation` entries (S1 to S4) carry no severity, so I followed the schema there. Every confirmed finding has severity, evidence_level, location, scenario and fix.