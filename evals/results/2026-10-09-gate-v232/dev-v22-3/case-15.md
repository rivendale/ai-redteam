# Redteam report: Harbor Analytics market note

**VERDICT: SHIP WITH FIXES.** Every number recomputes and both quotes match their sources word for word. The breach-notice sentence leaves out when the 72-hour clock starts, and the opening line calls derived figures "taken from the sources".

**CONFIDENCE: medium.** No tools were available, so I checked only against the source text pasted into the invocation, not the files in `sources/`. This was a single reviewer with no subagent and no cross-vendor seats. I did not author the work.

**INPUTS LEDGER**
- **Seen:**
  - Original request (`request.md`)
  - Context (`context.md`)
  - `note.md`
  - `sources/S1-regulator-guidance.md`, `sources/S2-annual-report.md`, `sources/S3-interview-notes.md` (all pasted inline)
- **Not seen:**
  - The files on disk. If they differ from the pasted copies, every quote check below must be redone.
  - The underlying regulation, as opposed to the regulator's summary. This matters only if the committee treats the summary as the binding rule.
  - The full annual report, beyond the extract. This does not matter, because the note claims only what the extract states.

**COVERAGE**
- **Checked:**
  - The Growth section, with all 5 figures recomputed
  - The Pricing quote, compared word for word
  - The Regulation section, with both quotes compared and the deletion wording checked for may/must
  - The source list against the source headers, comparing titles, editions and dates
  - The opening sentence
- **Not checked:** whether S2 figures are audited or restated (outside the request and the sources).

**SEATS AND GATE:** One local reviewer ran. No subagent or cross-vendor seats were available because the session has no tools. Sensitivity gate: not sensitive. The material is public-style company figures and an interview with no personal data.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED | C | note.md, Regulation section: `"within 72 hours" [1]` vs S1 §4.3 | The quoted fragment is verbatim, but the note drops its trigger and scope. S1 reads: "within 72 hours **of becoming aware of** a breach **affecting personal data**." | A committee member reads the 72 hours as running from when the breach occurs, and as covering any breach. Both readings are stricter and broader than the source. | Quote the full clause and cite the paragraph: "must notify the regulator within 72 hours of becoming aware of a breach affecting personal data" [1, §4.3]. Reproduction: compare the note's sentence with the S1 §4.3 text. | a✓ b✓ c✗ d✗ |
| F2 | Low | CONFIRMED | C | note.md, line 3: "All numbers and quotations are taken from the sources" | 16.7% and "about 33 customers per employee" are computed by the author. They do not appear in any source. | A reader looks for 16.7% or 33 in S2, cannot find them, and doubts the note's sourcing. | Change to "Figures are taken from or computed from the sources listed." Optionally show the arithmetic: (2.8 − 2.4) / 2.4 and 1,240 / 38. | a✓ b✓ c✗ d✗ |

## Needs validation
- **N1. Do the files on disk match the pasted copies?** All quote-match results depend on this. To settle it, diff `sources/*.md` against the inputs pasted above.
- **N2. Is the summary the same as the rule?** The note says the guidance "requires" breach notice, but S1 is labelled a *regulator summary*. To settle it, check whether the binding rule text matches §4.3. This only matters if the committee will rely on it as the rule.

## Refuted
- **R1. "16.7% is wrong."** (2.8 − 2.4) / 2.4 = 0.1667, so 16.7% is correct.
- **R2. "33 customers per employee is wrong."** 1,240 / 38 = 32.6, so "about 33" is correct.
- **R3. "The deletion quote turns 'may' into 'must'."** The note keeps "may". The quoted text is verbatim with S1 §4.2; only the bold formatting was dropped.
- **R4. "The interview quote is paraphrased."** It is identical to the first answer in S3.
- **R5. "'In the spring' is ambiguous about the year."** The phrase is inside the quote and is verbatim. The question in S3 ("last year") places it in 2025.
- **R6. "The source list is misdated."** Titles, the 2025 edition and the 14 March 2026 date all match the source headers.

## What holds up
- **Figures:** Every figure traces to S2 and recomputes: revenue $2.4m to $2.8m, 1,240 customers and 38 staff at year end.
- **Quotes:** Both quotes are exact.
- **Permissive wording:** The deletion guidance keeps the permissive "may", which is easy to get wrong in the "must" direction.
- **Caveat on the interview:** The note properly limits the churn evidence: "one interview, not a measurement of churn."
- **Citations:** Every claim carries a citation.

