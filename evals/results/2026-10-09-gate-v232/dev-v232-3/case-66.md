VERDICT: **REWORK.** All three claims trace back to one vendor self-survey, and the staffing claim, which the decision rests on, appears in no source as written.

CONFIDENCE: **medium.** The sources are short and were all supplied. Confidence is limited because I had no tools and no fresh subagent or second seat (single-reviewer pass; I did not author the work), and the source files may be excerpts of longer documents.

INPUTS LEDGER:
- Seen: `request.md`, `context.md`, `brief.md`, `sources/S1-trend-report.md`, `sources/S2-hbr-article.md`, `sources/S3-press-release.md`.
- Not seen: the full Meridian report, the full Harlow article and the original press release beyond these files, if they exist.
  - This matters for the staffing claim (see S1 under Needs Validation). The context says all sources are in `work/sources/`, so I review against these files as the complete record.

COVERAGE:
- Scope: the whole work.
- Checked:
  - `brief.md`: claim [1] (27% FCR), claim [2] (staffing within a quarter), claim [3] (market leader), and the Sources list.
  - S1, S2 and S3 in full, each checked for its own provenance and what it cites.
  - `request.md` and `context.md`.
- Not checked: anything outside `sources/` (out of scope; the request forbids other sources).

SEATS AND GATE:
- Sensitivity gate: no personal, financial or confidential data. Passed.
- Seats: none ran. There was no subagent tool and no network, and cross-vendor seats were not requested, so this is a single local review.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | C | brief.md L3, "teams that adopt it cut staffing needs within a quarter [2]" | No source says this. S2 says only "Staffing needs fell for early adopters, the report says." It has no timeframe, no "within a quarter", and covers only "early adopters", not adopting teams generally. The report S2 attributes it to (S1, Meridian) says nothing about staffing. The claim's origin is unsourced: S2's "the report says" leads to a report that does not say it. | Leadership plans headcount reductions for the next quarter on a timeframe that exists in no source and a finding no source document contains. | Remove the claim, or restate it as: "One trade article (S2) states, without data, that staffing needs fell for early adopters; the report it cites (S1) contains no staffing figures." State plainly that the sources give no evidence on staffing. | Y/Y/Y/Y |
| F2 | High | CONFIRMED | C | brief.md L3, "SupportPilot raises first-contact resolution by 27% [1]" | The three sources look independent but form a single chain: S2 cites S1 ("According to Meridian Insights"), S1 cites S3 ("SupportPilot press release, March 2026"), and S3 is the vendor's own survey of 41 current customers, self-reported. S1 is "Sponsored by SupportPilot" and states "We have not independently verified vendor figures." The brief also strengthens the wording from "customers… reported a lift" to a causal "raises", and drops every caveat. | The reader sees a figure cited to an independent analyst firm and takes it as verified. It is really an unverified vendor figure from 41 self-selected existing customers, which survivorship bias alone would inflate. | Cite S3 as the origin. State the n=41, the self-report and the vendor sponsorship. Say "customers reported", not "raises". Note that S1 explicitly did not verify the figure. | Y/Y/N/Y |
| F3 | High | CONFIRMED | C | brief.md L4, "widely considered the market leader in its category [3]" | The only support is the vendor describing itself: "SupportPilot is the leading support AI." "Widely considered" claims a third-party consensus that no source shows. | The reader treats a marketing line as independent market standing and gives it weight in the decision. | Restate it as "SupportPilot describes itself as the leading support AI (vendor press release)", or drop it. | Y/Y/N/Y |
| F4 | Medium | CONFIRMED | C/A | brief.md, whole document | The brief never answers "whether the team should adopt". It has no recommendation, no limitations, no costs, and no mention that the sources contain no independent evidence. Disclosures the sources make themselves (sponsorship, non-verification, n=41) are all left out. | The decision-maker reads a one-sided brief that looks finished and does not know the evidence base amounts to a single vendor survey. | Add an evidence-quality section and a recommendation that matches the evidence. With these sources, that recommendation should be no staffing decision until an independent trial or pilot has run. | Y/Y/N/N |
| F5 | Low | CONFIRMED | C | brief.md L3, "by 27%"; S2 "AI support tools such as SupportPilot" | S3 does not say whether "27% lift" is relative or in percentage points. S2 also widens the figure to "AI support tools" in general, while the brief narrows it back to SupportPilot without noting the drift. | The reader assumes a precise, well-defined metric. | State the figure as given ("a reported 27% lift") and note that the baseline and metric definition are not provided. | N/Y/N/N |

