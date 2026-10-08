> **Review setup:** This is a single-context review. I could not hand it to a fresh subagent, and I had no tools. I checked every claim against the source text supplied inline, as if those were the files in `sources/`. I did the arithmetic by hand.

**VERDICT: SHIP WITH FIXES.** Every citation exists and supports its claim, both quotes match the source words exactly, and the numbers recompute. Four small fixes would stop an investment committee from reading more into the note than the sources support.

**CONFIDENCE IN VERDICT: High.** The sources are short and the claims are few. Two things limit it: I checked the sources only as provided inline, not as files on disk, and nothing confirms the sources themselves are authentic.

## Pass 1: Reconstruct

The note says Harbor Analytics grew revenue 16.7% in 2025, from $2.4M to $2.8M. It says the company ended the year with 1,240 customers and 38 staff, about 33 customers per employee. It quotes the head of product saying churn fell after a pricing change, and quotes regulator guidance on deletion and breach notice.

For the note to be correct, four things must hold:
- Each cited source contains the claim.
- Each quote matches the source exactly.
- The derived figures (16.7%, about 33) follow from the source figures.
- The way the note frames each source does not overstate it.

An unstated assumption is that the rounded revenue figures support a growth rate to one decimal place.

## Claim-by-claim check

| Claim | Source | Result |
|---|---|---|
| $2.4M (2024) → $2.8M (2025) | S2 line 1 | Matches |
| 16.7% growth | (2.8−2.4)/2.4 = 0.1667 | Recomputes |
| 1,240 customers | S2 line 2 | Matches |
| 38 staff | S2 line 3 | Matches |
| About 33 customers per employee | 1,240/38 = 32.6 | Recomputes |
| Pricing quote | S3, first answer | Same words, character for character |
| Deletion quote | S1 §4.2 | Same words; the source's bold on "**may**" is dropped |
| "within 72 hours" | S1 §4.3 | Fragment matches; the trigger condition is omitted |

## Findings

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Medium | CONFIRMED | Growth: "grew revenue by **16.7%**" | The growth rate is more precise than the inputs. S2 gives revenue rounded to $0.1M. Inputs anywhere in $2.35–2.45M and $2.75–2.85M give growth between about 12.2% and 21.3%. The bold makes the number look exact. | The committee compares 16.7% against a 15% hurdle or a peer's 17% and draws a conclusion the data cannot support. | Write "about 17% (from rounded figures of $2.4M and $2.8M)". Alternatively, get unrounded revenue before stating a decimal. |
| 2 | Medium | CONFIRMED | Pricing section; S3, second answer | The note leaves out the only risk statement in the sources: "Larger customers are asking for on-premises installs, which we do not offer." It keeps the positive quote from the same interview. | The committee sees only the favourable half of the interview and misses a stated limit on growth in larger accounts. | Add the on-premises quote with citation [3], or say why it was left out. |
| 3 | Low | CONFIRMED | Regulation: "requires breach notice to the regulator 'within 72 hours'" | The note drops what starts the clock and what the rule covers. S1 says "within 72 hours of becoming aware of a breach affecting personal data." | A reader assumes the 72 hours runs from the breach itself, or applies to any breach. That gives a wrong view of compliance exposure. | Quote the full phrase "within 72 hours of becoming aware of a breach affecting personal data". |
| 4 | Low | CONFIRMED | Regulation, deletion quote; Sources item 1 | The bold on "**may**" in S1 is dropped without a note. The note also says "The regulator's guidance says" when S1 is a regulator *summary*. | The source stresses that deletion is permissive, and that stress is lost. A reader may also treat a summary as the binding text. | Keep the emphasis or add "(emphasis in original)". Write "the regulator's summary of its guidance says". |
| 5 | Low | CONFIRMED | Pricing: "in the spring" | The interview took place on 14 March 2026 and the question was about "last year", so "the spring" means spring 2025. The note drops "last year", so a reader could take it as spring 2026. | The committee places the pricing change in the wrong year relative to the 2025 results. | Write "in spring 2025 (per interview, 14 March 2026)". |
| 6 | Low | CONFIRMED | Opening: "All numbers and quotations are taken from the sources" | 16.7% and "about 33" are calculated by the author, not taken from the sources. | The committee assumes the derived ratios are company-reported. | Write "All figures are from or calculated from the sources listed at the end". |

## What holds up

- Every citation points to a source that exists in the set, and each source says what it is cited for.
- Both full quotes match the source words exactly.
- Both calculations are arithmetically correct.
- The note flags that the churn claim is "one interview, not a measurement of churn". That is the right caveat.
- It correctly keeps "may" in the deletion clause and does not turn it into an obligation.
- It brings in no outside facts, which fits "use only the sources".

## Unverified claims

- **The sources are authentic and complete.** S2 is labelled an "extract". To confirm, compare it with the full 2025 annual report.
- **The files on disk match what I reviewed.** I checked the inline copies only. To confirm, diff `work/sources/*` against the text in this review.
- **The 2025 edition of the regulator summary is still current** as of October 2026. To confirm, check the regulator's site for a later edition.

## Questions for the author

1. Is unrounded 2024 and 2025 revenue available?
2. Was the on-premises risk left out on purpose, and if so, why?

## Decision-maker summary

The note is accurate to its sources, and none of its quotes or numbers is fabricated. Before circulating it, soften the 16.7% to "about 17%", add the on-premises risk the interview raised, and restore the 72-hour trigger condition. If it goes out unchanged, the main risk is that the committee treats a rounded growth rate as precise and does not see a disclosed constraint on growth.

```json
{
  "verdict": "SHIP WITH FIXES",
  "findings": [
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "note.md Growth: \"grew revenue by **16.7%**\"",
      "scenario": "Revenue figures in S2 are rounded to $0.1M; true growth could be ~12.2%-21.3%, so the committee may compare a falsely precise 16.7% against hurdles or peers.",
      "fix": "State 'about 17% (from rounded figures)' or obtain unrounded revenue before quoting a decimal."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "note.md Pricing section vs S3 second answer",
      "scenario": "The note quotes the positive pricing answer but omits the same interview's only risk statement (on-prem demand not offered), so the committee sees a one-sided picture.",
      "fix": "Add the on-premises quote with citation [3] or state why it was excluded."
    },
    {
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "location": "note.md Regulation: \"requires breach notice to the regulator 'within 72 hours'\"",
      "scenario": "Omitting 'of becoming aware of a breach affecting personal data' lets a reader assume the clock starts at the breach or applies to all breaches.",
      "fix": "Quote the full phrase from S1 section 4.3."
    },
    {
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "location": "note.md Regulation deletion quote; Sources item 1",
      "scenario": "Source emphasis on 'may' is dropped without a note, and a regulator summary is described as 'the regulator's guidance', so a reader may treat a summary as binding text.",
      "fix": "Keep the emphasis or mark 'emphasis in original'; say 'the regulator's summary of its guidance'."
    },
    {
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "location": "note.md Pricing: \"in the spring\"",
      "scenario": "The interview was on 14 March 2026 about 'last year'; without a year, readers may place the change in spring 2026.",
      "fix": "Write 'in spring 2025'."
    },
    {
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "location": "note.md opening: \"All numbers and quotations are taken from the sources\"",
      "scenario": "16.7% and ~33 customers per employee are calculated by the author, and readers may take them as company-reported.",
      "fix": "Write 'All figures are from or calculated from the sources'."
    }
  ]
}
```