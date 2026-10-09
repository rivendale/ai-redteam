# Redteam report: Harbor Analytics market note

**Same-context review, no tools.** No subagent or file access was available in this session. The note was supplied as input and was not written in this conversation, so the anchoring risk is lower. Still, re-run it in a fresh session before the committee relies on it. All checks below are against the source text pasted into the inputs.

**VERDICT: SHIP WITH FIXES.** Every cited claim matches its source, every quote is verbatim, and every number recomputes. The remaining issues are a clipped regulatory quote, more precision in the growth figure than the inputs support, and a material risk from the sources that the note leaves out.

**CONFIDENCE: medium.** Limited by the same-context review, no tools, and only an extract of the annual report.

**INPUTS LEDGER**
- **Seen:**
  - request.md
  - context.md
  - note.md
  - sources/S1-regulator-guidance.md
  - sources/S2-annual-report.md
  - sources/S3-interview-notes.md
- **Not seen:**
  - **Full 2025 annual report.** S2 is an extract. This does not matter for the claims made, because each one is in the extract.
  - **The underlying regulation behind the S1 "summary".** This matters only if the committee treats the summary as the rule itself (see S1 below).

**COVERAGE**
- **Checked:**
  - note.md, all sections: Growth, Pricing, Regulation, Sources
  - Each of the 7 factual claims and both derived figures
  - All 3 quotations, compared word by word
  - All 3 source files
- **Not checked:**
  - The full annual report
  - The primary regulation text

**SEATS AND GATE**
- Sensitivity gate: passed. The material is published company figures, regulator guidance and an attributed interview by role only, with no personal data.
- Seats: one local reviewer only.
- Cross-vendor seats: not requested and no tools were available, so none ran.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Low | CONFIRMED | C | note.md, Regulation: "within 72 hours" [1] | The quote is clipped. The source says "within 72 hours **of becoming aware** of a breach **affecting personal data**." The note drops both the point the clock starts and the scope. | A reader assumes the 72 hours run from when the breach occurs, or apply to any breach, and misjudges Harbor's compliance exposure. | Quote the full clause: "must notify the regulator within 72 hours of becoming aware of a breach affecting personal data" (S1 §4.3). | a Y, b Y, c N, d N |
| F2 | Low | PROBABLE | C | note.md, Growth: "**16.7%**" | The arithmetic is correct: 0.4 / 2.4 = 16.67%. But S2 gives revenue to the nearest $0.1M. If those are rounded figures, true growth lies anywhere from 12.2% (2.75/2.45) to 21.3% (2.85/2.35), so one decimal place overstates precision. | The committee compares 16.7% with a peer's 17.5% and draws a distinction the data cannot support. | Write "about 17%", or get unrounded revenue from the full report. | a Y, b N, c N, d N |
| F3 | Low | CONFIRMED | C/A | note.md, whole note, against S3 line 5 | The note uses S3 only for the pricing positive. It leaves out the interviewee's answer to "biggest risk": "Larger customers are asking for on-premises installs, which we do not offer." | The committee reads a note that is positive on growth and pricing and never sees the risk the company itself named. | Add one cited sentence quoting the S3 risk answer. | a Y, b Y, c N, d N |

### NEEDS VALIDATION
- **S1:** The note says "The regulator's guidance says…" but the source is titled "Regulator summary". It is unresolved whether this is the regulator's own authoritative text or a secondary summary. If it is secondary, the note should say so and the committee should not treat it as rule text.

### REFUTED
- **R1: the S1 quote drops the bold on "may".** The note keeps the word "may" and presents the deletion provision as permissive, which is the sense the emphasis carries. The words are verbatim, so there is no distortion.
- **R2: the pricing quote is not verbatim.** It matches S3 word for word. Only the closing period moved outside the quotation marks, which is a punctuation convention.
- **R3: "about 33 customers per employee" is uncited.** It is derived from two cited figures and recomputes: 1,240 / 38 = 32.6, which rounds to 33.

