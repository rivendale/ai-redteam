# Provider cost comparison for the summarisation job

The job reads 40 million input tokens and writes 4 million output tokens per month.

| provider | input cost | output cost | total per month |
|---|---|---|---|
| Alder | 40 x $3.00 = $120.00 | 4 x $15.00 = $60.00 | **$180.00** |
| Birch | 40 x $1.25 = $50.00 | 4 x $10.00 = $40.00 | **$90.00** |

Prices are from each provider's pricing page [1][2]. Birch is $90.00 a month cheaper (half the cost). Alder's context window is
200,000 tokens and Birch's is 128,000 tokens [1][2]; our longest document is 70,000 tokens, so both fit. Birch retains inputs for
30 days for abuse monitoring [2]; this job uses public filings only, so that does not matter here.

Sources: [1] sources/alder-pricing.md, [2] sources/birch-pricing.md. Prompt caching was not modelled because the inputs do not repeat.
