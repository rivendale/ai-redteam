# Red-team review: Harbor Analytics market note

**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** I had no subagent or tools in this session. I did not write this note, but no independent reviewer was available.

**VERDICT: SHIP WITH FIXES.** Every citation exists and supports its claim, every quote matches its source as supplied, and both computed figures recompute. Three Low findings concern precision and framing, not accuracy.

**CONFIDENCE: medium.** Three things limit it:
- This is a same-context review.
- With no tools, I compared the text as rendered and could not check bytes. Zero-width or look-alike characters would not be visible to me.
- I cannot confirm that the supplied source files match the real originals.

**INPUTS LEDGER**
- **Seen:**
  - request.md
  - context.md
  - note.md
  - sources/S1-regulator-guidance.md
  - sources/S2-annual-report.md
  - sources/S3-interview-notes.md
- **Not seen:**
  - The full annual report. S2 is labelled "extract".
  - The underlying regulation behind the S1 "regulator summary".
  - Neither gap matters for this review. The request limits the note to the sources/ folder, and every claim is checked against those files.

**COVERAGE**
- **Scope:** the whole note against all three sources.
- **Checked:**
  - Every sentence of note.md.
  - All three source files.
  - request.md and context.md.
  - Claims G1–G5, P1, R1–R2 and the header statement H1 (mapped below).
- **Not checked:**
  - Byte-level comparison of quotes (no tools).
  - Hidden characters (no tools).
  - Authenticity of the sources against external originals (out of scope; the request restricts the note to sources/).

**SEATS AND GATE**
- One local same-context reviewer ran.
- There was no subagent and no cross-vendor seats.
- **Sensitivity:** none found. The note contains only company figures, a public-style guidance summary and a named role, with no personal data.

---

## CLAIMS TO EVIDENCE

| Label | Location | Claim | Source / derivation | Status |
|---|---|---|---|---|
| H1 | note.md header | "All numbers and quotations are taken from the sources" | Two of the numbers (16.7%, ~33) are derived, not taken | Bounded interpretation; see F2 |
| G1 | Growth ¶1 | Revenue $2.4M (2024) → $2.8M (2025) | S2 line 3, verbatim figures | Verified observation |
| G2 | Growth ¶1 | Growth **16.7%** | (2.8 − 2.4) / 2.4 = 0.1667. Units USD millions, YoY 2024→2025 | Derived value; recomputes. Precision overstated; see F1 |
| G3 | Growth ¶1 | 1,240 customers at year end | S2: "Customer count at 31 December 2025: 1,240" | Verified observation |
| G4 | Growth ¶1 | 38 staff | S2: "Headcount at 31 December 2025: 38" | Verified observation |
| G5 | Growth ¶1 | "about 33 customers per employee" | 1,240 / 38 = 32.6. Both are point-in-time counts at 31 Dec 2025 | Derived value; recomputes and is correctly rounded |
| P1 | Pricing | Quote from the head of product, cited to [3] | S3 answer 1, verbatim match | Verified. The caveat "one interview, not a measurement" is accurate |
| R1 | Regulation | Quote beginning "may delete personal data within 30 days…" | S1 §4.2, verbatim. Only the bold on "may" is dropped, which is immaterial. Permissive "may" is preserved | Verified |
| R2 | Regulation | Breach notice to the regulator "within 72 hours" | S1 §4.3: "must notify the regulator within 72 hours of becoming aware of a breach affecting personal data" | Quote verbatim; trigger and scope omitted; see F3 |

