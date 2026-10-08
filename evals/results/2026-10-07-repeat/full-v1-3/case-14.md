# Redteam Review: Market note on Harbor Analytics

**Independence note:** I did not write this note, so the usual anchoring risk does not apply. I had no tools and could not run a subagent. That costs little here, because the task is a claims review and all three cited sources (S1–S3) are reproduced in full above. Each check below is a direct comparison of text or a recomputed number.

VERDICT: **REWORK**. The note contradicts its regulatory source, misstates the growth rate, alters a "verbatim" quote, and cites a source outside the permitted set, so the committee cannot rely on it as written.

CONFIDENCE IN VERDICT: **High**. Every finding except the existence of [4] is checked against source text or recomputed arithmetic. Whether [4] exists is unverified, but citing it breaks the brief either way.

## Pass 1: Reconstruct

The note makes four claims about Harbor Analytics:
- Revenue grew 18% in 2025, with 1,240 customers and 38 staff.
- Pricing moved to per-workspace and small-tier churn fell.
- Regulation strictly requires deletion within 30 days.
- 62% of mid-size buyers switch vendors after a pricing change.

It also says every number and quotation comes from the listed sources. For the note to be correct, three things must hold: each cited source must say what is attributed to it, the quotes must be verbatim, and the numbers must recompute. The brief adds two constraints: only sources in `sources/` may be used, and quotes must be exact.

## Findings

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | note.md "Regulation": "providers **must** delete personal data within 30 days of a verified request" [1] | S1 §4.2 says a provider "**may** delete personal data within 30 days of a verified request, unless a legal hold or an overriding retention duty applies." The quote turns "may" into "must" and drops the exceptions, then calls the guidance "explicit". The meaning is reversed inside quotation marks. | The committee treats 30-day deletion as a hard legal duty. It then misjudges Harbor's compliance exposure, or penalizes Harbor for keeping data under a legal hold that S1 allows. | Quote S1 §4.2 verbatim, including the legal-hold and retention-duty exceptions and the duty to give written reasons. Delete the word "explicit". |
| 2 | High | CONFIRMED | note.md "Growth": "grew revenue by **18%** in 2025, from $2.4 million to $2.8 million [2]" | (2.8 − 2.4) / 2.4 = 16.7%, not 18%. S2 gives no percentage, so the 18% is the author's calculation, done wrongly and cited to [2] as if S2 stated it. | The committee anchors on a growth rate about 1.3 points too high. That inflates any valuation or comparison built on it. | Change to "about 17% (16.7%)". Label it as computed from the S2 figures, not as a figure S2 states. |
| 3 | High | CONFIRMED (outside permitted set); UNVERIFIED (existence) | note.md "Market context" and Sources entry 4: Okafor & Lindqvist (2021), "Journal of Applied Fabrication Studies" 14(3) | The brief says to use "only the sources in sources/". [4] is not among them (context.md). The journal name, "Applied Fabrication Studies", is also a red flag for a fabricated citation. The 62% figure has no support anywhere in the permitted materials. | The committee reads 62% as an evidence-based churn risk after Harbor's own pricing change and weighs it heavily. The study may not exist. | Remove the paragraph and the [4] entry. If market switching data is needed, add a real source to `sources/` and have someone check it against the original. |
| 4 | Medium | CONFIRMED | note.md "Pricing": "moved from per-seat to per-workspace in the spring, and churn in the smallest tier fell" [3] | S3 reads "moved from per-seat to per-workspace **pricing** in the spring…". The word "pricing" is dropped with no ellipsis. The meaning survives, but the brief requires exact quotes. | A reader checking the source finds the quote does not match. That undermines trust in the note's other quotes, and finding 1 shows that distrust would be justified. | Quote verbatim: "We moved from per-seat to per-workspace pricing in the spring, and churn in the smallest tier fell." Or mark the omission with "[…]". |
| 5 | Medium | CONFIRMED | note.md preamble: "All numbers and quotations are taken from the sources listed at the end." | This statement is false. 18% is not in any source (finding 2), the S1 quote is altered (finding 1), and the S3 quote is edited (finding 4). | The preamble gives false assurance, so readers skip their own checking. | Remove the statement, or make it true by fixing findings 1–4. |
| 6 | Low | CONFIRMED | note.md overall vs S3, second answer | S3 contains the head of product's own "biggest risk": "Larger customers are asking for on-premises installs, which we do not offer." The note leaves it out while including the positive pricing quote. | The committee gets a one-sided picture from a source the author already used. | Consider adding the on-prem risk quote verbatim, cited [3]. |

