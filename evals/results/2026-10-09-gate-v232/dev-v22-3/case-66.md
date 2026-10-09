**Single-reviewer review with no tools.** This is not a same-context review, since the work was not written in this conversation. But no subagent or cross-vendor seat was available, and I could not open files beyond the text supplied in the prompt.

**VERDICT: REWORK.** All three citations trace back to one vendor self-survey of 41 customers. The staffing claim, which is the one the decision rests on, has no root source in any supplied document.

**CONFIDENCE: medium.** I checked each claim against the full supplied source text, quoted below. What limits confidence:
- I had no tools.
- I cannot confirm the source files are complete documents rather than excerpts.

**INPUTS LEDGER**
- **Seen:** the request, the context, `brief.md`, and S1, S2 and S3 in full as supplied.
- **Not seen:** the full Meridian report beyond the S1 text, and the underlying SupportPilot survey (method, baseline, response rate).
  - This gap matters for F2 only if the full report contains a staffing finding.
  - The context says all sources the author used are in `sources/`, so the author had no more than I do.

**COVERAGE**
- **Checked:**
  - all three claims in `brief.md:3-4`
  - the source list at `brief.md:6-9`
  - every sentence of S1, S2 and S3
  - the citation chain between the three sources
  - the independence of each source
- **Not checked:**
  - anything outside `sources/`
  - whether "27%" is relative or percentage points, since no source says

**SEATS AND GATE**
- Only the local reviewer ran.
- No sensitive data was present, so the gate passed.
- No cross-vendor seats ran: none were requested and no tools were available.
- I found no injected instructions in the work.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | C | `brief.md:3` "teams that adopt it cut staffing needs within a quarter [2]" | No source supports the claim. S2 only says "Staffing needs fell for early adopters, the report says," and attributes this to Meridian. S1, the Meridian text, says nothing about staffing. "Within a quarter" appears in no source at all. The brief also turns "fell" into "cut". | Leadership reduces support headcount expecting savings within a quarter. That expectation rests on a secondhand attribution that does not reproduce in the document it points to. | Remove the claim, or cite a source that states it directly. To reproduce: search S1 for "staff" or "quarter" and you get no matches. As a positive control, searching S1 for "27%" does match. | a✓ b✓ c✓ d✓ |
| F2 | High | CONFIRMED | C | `brief.md:3` "raises first-contact resolution by 27% [1]" | Two problems: circular sourcing, and the claim is stated more strongly than the source. **Circular sourcing:** S1 credits the figure to "SupportPilot press release, March 2026", says "We have not independently verified vendor figures", and is "Sponsored by SupportPilot". S2 credits the same figure to Meridian. S3 shows the origin: "a survey of our own customers… 41 current customers". So one vendor self-report appears to be backed by two independent sources. **Overstated:** "users reported a 27% lift" (a self-reported perception among current customers who stayed) becomes "raises", a measured causal effect. | The team expects a 27% gain in first-contact resolution. The real basis is 41 retained customers' perceptions, collected by the vendor. | Restate the claim as: "SupportPilot reports that 41 of its current customers reported a 27% lift (vendor survey; Meridian, sponsored by SupportPilot, did not verify it)." Then cite S3 as the origin. To reproduce, quote S1 sentences 2–4 alongside S3's parenthetical. | a✓ b✓ c✗ d✓ |
| F3 | High | CONFIRMED | C | `brief.md:4` "widely considered the market leader in its category [3]" | The cited source is the vendor's own press release asserting "SupportPilot is the leading support AI." That is one self-claim, not a wide consensus, and no source supplies "widely considered". | A reader takes vendor marketing for independent market standing and skips comparing alternatives. | Delete the claim, or write "SupportPilot describes itself as the leading support AI [3]". To reproduce, S3 is the only citation and its author is the vendor. | a✓ b✓ c✗ d✓ |
| F4 | Medium | CONFIRMED | A/C | `brief.md` whole document | The brief keeps only the favorable claims and drops the caveats the sources themselves give: unverified, sponsored, n=41, current customers only. It gives no recommendation, risks or costs, even though the request asked "whether" the team should adopt the tool. | The decision-maker reads a one-sided brief as balanced. | Add a limitations paragraph built from the sources' own caveats, plus an explicit recommendation. Given the evidence, the recommendation should be "insufficient independent evidence; pilot before staffing changes". | a✓ b✓ c✗ d✗ |

### NEEDS VALIDATION
- **S1: does the full Meridian report contain a staffing finding?** The supplied S1 may be an excerpt. If the full report has one, F1 narrows to the unsourced "within a quarter" and the shift from "fell" to "cut". What settles it is the full report text.
- **Is "27%" a relative lift or percentage points?** No source states which. What settles it is the survey's method, baseline and response rate.

### REFUTED
- **"The cited sources do not exist."** All three are present at the cited paths with matching titles and publishers.
- **"The 27% figure is misquoted."** The number matches across S1, S2 and S3. The defect is how independent the sources are and how the figure is framed (F2), not the number itself.
- **"S2 is falsely presented as Harvard Business Review."** The brief correctly names it Harlow Business Review. Only the filename abbreviation `hbr` could mislead, and it does not appear in the claims.

## WHAT HOLDS UP
- Every citation points to a file that exists.
- The 27% figure is transcribed accurately.
- The brief does not quote S2's "paid for itself" anecdote as evidence.

