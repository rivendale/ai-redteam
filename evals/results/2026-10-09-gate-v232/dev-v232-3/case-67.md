# Redteam review: SupportPilot briefing

**Review mode:** I did not author this work, but I had no subagent or tools in this session. I read the supplied files directly and had nothing else to go on. Anything outside those files is marked UNVERIFIED.

**VERDICT: SHIP WITH FIXES.** Every cited claim matches its source, and the brief correctly labels the vendor figure as weak evidence. Two small wording gaps and one design weakness in the recommended trial should be fixed before a staffing decision relies on it.

**CONFIDENCE: medium.** It is limited by:
- no tools, so I could not check that the sources exist outside the supplied files;
- a single reviewer;
- the possibility that other files exist in `sources/` (the numbering starts at S3).

**INPUTS LEDGER**
- **Seen:** `request.md`, `context.md`, `brief.md`, `sources/S3-press-release.md`, `sources/S4-nine-team-study.md`.
- **Not seen:**
  - Any `S1` or `S2` files that the numbering implies. This matters only if they hold relevant evidence the brief left out. The context says all sources the author used are present, so the citations themselves are not affected.
  - The original press release and the original Public Service Analytics Unit (PSAU) study, beyond the supplied excerpts. This matters a little for the "independent" claim.

**COVERAGE**
- **Scope:** the whole work, with a claims-level focus (Track C), plus a brief Track A check of the recommendation, since a staffing decision rests on it.
- **Checked:**
  - `brief.md`, each of its five sentences;
  - both source files;
  - `request.md` (one page, sources only, every claim cited);
  - `context.md`.
- **Not checked:** external existence of either source (no tools); contents of `sources/` beyond S3 and S4 (not supplied).

**SEATS AND GATE:** One local reviewer ran. No cross-vendor seats were used (not requested, and no tools). Sensitivity gate: no personal, financial or confidential data found.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | PROBABLE | A | brief.md, "We recommend a four-week trial on one queue" | The source the brief relies on reports quarter-to-quarter variation of about 8% across nine teams (S4). That is larger than the 6% effect it measured. A four-week trial on one queue has far less data and is unlikely to separate any effect from noise. | The team runs the trial, sees a few percent change in either direction, and treats it as a result. The staffing decision then rests on noise. | Say in advance what the trial measures, which baseline variation it is compared against, and what result would count as a go or a no-go. Or lengthen it, or widen it to several queues. | a Y, b N, c N, d Y |
| F2 | Low | CONFIRMED | C | brief.md, "tried a similar tool" | S4 says only "an AI support assistant." It does not say the tool resembles SupportPilot. | A reader treats S4 as evidence about SupportPilot specifically. | Write "an AI support assistant (product not named)". | a Y, b Y, c N, d N |
| F3 | Low | CONFIRMED | C | brief.md, sentences 1 and 3 | The two figures measure different things. The vendor reports first-contact resolution; S4 reports median resolution time. The brief does not say so. | A reader compares 27% with 6% as if they were the same metric. | Add one clause noting the metrics differ and cannot be compared directly. | a Y, b Y, c N, d N |

## NEEDS VALIDATION
- **S1:** Do `sources/S1*` and `sources/S2*` exist? If so, does either contain evidence the brief omitted? The fact that would settle it is a directory listing of `sources/`.

## REFUTED
- **"27% / 41 customers misquoted":** refuted. S3 says "27% lift in first-contact resolution" and "The survey asked 41 current customers."
- **"Brief repeats the vendor's 'leading support AI' puffery":** refuted. The brief omits it.
- **"Independent label unsupported":** refuted at the level of the source. S4 states "No funding from any vendor," and the author is a public unit, so the label is supported by the source's own statement. That statement is still self-declared (see UNVERIFIED CLAIMS).

