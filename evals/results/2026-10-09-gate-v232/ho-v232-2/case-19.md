VERDICT: **SHIP.** All three rows recompute correctly from suppliers.csv, and Volta wins under any reasonable change to the assumptions. The two findings below are about how the memo presents its figures; neither changes the recommendation.

CONFIDENCE: **high** for the arithmetic and the ranking, **medium** for the absolute five-year figure. Limits: there were no tools, so all figures were recomputed by hand. The once-a-day usage assumption has no stated source. This is not a same-context review, because the memo was not written in this conversation, but no fresh subagent was available.

**INPUTS LEDGER**
- Seen: request.md, context.md, memo.md, suppliers.csv.
- Not seen: the source of "each bike uses its battery once a day" and actual fleet ride data. This matters for the absolute cost figure, not for the ranking.

**COVERAGE**
- Scope: the whole memo, Track A, with numbers recomputed as in Track C.
- Checked:
  - memo.md: the cycle count, all 3 rows, the labor rule and the recommendation.
  - suppliers.csv: all 3 rows.
  - The request, for fit.
  - The context, for stakes.
- Not checked:
  - Costs that are not in the data (warranty, disposal, downtime, capacity fade). Reason: not supplied, and the request scoped TCO to suppliers.csv.

**SEATS AND GATE**
- Seats: a single local reviewer, with no tools and no subagent.
- Sensitivity gate: passed. The work holds only supplier prices and contains no personal or confidential data.
- Embedded instructions: none were found in the work.

**Recomputation**

| Supplier | Batteries for 1,825 cycles | Purchase | Swaps × $15 | Total | Matches memo |
|---|---|---|---|---|---|
| Volta | ⌈1825/2000⌉ = 1 | 1 × 410 = 410 | 0 | 410 | ✓ |
| Amperia | ⌈1825/1000⌉ = 2 | 2 × 380 = 760 | 1 → 15 | 775 | ✓ |
| Zesto | ⌈1825/600⌉ = 4 | 4 × 335 = 1,340 | 3 → 45 | 1,385 | ✓ |

- Cycles: 365 × 5 = 1,825 ✓. The leap day gives 1,826, which does not change any battery count.

**FINDINGS**

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED | A | memo.md line 3 ("once a day: 1,825 cycles") and the Volta row | Volta's $410 depends on staying under a 2,000-cycle life with only 175 cycles (9.6%) to spare. The usage assumption has no source and the memo has no sensitivity check. | Suppose bikes average ≥1.096 battery cycles a day (some bikes need two charges on busy days), or real cycle life falls about 9% short of spec. Each bike then needs a second Volta in year 5, and the cost becomes 820 + 15 = **$835 per bike**. Across the fleet that is $2.57M instead of $1.26M if budgeted from the memo. Volta still wins: Amperia becomes 3 × 380 + 30 = $1,170. | Source the usage figure from ride data. Add a one-line sensitivity check: Volta stays cheapest at any usage level, but its figure roughly doubles above about 1.1 cycles a day. | a ✓, b ✓, c ✗, d unknown |
| F2 | Low | CONFIRMED | A | memo.md title and table | The memo calls this "total cost of ownership" but counts only purchase and swap labor. It does not say that this scope is set by the supplied data. It also gives no fleet total, even though fleet size is stated in the context. | A reader takes $410 as full TCO and budgets the fleet without warranty, disposal or downtime costs. | State the scope in one sentence. Add the fleet totals: $1.26M Volta, $2.39M Amperia, $4.27M Zesto. | a ✓, b ✓, c ✗, d ✗ |

**NEEDS VALIDATION**
- Is "once a day" the real average cycle rate per battery? This is settled by fleet charge logs.
- Is the supplier cycle life measured to end of use or to 80% capacity? This is settled by the supplier spec sheets.

