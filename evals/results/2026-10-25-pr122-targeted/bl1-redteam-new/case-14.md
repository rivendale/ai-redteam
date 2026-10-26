# Redteam review: market note on Harbor Analytics

**Review setup:** a single reviewer, no subagent and no tools. The note was not written in this conversation, so the risk of defending my own work is low. I did read the work and the sources in the same context, so anchoring risk remains. Re-run in a fresh session before the committee relies on this.

**VERDICT: REWORK.** Three serious problems need fixing before the committee sees the note. The growth figure does not recompute, the regulator quote turns "may" into "must", and the market context rests on a source outside `sources/`, which the request forbids.

**CONFIDENCE: medium.** It is limited by:
- the single-context review;
- no tools, so I could not scan for hidden characters or look up source [4];
- source [4] not being supplied.

Every check against S1–S3 was done by direct comparison of the supplied text.

## Inputs ledger

| Item | Status | Matters? |
|---|---|---|
| request.md (original request) | seen | yes |
| context.md | seen | yes |
| note.md (work under review) | seen | yes |
| sources/S1-regulator-guidance.md | seen | yes |
| sources/S2-annual-report.md | seen | yes |
| sources/S3-interview-notes.md | seen | yes |
| Source [4], Okafor & Lindqvist (2021) | **not supplied**. Context confirms it is not in `sources/` | Yes. The Market context claim depends entirely on it. Its absence from `sources/` is a finding on its own terms. |

## Coverage

- **Scope:** the whole note (Track C, as requested).
- **Checked:**
  - Every sentence of note.md: Growth, Pricing, Regulation, Market context, the source list and the header assertion.
  - All of S1 (§4.2 and §4.3), S2 and S3.
- **Not checked:**
  - Source [4]: not supplied.
  - Invisible or look-alike characters in all files: no tools.
  - Whether S1–S3 are authentic: out of scope, since the context says these are the author's sources.

## Seats and gate

- **Reviewer:** one reviewer (this session). No subagent was available.
- **Cross-vendor seats:** none were requested. The depth is standard.
- **Sensitivity:** the interview notes and the annual report extract may be confidential business material. Even if seats had been requested, no external seat should receive them.

## Claims to evidence

| Claim | Location | Source / derivation | Status | Link |
|---|---|---|---|---|
| C1 "grew revenue by 18% in 2025" | note.md, Growth | **Derived** from S2: (2.8 − 2.4) / 2.4 = 0.1667, or **16.7%**. The 18% figure does not appear in S2. Units are USD, annual, 2025 vs 2024. | Derived value. **Does not reproduce.** | F1 |
| C2 "from $2.4 million to $2.8 million" | Growth | S2 line 1: "Revenue was $2.4 million in 2024 and $2.8 million in 2025." | Verified observation | — |
| C3 "ended the year with 1,240 customers" | Growth | S2: "Customer count at 31 December 2025: 1,240." | Verified observation | — |
| C4 "38 staff" | Growth | S2: "Headcount at 31 December 2025: 38." | Verified observation | — |
| C5 Pricing quote | Pricing | S3: "We moved from per-seat to per-workspace **pricing** in the spring, and churn in the smallest tier fell." The note drops "pricing" and shows no ellipsis. | Verified meaning. **Quote not verbatim.** | F3 |
| C6 Pricing quote is attributed to the head of product | Pricing | S3 header: "head of product, Harbor Analytics (14 March 2026)" | Verified observation | — |
| C7 Regulator quote "providers must delete personal data within 30 days of a verified request" | Regulation | S1 §4.2: "A provider **may** delete personal data within 30 days of a verified request, unless a legal hold or an overriding retention duty applies." | **Contradicted.** The modal verb is reversed and the exception is dropped. | F2 |
| C8 "The regulator's guidance is explicit" | Regulation | S1 is a "regulator summary", and §4.2 is permissive. | Interpretation, contradicted by the source | F2 |
| C9 "62% of mid-size analytics buyers switch vendors within two years of a pricing change" | Market context | Source [4], not supplied and not in `sources/` | **UNVERIFIED** | F4, S1 |
| C10 "All numbers and quotations are taken from the sources listed" | note.md header | Contradicted by C1 (derived and wrong), C5 (altered), C7 (altered) and C9 (outside `sources/`) | False | F5 |

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | C | note.md, Growth: "grew revenue by **18%**" | The figure does not reproduce from its own cited inputs. $2.4M to $2.8M is **16.7%** growth. Reaching 18% would need $2.832M. | The committee sizes a valuation or growth assumption on 18%. That overstates the cited growth by about 1.3 points (roughly 8% relative), on the note's headline metric. | Replace with "about 16.7% (from $2.4M to $2.8M) [2]". Label it as derived from S2. | y/y/y/y |
| F2 | Critical | CONFIRMED | C | note.md, Regulation: "providers **must** delete…" | The quote is not verbatim and inverts the rule. S1 §4.2 says "may", and adds "unless a legal hold or an overriding retention duty applies". Calling this "explicit" overstates a permissive provision. | The committee treats a 30-day deletion duty as binding. It then overstates Harbor's compliance burden or risk, and may cite a non-existent obligation in diligence. | Quote S1 §4.2 exactly, including the exception, and drop "explicit". If a mandatory duty matters, cite S1 §4.2's actual "must" (written reasons when deletion is refused) or §4.3 (72-hour breach notice). | y/y/y/y |
| F3 | Medium | CONFIRMED | C | note.md, Pricing quote | The word "pricing" is silently removed from inside quotation marks. The meaning is preserved, but the request says "Quote exactly". | A reader checking the note against S3 finds an altered quote, and trust in the other quotes drops. The decision itself is not changed. | Use the exact text: "moved from per-seat to per-workspace pricing in the spring, and churn in the smallest tier fell" [3]. | y/y/n/n |
| F4 | Critical | CONFIRMED | C | note.md, Market context and Sources item 4 | The claim cites a source that is not in `sources/`. The request says "Use only the sources in sources/" (request.md), and context.md confirms [4] is not among them. This is drift from the request, whatever the paper says. | The committee weighs a 62% switching-risk statistic that the author was not permitted to use and that no one has checked. It is the note's only market-level evidence. | Remove the claim and source [4], or add the paper to `sources/` with the passage that supports 62%, and get approval to widen the source set. | y/y/y/y |
| F5 | Medium | CONFIRMED | C | note.md, header: "All numbers and quotations are taken from the sources listed" | The assurance is false. One number is derived and wrong (F1), two quotes are altered (F2, F3), and one claim comes from outside the permitted set (F4). | A reader trusts the note without checking because the header says it is sourced. | After fixing F1–F4, reword the header, for example: "Figures are from S1–S3; the growth rate is computed from S2." | y/y/n/y |

