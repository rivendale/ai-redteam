# Redteam report: Alder vs Birch cost comparison

**Review mode:** No tools were available in this session, so no subagent or external seats could run and no live pages could be opened. I am not the author of this work, but there was no fresh instance either. Every number below was recomputed by hand from the supplied source files.

**VERDICT: SHIP WITH FIXES.** The arithmetic and the price, context-window and conclusion claims all match the supplied sources. One sentence misstates the Birch retention clause and should be corrected.

**CONFIDENCE: medium.** Limits: no tools, so the live vendor pages could not be checked against the supplied copies. The "longest document is 70,000 tokens" figure has no supplied evidence.

**INPUTS LEDGER:**
- **Seen:** request.md, context.md, comparison.md, sources/alder-pricing.md, sources/birch-pricing.md.
- **Not seen:**
  - The live vendor pricing pages. This matters a little: the sources are dated 5 Oct 2026, three days ago, so staleness risk is low.
  - The document-length data behind "longest document is 70,000 tokens". This matters only for the context-window claim.
  - The job's prompt structure, which would show whether any input repeats. This matters for the caching exclusion.

**COVERAGE:**
- **Checked:** the cost table (both rows, all four products and both totals), the "$90 cheaper / half the cost" claim, both context-window claims, the retention claim, the source citations, and the caching exclusion.
- **Not checked:** the live pages, the document-length data, and other price dimensions (batch discounts, tiers, minimums). Those dimensions do not appear in the supplied sources.

**SEATS AND GATE:** Same-session reviewer only. No subagent or cross-vendor seats were available. Sensitivity gate passed: the work covers public filings and public pricing, with no personal or confidential data.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Low | CONFIRMED | C | comparison.md, "Birch retains inputs for 30 days for abuse monitoring [2]" | The source says "inputs **and outputs** are retained for 30 days". The work drops "outputs". | Someone reuses this comparison for a later job on non-public data. They believe Birch keeps only prompts, but generated summaries of confidential material are also retained for 30 days. | Change to "Birch retains inputs and outputs for 30 days for abuse monitoring [2]". To reproduce, compare the sentence with line 4 of sources/birch-pricing.md. | a yes, b yes, c no (public filings only), d no |

## Needs validation (no severity)

- **S1: "our longest document is 70,000 tokens".** No evidence was supplied for this figure. It would be settled by a token count of the largest filing in the corpus, measured with each vendor's tokenizer, plus the prompt and expected output length. It is comfortably under 128,000 unless documents are far larger than stated.
- **S2: "Prompt caching was not modelled because the inputs do not repeat".** A summarisation job usually sends the same system prompt or instructions with every document. If so, Alder's $0.30/M cache-read price would apply to that repeated part. The deciding fact is the size of the repeated prefix per request and how many requests run a month. A typical short prefix would barely move the totals, and it cannot close a $90 gap.

## Refuted

- **R1: arithmetic error in the table.** Recomputed:
  - Alder: 40 × 3.00 = 120.00; 4 × 15.00 = 60.00; total 180.00.
  - Birch: 40 × 1.25 = 50.00; 4 × 10.00 = 40.00; total 90.00.
  
  All correct.
- **R2: "$90 cheaper (half the cost)" is wrong.** 180 − 90 = 90, and 90 / 180 = 50%. Correct.
- **R3: prices or context windows misquoted.** All four prices and both context windows (200,000 and 128,000) match the source files exactly.

## What holds up

- The arithmetic is shown as requested and every figure reproduces.
- Each claim cites the vendor page it came from, as the request specified.
- The sources are three days old, so price staleness is unlikely.
- Dismissing retention as irrelevant is sound for public filings.

## Unverified claims

- The 70,000-token longest document (see S1).
- "Inputs do not repeat" (see S2).
- Whether the supplied source files faithfully reflect the live vendor pages. Settle this by opening each page and comparing it line by line.

## Questions for the author

1. Is there a fixed instruction prompt sent with every document? If so, how long is it?
2. Where does the 70,000-token figure come from, and which tokenizer produced it?

## Summaries

**DECISION-MAKER SUMMARY:** The comparison is arithmetically correct: Birch costs $90 a month and Alder $180, using the supplied pricing pages. Fix the retention wording (Birch also retains outputs) before this document is reused for any non-public workload. Proceeding as-is carries negligible risk for public filings.

**OWNER SUMMARY:** The cost figures check out: the cheaper provider costs half as much, about $90 a month instead of $180. One sentence understates how much data the cheaper provider keeps for 30 days; it keeps outputs as well as inputs. That does not matter for public documents but should be corrected.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "comparison.md", "status": "seen", "matters": true},
    {"item": "sources/alder-pricing.md", "status": "seen", "matters": true},
    {"item": "sources/birch-pricing.md", "status": "seen", "matters": true},
    {"item": "live vendor pricing pages", "status": "not_seen", "matters": false},
    {"item": "document length data (70,000-token claim)", "status": "not_seen", "matters": true},
    {"item": "job prompt structure (caching exclusion)", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Public filings and public pricing pages only."},
  "coverage": {
    "checked": [
      {"unit": "comparison.md", "kind": "file"},
      {"unit": "sources/alder-pricing.md", "kind": "file"},
      {"unit": "sources/birch-pricing.md", "kind": "file"},
      {"unit": "comparison.md: cost table arithmetic", "kind": "claim"},
      {"unit": "comparison.md: $90 cheaper / half the cost", "kind": "claim"},
      {"unit": "comparison.md: context windows", "kind": "claim"},
      {"unit": "comparison.md: Birch retention", "kind": "claim"},
      {"unit": "comparison.md: caching not modelled", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "live vendor pricing pages", "reason": "no tools in session"},
      {"unit": "longest document 70,000 tokens", "reason": "no supporting data supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "C",
     "location": "comparison.md: 'Birch retains inputs for 30 days for abuse monitoring [2]'",
     "scenario": "If the comparison is reused for a non-public job, a reader would believe Birch keeps only inputs, while sources/birch-pricing.md says inputs and outputs are retained for 30 days.",
     "fix": "Reword to 'Birch retains inputs and outputs for 30 days for abuse monitoring [2]'.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Compare the sentence with sources/birch-pricing.md line 4 ('inputs and outputs are retained for 30 days')."},
    {"id": "S1", "status": "needs_validation", "track": "C", "location": "comparison.md: 'our longest document is 70,000 tokens'",
     "suspicion": "The longest-document figure has no supplied evidence.",
     "unresolved_fact": "Token count of the largest filing (per vendor tokenizer) plus prompt and output length."},
    {"id": "S2", "status": "needs_validation", "track": "C", "location": "comparison.md: 'Prompt caching was not modelled because the inputs do not repeat'",
     "suspicion": "A shared instruction prompt per request would repeat and be cacheable at Alder's $0.30/M.",
     "unresolved_fact": "Size of any fixed prompt prefix and number of requests per month."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Arithmetic error in the cost table.", "evidence": "40x3.00=120, 4x15.00=60, total 180; 40x1.25=50, 4x10.00=40, total 90."},
    {"id": "R2", "candidate": "'$90 cheaper (half the cost)' is wrong.", "evidence": "180-90=90; 90/180=50%."},
    {"id": "R3", "candidate": "Prices or context windows misquoted.", "evidence": "All values match sources/alder-pricing.md and sources/birch-pricing.md exactly."}
  ]
}
```