# Redteam report: Harbor Analytics market note

**VERDICT: SHIP.** Every cited source exists and says what the note claims, all three quotations match their sources word for word, and every figure recomputes. The two Low findings are optional wording fixes.

**CONFIDENCE: high.** Two things limit it:
- This is a same-context review: no fresh subagent and no tools, so anchoring is a risk. Re-run it in a fresh session if anything high-stakes depends on it. I did not write this note, which lowers the risk somewhat.
- Two of the sources are excerpts, so I could not compare the note against the full documents behind them.

**INPUTS LEDGER**
- Seen: the request, the context, `note.md`, `sources/S1-regulator-guidance.md`, `sources/S2-annual-report.md` and `sources/S3-interview-notes.md`.
- Not seen:
  - The full 2025 annual report. S2 is an extract. This does not matter, because every claim ties to a line in the extract.
  - The full regulator guidance behind S1, which is a summary. This matters a little: see S1 under Needs Validation.

**COVERAGE**
- Checked:
  - Every claim in the Growth, Pricing and Regulation sections.
  - All three quotations, compared character by character.
  - Both derived figures, recomputed.
  - The source list in the note against the files in `sources/`.
  - The note's opening statement about where its numbers and quotes come from.
- Not checked: the primary regulation text and the full annual report, because neither was supplied.

**SEATS AND GATE**
- One local reviewer (this session) ran. No subagent was available and no cross-vendor seats ran.
- Sensitivity gate: passed. The material is company financials and public regulatory text, with no personal data.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Low | CONFIRMED | C | note.md, opening line: "All numbers and quotations are taken from the sources" | 16.7% and "about 33 customers per employee" are calculated by the note. Neither appears in S2. | A committee member searches S2 for "16.7%" or "33", finds nothing, and doubts the sourcing. | Reword to "taken from, or calculated from, the sources". Reproduction: search S2 for "16.7" and "33"; there are no matches. | T/T/F/F |
| F2 | Low | CONFIRMED | C | note.md, Regulation section: "requires breach notice to the regulator 'within 72 hours'" | The quotation is accurate, but the note leaves out when the clock starts ("of becoming aware of a breach") and the scope ("affecting personal data"), both in S1 §4.3. | A reader assumes the 72 hours run from the breach itself and misjudges Harbor's compliance exposure. | Quote the full clause: "within 72 hours of becoming aware of a breach affecting personal data". | T/T/F/F |

## Needs validation

- **S1: what kind of document S1 is.** The note calls S1 "the regulator's guidance". The file's own title is "Regulator summary, 2025 edition", so it may be a secondary summary rather than the regulator's text. The question to settle: did the regulator publish S1, or did someone else summarise the guidance? If someone else wrote it, the note should say "a summary of the regulator's guidance", and the quotations should be checked against the primary text.

## Refuted

- **"16.7% is wrong."** Refuted: (2.8 − 2.4) / 2.4 = 0.1667, which rounds to 16.7%.
- **"About 33 customers per employee is wrong."** Refuted: 1,240 / 38 = 32.6, which rounds to about 33.
- **"The pricing quote is paraphrased."** Refuted: it matches the answer in S3 exactly.
- **"The deletion quote is paraphrased."** Refuted: it matches S1 §4.2 exactly. The only difference is that the source's bold on "may" is not carried over, and that does not change the meaning.
- **"The note turns 'may delete' into an obligation."** Refuted: the note keeps "may".

## What holds up

- Every citation points to the right source file.
- The figures for revenue, customers and headcount all match S2.
- The quotations are verbatim.
- The note rightly limits its own evidence: it says the interview is "one interview, not a measurement of churn".
- The note correctly keeps "may delete", which is permission, separate from the 72-hour notice, which is a requirement.

## Unverified claims

None of the note's claims are unverified against the supplied sources. Whether S1 faithfully reflects the primary regulation can only be confirmed against the regulator's published text.

## Questions for the author

1. Is S1 published by the regulator, or is it a third-party summary?

