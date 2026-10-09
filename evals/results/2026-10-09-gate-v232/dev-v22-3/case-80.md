# Redteam review: contract-summary model memo

**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent or tools were available, so every check below compares the memo with the supplied price page by hand.

**VERDICT: REWORK.** None of the memo's four figures matches any single model on the price page. Its $8 price belongs to a model retired on 2026-08-15, so next year's budget rests on a model that cannot be bought.

**CONFIDENCE: medium.** The comparison against the supplied page is exact. What limits confidence: this was a same-context review, no tools were available, and the live price page and the source of the 91% benchmark were not supplied.

**INPUTS LEDGER**
- **Seen:** request.md, context.md, memo.md, price_page.md (captured 2026-09-30).
- **Not seen:** the live vendor price page, which matters because the page itself warns it may have changed. Any source for "1M context" or "91%", which matters because no claim can be traced without one; the context says the page was all the author had. The volume of output tokens, which matters for the budget. The length of the contracts to be summarised, which matters for whether 128k or 200k tokens of context is enough.

**COVERAGE**
- **Checked:** memo.md, all four claims (context window, input price, benchmark, monthly cost) and the model naming. price_page.md, every row and the benchmark note.
- **Not checked:** the live pricing and the vendor's benchmark method. Neither was supplied.

**SEATS AND GATE:** Only the local same-context reviewer ran. No cross-vendor seats were requested at this depth. The sensitivity gate passed: the work contains no personal or confidential data.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | C | memo.md: "costs $8 per million input tokens" and "about $320 a month" | $8.00 is the input price of `lumen-1-large`, which the page marks "(retired 2026-08-15)". The arithmetic itself holds (40 × $8 = $320). | Finance sets next year's budget on a model that cannot be bought. Current models cost $120 a month (`lumen-2-large`, 40 × $3.00) or $24 a month (`lumen-2-small`, 40 × $0.60), so the budget line is wrong by a factor of 2.7 to 13. | Name an available model and recompute from its row. Check: look up $8.00 on the page; it appears only on the retired row. | a✓ b✓ c✓ d✓ |
| F2 | Critical | CONFIRMED | C | memo.md: "one-million-token context window" | No model on the page has a 1M context window. The largest is 200,000 (`lumen-2-large`); the $8 model has 100,000. | The feature is designed around feeding whole contracts in one call. Long contracts then exceed the real limit and fail or get truncated in production. | Use the context window from the chosen model's row (200,000 or 128,000). Check: the page's maximum context window is 200,000. | a✓ b✓ c✓ d✓ |
| F3 | Critical | CONFIRMED (absent from the only source) | C | memo.md: "scores 91% on reasoning benchmarks" | 91% appears nowhere. The vendor note dated 2026-09-12 gives 84.1% (`lumen-2-large`) and 71.0% (`lumen-2-small`) on "the vendor's reasoning set". It gives no figure for `lumen-1-large`. "Reasoning benchmarks" names no benchmark. | Decision-makers compare models on a quality score that has no source and is 7 or more points above anything published. | Quote 84.1% or 71.0% with the model id, "vendor reasoning set (vendor-reported)", and the date 2026-09-12. | a✓ b✓ c✓ d✓ |
| F4 | High | CONFIRMED | C | memo.md: "We recommend Lumen." | "Lumen" is a family name, not a model id. No claim carries the date it was true. The context explicitly requires both. | Procurement or engineering picks a Lumen model; the figures belong to three different ones. The memo also gives no warning that prices were captured 2026-09-30 and may change before next year. | State the model id (for example `lumen-2-large`) and add "per vendor price page captured 2026-09-30" and "benchmark per vendor note 2026-09-12". | a✓ b✓ c✗ d✓ |
| F5 | Medium | CONFIRMED | C | memo.md: "the model cost is about $320 a month" | The memo calls input-only spend "the model cost". Output pricing ($15.00, $2.40 and $24.00 per 1M) is left out. | Summaries produce output tokens, so the budget is understated by the whole output spend. For `lumen-2-large`, every 1M output tokens adds $15. | Label the figure "input cost", or add an estimate of output volume times the output price. | a✓ b✓ c✗ d✓ |

**Root cause across F1 to F4:** the memo combines a retired model's price, a context window that matches no model, and an unsourced score under a family name. It describes a model that does not exist.

## Needs validation
- **S1:** Is 200,000 or 128,000 tokens of context enough for the actual contracts? This is settled by the token-length distribution of real contracts, the longest in particular.
- **S2:** Were prices on the live page still those of 2026-09-30 on 2026-10-08, and are any changes announced for next year? This is settled by a fresh capture of the page with its date.
- **S3:** Does the 91% come from some other source, such as a different benchmark or a third party? This is settled by the author naming the source; none was supplied.

## Refuted
- **R1:** "The $320 arithmetic is wrong." Refuted: 40 × $8.00 = $320.00 exactly. The defect is the price used (F1), not the multiplication.

## What holds up
The monthly volume is applied correctly, and the cost formula (millions of tokens × price per million) is right. The memo also answers each part of the request's structure: a recommendation, a context window, a price, a benchmark and a monthly cost.

