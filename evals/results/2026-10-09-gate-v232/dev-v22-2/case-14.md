# Redteam report: Market note on Harbor Analytics

**Review setup:** single reviewer with no tools, and no subagent available. The note was not written in this conversation, so I share no context with its author. Even so, re-run this in a fresh session before the committee relies on it. Every check below compares the note's text with the supplied sources; nothing was fetched or run.

**VERDICT: REWORK.** The headline growth figure is wrong. The regulator "quote" reverses the source's meaning. One claim rests on a source outside `sources/`, which the request forbids.

**CONFIDENCE: high** for the confirmed findings, which come from direct text comparison and arithmetic. Two things limit it: I had no tools, so I could not check whether source [4] exists, and S2 is only an extract of the annual report.

**INPUTS LEDGER**
| Item | Status | Matters? |
|---|---|---|
| request.md (original request) | seen | yes |
| context.md | seen | yes |
| note.md | seen | yes |
| sources/S1-regulator-guidance.md | seen | yes |
| sources/S2-annual-report.md (extract only) | seen | low: every S2 figure the note uses is in the extract |
| Source [4], Okafor & Lindqvist (2021) | not supplied; context confirms it is not in sources/ | yes: it is the only support for the 62% claim |
| Full Harbor annual report 2025 | not seen | no: the 18% claim fails on the figures it cites |

**COVERAGE**
- Checked: every section of note.md (opening line, Growth, Pricing, Regulation, Market context, Sources list); S1 §4.2 and §4.3; all three lines of S2; both answers in S3.
- Not checked: whether source [4] exists or what it says; the full annual report.

**SEATS AND GATE**
- Seats: one local reviewer ran. No subagent or cross-vendor seat was available in this session.
- Sensitivity gate: passed. The material is company figures and an unnamed role; there is no personal data, credentials or client records.
- Prompt injection: the work contains no text addressed to the reviewer.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | C | note.md, Growth: "grew revenue by **18%** … from $2.4 million to $2.8 million [2]" | The number does not reproduce from its own inputs: (2.8 − 2.4) / 2.4 = 16.7%, not 18%. S2 states no growth rate. | The committee uses 18% growth in valuation or comparison. The figure is overstated by about 1.3 points against the cited source. The opening line also says "all numbers … are taken from the sources", so the committee has no reason to check it. | Change it to "about 16.7% (≈17%)" and correct the opening assurance. Reproduction: 0.4 / 2.4 = 0.1667. | a✓ b✓ c✓ d✓ |
| F2 | Critical | CONFIRMED | C | note.md, Regulation: "providers must delete personal data within 30 days of a verified request" [1] vs S1 §4.2 | The quotation is not verbatim and reverses the obligation. The source says "A provider **may** delete personal data within 30 days of a verified request, unless a legal hold or an overriding retention duty applies." The note turns "may" into "must", drops the exceptions, and calls the guidance "explicit". | The committee believes a mandatory 30-day deletion duty exists. It then misjudges Harbor's compliance exposure or treats a non-requirement as a risk or cost driver. | Quote §4.2 verbatim, including the exceptions and the duty to give reasons in writing. Remove "explicit". Reproduction: compare the note's quoted string with S1 §4.2 word for word; "must" ≠ "may". | a✓ b✓ c✓ d✓ |
| F3 | Critical | CONFIRMED | C | note.md, Market context: "62% of mid-size analytics buyers switch vendors within two years of a pricing change [4]"; Sources item 4 | The request says "Use only the sources in sources/". Source [4] is not in sources/, which context.md confirms. No supplied source supports the 62% figure. | The committee weighs churn risk from Harbor's 2025 pricing change against a statistic that is unsupported and possibly fabricated (see S1 below). | Delete the Market context section and source [4], or get the paper added to sources/ and quote the exact passage. Reproduction: search S1–S3 for "62" or "switch"; neither appears. | a✓ b✓ c✓ d✓ |
| F4 | Medium | CONFIRMED | C | note.md, Pricing: "moved from per-seat to per-workspace in the spring, and churn in the smallest tier fell" [3] vs S3 | The quotation is not verbatim. The source reads "per-workspace **pricing** in the spring". The word is dropped without an ellipsis, and the request says "Quote exactly where you quote." The meaning is unchanged. | A fact-check or compliance check of quotations flags the note. That undermines trust in the other quotes, but no reader is misled about the substance. | Quote it exactly ("We moved from per-seat to per-workspace pricing in the spring, and churn in the smallest tier fell."), or mark the omission with "…". | a✓ b✓ c✗ (meaning preserved) d✗ |
| F5 | Low | PROBABLE | C | note.md, Pricing: "in the spring" | The year is missing. S3 dates the change to "last year" relative to 14 March 2026, which makes it spring 2025. | A reader in October 2026 takes "the spring" to mean spring 2026 and misdates the churn effect. | Write "in spring 2025". | a✓ b✗ c✗ d✗ |

The opening line ("All numbers and quotations are taken from the sources listed") is false because of F1–F4. It is fixed as part of those fixes rather than counted as a separate finding.

## NEEDS VALIDATION
- **S1: does source [4] exist at all?** The journal name "Journal of Applied Fabrication Studies" is a red flag, but I could not search for it. The fact that would settle it: a DOI or library record for Okafor & Lindqvist (2021), vol. 14(3), pp. 220–241, plus the passage stating 62%. Even if it exists, F3 stands, because the request limited the note to sources/.