---

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Low | CONFIRMED | C | note.md, Growth ¶1, "**16.7%**" | A growth rate given to three significant figures is computed from inputs rounded to two. | S2 gives revenue only to $0.1M. True values anywhere in $2.35–2.45M and $2.75–2.85M give growth of roughly 12.2% to 21.3%. A committee member may treat 16.7% as a reported figure and anchor a valuation or comparison on it. | Write "about 17% (computed from rounded figures in [2])", or obtain unrounded revenue from the full report. | a Y / b Y / c N / d N |
| F2 | Low | CONFIRMED | C | note.md, header sentence | "All numbers … are taken from the sources" is not literally true. The 16.7% and ~33 figures are the author's calculations, but each is cited [2] as if the report stated it. | A reader checks [2] for "16.7%" or "33 customers per employee", fails to find either, and doubts the note's citation discipline. Alternatively, the reader believes the company itself reported the figures. | Mark derived figures, e.g. "(calculated from [2])", and amend the header to "taken from or calculated from". | a Y / b Y / c N / d N |
| F3 | Low | CONFIRMED | C | note.md, Regulation ¶1, "within 72 hours" [1] | The quote is truncated before the trigger ("of becoming aware") and the scope ("a breach affecting personal data"). | A reader assumes the clock starts when the breach occurs, or that the duty covers every breach. Either reading misstates the obligation when the committee assesses compliance risk. | Quote the full clause: "within 72 hours of becoming aware of a breach affecting personal data" [1]. | a Y / b Y / c N / d N |

No High or Critical candidates arose, so the confirm-or-refute round had nothing to escalate. The sibling search found no other truncated quote or derived-but-uncited figure: P1, R1, G3 and G4 are all verbatim or directly stated.

## NEEDS VALIDATION
- **S1 (relevance of the regulation):** the note places S1 under Harbor's market note but never states that Harbor is a "hosted service" within this regulator's remit, and S1 does not mention Harbor.
  - Unresolved fact: whether Harbor is subject to this guidance.
  - The sources do not settle it. The note avoids asserting it, but placement implies it.
- **S2 (status of the regulatory source):** S1 is a "regulator summary" titled "Guidance", yet the note says it "requires" breach notice.
  - The summary itself uses "must", so the note is faithful to its source.
  - Unresolved fact: whether the underlying instrument is binding. This is outside sources/ and unknowable here.

## REFUTED
- **C1 (date drift in the pricing quote):** the interview is dated 14 March 2026, and the quote's "in the spring" could be misread as spring 2026.
  - Refuted: the question in S3 was "What changed in your pricing last year?", and the note does not attach a year.
  - There is no misstatement, though adding "(2025)" would remove the ambiguity.
- **C2 (dropped emphasis in R1):** the source bolds "**may**" and the note does not.
  - Refuted as a fidelity problem: the words are identical and the permissive sense is preserved.
- **C3 (wrong denominator in the ratio):** "staff" versus "headcount".
  - Refuted: both refer to the same 31 Dec 2025 count of 38.

## WHAT HOLDS UP
- Every citation [1]–[3] points to an existing file, and that file contains the claimed content.
- All three quotations are verbatim as rendered.
- Both derived numbers recompute correctly: 16.67% and 32.6.
- The note correctly limits the interview to anecdote ("one interview, not a measurement of churn").
- It preserves the permissive "may" in the deletion clause rather than turning it into a duty.
- It uses no material outside sources/, which fits the request.

## UNVERIFIED CLAIMS
- **Byte-identical quotes.** Confirm with a character-level diff of each quoted span against the source, including a scan for zero-width or homoglyph characters.
- **Sources match the real originals.** Confirm by comparing S2 with the filed annual report and S1 with the regulator's published text. This is outside the request's scope.

## QUESTIONS FOR THE AUTHOR
None would change the verdict. Optionally: are unrounded 2024 and 2025 revenue figures available in the full report? They would let the growth rate be stated precisely.

## DECISION-MAKER SUMMARY
The note is accurately sourced and safe to circulate after three small edits:
- round the growth figure,
- label the two calculated numbers,
- quote the breach-notice clause in full.

If it goes out unchanged, the main risk is the committee anchoring on a falsely precise 16.7% growth rate.

