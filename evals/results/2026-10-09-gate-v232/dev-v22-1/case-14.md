# Redteam report: Harbor Analytics market note

**Review conditions:** I ran this review with no tools and no subagent or cross-vendor seats. I did not write the work, so there is no author anchoring, but it is a single-reviewer pass. All checks below are hand comparisons of the note against the supplied source text, plus hand recomputation.

**VERDICT: REWORK.** Three of the note's four sections misstate their sources in ways the committee would rely on:
- the growth figure does not recompute;
- the regulatory "quote" turns "may" into "must";
- the market-context claim comes from a source outside the permitted set.

**CONFIDENCE: high** for the confirmed findings, because each rests on exact quotes and arithmetic from supplied text. Two things limit it:
- I had no tools, so every check was manual.
- Source [4] was not supplied, so whether it exists and says 62% is unverified.

## INPUTS LEDGER

| Item | Status | Matters? |
|---|---|---|
| request.md | seen | yes |
| context.md | seen | yes |
| note.md | seen | yes |
| sources/S1-regulator-guidance.md | seen | yes |
| sources/S2-annual-report.md | seen | yes |
| sources/S3-interview-notes.md | seen | yes |
| Source [4], Okafor & Lindqvist (2021) | **not supplied, not openable** | Yes, because the 62% claim depends on it. The gap does not change F3: using it breaks the request whatever it says. |

## COVERAGE

**Checked:**
- note.md sections: header, Growth, Pricing, Regulation, Market context, Sources list
- Claims:
  - 18% growth
  - $2.4M → $2.8M revenue
  - 1,240 customers
  - 38 staff
  - the pricing quote
  - the regulator quote
  - the 62% switching claim
  - the header's "all numbers and quotations are taken from the sources"
- S1, S2 and S3 in full

**Not checked:**
- Source [4]: not supplied
- Whether the journal "Journal of Applied Fabrication Studies" exists: no tools

## SEATS AND GATE

- **Sensitivity gate:** passed. The material is a company report extract, interview notes and regulator guidance, with no personal data or credentials.
- **Seats:** only the local reviewer ran. No fresh subagent was available, and no cross-vendor seats were run because I have no tools to reach them. The stakes (investment committee) would justify a `deep` run with independent seats.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | C | note.md, Regulation; S1 §4.2 | The note quotes "providers **must** delete personal data within 30 days of a verified request". S1 says "A provider **may** delete personal data within 30 days of a verified request, unless a legal hold or an overriding retention duty applies." The quote is not verbatim ("providers" for "A provider"; "must" for "may"), it inverts permission into obligation, it drops the exceptions, and it is framed as "explicit". | The committee assesses Harbor's compliance exposure, or a competitor's, against a mandatory 30-day deletion duty that the cited guidance does not impose. This breaks the instruction "Quote exactly where you quote." | Replace the sentence with the verbatim S1 §4.2 text, including the exceptions, and remove "explicit". If an obligation is wanted, cite S1's real "must" duties: written reasons when deletion is refused (§4.2) and breach notice within 72 hours (§4.3). **Reproduction:** put the note's quoted string beside S1 §4.2; "must" does not appear in that sentence. | a Y / b Y / c Y / d Y |
| F2 | Critical | CONFIRMED | C | note.md, Growth, "grew revenue by **18%**" [2] | S2 gives $2.4M in 2024 and $2.8M in 2025. (2.8 − 2.4) / 2.4 = 16.67%, not 18%, and S2 states no growth rate. The headline figure does not reproduce from its own inputs, yet it is attributed to [2]. | The committee uses 18% (bolded, the headline metric) in valuation or comparison work. The figure is overstated by about 1.3 points, and the header's claim that "all numbers ... are taken from the sources" is false. | Change it to "about 16.7% (from $2.4M in 2024 to $2.8M in 2025, [2])". **Reproduction:** 0.4 / 2.4 = 0.1667. | a Y / b Y / c Y / d Y |
| F3 | Critical | CONFIRMED | C | note.md, Market context; Sources item 4 | The request says "Use only the sources in sources/". Source [4] is not in sources/, as context.md confirms. The 62% claim rests entirely on it, and it is the only market context in the note. | The committee weighs a 62% vendor-switching rate after pricing changes against Harbor's 2025 pricing change ([3]). That is a direct churn-risk inference drawn from an unpermitted, unverified source. The journal name, "Journal of Applied Fabrication Studies", adds to the doubt (see S1 below). | Remove the claim and source [4]. If market context is needed, the author should ask for permission to add the source and supply it to sources/. **Reproduction:** list sources/; only S1–S3 are present. | a Y / b Y / c Y / d Y |
| F4 | Medium | CONFIRMED | C | note.md, Pricing; S3 first answer | The quote drops a word inside the quotation marks. S3: "We moved from per-seat to per-workspace **pricing** in the spring…". Note: "moved from per-seat to per-workspace in the spring…". There is no ellipsis or bracket. The meaning is preserved, but the quote is not verbatim. | A reader checking the quote against the interview notes finds a mismatch, which undermines trust in the note's other quotes. Combined with F1, it breaks the "quote exactly" instruction. | Quote the sentence in full, or mark the omission: "moved from per-seat to per-workspace [pricing] in the spring…". **Reproduction:** compare the strings side by side. | a Y / b Y / c N / d N |

