# Redteam report: Harbor Analytics market note

**Review setup:** The note was not produced in this conversation, so there is no shared-context anchoring. No tools were available, so every check below is a manual comparison of the note against the text of S1–S3. Arithmetic was done by hand.

## Pass 1: Reconstruct

The note makes four claims to the investment committee:

- Harbor grew revenue 18% in 2025, from $2.4M to $2.8M, with 1,240 customers and 38 staff.
- Harbor switched to per-workspace pricing and smallest-tier churn fell.
- Regulation *requires* deletion of personal data within 30 days.
- 62% of mid-size buyers switch vendors after a pricing change.

It also asserts that "all numbers and quotations are taken from the sources listed."

For the note to be correct, four things must hold:

- Every figure and quote must trace verbatim to S1–S3.
- The derived growth rate must recompute.
- The regulator text must say "must."
- Source [4] must be one of the permitted sources and must exist.

## Pass 2: Attack

VERDICT: **REWORK**. One quotation reverses the meaning of its source, the headline growth figure does not recompute, and one claim relies on a source outside the permitted set that may not exist.

CONFIDENCE IN VERDICT: **high**. Every finding below except the existence of [4] is a direct text-to-text comparison. Confidence is limited only by the lack of tools to search for the Okafor & Lindqvist paper.

### Findings

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | Regulation: "providers must delete personal data within 30 days of a verified request" [1] | The quote is not in S1. S1 §4.2 says a provider "**may** delete personal data within 30 days of a verified request, unless a legal hold or an overriding retention duty applies." The note turns a permission into an obligation, puts that wording in quotation marks, and drops the exceptions. | The committee treats a 30-day deletion mandate as a compliance cost or risk for Harbor. That obligation does not exist in the cited guidance, so any compliance or valuation reasoning built on it is wrong. | Quote S1 §4.2 verbatim, including "may" and the legal-hold exception. Recheck any conclusion drawn from this section. |
| 2 | High | CONFIRMED | Growth: "grew revenue by **18%** in 2025, from $2.4 million to $2.8 million [2]" | (2.8 − 2.4) / 2.4 = 16.7%, not 18%. S2 states no percentage, so the 18% is derived, and derived wrongly. It is the bolded headline number. | The committee anchors on a growth rate about 1.3 points too high. That overstates momentum in any multiple or projection built on it. | State ~16.7% (or "about 17%") and label it as computed from S2. Recompute every derived figure. |
| 3 | Critical | CONFIRMED (not in sources/); PROBABLE (fabricated) | Market context: "62% of mid-size analytics buyers switch vendors…" [4]; Sources item 4 | The request says to "use only the sources in sources/." Source [4] is not in sources/, which the context confirms, so the claim breaks the brief whatever its accuracy. The citation also looks fabricated: "Journal of Applied Fabrication Studies" is not a plausible venue for software-pricing research. | The committee relies on a 62% switching statistic that may not exist. It is the only claim that links Harbor's pricing change to churn risk, so it can drive the investment thesis. | Remove the claim. If it matters, obtain the paper, confirm the journal, volume, pages, and the 62% figure, add it to sources/, and get permission to expand the source set. |
| 4 | Medium | CONFIRMED | Pricing: "moved from per-seat to per-workspace in the spring, and churn in the smallest tier fell" [3] | This is not verbatim. S3 reads "We moved from per-seat to per-workspace **pricing** in the spring…". The word "pricing" was removed from inside the quotation marks with no ellipsis. The meaning is preserved, but the brief said "quote exactly." | A reader checking quotes against the interview finds a mismatch. That undermines trust in every other quote in the note, which finding 1 shows is justified. | Quote exactly ("We moved from per-seat to per-workspace pricing in the spring…"), or use an ellipsis or square brackets for edits. |
| 5 | Medium | CONFIRMED | Header: "All numbers and quotations are taken from the sources listed at the end." | This assurance is false. The 18% is not in any source, two quotations are altered (findings 1 and 4), and one number comes from an unpermitted source (finding 3). | The committee skips verification because the note certifies its own sourcing. | Remove the line, or make it true and then keep it. |
| 6 | Low | CONFIRMED | Whole note vs. S3 | The only risk management named in S3, "Larger customers are asking for on-premises installs, which we do not offer," is omitted. The note presents only positives from that interview. | The committee gets a one-sided picture of a product gap that management itself flagged as the biggest risk. | Add the on-premises risk with an exact quote from S3. |