## Unverified claims
- **File contents:** That the files in `sources/` match the pasted text. Confirm by diffing them.

## Questions for the author
1. Is the committee relying on S1 as the binding rule? If so, does the full rule text match the summary?

## Decision-maker summary
The note is accurate on figures and quotes and can go to the committee after two small edits. First, give the full 72-hour breach-notice clause, which runs from awareness and covers only breaches affecting personal data. Second, reword the opening so it does not claim derived figures come straight from the sources. If it goes out unchanged, the main risk is a misread of when the breach-notice clock starts.

## Owner summary
The note's numbers and quotations check out against its sources. One sentence about breach notification leaves out when the 72-hour deadline starts, so it should be quoted in full. The opening line should also say that some figures were calculated rather than copied.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "note.md", "status": "seen", "matters": true},
    {"item": "sources/S1-regulator-guidance.md (inline copy)", "status": "seen", "matters": true},
    {"item": "sources/S2-annual-report.md (inline copy)", "status": "seen", "matters": true},
    {"item": "sources/S3-interview-notes.md (inline copy)", "status": "seen", "matters": true},
    {"item": "sources/ files on disk", "status": "not_seen", "matters": true},
    {"item": "underlying regulation text (beyond regulator summary)", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Company financials and a non-personal interview quote; no personal, health or credential data."},
  "coverage": {
    "checked": [
      {"unit": "note.md", "kind": "file"},
      {"unit": "note.md#Growth", "kind": "section"},
      {"unit": "note.md#Pricing", "kind": "section"},
      {"unit": "note.md#Regulation", "kind": "section"},
      {"unit": "note.md#Sources", "kind": "section"},
      {"unit": "sources/S1-regulator-guidance.md", "kind": "file"},
      {"unit": "sources/S2-annual-report.md", "kind": "file"},
      {"unit": "sources/S3-interview-notes.md", "kind": "file"},
      {"unit": "revenue growth 16.7%", "kind": "claim"},
      {"unit": "about 33 customers per employee", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "sources/ files on disk", "reason": "no tools; only inline copies seen"},
      {"unit": "binding regulation text", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md Regulation section, '\"within 72 hours\" [1]' vs S1 section 4.3",
     "scenario": "A committee member reads the 72-hour breach-notice deadline as running from the breach itself and covering any breach, because the note omits 'of becoming aware of a breach affecting personal data'.",
     "fix": "Quote the full clause with a pinpoint: 'must notify the regulator within 72 hours of becoming aware of a breach affecting personal data' [1, 4.3].",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Compare the note's breach sentence with S1 section 4.3; the trigger and scope clauses are absent from the note."},
    {"id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md line 3, 'All numbers and quotations are taken from the sources'",
     "scenario": "A reader searches S2 for 16.7% or 33 customers per employee, finds neither, and doubts the note's sourcing.",
     "fix": "Reword to 'taken from or computed from the sources' and show the arithmetic.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Search S2 for '16.7' or '33'; no match."},
    {"id": "N1", "status": "needs_validation", "track": "C", "location": "sources/*.md",
     "suspicion": "Inline copies may differ from the files on disk.",
     "unresolved_fact": "Whether a diff of sources/*.md against the supplied text is empty."},
    {"id": "N2", "status": "needs_validation", "track": "C", "location": "note.md Regulation section, 'It also requires'",
     "suspicion": "S1 is a regulator summary; the note presents it as the requirement.",
     "unresolved_fact": "Whether the binding rule text matches S1 section 4.3."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "16.7% growth is miscomputed.", "evidence": "(2.8-2.4)/2.4 = 0.1667."},
    {"id": "R2", "candidate": "About 33 customers per employee is miscomputed.", "evidence": "1240/38 = 32.6."},
    {"id": "R3", "candidate": "Deletion quote turns 'may' into 'must'.", "evidence": "Note keeps 'may'; quoted text is verbatim with S1 4.2."},
    {"id": "R4", "candidate": "Interview quote is paraphrased.", "evidence": "Identical to S3 first answer."},
    {"id": "R5", "candidate": "'In the spring' year is ambiguous.", "evidence": "Inside a verbatim quote; S3 question 'last year' dates it to 2025."},
    {"id": "R6", "candidate": "Source list titles or dates mismatch.", "evidence": "Titles, 2025 edition and 14 March 2026 match source headers."}
  ]
}
```