## Unverified claims
- The 1M context window and the 91% benchmark: no source was supplied, so ask the author for one.
- Whether the prices are still current: capture the live page again.

## Questions for the author
1. Which model id do you mean?
2. Where do the 1M context and 91% figures come from?
3. What output volume should the budget assume?

## Decision-maker summary
The memo's price, context window and benchmark match no single available model, and the $8 price is from a model retired 2026-08-15. Do not use $320 a month for the budget. Have the memo redone on `lumen-2-large` ($120 a month input) or `lumen-2-small` ($24 a month input), with output cost added and every figure dated. If you proceed anyway, the budget and the feature's design rest on a model that cannot be bought and a context limit five times too large.

## Owner summary
The recommendation describes a model that cannot be bought today: its price comes from a retired product, and its memory size and quality score do not match the vendor's published figures. The real monthly cost will probably be lower than stated for the input side, but the memo leaves out the cost of the generated summaries. Please ask for a corrected memo before setting the budget.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "memo.md", "status": "seen", "matters": true},
    {"item": "price_page.md (captured 2026-09-30)", "status": "seen", "matters": true},
    {"item": "live vendor price page", "status": "not_seen", "matters": true},
    {"item": "source for 1M context and 91% benchmark", "status": "not_seen", "matters": true},
    {"item": "output token volume", "status": "not_seen", "matters": true},
    {"item": "contract length distribution", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "memo.md", "kind": "file"},
      {"unit": "price_page.md", "kind": "file"},
      {"unit": "memo.md: context window claim", "kind": "claim"},
      {"unit": "memo.md: input price claim", "kind": "claim"},
      {"unit": "memo.md: benchmark claim", "kind": "claim"},
      {"unit": "memo.md: monthly cost claim", "kind": "claim"},
      {"unit": "memo.md: model naming and dating", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "live vendor pricing", "reason": "not supplied; no tools"},
      {"unit": "vendor benchmark methodology", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "memo.md: 'costs $8 per million input tokens' / 'about $320 a month'",
     "scenario": "The $8 price is lumen-1-large's, retired 2026-08-15; next year's budget is set on a model that cannot be bought. Available models cost $120/mo (lumen-2-large) or $24/mo (lumen-2-small) for 40M input tokens.",
     "fix": "Name an available model id and recompute from its row on the 2026-09-30 page.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Look up $8.00 on price_page.md: it appears only on the lumen-1-large row marked retired 2026-08-15."},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "memo.md: 'one-million-token context window'",
     "scenario": "The feature is designed for whole contracts in one call; the real maximum is 200,000 tokens (100,000 for the $8 model), so long contracts fail or are truncated.",
     "fix": "State the chosen model's context window from the page (200,000 or 128,000).",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "The maximum of the context window column on price_page.md is 200,000; no row shows 1,000,000."},
    {"id": "F3", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "memo.md: 'scores 91% on reasoning benchmarks'",
     "scenario": "The model choice rests on an unsourced score; the vendor note (2026-09-12) gives 84.1% for lumen-2-large and 71.0% for lumen-2-small, and nothing for lumen-1-large.",
     "fix": "Quote the vendor figure with model id, benchmark name (vendor reasoning set, vendor-reported) and date 2026-09-12.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Search price_page.md for 91: no match; the benchmark note lists only 84.1% and 71.0%."},
    {"id": "F4", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "C",
     "location": "memo.md: 'We recommend Lumen.'",
     "scenario": "No model id and no dates are given, contrary to the stated requirement; a reader cannot tell which model is meant or that prices date from 2026-09-30 and may change.",
     "fix": "Name the model id and date each claim (price page 2026-09-30, benchmark 2026-09-12).",
     "answers": {"a": true, "b": true, "c": false, "d": true}},
    {"id": "F5", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "C",
     "location": "memo.md: 'the model cost is about $320 a month'",
     "scenario": "Input-only spend is called 'the model cost'; output tokens for summaries ($15/1M on lumen-2-large) are omitted, so the budget is understated.",
     "fix": "Label it as input cost, or add estimated output volume times the output price.",
     "answers": {"a": true, "b": true, "c": false, "d": true}},
    {"id": "S1", "status": "needs_validation", "track": "C", "location": "memo.md: context window claim",
     "suspicion": "Even 200,000 tokens may not fit the longest contracts.",
     "unresolved_fact": "Token-length distribution of the actual contracts."},
    {"id": "S2", "status": "needs_validation", "track": "C", "location": "price_page.md header",
     "suspicion": "Prices may have changed since the 2026-09-30 capture.",
     "unresolved_fact": "A fresh, dated capture of the live vendor price page."},
    {"id": "S3", "status": "needs_validation", "track": "C", "location": "memo.md: benchmark claim",
     "suspicion": "91% may come from a different benchmark or a third-party source.",
     "unresolved_fact": "The author's source for 91%."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "The $320 monthly arithmetic is wrong.",
     "evidence": "40 x $8.00 = $320.00 exactly; the defect is the price used (F1), not the multiplication."}
  ]
}
```