## WHAT HOLDS UP
- **Revenue:** $2.4M in 2024 and $2.8M in 2025 match S2, and the 16.7% growth recomputes.
- **Customers and staff:** 1,240 customers and 38 staff match S2, and both are dated 31 December 2025, which supports "ended the year".
- **Pricing quote:** verbatim. The caveat "one interview, not a measurement of churn" is correct and appropriately cautious.
- **Deletion quote:** verbatim. "May" is correctly kept as permissive rather than turned into an obligation.
- **"Requires" for breach notice:** correct, because the source says "must".
- **Source list:** all three sources exist, with titles and dates matching their headers.

## UNVERIFIED CLAIMS
- **Whether S2's revenue figures are rounded.** Check the full annual report.
- **Whether S1 is authoritative regulator text.** Check its provenance.

## QUESTIONS FOR THE AUTHOR
1. Is S1 the regulator's own publication, or a third-party summary?
2. Did the omission of the on-premises risk reflect a scope decision?

## DECISION-MAKER SUMMARY
The note's facts, quotes and arithmetic all check out against the supplied sources. Before circulating it, restore the full 72-hour clause, round the growth figure to "about 17%", and add the company's own stated on-premises risk. Proceeding as is risks a one-sided read, not a factual error.

## OWNER SUMMARY
The note is accurate: its numbers, quotes and sources all match. Three small edits would make it safer to rely on: complete one shortened regulatory quote, avoid overly precise growth figures, and mention the main risk the company itself named. None of these change the facts already in the note.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "note.md", "status": "seen", "matters": true},
    {"item": "sources/S1-regulator-guidance.md", "status": "seen", "matters": true},
    {"item": "sources/S2-annual-report.md", "status": "seen", "matters": true},
    {"item": "sources/S3-interview-notes.md", "status": "seen", "matters": true},
    {"item": "Full Harbor Analytics annual report 2025", "status": "not_seen", "matters": false},
    {"item": "Primary regulation underlying S1 summary", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-local-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Public company figures, regulator guidance, role-attributed interview; no personal data."},
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
      {"unit": "Revenue growth 16.7% recompute", "kind": "claim"},
      {"unit": "Customers per employee ~33 recompute", "kind": "claim"},
      {"unit": "Three quotations verbatim check", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "Full annual report 2025", "reason": "not supplied; only extract provided"},
      {"unit": "Primary regulation text", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md Regulation: \"within 72 hours\" [1]; S1 §4.3",
     "scenario": "The quote omits 'of becoming aware of a breach affecting personal data'; a reader assumes the clock starts at the breach or applies to all breaches and misjudges compliance exposure.",
     "fix": "Quote the full clause from S1 §4.3.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "PROBABLE", "track": "C",
     "location": "note.md Growth: \"16.7%\"; S2 line 3",
     "scenario": "Revenue is given to $0.1M; if rounded, true growth is anywhere from 12.2% to 21.3%, so 16.7% implies false precision in peer comparisons.",
     "fix": "State 'about 17%' or obtain unrounded revenue from the full report.",
     "answers": {"a": true, "b": false, "c": false, "d": false}},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md (whole); S3 'biggest risk' answer",
     "scenario": "The note omits the company's own stated biggest risk (on-premises demand it cannot serve), so the committee sees only positives from S3.",
     "fix": "Add one cited sentence quoting the S3 risk answer.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "C",
     "location": "note.md Regulation: \"The regulator's guidance says\"; S1 title",
     "suspicion": "S1 is labelled a 'summary' but is presented as the regulator's guidance itself.",
     "unresolved_fact": "Whether S1 is authoritative regulator text or a secondary summary."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "S1 quote drops bold emphasis on 'may'.", "evidence": "The words are verbatim and 'may' is kept as permissive; the meaning is preserved."},
    {"id": "R2", "candidate": "Pricing quote is not verbatim.", "evidence": "It matches S3 word for word; only the terminal period moved outside the quotation marks."},
    {"id": "R3", "candidate": "'About 33 customers per employee' is uncited.", "evidence": "Derived from cited S2 figures: 1240/38 = 32.6."}
  ]
}
```