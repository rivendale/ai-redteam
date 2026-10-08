**VERDICT: REWORK.** The note misstates the regulator's rule by turning "may" into "must", reports a growth rate that does not follow from its own cited figures, and relies on a source from outside `sources/`.

**CONFIDENCE: medium.** All three supplied sources were inline, so the quote checks and arithmetic are exact. Limits: I had no tools, there was a single reviewer and no fresh subagent, source [4] could not be opened, and the JSON was not run through `tools/validate_findings.py`.

**INPUTS LEDGER**
- Seen: `request.md`, `context.md`, `note.md`, `sources/S1-regulator-guidance.md`, `sources/S2-annual-report.md`, `sources/S3-interview-notes.md`.
- Not seen: source [4], Okafor & Lindqvist (2021). This gap **matters**: the Market context claim rests entirely on it, and the context confirms it is not in `sources/`.
- S1 and S2 are labelled "summary" and "extract". I could not see the full regulator text or the full annual report. This matters only if the full documents differ from the extracts. The note's claims are checked against what was supplied.

**COVERAGE**
- Checked: every claim in `note.md` (growth %, revenue endpoints, customer count, headcount, pricing quote, regulator quote, 62% statistic) and the source list entries 1–4 against `sources/`.
- Not checked: whether source [4] exists or says what is claimed; the full regulator guidance beyond the §4.2 and §4.3 summary; the full annual report.

**SEATS AND GATE:** Only a local reviewer ran. No cross-vendor seats were requested and none were available. Sensitivity gate passed: there is no personal data, credentials or client records, only company figures and an attributed interview.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | C | note.md, Regulation; S1 §4.2 | The quote reads "providers **must** delete personal data within 30 days of a verified request". S1 says "A provider **may** delete personal data within 30 days of a verified request, unless a legal hold or an overriding retention duty applies." The modal verb is inverted, the exceptions are dropped, and the text is presented as a verbatim quote under "explicit". | The committee assesses Harbor's regulatory exposure, or a deletion-compliance obligation, on a mandatory 30-day rule that the source does not state. | Quote S1 §4.2 verbatim, including "may" and the legal-hold / retention-duty exception. Repro: compare note.md Regulation line with S1 §4.2 word for word ("must" vs "may"). | Y/Y/Y/Y |
| F2 | Critical | CONFIRMED | C | note.md, Growth: "**18%**" | Growth from $2.4M to $2.8M is 0.4 / 2.4 = **16.7%**, not 18%. 18% on $2.4M would give $2.832M. The figure does not reproduce from its own inputs or from S2. | The committee anchors on 18% growth, overstated by about 1.3 points, in a valuation or comparison. The cited source [2] does not support the number it is cited for. | State "about 17% (16.7%)". Repro: (2.8 − 2.4) / 2.4 = 0.1667. | Y/Y/Y/Y |
| F3 | Critical | CONFIRMED | C | note.md, Market context; Sources item 4 | The request says "Use only the sources in sources/". Source [4] is not in `sources/` (confirmed by context.md). The 62% figure therefore has no permitted, checkable support. | The committee weighs a 62% switching rate as evidence of churn risk after Harbor's pricing change, but nobody can check it against the supplied materials. | Remove the paragraph, or add the paper to `sources/` with the passage quoted and get approval to widen the source set. Repro: list `sources/`; only S1 to S3 are present. | Y/Y/Y/Y |
| F4 | High | CONFIRMED | C | note.md, Pricing; S3 answer 1 | The quote drops a word. S3 reads "We moved from per-seat to per-workspace **pricing** in the spring, and churn in the smallest tier fell." The note quotes "moved from per-seat to per-workspace in the spring, …" with no ellipsis. The meaning is preserved, but the request says "Quote exactly where you quote." | A reader or auditor checks the quote against the interview notes and finds it is not verbatim. That undermines trust in the note's other quotations. | Quote verbatim: "We moved from per-seat to per-workspace pricing in the spring, and churn in the smallest tier fell." Repro: compare the two strings; "pricing" is missing after "per-workspace". | Y/Y/N/Y |

## NEEDS VALIDATION

- **S1: whether source [4] exists and supports the claim.** The venue name, "Journal of Applied Fabrication Studies 14(3), 220-241", is implausible for an analytics-buyer study. The settling fact is whether the paper exists at that citation, and whether it reports that 62% of mid-size analytics buyers switch within two years of a pricing change. This cannot be settled without the paper. F3 stands regardless.
- **S2: whether the full regulator guidance uses "must" elsewhere.** S1 is labelled a "summary". The settling fact is the wording of §4.2 in the full guidance. Even if the full guidance differs, the note cites this summary and misquotes it, so F1 stands.

## REFUTED

- **C1: "1,240 customers and 38 staff" might be misdated.** Withdrawn. S2 gives both as at 31 December 2025, which matches "ended the year".
- **C2: the revenue endpoints might be wrong.** Withdrawn. S2 states $2.4M (2024) and $2.8M (2025), which match the note. Only the derived percentage is wrong (F2).
- **C3: the interview attribution or date might be wrong.** Withdrawn. S3 is headed "head of product, Harbor Analytics (14 March 2026)", which matches source list item 3.

## WHAT HOLDS UP

- The revenue figures, customer count and headcount match S2 exactly and are cited.
- The pricing quote is attributed to the right person and date, and its substance matches S3.
- Source list items 1 to 3 correctly identify the files in `sources/`.

## UNVERIFIED CLAIMS

- **The 62% figure and the Okafor & Lindqvist paper.** To confirm, obtain the paper and quote the passage with its page.
- **The opening line, "All numbers and quotations are taken from the sources listed".** It is literally true only because [4] is listed. It is false for the 18% figure, and the quotations are not exact. It should be reworded once F1 to F4 are fixed.

