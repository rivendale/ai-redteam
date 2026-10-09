# Redteam report: model-choice memo (Track C claims review)

**VERDICT: SHIP.** Every capability, price, benchmark and retirement claim in the memo matches the supplied price page, names the model id, and carries a date. The 40M-token cost recomputes correctly.

**CONFIDENCE: medium.** Three things limit it:
- I had no tools, so I checked only against the supplied capture.
- The live vendor page was not openable, and it may have changed since 2026-09-30.
- This is a single reviewer in this session with no fresh subagent. The work was not written in this conversation, so the risk of inheriting the author's view is low. Re-run in a fresh session if the budget decision is high-stakes.

**INPUTS LEDGER**
- **Seen:** `request.md`, `context.md`, `memo.md`, `price_page.md` (captured 2026-09-30).
- **Not seen:**
  - The live vendor price page. This matters for the budget because prices can change, but the memo already says "re-check before signing".
  - The vendor's benchmark source behind the "benchmark note". This matters little, because the memo labels the figure vendor-reported and not independently checked.
  - Expected output-token volume and contract lengths. These matter for the total budget and for the choice of model; see S1 and S2.

**COVERAGE**
- **Checked:**
  - `memo.md`: every claim (model id, context window, input price, benchmark and its date, monthly cost, lumen-1-large retirement, capture date).
  - `price_page.md`: the table and the benchmark note.
- **Not checked:** the live price page, the vendor benchmark methodology, and the actual workload profile. None of these was supplied.

**SEATS AND GATE:** One same-session reviewer ran. No cross-vendor seats were used; none were requested and there were no tools. Sensitivity gate: no personal, client or confidential data was found (`sensitive: false`).

## Claim-by-claim check (Track C)

| Claim in memo | Price page | Model id named | Date named | Result |
|---|---|---|---|---|
| lumen-2-large, 200,000-token context | 200,000 | yes | 2026-09-30 | matches |
| $3.00 per 1M input tokens | $3.00 | yes | 2026-09-30 | matches |
| 84.1% on vendor reasoning set, vendor-reported | 84.1%, "Benchmark note (vendor, 2026-09-12)" | yes | 2026-09-12 | matches, correctly qualified |
| ~$120/month at 40M input tokens | 40 × $3.00 = $120.00 | yes | (derived) | recomputed, correct; labelled "input cost" |
| lumen-1-large retired 2026-08-15 | "(retired 2026-08-15)" | yes | 2026-08-15 | matches |

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| none | | | | | No confirmed defects. | | | |

## NEEDS VALIDATION

- **S1. Output cost is missing from a memo that sets the budget.**
  - Location: `memo.md`, "the input cost is about $120 a month".
  - The request asked only for cost at 40M input tokens, and the memo correctly calls the figure "input cost". Summaries also generate output tokens, which cost $15.00 per 1M (`price_page.md`, lumen-2-large row). The memo omits this rate.
  - If a budget owner reads $120 as the total, the budget is understated by the output spend.
  - Unresolved fact: the expected monthly output-token volume. For example, 4M output tokens would add $60, making the total 50% higher.
  - Suggested fix: add one line stating the output price, and that the $120 excludes output.
- **S2. No rationale for choosing lumen-2-large over lumen-2-small.**
  - lumen-2-small costs $0.60 per 1M input, so $24/month at 40M. It has a 128,000-token context and scores 71.0%.
  - The memo does not say why the larger model is needed.
  - Unresolved fact: whether contracts plus the prompt exceed 128k tokens, or whether the gap from 71.0% to 84.1% matters for summary quality. If neither holds, the recommendation costs about 5× more than it needs to.

## REFUTED

- **Possible stale claim (benchmark dated 12 days before the capture).** Refuted: the memo states the date and attributes the figure to the vendor, which satisfies the dating requirement.
- **Possible arithmetic error.** Refuted: 40,000,000 / 1,000,000 × $3.00 = $120.00, exactly as stated.

