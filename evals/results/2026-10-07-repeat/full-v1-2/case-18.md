# Redteam report: Alder vs Birch cost comparison

**Review conditions:** I did not write this work, so it is not a same-context review. I had no tools, so I could not open the live vendor pages. All checks were done by hand against the two files in `sources/`. The context asks for "Track C", which this skill does not define. I applied Track A (decisions and analysis), which is the closest fit for a claims review.

**VERDICT: SHIP WITH FIXES.** The arithmetic and the cost conclusion are correct and robust. One source is misquoted, and one load-bearing fact has no source.

**CONFIDENCE IN VERDICT: medium-high.** Every number checks out against the source files. Confidence is limited because I could not confirm the source files are complete or current excerpts of the live pricing pages.

## Pass 1: Reconstruct

The work says the job costs $180.00 a month on Alder and $90.00 on Birch, so Birch is $90.00 (50%) cheaper. It says both context windows fit the longest document, and that Birch's retention policy is irrelevant because the inputs are public. For this to be correct, these must be true:

1. The source prices are the complete price for this usage: no tiers, minimums, surcharges or discounts.
2. The volumes are 40M input and 4M output tokens a month.
3. The longest document is 70,000 tokens.
4. The inputs do not repeat, so caching does not apply.
5. Nothing sensitive goes into prompts or outputs.

## Pass 2: Attack, and what holds

**Arithmetic (CONFIRMED correct):**
- Alder: 40 × $3.00 = $120.00, plus 4 × $15.00 = $60.00, total $180.00.
- Birch: 40 × $1.25 = $50.00, plus 4 × $10.00 = $40.00, total $90.00.
- Difference: $90.00, which is half of Alder's cost.
- All unit prices match the source files exactly.

**Caching:** The work's caching exclusion does not change the answer. I worked out how much caching Alder would need to match Birch. If a fraction *f* of input is uncached, Alder's input cost is 120f + 12(1−f). For Alder to reach $90 total, that must be at most $30, which needs f ≤ 0.167. In other words, more than about 83% of input would have to be cache reads. That is implausible for distinct filings. Alder's cache-write price is also not given, which would only make Alder more expensive.

## FINDINGS

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Medium | CONFIRMED | comparison.md: "Birch retains inputs for 30 days" vs sources/birch-pricing.md: "inputs and outputs are retained for 30 days" | The source is misquoted: outputs are dropped from the retention statement. The "does not matter" reasoning only covers inputs. | A reader relies on the summary and later sends prompts that contain non-public instructions, annotations or derived analysis. They believe only the public inputs are retained, but outputs are kept for 30 days too. | Quote the source exactly ("inputs and outputs"). State that prompts and outputs contain nothing non-public, or check that this is so. |
| 2 | Medium | CONFIRMED (unsourced) | comparison.md: "our longest document is 70,000 tokens, so both fit" | This is the only basis for saying both providers are viable, and it cites no source. The fit check also ignores system prompt, instructions and output tokens. | The real longest filing is more than about 120k tokens, or the input plus output exceeds 128k. Birch then needs chunking or fails, and a cost comparison of like for like no longer holds. | Cite how the 70k figure was measured: which tokenizer and which document set. Check that max input + prompt + max output is under 128k. |
| 3 | Low | PROBABLE | comparison.md: "the inputs do not repeat" | Unsourced. A shared system prompt or instructions will repeat on every call. | There is repeated prompt overhead. As shown above, this cannot change the ranking unless more than 83% of input is cached. | Note the break-even point in one line, or drop the claim. |
| 4 | Low | UNVERIFIED | sources/*.md | The excerpts may leave out volume tiers, batch discounts, minimum spend, rate limits or regional pricing. | Birch has a monthly minimum, or Alder has a batch discount of about 50% (Alder would then be about $90). The ranking narrows or flips. | Re-check the full vendor pages for batch, tier and minimum terms. Record the URLs. |
| 5 | Low | PROBABLE | comparison.md as a whole | The request says "compare ... for the summarisation job". The work compares only cost, context window and retention. Summary quality and throughput are not addressed and are not flagged as out of scope. | Birch is chosen on cost, but its summaries are noticeably worse, so the $90 saving is outweighed by rework. | Add one line stating the scope (cost only), or run a small quality comparison on sample filings. |

## WHAT HOLDS UP

- All arithmetic is correct.
- The prices and context windows match the sources.
- The cost difference is stated correctly.
- Birch being cheaper holds up against caching, and against any plausible prompt overhead.
- The sources are dated 5 October 2026, two days ago, so they are current.

## UNVERIFIED CLAIMS

- **Longest document is 70,000 tokens:** confirm by tokenising the corpus.
- **Inputs do not repeat:** confirm by inspecting the prompt template.
- **Source excerpts are complete and accurate copies of the vendor pages:** confirm by checking the live pages and archiving them.
- **The 40M / 4M monthly volumes:** taken from the request and not independently checked.

## QUESTIONS FOR THE AUTHOR

1. How was the 70k maximum measured, and with which tokenizer?
2. Do prompts or outputs contain any non-public material?
3. Do either vendor's full pages list batch discounts, tiers or minimums?

## DECISION-MAKER SUMMARY

Birch at $90 a month against Alder at $180 is correct on the cited prices and holds up against caching. Before relying on the document, correct the retention misquote (outputs are retained too) and add a source for the 70k-token maximum. The remaining risk is unlisted pricing terms or a quality gap, neither of which the work examined.

```json
{
  "verdict": "SHIP WITH FIXES",
  "findings": [
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "comparison.md 'Birch retains inputs for 30 days' vs sources/birch-pricing.md 'inputs and outputs are retained for 30 days'",
      "scenario": "Source misquoted; outputs also retained. If prompts or outputs ever include non-public instructions or analysis, the 'does not matter' reasoning fails and the reader is misled.",
      "fix": "Quote the source exactly and confirm that prompts and outputs contain nothing non-public."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "comparison.md 'our longest document is 70,000 tokens, so both fit'",
      "scenario": "Load-bearing figure with no source; the fit check ignores prompt and output tokens. If the real maximum, or input plus output, exceeds 128k, Birch needs chunking or fails.",
      "fix": "Cite the measurement (tokenizer and corpus) and check that max input + prompt + max output < 128k."
    },
    {
      "severity": "Low",
      "evidence_level": "PROBABLE",
      "location": "comparison.md 'the inputs do not repeat'",
      "scenario": "A shared system prompt repeats on every call. Alder only matches Birch if more than ~83% of input is cache reads, so the ranking is unaffected.",
      "fix": "State the break-even point or drop the claim."
    },
    {
      "severity": "Low",
      "evidence_level": "UNVERIFIED",
      "location": "sources/alder-pricing.md, sources/birch-pricing.md",
      "scenario": "The excerpts may leave out batch discounts, tiers or minimums. For example, a ~50% Alder batch discount would bring it to about $90 and erase the gap.",
      "fix": "Check the full vendor pages for batch, tier and minimum terms and record the URLs."
    },
    {
      "severity": "Low",
      "evidence_level": "PROBABLE",
      "location": "comparison.md (scope)",
      "scenario": "Quality and throughput are not compared. Choosing Birch on cost alone could cost more in rework than it saves.",
      "fix": "Declare the scope as cost only, or run a small quality comparison on sample filings."
    }
  ]
}
```