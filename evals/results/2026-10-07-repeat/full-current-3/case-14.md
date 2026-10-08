# Redteam review: Harbor Analytics market note

**VERDICT: REWORK.** The note misquotes the regulator, turning "may" into "must" and dropping the stated exceptions, and its headline growth figure does not match its own numbers. It also relies on a source outside the permitted set.

**CONFIDENCE: high** on the findings, because all three permitted sources were supplied in full and every claim could be checked by hand. Three things limit it:
- I had no tools, so I could not check whether source [4] exists.
- No fresh subagent was available, so this is my own review rather than an independent one. The work was not written in this conversation, which reduces the anchoring risk, but for anything high-stakes it should be re-run in a fresh session.
- S1 is a "regulator summary", not the full guidance. That does not change the quote finding, because the note cites this document.

**INPUTS LEDGER:**

| Item | Status | Matters? |
|---|---|---|
| request.md | seen | yes |
| context.md | seen | yes |
| note.md | seen | yes |
| S1-regulator-guidance.md | seen | yes |
| S2-annual-report.md | seen | yes |
| S3-interview-notes.md | seen | yes |
| Source [4], Okafor & Lindqvist (2021) | not supplied, not openable | Yes. The 62% claim rests entirely on it, and the request forbids sources outside sources/. |
| Full regulator guidance, beyond the summary | not supplied | Low. The note quotes the summary, and the summary says "may". |

**SEATS AND GATE:** I reviewed it myself, with no subagent and no tools. No cross-vendor seats were used; none were requested and this was a standard-depth review. Sensitivity gate: no personal data, credentials or confidential client material found; the sources are a public-style summary, a report extract and interview notes. The work contains no text addressed to the reviewer.

## Findings, ordered by severity

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | C | note.md, "Regulation"; S1 §4.2 | The quote "providers must delete personal data within 30 days of a verified request" is not in S1. S1 says: "A provider **may** delete personal data within 30 days of a verified request, unless a legal hold or an overriding retention duty applies." The note changes "may" to "must", changes "A provider" to "providers", drops the exception clause, and calls it "explicit". | The committee believes a hard 30-day deletion duty exists. It then misjudges Harbor's compliance burden or risk, or repeats a false regulatory claim in its own materials. The actual guidance is permissive and has exceptions. | Quote S1 §4.2 verbatim, including the "unless…" clause. Rewrite the framing: the guidance permits deletion within 30 days, and a refusal must be explained in writing. | Confirmed. A defender could argue the full guidance says "must" elsewhere, but the note attributes the quote to this summary, and the summary says "may". |
| 2 | High | CONFIRMED | C | note.md, "Growth", "grew revenue by **18%**" | $2.4M to $2.8M is (2.8 − 2.4) / 2.4 = 16.7%, not 18%. S2 states no growth percentage, so the figure is derived, and it is derived wrongly. | The committee anchors on a growth rate that overstates the source by about 1.3 points, roughly 8% relative, and carries it into valuation or comparisons. | Write "about 17% (16.7%)", or ask the company for unrounded revenue if precision matters. | Confirmed. A defender could note that unrounded revenue might give 18%, but those figures are not in S2. From the note's own inputs, the number does not reproduce. |
| 3 | High | CONFIRMED (out of scope) / UNVERIFIED (existence) | C, A | note.md, "Market context"; Sources item 4 | The request says "Use only the sources in sources/". Source [4] is not in sources/, which context.md confirms, so the 62% claim breaks the instruction. Separately, the journal title ("Journal of Applied Fabrication Studies") is not one I can confirm, so the citation may not exist. | The committee treats 62% as evidence that customers churn after pricing changes. That bears directly on the per-workspace pricing change described in the Pricing section, and the figure is unsupported and possibly invented. | Remove the paragraph. Or, if the author wants it, obtain the paper, confirm the 62% figure at a page, add it to sources/, and get approval to widen the source set. Checking the DOI or the journal's table of contents for vol. 14(3), pp. 220–241 would settle whether it exists. | Confirmed as a request violation. Its existence stays UNVERIFIED. |
| 4 | Medium | CONFIRMED | C | note.md, "Pricing" | The quote is not verbatim. S3 says "We moved from per-seat to per-workspace **pricing** in the spring…", and the note's quote drops "pricing" with no ellipsis. Dropping the leading "We" is acceptable for a fragment; removing a word inside the quote is not. The meaning is preserved. | It breaks the explicit "Quote exactly" instruction and weakens trust in the note's other quotes. | Quote it exactly: "moved from per-seat to per-workspace pricing in the spring, and churn in the smallest tier fell". | n/a (Medium) |
| 5 | Low | CONFIRMED | C | note.md, line 3, "All numbers and quotations are taken from the sources listed" | This blanket assurance is false. The 18% figure is not in any source, and two of the quotations were altered. | A reader skips checking because of the assurance. | Remove the line, or make it true after fixing findings 1 to 4. | n/a |
| 6 | Low | PROBABLE | A | note.md, overall; S3 second answer | The note leaves out the interviewee's own stated "biggest risk": larger customers want on-premises installs, which Harbor does not offer. The note includes only positive material from S3. | The committee gets a one-sided picture. | Add one cited sentence on the on-premises gap. | n/a |