## What holds up

- $2.4M (2024) and $2.8M (2025) revenue match S2.
- 1,240 customers and 38 headcount at 31 December 2025 match S2.
- Source entries 1–3 match their files: titles, the 2025 edition, and the 14 March 2026 interview date.
- The citation numbers attached to S1–S3 claims point to the right files.

## Unverified claims

- **Existence and content of Okafor & Lindqvist (2021), J. Appl. Fabrication Stud. 14(3):220–241, and its 62% figure.** To confirm: search the journal, check the DOI or publisher listing, and read the paper's results section.
- **Timing of the pricing change.** S3 says "last year" in a March 2026 interview, which implies spring 2025. The note's "in the spring" is consistent but unanchored. To confirm: ask Harbor for the effective date.

## Questions for the author

1. Where did "must delete" come from? Was there a different version of S1?
2. Where did the 18% come from? Is it a computation error or a figure from another document?
3. Where did you obtain source [4]? Did you read it, and why was it used despite the sources/-only constraint?

## Decision-maker summary

Do not circulate this note. It misquotes the regulator (turning "may" into "must"), overstates growth (16.7%, not 18%), and relies on an out-of-scope, possibly fabricated study for its only market-risk claim. The revenue, customer, and headcount figures are accurate. If the note is used as is, the committee's compliance and growth assumptions will rest on statements the sources do not support.

```json
{
  "verdict": "REWORK",
  "findings": [
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "Regulation section, quote attributed to [1]",
      "scenario": "S1 §4.2 says a provider 'may' delete within 30 days, subject to legal hold or retention duty; the note quotes 'must delete', fabricating a mandatory obligation and dropping the exceptions, so the committee prices in a compliance duty that does not exist.",
      "fix": "Quote S1 §4.2 verbatim including 'may' and the legal-hold exception; recheck any conclusion based on it."
    },
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "Market context section and Sources item 4 (Okafor and Lindqvist 2021)",
      "scenario": "Source [4] is not in sources/, violating 'use only the sources in sources/'; the venue 'Journal of Applied Fabrication Studies' suggests fabrication (PROBABLE); the committee may rely on a nonexistent 62% switching statistic.",
      "fix": "Remove the claim, or obtain and verify the paper, add it to sources/, and get approval to expand the source set."
    },
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "location": "Growth section: 'grew revenue by 18%'",
      "scenario": "(2.8-2.4)/2.4 = 16.7%, not 18%; S2 gives no percentage; the committee anchors on an overstated growth rate.",
      "fix": "State ~16.7% and label it as computed from S2; recompute all derived figures."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "Pricing section, quote attributed to [3]",
      "scenario": "S3 reads 'per-workspace pricing in the spring'; the note silently drops 'pricing' inside quotation marks, breaching 'quote exactly' and undermining trust in the quotes.",
      "fix": "Quote verbatim or mark edits with an ellipsis or brackets."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "Header: 'All numbers and quotations are taken from the sources listed at the end.'",
      "scenario": "The assurance is false (derived 18%, two altered quotes, out-of-scope source), so the committee may skip verification.",
      "fix": "Remove the line, or correct the note so that it is true."
    },
    {
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "location": "Whole note vs S3 (on-premises risk answer)",
      "scenario": "Management's stated biggest risk (no on-premises offering) is omitted, giving the committee a one-sided view.",
      "fix": "Add the on-premises risk with an exact quote from S3."
    }
  ]
}
```