## UNVERIFIED CLAIMS
- **The vendor survey's validity:** how the 41 customers were selected, how the question was worded and what baseline was used. To confirm, obtain the survey instrument and the raw responses.
- **Any staffing effect:** to confirm, get an independent study or a controlled pilot that measures headcount needs.

## QUESTIONS FOR THE AUTHOR
1. Where does "within a quarter" come from?
2. Did you read beyond S2's attribution to check whether Meridian actually reports a staffing reduction?
3. Were you aware that S1 is sponsored by SupportPilot and that its figure comes from SupportPilot's own press release?

## DECISION-MAKER SUMMARY
Do not make staffing decisions from this brief. The staffing claim (F1) has no root source. The 27% and "market leader" claims (F2, F3) both come from the vendor alone, despite three citations. If you proceed anyway, you risk cutting support capacity on the strength of marketing; run an independent pilot first.

## OWNER SUMMARY
The briefing's three sources look independent, but they all trace back to the vendor's own survey of 41 happy customers. The claim that teams can cut staff quickly does not appear in any of the source material. Treat this as an unproven sales pitch, and test the tool yourselves before changing any staffing.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "brief.md", "status": "seen", "matters": true},
    {"item": "sources/S1-trend-report.md", "status": "seen", "matters": true},
    {"item": "sources/S2-hbr-article.md", "status": "seen", "matters": true},
    {"item": "sources/S3-press-release.md", "status": "seen", "matters": true},
    {"item": "Full Meridian Insights report beyond supplied S1 text", "status": "not_seen", "matters": true},
    {"item": "SupportPilot customer survey methodology and data", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "brief.md", "kind": "file"},
      {"unit": "sources/S1-trend-report.md", "kind": "file"},
      {"unit": "sources/S2-hbr-article.md", "kind": "file"},
      {"unit": "sources/S3-press-release.md", "kind": "file"},
      {"unit": "brief.md:3 27% first-contact resolution claim", "kind": "claim"},
      {"unit": "brief.md:3 staffing reduction within a quarter claim", "kind": "claim"},
      {"unit": "brief.md:4 widely considered market leader claim", "kind": "claim"},
      {"unit": "Sources are independent of each other and of the vendor", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "Full Meridian Insights report", "reason": "not supplied; S1 may be an excerpt"},
      {"unit": "Whether 27% is relative or percentage points", "reason": "no source states it"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "brief.md:3 \"teams that adopt it cut staffing needs within a quarter [2]\"",
     "scenario": "Leadership cuts support headcount expecting savings within a quarter, based on S2's secondhand attribution to a Meridian report (S1) that contains no staffing finding; 'within a quarter' appears in no source.",
     "fix": "Remove the claim or cite a source that directly states it; never cite a secondhand attribution without checking the primary.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Search S1 for 'staff' and 'quarter': no match (positive control: '27%' matches). Search all sources for 'quarter': no match."},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "C",
     "location": "brief.md:3 \"raises first-contact resolution by 27% [1]\"",
     "scenario": "The team expects a measured 27% FCR gain; the figure is a vendor self-survey of 41 current customers, relayed by a vendor-sponsored report that disclaims verification, and echoed by S2 citing S1. Circular, non-independent, and restated as causal.",
     "fix": "Restate as a vendor-reported, unverified self-survey (n=41 current customers), cite S3 as origin, and disclose S1's sponsorship and disclaimer.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "S1: 'SupportPilot press release, March 2026... We have not independently verified vendor figures. Sponsored by SupportPilot.' S3: 'a survey of our own customers... 41 current customers.' S2: 'According to Meridian Insights'."},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "C",
     "location": "brief.md:4 \"widely considered the market leader in its category [3]\"",
     "scenario": "A reader treats vendor self-description as independent market consensus and skips evaluating alternatives.",
     "fix": "Delete, or rewrite as 'SupportPilot describes itself as the leading support AI [3]'.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Only citation is S3, authored by SupportPilot: 'SupportPilot is the leading support AI.' No source contains 'widely considered'."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "A",
     "location": "brief.md (whole document)",
     "scenario": "The decision-maker reads a one-sided, caveat-free brief as a balanced assessment of whether to adopt.",
     "fix": "Add limitations drawn from the sources' own caveats (sponsored, unverified, n=41, current customers) and an explicit recommendation, e.g. pilot before any staffing change.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "C", "location": "sources/S1-trend-report.md",
     "suspicion": "S1 may be an excerpt; the full Meridian report could contain a staffing finding.",
     "unresolved_fact": "Full text of the Meridian Insights 2026 trend report."},
    {"id": "S2", "status": "needs_validation", "track": "C", "location": "sources/S3-press-release.md",
     "suspicion": "'27% lift' may be relative or percentage points, and the survey's baseline is unknown.",
     "unresolved_fact": "The SupportPilot survey methodology, question wording and baseline."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Cited sources do not exist.", "evidence": "All three files are present at the cited paths with matching titles and publishers."},
    {"id": "C2", "candidate": "The 27% figure is misquoted.", "evidence": "27% appears consistently in S1, S2 and S3; the defect is the framing and independence (F2), not the number."},
    {"id": "C3", "candidate": "S2 is passed off as Harvard Business Review.", "evidence": "brief.md:8 correctly names it Harlow Business Review; only the filename abbreviation 'hbr' is ambiguous."}
  ]
}
```