# Redteam report: Alder vs Birch cost comparison

**Review conditions:** I had no tools, so I could not open the vendor pages or files on disk. I checked the work only against the source text supplied with it. The work was not written in this conversation, so anchoring risk is low. The context asks for "Track C", which this skill does not define. I treated this as a claims review and applied Track A, which covers facts, logic and assumptions.

## Pass 1: Reconstruct

The work prices the job at 40M input and 4M output tokens a month, using each vendor's per-million rates. It finds Alder costs $180.00 and Birch costs $90.00, so Birch is $90.00 cheaper, or half the cost. It also says:
- Both context windows fit the longest document.
- Birch's 30-day retention does not matter because the inputs are public.
- Prompt caching does not apply.

These conclusions rest on four assumptions:
1. The source files faithfully reflect the vendor pages.
2. List price is the whole cost, with no tiers, batch rates, minimums or taxes.
3. The longest document is 70,000 tokens.
4. Inputs do not repeat, so caching savings are negligible.

## Verdict

**VERDICT: SHIP WITH FIXES.** The arithmetic and the cost conclusion are correct against the supplied sources. One sourced claim is misquoted and two load-bearing figures are unsourced, but none of these changes which provider is cheaper.

**CONFIDENCE IN VERDICT: High** on the arithmetic and the source matching. **Medium** overall, for two reasons: I could not check the source files against the live vendor pages, and the document size and the "no repeated input" claim are asserted without evidence.

## Findings

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Low | CONFIRMED | comparison.md: "Birch retains inputs for 30 days for abuse monitoring [2]" | The source says "inputs **and outputs** are retained for 30 days". The work drops outputs. | A reader relies on the citation to judge data handling and believes generated summaries are not retained. Impact is small here because the outputs derive from public filings, but the cited claim is inaccurate. | Change to "retains inputs and outputs for 30 days". |
| 2 | Low | UNVERIFIED | comparison.md: "our longest document is 70,000 tokens, so both fit" | No source or measurement is cited for 70,000. The fit check also ignores the system prompt and output tokens that share the window. | If some filings are longer than about 120k tokens (for example, large annual reports with exhibits), Birch's 128k window fails or forces chunking. Chunking changes both cost and quality, and Alder becomes the only single-pass option. | Cite the measurement: token count of the largest document in the corpus with the tokenizer used. State the margin after adding prompt and output tokens. |
| 3 | Low | UNVERIFIED | comparison.md: "Prompt caching was not modelled because the inputs do not repeat" | This is asserted without support. Any fixed system prompt or instructions repeat on every call. Only Alder lists a cache-read price ($0.30/M), and its cache-write price is not given. | If a large fixed preamble is sent with each document, Alder's effective input cost falls. Bounding it: Alder would need about 30M of the 40M input tokens cached to reach $90. That is implausible for distinct filings, so the ranking almost certainly holds. | State the size of the repeated prompt per call and the number of calls. Then show the caching-adjusted Alder figure or the bound above. |
| 4 | Low | UNVERIFIED | comparison.md table; both source files | Only list per-token prices are used. Batch or async discounts, volume tiers, minimums, and taxes or fees are not mentioned. The source excerpts may be partial pages. | If one vendor offers a batch discount (for example, 50%) suited to an offline summarisation job, the monthly figures change. With a 50% discount on Alder only, both come to $90 and the ranking ties. | Confirm on each live pricing page whether batch or volume pricing exists. Note the outcome even if there is none. |

## What holds up

- **Arithmetic is correct:**
  - Alder: 40 × $3.00 = $120.00, plus 4 × $15.00 = $60.00, total $180.00.
  - Birch: 40 × $1.25 = $50.00, plus 4 × $10.00 = $40.00, total $90.00.
  - The difference is $90.00, and "half the cost" is exact.
- **Rates match the sources:** every rate and context-window figure matches the supplied source files.
- **Sources are fresh:** they were retrieved 5 Oct 2026, two days before this review.
- **Retention reasoning is sound in substance:** retention matters little for public filings.
- **No drift from the request:** the work answers the question asked, compares the two named vendors, uses the stated volumes, and shows the arithmetic.

## Unverified claims

- **Source files reflect the live vendor pages.** Confirm by opening both pages and comparing them line by line.
- **Longest document is 70,000 tokens.** Confirm by tokenizing the corpus and reporting the maximum.
- **Inputs do not repeat.** Confirm by inspecting the request template and reporting the fixed prompt size times the number of calls.
- **No batch, tier or minimum pricing applies.** Confirm on the vendor pages.

## Questions for the author

1. Is there a batch or volume discount on either vendor's page? This is the only finding that could plausibly narrow or tie the ranking.
2. Where does the 70,000-token maximum come from, and is it measured with each vendor's tokenizer?

## Decision-maker summary

On the supplied sources, Birch is correctly costed at $90.00 a month against $180.00 for Alder. Correct the retention wording and cite the document-size figure before relying on the comparison. The remaining risk is a batch or volume discount not captured in the source excerpts, which could narrow the gap.

```json
{
  "verdict": "SHIP WITH FIXES",
  "findings": [
    {
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "location": "comparison.md: \"Birch retains inputs for 30 days for abuse monitoring [2]\"",
      "scenario": "Source [2] says inputs and outputs are retained for 30 days; the work omits outputs, so a reader relying on the citation misjudges what Birch retains.",
      "fix": "Reword to 'retains inputs and outputs for 30 days', matching sources/birch-pricing.md."
    },
    {
      "severity": "Low",
      "evidence_level": "UNVERIFIED",
      "location": "comparison.md: \"our longest document is 70,000 tokens, so both fit\"",
      "scenario": "The figure is unsourced and the check ignores prompt and output tokens; filings longer than about 120k tokens would not fit Birch's 128k window, forcing chunking or making Alder the only single-pass option.",
      "fix": "Cite a measured maximum token count from the corpus with the tokenizer used, and show the margin after adding prompt and output tokens."
    },
    {
      "severity": "Low",
      "evidence_level": "UNVERIFIED",
      "location": "comparison.md: \"Prompt caching was not modelled because the inputs do not repeat\"",
      "scenario": "Fixed system prompts repeat on every call; Alder lists $0.30/M cache reads, which lowers its effective cost. About 30M of 40M input tokens would need to be cached to reach parity, so the ranking very likely holds, but the claim is unsupported.",
      "fix": "State the repeated prompt size and call count, then show the caching-adjusted Alder cost or the parity bound."
    },
    {
      "severity": "Low",
      "evidence_level": "UNVERIFIED",
      "location": "comparison.md cost table; sources/alder-pricing.md; sources/birch-pricing.md",
      "scenario": "Only list prices are used; a batch or volume discount on either vendor (for example, 50% off Alder) would change totals and could tie the ranking at $90.",
      "fix": "Check both live pricing pages for batch, tier, minimum or fee terms and record the result in the comparison."
    }
  ]
}
```