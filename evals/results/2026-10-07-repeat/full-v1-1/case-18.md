# Redteam report: Alder vs Birch cost comparison

**Review setup:** The work was not produced in this conversation, so this is an independent review and no subagent was needed. The context asks for "Track C (claims review)", but the skill defines only Tracks A and B. I applied **Track A** (claims and analysis), which fits a sourced cost comparison. I had no tools, so all arithmetic and source checks were done by reading the provided files.

## Pass 1: Reconstruct

The work says the job costs **$180.00/month on Alder** and **$90.00/month on Birch**, using vendor list prices. It implies Birch is the better choice: half the cost, enough context window, and a retention policy that doesn't matter for public data.

For this to be correct, several things must hold:
- The 40M input and 4M output volumes are accurate.
- Both vendors would count the same text as the same number of tokens.
- List prices apply, with no tiers, minimums or discounts.
- The longest document really is 70,000 tokens.
- Caching would not materially change Alder's cost.
- Cost and context window are the only criteria that matter. The request says "compare for the summarisation job", which could include quality.

## Pass 2: Attack (Track A)

**Facts and arithmetic: these hold.**
- Alder: 40 × $3.00 = $120.00, plus 4 × $15.00 = $60.00, total $180.00. Correct.
- Birch: 40 × $1.25 = $50.00, plus 4 × $10.00 = $40.00, total $90.00. Correct.
- The difference is $90.00, which is exactly half. Correct.
- Every price and context window matches the source files exactly.
- One mismatch: the retention claim is narrower than the source (see finding 1).

**Logic.** The conclusion follows from the premises. "Both fit" holds because 70k tokens plus prompt and output is well under 128k.

**Load-bearing assumptions.** I checked each one to see whether it could reverse the conclusion:
- **Tokenizer parity.** Birch would need to count roughly 2× as many tokens as Alder to lose the cost lead. That is implausible for public-filing text.
- **Caching.** Even if all 40M Alder inputs were cache reads at $0.30/M, Alder would cost $12 + $60 = $72 and beat Birch. That ceiling is unrealistic because each document is unique. A shared instruction prefix of about 10% of inputs saves only about $10.80, leaving Alder at about $169.
- **Retention.** The work's reasoning (public filings, so retention is harmless) holds.

**Counter-case.** The strongest argument for Alder is that it summarises filings better, or that its larger window leaves headroom if documents grow. The work does not address quality at all. The request leans toward a cost comparison ("use the pricing pages… show the arithmetic"), so this is a scope note rather than a defect.

**Pre-mortem.** The three most likely reasons this decision fails:
1. Birch's summaries turn out worse, and nobody evaluated quality.
2. Real volumes or document lengths are larger than stated. For example, a 150k-token filing would not fit Birch's window.
3. Pricing changes or tiers that are not on the page.

None of these makes the arithmetic wrong.

## Pass 3: Self-check

- I dropped a possible finding about "missing volume discounts". The sources show none, so it cannot be tied to a location.
- I downgraded tokenizer parity to Low because it cannot reverse the result.
- The most serious issue that could still be missed is the unsourced 70,000-token figure. If that figure is wrong, the context-window claim fails, and the evidence for it lives outside the provided files.

---

**VERDICT: SHIP.** The arithmetic and every sourced figure check out. No finding reverses or materially changes the conclusion that Birch costs half as much.

**CONFIDENCE IN VERDICT: High.** It is limited by two things: the volume and document-length figures are not sourced, and I could not open the live vendor pages.

