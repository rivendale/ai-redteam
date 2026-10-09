# Redteam report: Alder vs Birch summarisation cost comparison

> **Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent and no tools were available in this session. I did all checks by reading the supplied text and recomputing by hand.

**VERDICT: SHIP.** The arithmetic is correct and every price and context window matches the supplied pricing pages. The only confirmed defects are two Low wording and precision issues, and neither changes the conclusion.

**CONFIDENCE: medium.** Three things limit it:
- This is a same-context review with no tools.
- I could not compare the supplied pricing excerpts with the live vendor pages.
- Two of the work's premises (the longest document size and that inputs never repeat) rest on facts I was not given.

## INPUTS LEDGER

| Item | Status | Matters? |
|---|---|---|
| request.md (original request) | seen | yes |
| context.md | seen | yes |
| comparison.md (the work) | seen | yes |
| sources/alder-pricing.md | seen (excerpt, retrieved 2026-10-05) | yes |
| sources/birch-pricing.md | seen (excerpt, retrieved 2026-10-05) | yes |
| Live vendor pricing pages | not openable (no tools) | partly: retrieved 3 days before review, so stale prices are unlikely, but I cannot confirm the excerpts are complete |
| The document set or a token profile (backing the "70,000 tokens" claim) | not supplied | yes for the context-window claim |
| Prompt structure of the job (backing "inputs do not repeat") | not supplied | yes for the caching exclusion |

## COVERAGE

**Scope:** the whole work. This is a Track C claims review, as the context requested.

**Checked:**
- comparison.md: the table arithmetic, the cost-difference sentence, and the price, context-window, retention and caching claims
- sources/alder-pricing.md
- sources/birch-pricing.md
- request.md and context.md, checked for fit with the request

**Not checked:**
- Live vendor pages (no tools)
- The document corpus behind the 70k-token claim (not supplied)
- The job's prompt template (not supplied)

**Seats and gate:** No seats ran: there were no tools and no subagent, so only this same-context reviewer took part. The sensitivity gate passed: the inputs are public pricing data and public filings. No reviewer-directed instructions were found in the work.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Low | CONFIRMED | C | comparison.md, para 2: "Birch retains inputs for 30 days" | The source says "inputs **and outputs** are retained for 30 days" (birch-pricing.md, line 3). The work drops outputs. | Later the job's outputs come to include non-public material, such as analyst notes merged into the summaries. A reader relying on this note would believe Birch keeps only the public inputs. | Change the sentence to "retains inputs and outputs for 30 days". | a Y / b Y / c N / d N |
| F2 | Low | CONFIRMED | C | comparison.md table; both source excerpts | Neither the work nor the sources name a model ID for the prices or context windows. Track C requires price and context claims to name the model ID and date. | A provider offers several models, or later adds one. A reader cannot tell which model was priced, so the comparison is silently mismatched to the model actually deployed. | Name the model ID priced at each provider, next to the retrieval date. | a Y / b Y / c N / d N |

## NEEDS VALIDATION

- **N1: the "longest document is 70,000 tokens" claim** (comparison.md, para 2). No source supports it.
  - **Settles it:** the measured maximum input size per call, including prompt overhead, plus the expected output length. The total must stay under Birch's 128,000-token window.
- **N2: "Prompt caching was not modelled because the inputs do not repeat"** (comparison.md, last line).
  - Most summarisation jobs reuse a fixed instruction prompt on every call. Alder lists cache reads at $0.30/M.
  - In the extreme case where all 40M input tokens were cached reads, Alder's input cost would fall to 40 × $0.30 = $12.00. Alder's total would then be $72.00, below Birch's $90.00. So the exclusion could, in principle, flip the conclusion.
  - Realistically the repeated share is small, but it is unstated. Birch's excerpt shows no caching price, so it is also unknown whether Birch offers caching.
  - **Settles it:** the fixed-prompt size × calls per month, and whether Birch has a cache tier.

## REFUTED

- **Candidate: the totals are wrong.** Refuted by recomputation:
  - Alder: 40 × 3.00 = 120.00; 4 × 15.00 = 60.00; total 180.00.
  - Birch: 40 × 1.25 = 50.00; 4 × 10.00 = 40.00; total 90.00.
  - Difference: 180.00 − 90.00 = 90.00, and 90 / 180 = 0.5. So "half the cost" is correct.
- **Candidate: the prices are stale.** Refuted for the supplied evidence: both pages were retrieved 2026-10-05, three days before this review.
- **Candidate: drift from the request.** Refuted. The comparison uses the vendors' own pages from sources/, uses the stated volumes, and shows the arithmetic, as asked.