**Severity note on F4:** taken alone, this one breaks the letter of "quote exactly" but not the meaning. I rated c as N because no reliance harm follows, and that keeps it at Medium.

## NEEDS VALIDATION

- **S1:** Does source [4] exist, and does it report 62% of *mid-size analytics buyers* switching *within two years of a pricing change*? The fact that would settle it is the paper's text at the cited pages (220–241), plus confirmation that the journal exists. This does not affect F3, which stands either way.

## REFUTED

- **Candidate:** "$2.4M → $2.8M in 2025" misdates the base year. **Evidence:** the note says the company "grew revenue … in 2025, from $2.4 million to $2.8 million". That matches S2's 2024 and 2025 figures. The wording is acceptable.
- **Candidate:** the claim that pricing changed "in the spring" is undated. **Evidence:** S3, dated 14 March 2026, answers a question about "last year", which places the change in spring 2025. The note is consistent with that, though adding "2025" would help.

## WHAT HOLDS UP

- The revenue levels ($2.4M in 2024, $2.8M in 2025) match S2.
- The customer count (1,240) and headcount (38) match S2, including the year-end date.
- The substance of the pricing quote matches S3.
- Citations [1]–[3] point to files that exist and are the right documents.

## UNVERIFIED CLAIMS

- **Source [4]'s existence and its 62% finding.** To confirm, obtain the paper and check the stated figure and the population it covers.
- **The header's "All numbers and quotations are taken from the sources".** F1 and F2 already show this is false for the supplied sources. It can only be restored after the fixes are made.

## QUESTIONS FOR THE AUTHOR

1. Where did 18% come from? Is there a source not supplied, or was it a calculation error?
2. Was [4] meant to be added to sources/? If not, should the Market context section be dropped?

## DECISION-MAKER SUMMARY

Do not circulate the note until F1–F3 are fixed. The regulatory quote reverses the source's meaning, the growth figure is overstated (16.7%, not 18%), and the market statistic comes from an unpermitted and unverified source. If the note goes out as is, the committee would form its views on compliance, growth and churn risk partly on misquoted or unsupported claims.

## OWNER SUMMARY