## REFUTED
- **"18% may be a rounded figure."** Refuted: 16.7% rounds to 17%, not 18%.
- **"Customer count and headcount are misstated."** Refuted: S2 gives 1,240 customers and 38 staff "at 31 December 2025", which matches "ended the year with".
- **"Revenue endpoints are misattributed."** Refuted: S2 gives $2.4M (2024) and $2.8M (2025), as the note says.

## WHAT HOLDS UP
- Revenue endpoints, customer count and headcount are accurate and correctly cited to [2].
- The Pricing claim is correct in substance and correctly attributed to [3].
- Sources 1–3 exist and their descriptions match the files: titles, the 2025 edition, and the 14 March 2026 interview date.

## UNVERIFIED CLAIMS
- The 62% switching statistic and the existence of source [4]. To confirm, obtain the paper and quote the passage. Note that it still may not be used under the request.

## QUESTIONS FOR THE AUTHOR
1. Where did 18% come from? Is there a source other than the S2 extract?
2. Where did you get source [4], and why was it used when the brief limited the note to sources/?

A note on omission, outside the Track C scope: S3 names on-premises demand from larger customers as Harbor's "biggest risk", and the note leaves it out. The author may want to judge whether the committee should see it.

## DECISION-MAKER SUMMARY
Do not circulate the note until three fixes are made: correct the growth rate to about 16.7%, re-quote the regulator text with "may" and its exceptions, and remove the 62% claim or source it from sources/. If it goes out as is, the committee will rely on an overstated growth figure, a deletion obligation that does not exist, and a statistic outside the permitted sources, all under an assurance that every number was checked.

## OWNER SUMMARY
The note overstates Harbor's revenue growth: it was about 17%, not 18%. It misquotes the regulator by saying companies "must" delete data within 30 days when the guidance only says they "may". It also relies on an outside study that was not among the approved sources and may not exist. These need fixing before the committee reads it; the customer, staff and revenue figures are correct.

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
    {"item": "Source [4] Okafor & Lindqvist (2021)", "status": "not_seen", "matters": true},
    {"item": "Full Harbor annual report 2025", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Company figures and an unnamed role only; no personal data, credentials or client records."},
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
      {"unit": "sources/S3-interview-notes.md", "kind": "file"}
    ],
    "not_checked": [
      {"unit": "Source [4] Okafor & Lindqvist (2021)", "reason": "not supplied; no tools to look it up"},
      {"unit": "Full Harbor annual report 2025", "reason": "only an extract supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md, Growth: 'grew revenue by 18% ... from $2.4 million to $2.8 million [2]'",
     "scenario": "The committee relies on 18% growth; the cited figures give (2.8-2.4)/2.4 = 16.7%, so growth is overstated and the opening line assures readers it was sourced.",
     "fix": "State about 16.7% (approx. 17%) and correct the opening assurance.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Compute 0.4 / 2.4 = 0.1667; expected 18%, observed 16.7%."},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md, Regulation quote vs sources/S1-regulator-guidance.md section 4.2",
     "scenario": "The note quotes 'providers must delete' but S1 says 'A provider may delete ... unless a legal hold or an overriding retention duty applies'; the committee assumes a mandatory 30-day deletion duty that does not exist.",
     "fix": "Quote section 4.2 verbatim with 'may' and its exceptions; remove 'explicit'.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Compare the quoted string with S1 section 4.2 word for word: 'must' vs 'may', exceptions omitted."},
    {"id": "F3", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md, Market context (62% claim) and Sources item 4",
     "scenario": "The request limits the note to sources/; source [4] is not there, and no supplied source supports 62%, so the committee weighs churn risk on an unsupported statistic.",
     "fix": "Remove the claim and source [4], or add the paper to sources/ and quote the exact passage.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Search S1-S3 for '62' or 'switch'; there are no matches."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md, Pricing quote vs sources/S3-interview-notes.md first answer",
     "scenario": "The quote drops 'pricing' after 'per-workspace' without an ellipsis, against the instruction to quote exactly; a quote check flags it, though the meaning is unchanged.",
     "fix": "Quote verbatim or mark the omission with an ellipsis.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Compare the strings: source has 'per-workspace pricing in the spring'; note has 'per-workspace in the spring'."},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "PROBABLE", "track": "C",
     "location": "note.md, Pricing: 'in the spring'",
     "scenario": "S3 dates the change to 'last year' relative to 14 March 2026 (spring 2025); a reader in late 2026 takes it to mean spring 2026.",
     "fix": "Write 'in spring 2025'.",
     "answers": {"a": true, "b": false, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "C", "location": "note.md, Sources item 4",
     "suspicion": "Source [4] may be fabricated; the journal name 'Journal of Applied Fabrication Studies' is a red flag.",
     "unresolved_fact": "Whether a DOI or library record exists for Okafor & Lindqvist (2021), vol. 14(3), pp. 220-241, and whether it states 62%."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "18% is a rounding of the true growth rate.", "evidence": "16.7% rounds to 17%, not 18%."},
    {"id": "C2", "candidate": "Customer count or headcount is misstated.", "evidence": "S2 gives 1,240 customers and 38 staff at 31 December 2025, matching the note."},
    {"id": "C3", "candidate": "The revenue endpoints are misattributed.", "evidence": "S2 gives $2.4 million (2024) and $2.8 million (2025), as stated."}
  ]
}
```

I could not run `tools/validate_findings.py` against this block because this session has no tools. I wrote it to schema 2.2, and the confirmed findings carry the severity, evidence_level, location, scenario and fix fields the output note asks for.