## WHAT HOLDS UP

- Every figure ties to the supplied page and is attributed to it.
- The vendor benchmark is labelled vendor-reported and not independently checked.
- The capture date is stated, and the memo warns to re-check before signing.
- The retired model is correctly excluded.

## UNVERIFIED CLAIMS

- That $3.00 per 1M and 200,000 tokens are still current. To confirm, read the live vendor page on the signing date and compare.
- That 84.1% is reproducible. To confirm, get the vendor benchmark report or run an independent evaluation on sample contracts.

## QUESTIONS FOR THE AUTHOR

1. What is the expected monthly output-token volume?
2. Do any contracts, plus the prompt, exceed 128k tokens? Was lumen-2-small considered?

## DECISION-MAKER SUMMARY

The memo's facts are accurate, sourced and dated, and the $120/month input figure is correct. Before using it for next year's budget, add the expected output-token cost at $15 per 1M and confirm prices on the live page. Otherwise the budget will be understated by an unknown amount.

## OWNER SUMMARY

The memo's numbers match the vendor's published prices and are correctly calculated. The $120 monthly figure covers only the text sent to the model, not the summaries it writes back, so the real monthly cost will be higher. Check current prices just before committing, and confirm the cheaper model really would not do the job.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "memo.md", "status": "seen", "matters": true},
    {"item": "price_page.md (captured 2026-09-30)", "status": "seen", "matters": true},
    {"item": "live vendor price page", "status": "not_seen", "matters": true},
    {"item": "vendor benchmark source", "status": "not_seen", "matters": false},
    {"item": "workload profile (output tokens, contract lengths)", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "same-session-reviewer", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "memo.md", "kind": "file"},
      {"unit": "price_page.md", "kind": "file"},
      {"unit": "memo.md: lumen-2-large 200,000-token context", "kind": "claim"},
      {"unit": "memo.md: $3.00 per 1M input", "kind": "claim"},
      {"unit": "memo.md: 84.1% vendor-reported 2026-09-12", "kind": "claim"},
      {"unit": "memo.md: ~$120/month at 40M input", "kind": "claim"},
      {"unit": "memo.md: lumen-1-large retired 2026-08-15", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "live vendor price page", "reason": "no tools; not supplied"},
      {"unit": "vendor benchmark methodology", "reason": "not supplied"},
      {"unit": "workload output volume and contract lengths", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "S1", "status": "needs_validation", "track": "C", "location": "memo.md: 'the input cost is about $120 a month'",
     "suspicion": "Budget memo omits output-token cost ($15.00 per 1M for lumen-2-large); $120 may be read as the total.",
     "unresolved_fact": "Expected monthly output-token volume for contract summaries.",
     "severity": null, "evidence_level": "UNVERIFIED",
     "scenario": "If the budget owner treats $120 as total spend, output costs are unbudgeted.",
     "fix": "State the output price and that $120 excludes output; add an estimate once volume is known."},
    {"id": "S2", "status": "needs_validation", "track": "C", "location": "memo.md: 'We recommend lumen-2-large'",
     "suspicion": "No stated reason lumen-2-small ($24/month at 40M, 128k context, 71.0%) is insufficient.",
     "unresolved_fact": "Whether contracts plus prompt exceed 128k tokens, or whether the 71.0% vs 84.1% gap matters for summary quality.",
     "severity": null, "evidence_level": "UNVERIFIED",
     "scenario": "If contracts fit in 128k and quality suffices, the recommendation costs about 5x more than needed.",
     "fix": "Add one sentence justifying the larger model with the contract-length or quality requirement."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Monthly cost arithmetic is wrong.", "evidence": "40,000,000 / 1,000,000 x $3.00 = $120.00, matching the memo."},
    {"id": "C2", "candidate": "Benchmark claim is undated or unattributed.", "evidence": "Memo says 'vendor-reported, 2026-09-12; not independently checked', matching the price page note."}
  ]
}
```