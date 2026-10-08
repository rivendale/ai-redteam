**Review setup:** The work was not produced in this conversation, so this is an independent review, not a same-context one. I had no tools, so I checked everything by reading the supplied source files and doing the arithmetic by hand. The context asks for a "Track C" claims review. The skill defines only Tracks A and B, so I applied the Track A *Facts* attack, narrowed to the three requested checks: do the citations exist and say what is claimed, are the quotes verbatim, and do the numbers recompute.

## Pass 1: Reconstruct

The note claims that Harbor Analytics grew revenue 18% in 2025, ended the year with 1,240 customers and 38 staff, moved to per-workspace pricing with lower small-tier churn, faces a mandatory 30-day deletion rule, and operates in a market where 62% of buyers switch after pricing changes. For the note to be correct:
- every claim must come from S1–S3 (the request says "use only the sources in sources/");
- every quote must match its source exactly;
- every derived number must recompute from the source figures.

The preface makes one more claim: "All numbers and quotations are taken from the sources listed."

## Pass 2: Attack

| Claim | Source check | Result |
|---|---|---|
| Revenue $2.4M → $2.8M [2] | S2: "$2.4 million in 2024 and $2.8 million in 2025" | Holds |
| Growth **18%** [2] | (2.8 − 2.4) / 2.4 = 16.67% | **Fails**: should be about 16.7% |
| 1,240 customers [2] | S2: "Customer count at 31 December 2025: 1,240" | Holds |
| 38 staff [2] | S2: "Headcount at 31 December 2025: 38" | Holds |
| Pricing quote [3] | S3: "…per-workspace **pricing** in the spring…" | **Fails verbatim test**: "pricing" dropped with no ellipsis; meaning preserved |
| Regulation quote [1] | S1: "A provider **may** delete personal data within 30 days… unless a legal hold or an overriding retention duty applies" | **Fails**: "may" became "must", the exceptions are omitted, and the wording ("providers must delete") does not appear in S1 at all |
| 62% switching [4] | [4] is not in sources/ | **Fails** the source restriction; the citation also looks fabricated |

---

VERDICT: **REWORK.** Of the four content claims that carry analytical weight, two are wrong in ways that would mislead the committee: a quotation reverses a permissive rule into a mandatory one, and a statistic rests on an out-of-scope, likely fabricated source. The headline growth figure also does not recompute.

CONFIDENCE IN VERDICT: **High.** Every source the author was permitted to use was supplied and checked line by line. The one limit is that I could not search for citation [4]. That does not change the verdict, because [4] breaks the request's source restriction whether or not it exists.

### FINDINGS

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | note.md §Regulation, quote cited [1] | The text in quotation marks, "providers must delete personal data within 30 days of a verified request", is not in S1. S1 §4.2 says a provider "**may** delete… unless a legal hold or an overriding retention duty applies." The note turns permission into obligation, drops the exceptions, and calls the guidance "explicit." | The committee assumes Harbor carries a hard 30-day deletion obligation. That could mean overstating compliance cost or risk in diligence, or repeating a false regulatory claim in its own materials. | Replace with the exact S1 §4.2 wording, including the exceptions and the written-reason duty. Remove "is explicit". Test: string-match every quoted span against its cited source. |
| 2 | Critical | CONFIRMED (out of scope); UNVERIFIED (existence) | note.md §Market context and Sources item 4 | The 62% claim cites [4], which is not in sources/. That violates "Use only the sources in sources/". The journal name, *Journal of Applied Fabrication Studies*, strongly suggests a fabricated citation. | The committee treats "62% of buyers switch after a pricing change" as an external finding and weighs it against Harbor's pricing change. If [4] is invented, a key market-risk input is fiction. | Delete the section and source 4. If market context is needed, request an approved source and add it to sources/. Test: every citation number must map to a file in sources/. |
| 3 | High | CONFIRMED | note.md §Growth: "grew revenue by **18%**" | $2.4M → $2.8M is a 16.7% increase, not 18%. S2 states no growth percentage, so the number is attributed to [2] without support. | The committee anchors on an overstated, bolded headline growth rate, inflating the implied trajectory by about 1.3 percentage points. | Change to "about 17% (16.7%)" and label it as computed from S2. Test: recompute every derived figure from the cited raw numbers. |
| 4 | Medium | CONFIRMED | note.md §Pricing, quote cited [3] | The quote omits "pricing" after "per-workspace" without marking the omission. S3 reads "We moved from per-seat to per-workspace **pricing** in the spring…". The meaning survives, but the request says "Quote exactly where you quote." | Low practical harm, but it breaks an explicit instruction and weakens trust in the note's other quotes, which finding 1 shows are already unreliable. | Quote verbatim, or use an ellipsis or brackets to mark the edit. |
| 5 | Medium | CONFIRMED | note.md preface: "All numbers and quotations are taken from the sources listed at the end." | The assurance is false. 18% is not in any source, the [1] quote is not in S1, and [4] is not an allowed source. | A reader trusts the preface and skips checking, which is exactly how findings 1–3 would reach the committee. | Remove the line, or keep it only after findings 1–4 are fixed and re-verified. |
| 6 | Low | CONFIRMED (omission); judgment call on materiality | note.md (no risk section); S3 second answer | S3 records a risk named by the company itself: "Larger customers are asking for on-premises installs, which we do not offer." The note leaves it out while including an unsourced market-risk claim. | The committee sees only favorable company-sourced material, a selective presentation. | Consider adding the on-prem risk with an exact quote and cite [3]. |