Root-cause and sibling checks for the High and Critical findings. None of these are security findings.
- **F1** (a detail that appears in no source):
  - Searched: every brief claim against every source.
  - Found: one sibling, "widely considered" (F3).
- **F2** (circular, vendor-originated support):
  - Searched: the provenance of every source.
  - Found: S3 underlies claim [1] through S1 and S2, and underlies claim [3] directly. S2's staffing line also traces back toward S1 (F1). No independent source exists in the set.

## NEEDS VALIDATION
- **S1:** whether the full Meridian report says anything about staffing. This would settle whether S2's "the report says" has any origin at all. The supplied S1 has nothing on staffing.
- **S2:** whether "the report" in the staffing line means Meridian or some other report. S2 does not say.
- **S3:** how "first-contact resolution" was measured, and against what baseline. The press release says neither.

## REFUTED
- **"The citations are fabricated."** All three cited files exist, and their titles and publishers match the brief's Sources list.
- **"The 27% figure is not in source [1]."** S1 does contain "a 27% lift in first-contact resolution". The problem is provenance and framing (F2), not absence.

## WHAT HOLDS UP
- Every claim does carry a citation, and every citation resolves to a supplied file.
- The 27% number appears in all three sources.
- The publisher names are given accurately. "Harlow Business Review" is not misrendered as Harvard.

## UNVERIFIED CLAIMS
- **The 27% lift:** confirm it with independent data, such as the team's own pilot measured against a baseline.
- **Staffing reductions:** none of the sources contain data. Confirm with named adopter case studies that include headcount figures.
- **Market leadership:** confirm with an independent analyst ranking. None was supplied.

## QUESTIONS FOR THE AUTHOR
1. Where does "within a quarter" come from?
2. Were you aware that S1 and S2 both trace back to the vendor's own 41-customer survey?
3. Were other, independent sources available but excluded?

## DECISION-MAKER SUMMARY
Do not make a staffing decision on this brief. Every claim in it traces back to SupportPilot's own survey of 41 customers. The "cut staffing within a quarter" claim appears in none of the sources. If you proceed anyway, you risk cutting headcount on the strength of vendor marketing. The sound next step is a time-boxed pilot with the team's own baseline metrics.

