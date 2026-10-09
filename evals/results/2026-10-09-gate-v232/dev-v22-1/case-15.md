# Redteam review: Harbor Analytics market note

**VERDICT: SHIP.** Every cited source exists and says what the note claims, both quotations are verbatim, and both computed figures recompute. Two Low wording fixes are recommended but none blocks reliance.

**CONFIDENCE: high** for the checks done. The work is short and all sources were supplied inline, so every claim was matched against its source text and every figure was recomputed by hand. Limits:
- This is a review with no tools. I could not confirm that the files on disk match the text supplied here.
- No independent subagent was available. The note was not written in this conversation, so the anchoring risk is low.

**INPUTS LEDGER**
- Seen: `request.md`, `context.md`, `note.md`, `sources/S1-regulator-guidance.md`, `sources/S2-annual-report.md`, `sources/S3-interview-notes.md`.
- Not seen:
  - The full regulation behind the S1 "regulator summary". It does not matter for this review, because the request limits the note to `sources/`. It is noted under NEEDS VALIDATION.
  - The full annual report (S2 is an extract). It does not matter, because every S2 figure the note uses appears in the extract.

**COVERAGE**
- Checked:
  - Claims: growth 16.7%, revenue $2.4m to $2.8m, customers 1,240, staff 38, ~33 customers per employee, the pricing quote and its attribution, the deletion quote, the 72-hour breach quote, the source list entries and dates, and the header claim "All numbers and quotations are taken from the sources".
  - Requirement fit: only `sources/` was used, each claim is cited, and quotes are exact.
- Not checked: anything outside the supplied files; whether S1 is still current as of 2026-10-08.

**SEATS AND GATE**
- Ran: one local reviewer (same vendor).
- No cross-vendor seats were requested at `standard` depth.
- Sensitivity gate: passed. The work contains no personal data, credentials or client records; the interviewee is identified only by role.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Low | CONFIRMED | C | `note.md`, Regulation, "breach notice to the regulator 'within 72 hours' [1]" | The quote is verbatim but cut before its trigger. S1 §4.3 reads "within 72 hours **of becoming aware of** a breach affecting personal data". | A committee member reads the deadline as 72 hours from when the breach occurred, which is stricter than the source. Or they miss that it applies only to breaches affecting personal data. Either way, compliance-risk discussion rests on a narrower or wrong obligation. | Quote the full clause: "within 72 hours of becoming aware of a breach affecting personal data" [1]. Check: compare the note's sentence with S1 §4.3. The trigger phrase is absent from the note. | a:Y b:Y c:N d:N |
| F2 | Low | CONFIRMED | C | `note.md` header ("All numbers… are taken from the sources") and Growth ("**16.7%**… [2]", "about 33 customers per employee") | 16.7% and ~33 do not appear in S2. They are the author's own calculations, but they are cited to [2] and covered by the claim that all numbers are "taken from" the sources. | A reader searches S2 for 16.7% to audit it, finds nothing, and doubts the note. Or a later edit changes an input and the "sourced" derived figure is never rechecked. | Mark them as computed, e.g. "16.7% (computed from [2]: 2.8/2.4 − 1)" and "≈33 (1,240 ÷ 38, computed)". Change the header to "taken from or computed from". Check: search S2 for "16.7" or "33"; there are no hits. The positive control is that "1,240" is found in S2. | a:Y b:Y c:N d:N |

## NEEDS VALIDATION
- **S1 currency.** S1 is a "2025 edition" regulator summary, and the review date is 2026-10-08. To settle: has a later edition been issued, or have §4.2 or §4.3 been amended? Under the request this does not affect citation accuracy, but it matters for a committee relying on the note.
- **Summary versus rule text.** S1 is a summary, not the rule itself. To settle: does the underlying rule use the same permissive "may" for deletion and the same 72-hour, from-awareness trigger? The note correctly says "guidance" and quotes "may", so this is a question about the source, not an error in the note.

## REFUTED
- **"16.7% growth is wrong."** Refuted: (2.8 − 2.4) / 2.4 = 0.1667, which is 16.7%.
- **"~33 customers per employee is wrong."** Refuted: 1,240 / 38 = 32.63, which rounds to 33, and the note says "about".
- **"The pricing quote is altered."** Refuted: it matches S3 word for word. Only the closing period moved outside the quotation marks, which is standard punctuation.
- **"The deletion quote turns 'may' into an obligation."** Refuted: the note quotes "may delete" verbatim and frames it as what the guidance "says", not as a requirement.
- **"'Requires' overstates the breach notice."** Refuted: S1 §4.3 says "must notify".
- **"The interview is misdated or misattributed."** Refuted: the note's source 3 gives "head of product, Harbor Analytics, 14 March 2026", which matches the S3 header. The note dates the pricing change only as "in the spring", which matches the quote.

## WHAT HOLDS UP
- Every claim carries a citation, and every citation points to a supplied file that contains the claimed content.
- Revenue, customer count, headcount and the "ended the year" timing (31 December 2025) all match S2.
- Both quotations are verbatim.
- The note handles evidence quality well: it labels the churn claim as "one interview, not a measurement of churn". That stops anecdote being read as data.
- No material outside `sources/` was introduced.
- The note does not cite the other S3 answer (on-premises requests). That omission is a scoping choice, not a misstatement.

