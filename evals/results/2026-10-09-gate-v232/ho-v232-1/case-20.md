# Redteam review: Q3 ridership report

**Single-reviewer review, no tools.** The work was not written in this session, so there is no authorship anchoring, but no independent second reviewer ran. All arithmetic was recomputed by hand from data.csv as given inline.

**VERDICT: SHIP.** Every number reproduces exactly from data.csv. The one weakness is a Low labelling issue: utilization is called "demand".

**CONFIDENCE: high.** Two-row dataset, all figures recomputed. Limits: hand arithmetic only, and no context beyond data.csv (prior years, seasonality).

**INPUTS LEDGER**
- **Seen:** request.md, context.md, data.csv (2 rows), report.md.
- **Not seen:** prior-year data or Q3 of last year. This matters only for the seasonality question (S1), not for any stated number.

**COVERAGE**
- **Scope:** the whole work (report.md against data.csv).
- **Checked:**
  - every number in the report: 412,000; 473,800; 15.0%; 3,000; 3,080; 1.51; 1.67; 10.8%
  - the day counts (Q2 = Apr–Jun = 91, Q3 = Jul–Sep = 92)
  - the "rose less" direction claim
  - the "better measure of demand" claim
  - the "too few to call a trend" caveat
- **Not checked:** nothing in scope.

**SEATS AND GATE:** local reviewer only. Sensitivity gate passed (aggregate ridership, no personal data). No cross-vendor seats were requested at standard depth.

### Recomputation

| Claim | Recomputed | Result |
|---|---|---|
| Trips 412,000 → 473,800 | data.csv rows | ✔ |
| Up 15.0% | 473,800 / 412,000 = 1.1500 | ✔ |
| Fleet 3,000 → 3,080 | data.csv | ✔ |
| Q3 has one more day | 92 vs 91 | ✔ |
| Q2 trips/bike/day 1.51 | 412,000 / (3,000 × 91) = 412,000 / 273,000 = 1.5092 | ✔ |
| Q3 trips/bike/day 1.67 | 473,800 / (3,080 × 92) = 473,800 / 283,360 = 1.6721 | ✔ |
| Up 10.8% | 1.6721 / 1.5092 = 1.1080 | ✔ (computed from unrounded values; the rounded 1.67/1.51 would give 10.6%) |
| "Rose less" | 10.8% < 15.0% | ✔ |

### FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Low | PROBABLE | C | report.md para 2: "We read the rise in trips per bike as the better measure of demand." | Trips per bike per day measures fleet utilization, not demand. Dividing by fleet size removes any demand that the 80 extra bikes served. | If bikes were added because riders were being turned away, the board reads 10.8% as demand growth when trips per day rose 13.8% (4,527.5 → 5,150.0) and total trips 15.0%. Both figures are shown and correctly labelled, so the harm is limited. | Report trips per day (+13.8%) as the day-adjusted demand figure. Present trips/bike/day as utilization. Repro: 473,800/92 ÷ 412,000/91 = 1.1375. | a: yes, b: no, c: no, d: yes |

### NEEDS VALIDATION
- **S1:** Q2→Q3 growth may be mostly seasonal (summer riding), not underlying demand growth. To settle it: compare Q3 against the same quarter last year, or use the seasonal index from prior years. The report's "two quarters are too few to call a trend" partly covers this.

### REFUTED
- **Candidate: 10.8% does not reproduce from the 1.51 and 1.67 shown.** Refuted. The 10.8% comes from the unrounded ratios (1.6721 / 1.5092 = 1.108), which is the correct method. The 10.6% figure is only a rounding artifact of the displayed values.

### WHAT HOLDS UP
- All eight figures reproduce exactly from data.csv.
- Normalizing for the extra day and the fleet change is correct and clearly explained.
- The trend caveat is appropriate.
- The report answers the request: it states demand growth.

### UNVERIFIED CLAIMS
None of the numbers. The demand interpretation is a judgment, covered under F1 and S1.

### QUESTIONS FOR THE AUTHOR
- Were the 80 bikes added in response to unmet demand? If yes, F1 matters more.

### DECISION-MAKER SUMMARY
The numbers are correct and can go to the board. Before sending, consider adding trips per day (+13.8%) as the day-adjusted demand figure and calling trips per bike per day "utilization". Without that change, the board may understate demand growth by about 3 points if fleet growth was demand-driven.

### OWNER SUMMARY
Every figure in the report checks out against the data. The only suggestion is a wording change: the per-bike figure describes how busy each bike is rather than how many more people rode, so it is worth also showing growth in trips per day. The quarter-to-quarter rise may partly reflect summer, which the report already partly acknowledges.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "data.csv", "status": "seen", "matters": true},
    {"item": "report.md", "status": "seen", "matters": true},
    {"item": "prior-year quarterly data", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "data.csv", "kind": "data"},
      {"unit": "report.md", "kind": "document"},
      {"unit": "trips 412,000 -> 473,800, +15.0%", "kind": "claim"},
      {"unit": "fleet 3,000 -> 3,080; one more day", "kind": "claim"},
      {"unit": "trips/bike/day 1.51 -> 1.67, +10.8%", "kind": "claim"},
      {"unit": "trips per bike is the better measure of demand", "kind": "claim"}
    ],
    "not_checked": []
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Low", "evidence_level": "PROBABLE", "track": "C",
     "location": "report.md para 2: \"We read the rise in trips per bike as the better measure of demand.\"",
     "scenario": "If the 80 added bikes served unmet demand, the board reads 10.8% (a utilization figure) as demand growth, while trips per day rose 13.8% and total trips 15.0%.",
     "fix": "Report trips per day (+13.8%: 473,800/92 vs 412,000/91) as the day-adjusted demand figure; label trips/bike/day as utilization.",
     "answers": {"a": true, "b": false, "c": false, "d": true}},
    {"id": "S1", "status": "needs_validation", "track": "A", "location": "report.md para 1-2",
     "suspicion": "Q2 to Q3 growth may be largely seasonal rather than demand growth.",
     "unresolved_fact": "Q3 trips versus the same quarter last year, or a prior-year seasonal index."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "10.8% does not reproduce from the displayed 1.51 and 1.67 (which give 10.6%).",
     "evidence": "Unrounded 1.6721/1.5092 = 1.108; the report correctly computed from unrounded values."}
  ]
}
```