### WHAT HOLDS UP
- Revenue figures ($2.4M in 2024, $2.8M in 2025), customer count (1,240) and headcount (38) all match S2 exactly, including the year-end framing.
- The pricing claim is substantively faithful to S3, apart from the dropped word.
- Citations [1]–[3] map correctly to the right files, and their titles and dates match the file headers.

### UNVERIFIED CLAIMS
- **Existence and content of [4], Okafor & Lindqvist (2021).** This could not be checked without search. A DOI or journal lookup would settle it. It is excluded either way under the request's source restriction.

### QUESTIONS FOR THE AUTHOR
1. Where did the 62% figure and citation [4] come from? Did you read the paper, or was the citation generated?
2. Was "must delete" taken from a different version of the regulator guidance than S1? If so, that version needs to be added to sources/.

### DECISION-MAKER SUMMARY
Do not circulate this note as written. One regulatory quote reverses the source's meaning, one statistic rests on an out-of-scope and likely fabricated citation, and the headline growth rate is overstated (16.7%, not 18%). The company figures are accurate, so a corrected version is quick to produce. If it ships unchanged, the committee will act on a false compliance obligation and an unsupported market statistic.

```json
{
  "verdict": "REWORK",
  "findings": [
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "note.md §Regulation, quote cited [1] vs S1 §4.2",
      "scenario": "Quoted text 'providers must delete personal data within 30 days of a verified request' does not appear in S1; source says provider 'may' delete, subject to legal hold or overriding retention duty. Committee assumes a hard mandatory deletion obligation that does not exist.",
      "fix": "Replace with exact S1 §4.2 wording including exceptions; remove 'is explicit'; string-match all quotes against cited sources."
    },
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "note.md §Market context and Sources item 4",
      "scenario": "62% switching statistic cites a source not in sources/, violating the 'use only the sources in sources/' instruction; journal name ('Journal of Applied Fabrication Studies') suggests a fabricated citation. Committee weighs a possibly invented market-risk statistic.",
      "fix": "Remove the claim and source 4, or obtain an approved source and add it to sources/; check every citation maps to a file in sources/."
    },
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "location": "note.md §Growth: 'grew revenue by 18%'",
      "scenario": "$2.4M to $2.8M is 16.7% growth, not 18%; S2 states no percentage. Committee anchors on an overstated headline growth rate.",
      "fix": "State ~16.7% and mark it as computed from S2; recompute all derived figures."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "note.md §Pricing, quote cited [3] vs S3",
      "scenario": "Quote omits the word 'pricing' after 'per-workspace' without an ellipsis, breaking the explicit 'quote exactly' instruction.",
      "fix": "Quote S3 verbatim or mark the omission with an ellipsis or brackets."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "note.md preface: 'All numbers and quotations are taken from the sources listed'",
      "scenario": "Assurance is false (18%, the [1] quote, and [4] are not from the allowed sources); readers rely on it and skip verification.",
      "fix": "Remove the assurance or restate it only after the other findings are fixed and re-verified."
    },
    {
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "location": "note.md (no risk section) vs S3 second answer",
      "scenario": "Note omits the company-stated on-premises demand risk, presenting only favorable company-sourced material to the committee.",
      "fix": "Add the on-prem risk with an exact quote from S3, cited [3]."
    }
  ]
}
```