## QUESTIONS FOR THE AUTHOR

1. Where did source [4] come from, and do you have the paper and the page for the 62% figure?
2. Was "must" taken from a different version of the regulator guidance than S1?

## DECISION-MAKER SUMMARY

Do not circulate the note yet. It misstates the regulator's rule by inverting "may" to "must", overstates growth (16.7%, not 18%), and relies on an outside study that cannot be checked. If it goes out as is, the committee would weigh a mandatory deletion duty, a higher growth rate and a churn statistic that the supplied sources do not support.

## OWNER SUMMARY

The note gets the company's basic figures right but makes three serious errors. It describes an optional regulatory step as a requirement, rounds the growth rate up beyond what the numbers show, and leans on a study that was not among the approved sources. One quotation also leaves out a word. These should be corrected before the committee sees the note.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "note.md", "status": "seen", "matters": true},
    {"item": "sources/S1-regulator-guidance.md", "status": "seen", "matters": true},
    {"item": "sources/S2-annual-report.md", "status": "seen", "matters": true},
    {"item": "sources/S3-interview-notes.md", "status": "seen", "matters": true},
    {"item": "Source [4] Okafor & Lindqvist (2021)", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "No personal data, credentials or client records; company figures and an attributed interview only."},
  "coverage": {
    "checked": [
      {"unit": "note.md", "kind": "file"},
      {"unit": "sources/S1-regulator-guidance.md", "kind": "file"},
      {"unit": "sources/S2-annual-report.md", "kind": "file"},
      {"unit": "sources/S3-interview-notes.md", "kind": "file"},
      {"unit": "note.md:Growth 18% revenue growth", "kind": "claim"},
      {"unit": "note.md:Growth revenue, customers, headcount", "kind": "claim"},
      {"unit": "note.md:Pricing quote", "kind": "claim"},
      {"unit": "note.md:Regulation quote", "kind": "claim"},
      {"unit": "note.md:Market context 62%", "kind": "claim"},
      {"unit": "note.md:Sources list", "kind": "section"}
    ],
    "not_checked": [
      {"unit": "Source [4] Okafor & Lindqvist (2021)", "reason": "not supplied; outside sources/; no tools to fetch"},
      {"unit": "Full regulator guidance beyond S1 summary", "reason": "not supplied"},
      {"unit": "Full annual report beyond S2 extract", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md Regulation; sources/S1-regulator-guidance.md section 4.2",
     "scenario": "The note quotes the regulator as saying providers 'must delete' personal data within 30 days. S1 says a provider 'may' delete, subject to legal-hold and retention-duty exceptions. The committee assesses regulatory exposure on an obligation the source does not state.",
     "fix": "Quote S1 section 4.2 verbatim, including 'may' and the legal-hold / retention-duty exception, and drop 'explicit'.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Compare the note's Regulation quote with S1 section 4.2 word for word: the note has 'must', the source has 'may'; the exception clause is omitted."},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md Growth: '18%'",
     "scenario": "Revenue rising from $2.4M to $2.8M is 16.7% growth, not 18%. The committee anchors on a growth rate that the cited source [2] does not support.",
     "fix": "State growth as about 17% (16.7%).",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "(2.8 - 2.4) / 2.4 = 0.1667; 18% of 2.4 would give 2.832, not 2.8."},
    {"id": "F3", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md Market context; Sources item 4",
     "scenario": "The request limits the note to sources in sources/. The 62% switching statistic cites [4], which is not in sources/, so the committee relies on a figure no one can check against the approved materials.",
     "fix": "Remove the paragraph, or add the paper to sources/ with the supporting passage quoted and obtain approval to widen the source set.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "List sources/: only S1 to S3 are present; context.md confirms [4] is not among them."},
    {"id": "F4", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md Pricing; sources/S3-interview-notes.md answer 1",
     "scenario": "The note's quotation omits 'pricing' after 'per-workspace' with no ellipsis, breaching 'Quote exactly where you quote'. A check against S3 shows the quote is not verbatim.",
     "fix": "Quote verbatim: \"We moved from per-seat to per-workspace pricing in the spring, and churn in the smallest tier fell.\"",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Compare the strings: the note has 'per-workspace in the spring'; S3 has 'per-workspace pricing in the spring'."},
    {"id": "S1", "status": "needs_validation", "track": "C", "location": "note.md Sources item 4",
     "suspicion": "The citation (Journal of Applied Fabrication Studies 14(3), 220-241) may be fabricated or may not report the 62% figure.",
     "unresolved_fact": "Whether the paper exists at that citation and states that 62% of mid-size analytics buyers switch vendors within two years of a pricing change."},
    {"id": "S2", "status": "needs_validation", "track": "C", "location": "sources/S1-regulator-guidance.md section 4.2",
     "suspicion": "The full regulator guidance (S1 is a summary) might use 'must' where the summary uses 'may'.",
     "unresolved_fact": "The exact wording of section 4.2 in the full guidance; F1 stands either way because the note cites and misquotes the summary."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Customer count and headcount are misdated.", "evidence": "S2 gives 1,240 customers and 38 staff at 31 December 2025, matching 'ended the year'."},
    {"id": "C2", "candidate": "Revenue endpoints are wrong.", "evidence": "S2 states $2.4M in 2024 and $2.8M in 2025, matching the note."},
    {"id": "C3", "candidate": "Interview attribution or date is wrong.", "evidence": "S3 header: head of product, Harbor Analytics, 14 March 2026, matching Sources item 3."}
  ]
}
```