## Decision-maker summary

The note is accurately sourced and its numbers check out, so the committee can rely on it as written. Two optional wording fixes would help: say that 16.7% and the per-employee figure are calculated, and quote the full 72-hour clause. One question remains open: whether the regulatory source is the regulator's own text.

## Owner summary

The note is accurate: its quotes match the sources word for word and its numbers add up. Two small wording changes would make it clearer: say which figures were calculated rather than copied, and quote the full rule on breach notice timing. It is also worth confirming that the regulation summary comes from the regulator itself.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "note.md", "status": "seen", "matters": true},
    {"item": "sources/S1-regulator-guidance.md", "status": "seen", "matters": true},
    {"item": "sources/S2-annual-report.md", "status": "seen", "matters": true},
    {"item": "sources/S3-interview-notes.md", "status": "seen", "matters": true},
    {"item": "full annual report 2025 (S2 is an extract)", "status": "not_seen", "matters": false},
    {"item": "primary regulator guidance text behind S1 summary", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Company financials and public regulatory text; no personal data."},
  "coverage": {
    "checked": [
      {"unit": "note.md", "kind": "file"},
      {"unit": "sources/S1-regulator-guidance.md", "kind": "file"},
      {"unit": "sources/S2-annual-report.md", "kind": "file"},
      {"unit": "sources/S3-interview-notes.md", "kind": "file"},
      {"unit": "note.md#Growth: 16.7% growth, $2.4m to $2.8m", "kind": "claim"},
      {"unit": "note.md#Growth: 1,240 customers, 38 staff, about 33 per employee", "kind": "claim"},
      {"unit": "note.md#Pricing: head of product quote", "kind": "claim"},
      {"unit": "note.md#Regulation: deletion quote", "kind": "claim"},
      {"unit": "note.md#Regulation: 72-hour breach notice", "kind": "claim"},
      {"unit": "note.md#Sources list", "kind": "section"}
    ],
    "not_checked": [
      {"unit": "primary regulator guidance", "reason": "not supplied"},
      {"unit": "full annual report 2025", "reason": "not supplied; only an extract given"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md: opening line 'All numbers and quotations are taken from the sources'",
     "scenario": "A committee member searches S2 for '16.7%' or '33 customers per employee', finds neither, and doubts the sourcing; both are derived by the note.",
     "fix": "Reword to 'taken from, or calculated from, the sources'.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Search S2 for '16.7' and '33': no matches; values come from (2.8-2.4)/2.4 and 1240/38."},
    {"id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md#Regulation: 'requires breach notice to the regulator \"within 72 hours\"'",
     "scenario": "A reader assumes the 72-hour clock runs from the breach itself rather than from awareness, and that it covers all breaches rather than those affecting personal data, misjudging compliance exposure.",
     "fix": "Quote the full clause from S1 4.3: 'within 72 hours of becoming aware of a breach affecting personal data'.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Compare the note's sentence with S1 section 4.3; the trigger and scope are omitted."},
    {"id": "S1", "status": "needs_validation", "track": "C",
     "location": "note.md#Regulation: 'The regulator's guidance says'; sources/S1 title 'Regulator summary'",
     "suspicion": "S1 may be a secondary summary rather than the regulator's own guidance text.",
     "unresolved_fact": "Whether S1 is published by the regulator or is a third-party summary of its guidance."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "16.7% growth figure is wrong.", "evidence": "(2.8-2.4)/2.4 = 0.1667, matching S2 figures."},
    {"id": "C2", "candidate": "'About 33 customers per employee' is wrong.", "evidence": "1240/38 = 32.6, which rounds to about 33."},
    {"id": "C3", "candidate": "Pricing quote is paraphrased.", "evidence": "Matches the S3 answer verbatim."},
    {"id": "C4", "candidate": "Deletion quote is paraphrased or turns 'may' into a duty.", "evidence": "Matches S1 4.2 verbatim (bold on 'may' omitted); 'may' is preserved."}
  ]
}
```