## What holds up

These claims match S2 exactly, with correct periods:
- Revenue was $2.4M in 2024 and $2.8M in 2025.
- Harbor had 1,240 customers at 31 Dec 2025.
- Headcount was 38 at 31 Dec 2025.

The citations [1] to [3] point to files that exist, and their titles and dates match them. The interview date (14 March 2026) and the "spring" timing are consistent with the question "last year". The note correctly leaves out S1 §4.3 on breach notice, which is not relevant.

## Unverified claims

- **Source [4] and the 62% figure.** Settle it by retrieving the article and checking the figure at a page number. Before that, check whether the journal and the volume/issue exist at all.
- **What the 18% figure was meant to be.** If the author used unrounded figures, they would need to be supplied and added to sources/.

## Questions for the author

1. Where did 18% come from? Is there an unrounded revenue figure we don't have?
2. Where did you get source [4], have you read it, and was it allowed despite the "only sources/" instruction?
3. Was the "must" wording taken from another version of the guidance? If so, which one?

## Decision-maker summary

Do not circulate the note as written. It misstates the regulator's deletion rule as mandatory, overstates revenue growth (16.7% vs 18%), and relies on an outside study that may not exist. All three can be fixed in under an hour from the supplied sources. If it goes out as is, the committee would be deciding on a false regulatory premise and an unsupported churn statistic.

## Owner summary

The note needs corrections before the committee sees it. One quotation changes what the regulator actually says, the growth figure is slightly too high, and one statistic comes from a study outside the approved sources that we could not confirm exists. The other figures check out against the company's report.

```json
{
  "verdict": "REWORK",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "sources/S1-regulator-guidance.md", "status": "seen", "matters": true},
    {"item": "sources/S2-annual-report.md", "status": "seen", "matters": true},
    {"item": "sources/S3-interview-notes.md", "status": "seen", "matters": true},
    {"item": "Source [4] Okafor & Lindqvist (2021)", "status": "not_seen", "matters": true},
    {"item": "Full regulator guidance (beyond summary)", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "C", "location": "note.md 'Regulation'; S1 §4.2",
     "scenario": "Quote changes 'may' to 'must' and drops the legal-hold/retention exception; committee believes a mandatory 30-day deletion duty exists.",
     "fix": "Quote S1 §4.2 verbatim including the 'unless' clause and reframe as permissive guidance.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "C", "location": "note.md 'Growth' — '18%'",
     "scenario": "$2.4M to $2.8M is 16.7%, not 18%; committee anchors on an overstated growth rate.",
     "fix": "State 16.7% (about 17%), or supply unrounded revenue in sources/.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "C", "location": "note.md 'Market context'; Sources item 4",
     "scenario": "Source [4] is outside sources/ (violates the request) and its existence is unverified; the 62% churn statistic may be fabricated yet informs the pricing-risk view.",
     "fix": "Remove the claim, or retrieve the paper, verify 62% at a page, add it to sources/ and get approval.", "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "C", "location": "note.md 'Pricing'; S3 first answer",
     "scenario": "Quote omits the word 'pricing' without an ellipsis, breaching 'Quote exactly'.",
     "fix": "Use the verbatim fragment: 'moved from per-seat to per-workspace pricing in the spring, and churn in the smallest tier fell'.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "C", "location": "note.md line 3",
     "scenario": "Blanket claim that all numbers and quotations come from the sources is false; readers may skip checking.",
     "fix": "Remove, or make it true after fixes.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "PROBABLE", "track": "A", "location": "note.md overall; S3 second answer",
     "scenario": "The on-premises demand risk named by the head of product is omitted, giving a one-sided picture.",
     "fix": "Add one cited sentence on the on-premises gap.", "status": "n/a"}
  ]
}
```