## UNVERIFIED CLAIMS
- That the supplied file text matches the files in `work/sources/`. To confirm: diff the files on disk against the text reviewed here.

## QUESTIONS FOR THE AUTHOR
- None would change the verdict.
- Optional: is there a newer edition of the S1 guidance?

## DECISION-MAKER SUMMARY
The note is accurate to its sources: figures recompute and quotes are exact, so the committee can rely on it as written. Two small wording fixes would make it more precise: give the full 72-hour trigger, and mark the two computed figures as computed. The remaining risk is that S1 is a 2025 summary that may since have been superseded.

## OWNER SUMMARY
The note matches its sources: the numbers add up and the quotes are word for word. Two small edits are suggested: spell out that the 72-hour breach deadline starts when the company becomes aware of the breach, and say that the growth rate and customers-per-employee figure were calculated rather than copied. It is also worth checking that the regulator's 2025 guidance has not been replaced by a newer version.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "note.md", "status": "seen", "matters": true},
    {"item": "sources/S1-regulator-guidance.md", "status": "seen", "matters": true},
    {"item": "sources/S2-annual-report.md", "status": "seen", "matters": true},
    {"item": "sources/S3-interview-notes.md", "status": "seen", "matters": true},
    {"item": "Underlying regulation text behind S1 summary", "status": "not_seen", "matters": false},
    {"item": "Full Harbor Analytics annual report 2025", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "No personal data, credentials or client records; interviewee identified by role only."},
  "coverage": {
    "checked": [
      {"unit": "note.md", "kind": "file"},
      {"unit": "sources/S1-regulator-guidance.md", "kind": "file"},
      {"unit": "sources/S2-annual-report.md", "kind": "file"},
      {"unit": "sources/S3-interview-notes.md", "kind": "file"},
      {"unit": "request.md", "kind": "file"},
      {"unit": "context.md", "kind": "file"},
      {"unit": "Revenue growth 16.7% from $2.4m to $2.8m", "kind": "claim"},
      {"unit": "1,240 customers and 38 staff, about 33 customers per employee", "kind": "claim"},
      {"unit": "Pricing quote, head of product", "kind": "claim"},
      {"unit": "Deletion-request quote, S1 4.2", "kind": "claim"},
      {"unit": "72-hour breach notice, S1 4.3", "kind": "claim"},
      {"unit": "Header: all numbers and quotations taken from sources", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "Currency of S1 2025 edition as of 2026-10-08", "reason": "no tools; outside supplied sources"},
      {"unit": "On-disk files in work/sources/ versus supplied text", "reason": "no tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md, Regulation section, 'breach notice to the regulator \"within 72 hours\" [1]'",
     "scenario": "The quote omits S1 4.3's trigger 'of becoming aware of a breach affecting personal data'; a committee member reads the deadline as running from the breach itself or applying to all breaches, misjudging the obligation.",
     "fix": "Quote the full clause: \"within 72 hours of becoming aware of a breach affecting personal data\" [1].",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Compare the note's sentence with S1 section 4.3; the phrase 'of becoming aware' is absent from the note."},
    {"id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md, header line and Growth section ('16.7%' [2]; 'about 33 customers per employee')",
     "scenario": "16.7% and ~33 are computed, not stated in S2, yet are cited to [2] and covered by 'all numbers are taken from the sources'; an auditor searching S2 for them finds nothing.",
     "fix": "Mark both as computed from [2] with the formula, and change the header to 'taken from or computed from the sources'.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Search S2 for '16.7' and '33': no hits (positive control: '1,240' is found)."},
    {"id": "S1", "status": "needs_validation", "track": "C", "location": "note.md, Sources item 1; sources/S1-regulator-guidance.md",
     "suspicion": "The 2025 edition of the regulator summary may have been superseded by the review date 2026-10-08.",
     "unresolved_fact": "Whether a later edition exists or sections 4.2 or 4.3 were amended."},
    {"id": "S2", "status": "needs_validation", "track": "C", "location": "sources/S1-regulator-guidance.md, sections 4.2 and 4.3",
     "suspicion": "S1 is a summary; the underlying rule text may differ from it.",
     "unresolved_fact": "Whether the underlying rule uses the same permissive 'may' for deletion and the same 72-hour from-awareness trigger."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "16.7% growth is miscomputed.", "evidence": "(2.8 - 2.4) / 2.4 = 0.1667."},
    {"id": "C2", "candidate": "About 33 customers per employee is miscomputed.", "evidence": "1,240 / 38 = 32.63, which rounds to 33."},
    {"id": "C3", "candidate": "Pricing quote is not verbatim.", "evidence": "Matches S3 word for word; only the closing period moved outside the quotation marks."},
    {"id": "C4", "candidate": "Deletion quote turns a permission into a duty.", "evidence": "The note quotes 'may delete' verbatim and frames it as what the guidance 'says'."},
    {"id": "C5", "candidate": "'Requires' overstates the breach-notice duty.", "evidence": "S1 4.3 says 'must notify'."},
    {"id": "C6", "candidate": "Interview misdated or misattributed.", "evidence": "Note's source 3 gives head of product, Harbor Analytics, 14 March 2026, matching the S3 header."}
  ]
}
```