The note gets the company's revenue, customer and staff numbers right, but it overstates revenue growth and turns an optional rule into a mandatory one in a quotation. It also relies on an outside study that was not among the approved sources and could not be checked. It should be corrected before the committee reads it.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "note.md", "status": "seen", "matters": true},
    {"item": "sources/S1-regulator-guidance.md", "status": "seen", "matters": true},
    {"item": "sources/S2-annual-report.md", "status": "seen", "matters": true},
    {"item": "sources/S3-interview-notes.md", "status": "seen", "matters": true},
    {"item": "Source [4] Okafor and Lindqvist (2021)", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Company report extract, interview notes and regulator guidance; no personal data or credentials."},
  "coverage": {
    "checked": [
      {"unit": "note.md", "kind": "file"},
      {"unit": "note.md#Growth", "kind": "section"},
      {"unit": "note.md#Pricing", "kind": "section"},
      {"unit": "note.md#Regulation", "kind": "section"},
      {"unit": "note.md#Market context", "kind": "section"},
      {"unit": "note.md#Sources", "kind": "section"},
      {"unit": "sources/S1-regulator-guidance.md", "kind": "file"},
      {"unit": "sources/S2-annual-report.md", "kind": "file"},
      {"unit": "sources/S3-interview-notes.md", "kind": "file"},
      {"unit": "18% revenue growth", "kind": "claim"},
      {"unit": "1,240 customers and 38 staff", "kind": "claim"},
      {"unit": "regulator deletion quote", "kind": "claim"},
      {"unit": "head of product pricing quote", "kind": "claim"},
      {"unit": "62% switching claim", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "Source [4] Okafor and Lindqvist (2021)", "reason": "not supplied; no tools to open it"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md Regulation; sources/S1-regulator-guidance.md section 4.2",
     "scenario": "The note quotes 'providers must delete personal data within 30 days'; S1 says 'A provider may delete ... unless a legal hold or an overriding retention duty applies'. The committee assesses compliance exposure against an obligation the source does not impose.",
     "fix": "Replace with the verbatim S1 4.2 sentence including exceptions; drop 'explicit'.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Compare the quoted string with S1 4.2: S1 reads 'may', not 'must', and the note omits the exceptions."},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md Growth, '18%' cited to [2]",
     "scenario": "S2 gives $2.4M (2024) and $2.8M (2025); growth is 16.67%, not 18%. The committee relies on an overstated headline growth figure attributed to a source that does not contain it.",
     "fix": "State about 16.7% growth, from $2.4M (2024) to $2.8M (2025) [2].",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "(2.8 - 2.4) / 2.4 = 0.1667; expected 18%, observed 16.7%."},
    {"id": "F3", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md Market context; Sources item 4",
     "scenario": "The request permits only sources in sources/; [4] is not there. The committee weighs a 62% post-pricing-change switching rate against Harbor's 2025 pricing change, based on an unpermitted, unverified source.",
     "fix": "Remove the 62% claim and source [4], or add the paper to sources/ with the requester's approval and verify the figure.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "List sources/: only S1-S3 are present; context.md confirms [4] is not among them."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md Pricing; sources/S3-interview-notes.md first answer",
     "scenario": "The quote omits 'pricing' inside quotation marks without an ellipsis; a reader checking against S3 finds a non-verbatim quote.",
     "fix": "Quote in full: 'We moved from per-seat to per-workspace pricing in the spring, and churn in the smallest tier fell.'",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Compare the note's quoted string with S3; the word 'pricing' is missing."},
    {"id": "S1", "status": "needs_validation", "track": "C",
     "location": "note.md Market context; Sources item 4",
     "suspicion": "Source [4] may not exist or may not report 62% (the journal name 'Journal of Applied Fabrication Studies' is a red flag).",
     "unresolved_fact": "The text of Okafor and Lindqvist (2021), pages 220-241, and whether the journal exists."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The note misdates the $2.4M revenue base year.",
     "evidence": "The note's 'grew revenue in 2025, from $2.4 million to $2.8 million' matches S2's 2024 and 2025 figures."},
    {"id": "C2", "candidate": "The pricing change timing ('in the spring') is unsupported.",
     "evidence": "S3 (14 March 2026) answers a question about 'last year', placing it in spring 2025; consistent with the note."}
  ]
}
```