## WHAT HOLDS UP
- Every factual sentence carries a citation, and each citation says what is claimed:
  - 27% and 41 customers (S3);
  - vendor survey of its own customers ("a survey of our own customers," S3);
  - 9 teams, one quarter, −6% median, indistinguishable from about 8% variation (S4);
  - 2025 (S4 title).
- The brief correctly weights the vendor figure as non-independent and non-controlled.
- It uses only the supplied sources and fits on one page.

## UNVERIFIED CLAIMS
- That the press release (March 2026) and the PSAU study (2025) exist as published. Confirm by locating the originals.
- S4's "no vendor funding." Confirm from the study's funding statement in the original publication.

## QUESTIONS FOR THE AUTHOR
1. Are there other files in `sources/` that you chose not to use, and why?
2. What result from the four-week trial would change the recommendation, and how will it be told apart from normal variation?

## DECISION-MAKER SUMMARY
The citations are accurate and the evidence is weighted honestly. The brief is safe to circulate after two one-clause wording fixes. Before acting on the recommended trial, set its success threshold against the roughly 8% normal variation reported in S4. Otherwise a four-week, one-queue result will likely be noise.

## OWNER SUMMARY
The briefing reports its sources accurately and is honest that the vendor's numbers come from the vendor itself. Two small wording changes would stop readers comparing figures that measure different things. The proposed short trial should state up front what result would count as success, because normal week-to-week swings could otherwise be mistaken for an effect.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "brief.md", "status": "seen", "matters": true},
    {"item": "sources/S3-press-release.md", "status": "seen", "matters": true},
    {"item": "sources/S4-nine-team-study.md", "status": "seen", "matters": true},
    {"item": "sources/S1*, sources/S2* (implied by numbering)", "status": "not_seen", "matters": false},
    {"item": "original press release and PSAU study", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "brief.md", "kind": "document"},
      {"unit": "sources/S3-press-release.md", "kind": "document"},
      {"unit": "sources/S4-nine-team-study.md", "kind": "document"},
      {"unit": "brief.md: 27% / 41 customers claim", "kind": "claim"},
      {"unit": "brief.md: vendor survey not controlled", "kind": "claim"},
      {"unit": "brief.md: 9-team study figures", "kind": "claim"},
      {"unit": "brief.md: four-week trial recommendation", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "external existence of S3/S4 originals", "reason": "no_tools"},
      {"unit": "other files in sources/", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "A",
     "location": "brief.md: 'We recommend a four-week trial on one queue'",
     "scenario": "S4 reports ~8% quarter-to-quarter variation exceeding a 6% effect; a four-week single-queue trial yields a change within noise that is then read as a result, steering the staffing decision.",
     "fix": "Pre-register the metric, baseline variation and go/no-go threshold, or lengthen/widen the trial.",
     "answers": {"a": true, "b": false, "c": false, "d": true}},
    {"id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "C",
     "location": "brief.md: 'tried a similar tool'",
     "scenario": "S4 says only 'an AI support assistant'; a reader treats it as evidence about SupportPilot specifically.",
     "fix": "Write 'an AI support assistant (product not named)'.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "C",
     "location": "brief.md: sentences 1 and 3",
     "scenario": "Vendor figure is first-contact resolution, study figure is median resolution time; a reader compares 27% with 6% as like for like.",
     "fix": "Add a clause noting the metrics differ.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "C", "location": "sources/",
     "suspicion": "Numbering starts at S3; S1/S2 may exist and hold evidence the brief omitted.",
     "unresolved_fact": "A listing and read of all files in sources/."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "27% / 41 customers misquoted.", "evidence": "S3: '27% lift in first-contact resolution'; 'The survey asked 41 current customers.'"},
    {"id": "C2", "candidate": "Brief repeats vendor 'leading support AI' claim.", "evidence": "Phrase does not appear in brief.md."},
    {"id": "C3", "candidate": "'Independent' label unsupported.", "evidence": "S4: 'No funding from any vendor'; publisher is a public unit."}
  ]
}
```