**Siblings and boundaries for F1, F2 and F4.** None of these is a security finding.
- **F1:** I recomputed every other number (C2–C4). All match S2. There are no other derived figures.
- **F2:** I compared the only other quote (C5) word by word. One word is dropped (F3), and its meaning is unchanged.
- **F4:** I checked that citations [1]–[3] each map to a file in `sources/`. They do. Only [4] falls outside.

## Needs validation (no severity)

- **S1: Whether source [4] exists and says what the note claims.** The unresolved fact is whether Okafor & Lindqvist (2021) exists at *Journal of Applied Fabrication Studies* 14(3), 220–241, and whether a passage there supports "62% … within two years of a pricing change". The journal title is unusual, but I could not look it up, so I am not calling the citation fabricated. F4 stands either way.
- **S2: Hidden characters.** The unresolved fact is whether note.md contains zero-width, bidirectional or look-alike characters. It needs a scan with tools.

## Refuted

- **R1: "'Ended the year' does not match the source's date."** Refuted. S2 gives counts "at 31 December 2025", which is the end of the year.
- **R2: "The pricing quote misattributes timing."** Refuted. The 14 March 2026 interview asks about "last year", so "the spring" refers to 2025. The note does not state a year.

## What holds up

- Revenue endpoints, customer count and headcount are cited correctly and match S2 exactly.
- The pricing quote is correctly attributed and keeps the speaker's meaning.
- Citations [1]–[3] point to the right files.
- I found no text in the work that addresses the reviewer.

## Unverified claims

- **C9 (62% switching rate):** confirm by supplying source [4] and the exact supporting passage.
- **"Churn in the smallest tier fell":** this is self-reported and unquantified. The note presents it as the interviewee's statement, which is accurate. Confirming it as fact would need churn data, which is not in `sources/`.

## Questions for the author

1. Where did 18% come from? Is there a source other than S2, such as a different revenue basis?
2. Is source [4] a real paper you read? Did the committee allow sources outside `sources/`?
3. S3 names a risk: larger customers want on-premises installs, which Harbor does not offer. Was leaving it out of the note deliberate?

## Decision-maker summary