## Findings, ordered by severity

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Low | CONFIRMED | comparison.md: "Birch retains inputs for 30 days"; sources/birch-pricing.md: "inputs and outputs are retained" | Misstates the source. Birch retains outputs too. | A reader reuses this summary for a job with sensitive data and assumes generated outputs are not retained. | Change to "retains inputs and outputs for 30 days". |
| 2 | Low | UNVERIFIED | comparison.md: "our longest document is 70,000 tokens" | Load-bearing for the context-window claim, but no source is given. | A filing over about 120k tokens, after prompt and output, fails on Birch or needs chunking. | Cite the measurement (tokenizer used, sample, date), or measure the longest filing in the corpus with Birch's tokenizer. |
| 3 | Low | PROBABLE | comparison.md: "Prompt caching was not modelled because the inputs do not repeat" | Instructions and system prompt usually do repeat on every call. The Alder source lists cache reads but no cache-write price. | Alder's real cost comes in slightly below $180 (about $169 with a 10% shared prefix). Birch still wins. | Restate as "the shared prefix is small; caching would save Alder at most about $X". Note that the cache-write price is not on the page. |
| 4 | Low | PROBABLE | Table: same 40M/4M used for both vendors | Assumes both vendors' tokenizers count the same text identically. | Birch counts 15% more tokens, so it costs about $103.50. Still cheaper. | State the tokenizer used for the 40M/4M estimate, or re-count a sample with each vendor's tokenizer. |
| 5 | Low | CONFIRMED | comparison.md overall, against request "compare… for the summarisation job" | Compares only cost and context window. Summary quality and rate limits are not mentioned. | Birch is chosen on price and produces worse summaries. | Add a line scoping the comparison to cost, or run a small quality eval on sample filings. |

## What holds up

- All four multiplications, both totals, and the "$90 cheaper / half the cost" claim are correct.
- All prices and context windows are quoted accurately from the sources.
- The conclusion that both models fit a 70k-token document holds, given that figure.
- The reasoning that retention doesn't matter for public filings holds.

## Unverified claims

| Claim | How to confirm |
|---|---|
| 40M input / 4M output tokens per month | Check usage logs or the job specification. |
| Longest document is 70,000 tokens | Measure the corpus. |
| "Inputs do not repeat" | Inspect the prompt template to see how large the shared prefix is. |
| Source files reflect the live vendor pages and no tiers or minimums apply | Re-open the vendor pages, retrieved 5 Oct 2026. |

## Questions for the author

1. How was the 70,000-token maximum measured, and with which tokenizer?
2. Is the decision cost-only, or does summary quality need to be compared too?

## Decision-maker summary

The arithmetic is correct and every price is quoted accurately. Birch is $90.00/month vs Alder's $180.00, and none of the weaknesses found would flip that result. Fix the retention wording and confirm the 70k-token maximum before relying on it. If you proceed, the remaining risk is that summary quality was never compared.

```json
{
  "verdict": "SHIP",
  "findings": [
    {
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "location": "comparison.md: 'Birch retains inputs for 30 days' vs sources/birch-pricing.md: 'inputs and outputs are retained for 30 days'",
      "scenario": "Summary is reused for a sensitive-data job and readers assume generated outputs are not retained by Birch.",
      "fix": "Change wording to 'retains inputs and outputs for 30 days for abuse monitoring'."
    },
    {
      "severity": "Low",
      "evidence_level": "UNVERIFIED",
      "location": "comparison.md: 'our longest document is 70,000 tokens'",
      "scenario": "If a filing exceeds ~120k tokens after prompt and output, it will not fit Birch's 128k window and will fail or need chunking.",
      "fix": "Cite how the 70k figure was measured (tokenizer, sample, date) or measure the longest filing with Birch's tokenizer."
    },
    {
      "severity": "Low",
      "evidence_level": "PROBABLE",
      "location": "comparison.md: 'Prompt caching was not modelled because the inputs do not repeat'",
      "scenario": "A shared instruction prefix repeats on every call; caching it lowers Alder's cost somewhat (about $169 at a 10% shared prefix). Birch remains cheaper. Alder's cache-write price is not on its page.",
      "fix": "Restate as a bounded estimate of caching savings and note that the cache-write price is missing from the source."
    },
    {
      "severity": "Low",
      "evidence_level": "PROBABLE",
      "location": "comparison.md table: identical 40M/4M token volumes applied to both providers",
      "scenario": "Vendor tokenizers count the same text differently; e.g. 15% more tokens on Birch gives about $103.50, still cheaper.",
      "fix": "State the tokenizer used for the volume estimate, or re-count a sample with each vendor's tokenizer."
    },
    {
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "location": "comparison.md overall vs request 'Compare Alder and Birch for the summarisation job'",
      "scenario": "Birch is chosen on price alone and produces lower-quality summaries; quality and rate limits were never compared.",
      "fix": "Add a line scoping the comparison to cost, or run a small quality eval on sample filings."
    }
  ]
}
```