## WHAT HOLDS UP

- All four unit prices match the sources exactly.
- Both context windows match the sources: Alder 200,000 and Birch 128,000.
- The arithmetic is shown and correct, and per-million scaling is applied consistently.
- The data-sensitivity reasoning is sound for the stated scope: public filings only, with retention noted.

## UNVERIFIED CLAIMS

- That the source excerpts match the live vendor pages and are complete. To confirm, open both pages and check for model tiers, a Birch caching price and any minimum charges.
- The 70k-token maximum (see N1).
- That the inputs do not repeat (see N2).

## QUESTIONS FOR THE AUTHOR

1. Which model at each provider do these prices refer to?
2. Does every call share a fixed instruction prompt, and how many tokens is it?

## DECISION-MAKER SUMMARY

The cost figures are correct: Birch at $90/month against Alder at $180/month, priced from current vendor pages. Proceed with Birch after two small edits: say that Birch also retains outputs, and name the model priced. The residual risk is that an unmodelled shared prompt makes Alder's caching narrow the gap. Only an unusually large repeated prompt would flip the result.

## OWNER SUMMARY

The price comparison adds up correctly, and the cheaper provider costs about half as much each month for this job. Two small wording fixes are needed: one provider keeps both what we send and what it returns for 30 days, and the note should say exactly which product was priced. It is worth confirming whether every request repeats the same instructions, because that could make the pricier provider somewhat cheaper.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "comparison.md", "status": "seen", "matters": true},
    {"item": "sources/alder-pricing.md", "status": "seen", "matters": true},
    {"item": "sources/birch-pricing.md", "status": "seen", "matters": true},
    {"item": "live vendor pricing pages", "status": "not_seen", "matters": false},
    {"item": "document corpus / token profile", "status": "not_seen", "matters": true},
    {"item": "job prompt template", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "public pricing data and public filings only"},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "comparison.md", "kind": "file"},
      {"unit": "sources/alder-pricing.md", "kind": "file"},
      {"unit": "sources/birch-pricing.md", "kind": "file"},
      {"unit": "comparison.md: cost table arithmetic", "kind": "claim"},
      {"unit": "comparison.md: context windows", "kind": "claim"},
      {"unit": "comparison.md: retention", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "live vendor pricing pages", "reason": "no_tools"},
      {"unit": "document corpus (70k-token claim)", "reason": "not_supplied"},
      {"unit": "job prompt template (caching claim)", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "C",
     "location": "comparison.md para 2: 'Birch retains inputs for 30 days'",
     "scenario": "Source says inputs and outputs are retained; if outputs later carry non-public material, readers wrongly believe only public inputs are kept.",
     "fix": "Reword to 'retains inputs and outputs for 30 days'.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "C",
     "location": "comparison.md table; sources/alder-pricing.md; sources/birch-pricing.md",
     "scenario": "No model ID is named for prices or context windows; if a provider has multiple models, the comparison may not match the model deployed.",
     "fix": "Name the model ID priced at each provider alongside the retrieval date.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "N1", "status": "needs_validation", "track": "C",
     "location": "comparison.md para 2: 'our longest document is 70,000 tokens'",
     "suspicion": "The size claim is unsourced; prompt overhead plus output must also fit in 128k.",
     "unresolved_fact": "Measured maximum per-call input tokens including prompt, plus expected output length."},
    {"id": "N2", "status": "needs_validation", "track": "C",
     "location": "comparison.md last line: 'Prompt caching was not modelled because the inputs do not repeat'",
     "suspicion": "A shared instruction prompt would be cacheable at Alder ($0.30/M); in the extreme this drops Alder to $72 < $90.",
     "unresolved_fact": "Fixed-prompt token count x calls per month, and whether Birch offers caching."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Totals are miscalculated.",
     "evidence": "40x3.00=120, 4x15=60, sum 180; 40x1.25=50, 4x10=40, sum 90; difference 90 = half."},
    {"id": "C2", "candidate": "Prices are stale.",
     "evidence": "Both pages retrieved 2026-10-05, three days before review."},
    {"id": "C3", "candidate": "Work drifts from the request.",
     "evidence": "Uses the stated volumes and vendor pages in sources/, and shows the arithmetic."}
  ]
}
```

I could not run `tools/validate_findings.py`, so the JSON block is not validated. The two `needs_validation` entries carry no severity, as the skill requires. That departs from the output note's "each finding has a severity", and is why they are kept separate from F1 and F2.