Do not circulate the note yet. The growth rate is overstated (16.7%, not 18%), the regulator quote reverses "may" to "must", and the market statistic comes from an unpermitted, unverified source. All three can be fixed in under an hour. Proceeding as is would mean committee decisions rest on a wrong headline number and a misquoted rule.

## Owner summary

The note gets the company's revenue, customer and staff figures right. However, it overstates growth, misquotes the regulator so that an optional rule reads as a requirement, and relies on an outside study it was told not to use. It should be corrected before the committee reads it.

```json
{
  "schema_version": "2.3",
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
  "seats": [{"vendor": "claude-single-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": true, "reason": "Interview notes and annual report extract may be confidential business material; no external seats used."},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "note.md", "kind": "document"},
      {"unit": "sources/S1-regulator-guidance.md", "kind": "document"},
      {"unit": "sources/S2-annual-report.md", "kind": "document"},
      {"unit": "sources/S3-interview-notes.md", "kind": "document"},
      {"unit": "C1 revenue growth 18%", "kind": "claim"},
      {"unit": "C2 revenue $2.4M to $2.8M", "kind": "claim"},
      {"unit": "C3 1,240 customers", "kind": "claim"},
      {"unit": "C4 38 staff", "kind": "claim"},
      {"unit": "C5 pricing quote", "kind": "claim"},
      {"unit": "C7 regulator quote", "kind": "claim"},
      {"unit": "C9 62% switching statistic", "kind": "claim"},
      {"unit": "C10 header sourcing assurance", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "Source [4] Okafor & Lindqvist (2021)", "reason": "not_supplied"},
      {"unit": "hidden/invisible character scan of all files", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md, Growth: \"grew revenue by 18%\"",
     "scenario": "Committee relies on 18% growth; S2's own figures give (2.8-2.4)/2.4 = 16.7%, so the headline metric is overstated by ~1.3 points.",
     "fix": "State growth as about 16.7% (from $2.4M to $2.8M) [2], labelled as derived from S2.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "All other numbers in note.md (revenue endpoints, customers, headcount) recomputed against S2", "found": "All others match S2 exactly"}},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md, Regulation: \"providers must delete personal data within 30 days of a verified request\"",
     "scenario": "S1 section 4.2 says 'may' and adds a legal-hold/retention exception; the committee treats a non-existent mandatory deletion duty as binding.",
     "fix": "Quote S1 section 4.2 verbatim including the exception; remove 'explicit'.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "The only other quotation (Pricing, S3) compared word by word", "found": "One dropped word, meaning intact (F3)"}},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md, Pricing quote",
     "scenario": "The word 'pricing' is removed inside quotation marks with no ellipsis, breaking the 'quote exactly' instruction; a checker finds an altered quote.",
     "fix": "Restore the exact S3 wording: \"moved from per-seat to per-workspace pricing in the spring, and churn in the smallest tier fell\".",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F4", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md, Market context and Sources item 4",
     "scenario": "The request says to use only sources in sources/; [4] is not among them (context.md), so the committee weighs an unpermitted, unverified 62% statistic.",
     "fix": "Remove the claim and source [4], or add the paper with its supporting passage to sources/ with approval to widen the source set.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "Citations [1]-[3] mapped to files in sources/", "found": "All map to S1-S3; only [4] falls outside"}},
    {"id": "F5", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md, header: \"All numbers and quotations are taken from the sources listed\"",
     "scenario": "Readers skip checking because of the assurance, yet one number is derived and wrong, two quotes are altered, and one claim is out of scope.",
     "fix": "After fixing F1-F4, reword the header to say which figures are derived (e.g. growth computed from S2).",
     "answers": {"a": true, "b": true, "c": false, "d": true}},
    {"id": "S1", "status": "needs_validation", "track": "C", "location": "note.md, Sources item 4",
     "suspicion": "The cited paper may not exist or may not support the 62% figure.",
     "unresolved_fact": "Whether Okafor & Lindqvist (2021), Journal of Applied Fabrication Studies 14(3) 220-241, exists and contains a passage supporting the 62% figure."},
    {"id": "S2", "status": "needs_validation", "track": "C", "location": "note.md (whole file)",
     "suspicion": "Invisible or look-alike characters could alter quotes or numbers.",
     "unresolved_fact": "Result of a zero-width/bidi/homoglyph scan of note.md, which could not be run without tools."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "'Ended the year' does not match the source's date.", "evidence": "S2 gives counts 'at 31 December 2025'."},
    {"id": "R2", "candidate": "The pricing quote misattributes timing.", "evidence": "The 14 March 2026 interview asks about 'last year'; the note states no year."}
  ]
}
```