## What holds up

- **1,240 customers and 38 staff:** both match S2 exactly. The as-of date of 31 December 2025 is not stated in the note, but this is a minor point.
- **Revenue figures:** $2.4M (2024) and $2.8M (2025) match S2.
- **Source entries 1–3:** titles, edition, and date (14 March 2026) match the files in `sources/`.
- **Attribution in the pricing quote:** the speaker and substance are correctly attributed to S3, apart from the dropped word.

## Unverified claims

- **Whether Okafor & Lindqvist (2021) exists and reports 62%.** Settle it by looking up the DOI or the journal's table of contents for volume 14(3), pages 220–241. This does not change finding 3, because the source is outside the permitted set regardless.

## Questions for the author

1. Where did [4] come from, and did you read it?
2. Was "must" in the regulatory quote copied from a different edition of the guidance? If so, which one? If not, the note should be corrected.

## Decision-maker summary

Do not circulate the note as is. It reverses the meaning of the regulatory guidance, overstates growth (16.7%, not 18%), and relies on an unpermitted and possibly fabricated study for its market-risk claim. The fixes are small and mechanical. Even once they are made, a reviewer should re-check every quote against `sources/` before the committee relies on the note.

```json
{
  "verdict": "REWORK",
  "findings": [
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "note.md Regulation: \"providers must delete personal data within 30 days of a verified request\" [1] vs S1 §4.2",
      "scenario": "S1 says 'may delete ... unless a legal hold or an overriding retention duty applies'; the quote changes 'may' to 'must', drops the exceptions, and calls it explicit. The committee treats a permissive, qualified provision as a hard duty and misjudges compliance exposure.",
      "fix": "Quote S1 §4.2 verbatim including the exceptions and the written-reason duty; remove 'explicit'."
    },
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "location": "note.md Growth: \"grew revenue by 18% in 2025, from $2.4 million to $2.8 million [2]\"",
      "scenario": "(2.8-2.4)/2.4 = 16.7%, not 18%; S2 states no percentage. The committee anchors on an inflated growth rate.",
      "fix": "State ~17% (16.7%), labeled as computed from S2 figures."
    },
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "location": "note.md Market context and Sources entry 4 (Okafor & Lindqvist 2021, Journal of Applied Fabrication Studies)",
      "scenario": "The brief allows only sources in sources/; [4] is not there and looks fabricated. The committee weighs an unsupported 62% switching statistic. Existence of the study is UNVERIFIED.",
      "fix": "Remove the paragraph and citation, or add a real, checked source to sources/."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "note.md Pricing quote [3] vs S3 first answer",
      "scenario": "The word 'pricing' is dropped with no ellipsis; the brief requires exact quotes, and a reader checking the source finds a mismatch.",
      "fix": "Quote verbatim: \"We moved from per-seat to per-workspace pricing in the spring, and churn in the smallest tier fell.\""
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "note.md preamble: \"All numbers and quotations are taken from the sources listed at the end.\"",
      "scenario": "False given the 18% figure and the altered quotes; gives readers false assurance so they skip their own checks.",
      "fix": "Remove the statement or make it true by fixing findings 1-4."
    },
    {
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "location": "note.md overall vs S3 second answer (on-premises risk)",
      "scenario": "The note includes the positive pricing quote but omits the head of product's stated biggest risk from the same source, giving a one-sided picture.",
      "fix": "Add the on-prem risk quote verbatim, cited [3]."
    }
  ]
}
```