**REFUTED**
- *"Zesto's 4 batteries are an off-by-one error."* Refuted: 3 × 600 = 1,800 < 1,825, so a fourth battery is needed at day 1,800.
- *"Excluding first-install labor biases the result."* Refuted: the omission applies equally to all suppliers, so it cannot change the ranking.
- *"Discounting would flip the result."* Refuted: Amperia's second purchase is about $395 in year 3, and even at 0% discount it comes to $775 against $410.
- *"Volta's leftover 175 cycles are ignored."* This is true, but counting their residual value would only favor Volta further.

**WHAT HOLDS UP**
- Every figure reproduces from the CSV.
- Swap labor is applied correctly (swaps = batteries − 1).
- Per cycle, Volta costs $0.205, against $0.38 for Amperia and $0.56 for Zesto. This dominance is why the ranking survives every perturbation tested.
- The memo answers exactly what was asked: a five-year TCO comparison of the three suppliers and one recommendation.

**UNVERIFIED CLAIMS**
- "Each bike uses its battery once a day." Confirm with ride and charge data.
- "A battery is replaced when it reaches its cycle life." Confirm with the operations replacement policy.

**QUESTIONS FOR THE AUTHOR**
- Where does the once-a-day figure come from?
- What is the peak-season cycle rate?

**DECISION-MAKER SUMMARY**
Choose Volta. The arithmetic is correct, and Volta stays cheapest even if usage or battery life differ from the memo's assumptions. Do not budget the fleet at $1.26M until usage is confirmed: above about 1.1 charges per bike per day the five-year cost roughly doubles, to about $2.57M.

**OWNER SUMMARY**
The recommended battery supplier is the right choice, and its numbers check out. Its battery costs more up front but lasts far longer, so it is the cheapest over five years. The total budget depends on how often bikes are charged, so confirm that figure before locking in the budget.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "memo.md", "status": "seen", "matters": true},
    {"item": "suppliers.csv", "status": "seen", "matters": true},
    {"item": "source for once-a-day usage", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "local-reviewer", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "memo.md", "kind": "document"},
      {"unit": "suppliers.csv", "kind": "data"},
      {"unit": "memo.md: 1,825-cycle assumption", "kind": "assumption"},
      {"unit": "memo.md: per-supplier cost rows", "kind": "claim"},
      {"unit": "memo.md: recommendation", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "costs beyond purchase and swap labor (warranty, disposal, downtime)", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md line 3 (once a day: 1,825 cycles) and Volta row",
     "scenario": "If average usage is at least 1.096 cycles/day or real cycle life is about 9% below spec, each bike needs a second Volta battery in year 5: $835/bike, $2.57M fleet instead of $1.26M. Volta remains cheapest (Amperia $1,170).",
     "fix": "Source the usage rate from fleet data and add a one-line sensitivity check showing the Volta figure roughly doubles above about 1.1 cycles/day while the ranking holds.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "A",
     "location": "memo.md title and table",
     "scenario": "A reader treats $410/bike as full TCO and budgets the 3,080-bike fleet without warranty, disposal or downtime costs; no fleet total is given.",
     "fix": "State that TCO covers purchase and swap labor only, per suppliers.csv, and add fleet totals ($1.26M / $2.39M / $4.27M).",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "A", "location": "memo.md line 3",
     "suspicion": "Once-a-day usage may understate real cycles per battery.",
     "unresolved_fact": "Average and peak charge cycles per bike per day from fleet logs."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Zesto needs 3 batteries, not 4.", "evidence": "3 x 600 = 1,800 < 1,825 cycles, so a fourth battery is required."},
    {"id": "C2", "candidate": "Omitting first-install labor biases the comparison.", "evidence": "The omission applies equally to all three suppliers; the ranking is unchanged."},
    {"id": "C3", "candidate": "Discounting future purchases would flip the result.", "evidence": "Even undiscounted, Amperia's deferred $395 keeps it at $775 against Volta's $410; discounting cannot close a $365 gap."}
  ]
}
```