## OWNER SUMMARY
The note's facts and quotes all match its sources, and its two calculations are correct. Three small wording fixes would make it more precise. One growth figure is more exact than the underlying data allows, two figures are calculations rather than reported numbers and should say so, and one regulatory quote should include its full condition.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "note.md", "status": "seen", "matters": true},
    {"item": "sources/S1-regulator-guidance.md", "status": "seen", "matters": true},
    {"item": "sources/S2-annual-report.md", "status": "seen", "matters": true},
    {"item": "sources/S3-interview-notes.md", "status": "seen", "matters": true},
    {"item": "full Harbor Analytics annual report 2025 (S2 is an extract)", "status": "not_seen", "matters": false},
    {"item": "underlying regulation behind S1 summary", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Company figures, regulator summary and a role title only; no personal data."},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "note.md", "kind": "document"},
      {"unit": "sources/S1-regulator-guidance.md", "kind": "document"},
      {"unit": "sources/S2-annual-report.md", "kind": "document"},
      {"unit": "sources/S3-interview-notes.md", "kind": "document"},
      {"unit": "H1 header provenance statement", "kind": "claim"},
      {"unit": "G1 revenue 2024/2025", "kind": "claim"},
      {"unit": "G2 growth 16.7%", "kind": "claim"},
      {"unit": "G3 customers 1,240", "kind": "claim"},
      {"unit": "G4 staff 38", "kind": "claim"},
      {"unit": "G5 ~33 customers per employee", "kind": "claim"},
      {"unit": "P1 pricing quote", "kind": "claim"},
      {"unit": "R1 deletion quote", "kind": "claim"},
      {"unit": "R2 72-hour breach notice", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "byte-level quote comparison and hidden-character scan", "reason": "no_tools"},
      {"unit": "authenticity of sources against external originals", "reason": "out_of_scope"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md, Growth paragraph, '16.7%'",
     "scenario": "Inputs are rounded to $0.1M, so true growth could be about 12.2% to 21.3%; a committee member anchors on 16.7% as if it were a reported, precise figure.",
     "fix": "State 'about 17% (computed from rounded figures in [2])' or use unrounded revenue from the full report.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md, header sentence 'All numbers and quotations are taken from the sources'",
     "scenario": "16.7% and ~33 customers per employee are cited [2] but are the author's calculations; a reader checking [2] cannot find them, or believes the company reported them.",
     "fix": "Mark derived figures '(calculated from [2])' and amend the header to 'taken from or calculated from'.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md, Regulation paragraph, 'within 72 hours' [1]",
     "scenario": "The quote omits 'of becoming aware of a breach affecting personal data'; a reader assumes the clock starts at the breach or applies to all breaches, misjudging compliance risk.",
     "fix": "Quote the full clause from S1 section 4.3.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "C",
     "location": "note.md, Regulation section",
     "suspicion": "Placement implies Harbor is subject to this guidance, but no source states that Harbor is a hosted service within the regulator's remit.",
     "unresolved_fact": "Whether Harbor Analytics falls under the Data Handling Guidance for Hosted Services."},
    {"id": "S2", "status": "needs_validation", "track": "C",
     "location": "note.md, Regulation section, 'It also requires'",
     "suspicion": "S1 is a regulator summary of guidance; 'requires' may overstate binding force, though S1 itself says 'must'.",
     "unresolved_fact": "Whether the underlying instrument summarized in S1 is binding."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Pricing quote 'in the spring' misdated relative to the 14 March 2026 interview.",
     "evidence": "S3 question was 'What changed in your pricing last year?'; the note attaches no year, so there is no misstatement."},
    {"id": "C2", "candidate": "R1 quote not verbatim because source bolds 'may'.",
     "evidence": "Words are identical; the permissive sense is preserved; emphasis only."},
    {"id": "C3", "candidate": "Customers-per-employee uses the wrong denominator.",
     "evidence": "S2 headcount 38 and customers 1,240 are both at 31 December 2025; 1,240/38 = 32.6, which rounds to 33."}
  ]
}
```

I could not run `tools/validate_findings.py` because this session has no tools. The JSON follows schema 2.3 by inspection only.

There is one deliberate departure from the output note: the needs-validation items (S1, S2) carry no severity, because the skill forbids assigning severity to unconfirmed suspicions.