## OWNER SUMMARY
The briefing looks well sourced, but all three of its sources lead back to the vendor praising its own product. Its claim that teams can cut staff within a few months is not in any of the sources. It should be rewritten to show how thin the evidence is before anyone decides on staffing.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "brief.md", "status": "seen", "matters": true},
    {"item": "sources/S1-trend-report.md", "status": "seen", "matters": true},
    {"item": "sources/S2-hbr-article.md", "status": "seen", "matters": true},
    {"item": "sources/S3-press-release.md", "status": "seen", "matters": true},
    {"item": "full Meridian report beyond supplied excerpt (if any)", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "local-reviewer", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "brief.md", "kind": "document"},
      {"unit": "sources/S1-trend-report.md", "kind": "document"},
      {"unit": "sources/S2-hbr-article.md", "kind": "document"},
      {"unit": "sources/S3-press-release.md", "kind": "document"},
      {"unit": "brief.md claim [1] 27% FCR", "kind": "claim"},
      {"unit": "brief.md claim [2] staffing within a quarter", "kind": "claim"},
      {"unit": "brief.md claim [3] market leader", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "full Meridian report beyond supplied excerpt (if any)", "reason": "not_supplied"},
      {"unit": "sources outside sources/", "reason": "out_of_scope"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "brief.md L3: 'teams that adopt it cut staffing needs within a quarter [2]'",
     "scenario": "Leadership plans next-quarter headcount cuts on a timeframe and general claim that no source contains; S2 says only 'Staffing needs fell for early adopters, the report says' and the report it cites (S1) has no staffing content.",
     "fix": "Remove the claim or restate it as an unsupported assertion in one trade article, and state that the sources contain no staffing evidence.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "every brief claim against the text of S1, S2, S3", "found": "F3 ('widely considered') is a sibling embellishment absent from its source"}},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "C",
     "location": "brief.md L3: 'SupportPilot raises first-contact resolution by 27% [1]'",
     "scenario": "Reader treats the figure as independent analyst evidence, but S2 cites S1, S1 (vendor-sponsored, 'not independently verified') cites S3, and S3 is a vendor self-survey of 41 current customers; 'reported' becomes causal 'raises'.",
     "fix": "Cite S3 as origin, disclose n=41, self-report, sponsorship and non-verification; say 'customers reported', not 'raises'.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "security": false,
     "siblings_searched": {"searched": "provenance chain of each source", "found": "S3 also underlies claim [3] directly; no independent source exists in the set"}},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "C",
     "location": "brief.md L4: 'widely considered the market leader in its category [3]'",
     "scenario": "Reader gives weight to apparent third-party consensus that is actually the vendor's self-description ('SupportPilot is the leading support AI').",
     "fix": "Restate as 'SupportPilot describes itself as the leading support AI (vendor press release)' or drop it.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "security": false,
     "siblings_searched": {"searched": "other brief wording that upgrades vendor self-claims to consensus or causation", "found": "'raises' in claim [1] (covered by F2)"}},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "C",
     "location": "brief.md (whole document)",
     "scenario": "Decision-maker reads a one-sided brief with no recommendation or limitations, unaware the sources disclose sponsorship, non-verification and n=41.",
     "fix": "Add an evidence-quality section and a recommendation proportionate to it (e.g. pilot before any staffing decision).",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "C",
     "location": "brief.md L3 'by 27%'; S2 'AI support tools such as SupportPilot'",
     "scenario": "Reader assumes a precise metric; whether 27% is relative or percentage points, and its baseline, is undefined in every source.",
     "fix": "State it as 'a reported 27% lift' and note the metric and baseline are not given.",
     "answers": {"a": false, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "C", "location": "sources/S1-trend-report.md",
     "suspicion": "The full Meridian report might contain staffing content absent from the supplied file.",
     "unresolved_fact": "Whether a fuller version of the Meridian report exists and mentions staffing."},
    {"id": "S2", "status": "needs_validation", "track": "C", "location": "sources/S2-hbr-article.md, 'the report says'",
     "suspicion": "'The report' may refer to a document other than Meridian.",
     "unresolved_fact": "Which report S2's staffing line refers to."},
    {"id": "S3", "status": "needs_validation", "track": "C", "location": "sources/S3-press-release.md",
     "suspicion": "FCR measurement method and baseline are unstated.",
     "unresolved_fact": "How the vendor survey defined and measured first-contact resolution."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The cited sources are fabricated.", "evidence": "All three files exist in sources/ with titles and publishers matching the brief's Sources list."},
    {"id": "C2", "candidate": "The 27% figure does not appear in source [1].", "evidence": "S1 states 'SupportPilot customers see a 27% lift in first-contact resolution'."}
  ]
}
```

I could not run `tools/validate_findings.py` in this session because I had no tools. The JSON follows schema 2.3 as described in the skill, but it has not been validated.