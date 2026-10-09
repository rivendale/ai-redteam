VERDICT: **REWORK**. The staffing claim, which the decision rests on, has no support in any source, and all three citations trace back to one vendor survey of its own 41 customers.

CONFIDENCE: **medium**. All four source files were supplied and quoted directly, so the citation checks are solid. Confidence is limited because this is a single reviewer with no tools: no subagent or second seat ran, and nothing outside the supplied text could be checked. Re-run in a fresh session if the decision is high-stakes.

INPUTS LEDGER:
- **Seen:** request.md, context.md, brief.md, sources/S1-trend-report.md, sources/S2-hbr-article.md, sources/S3-press-release.md.
- **Not seen:**
  - The full Meridian report, if S1 is only an excerpt. This matters: it is the only place a staffing figure could exist. context.md says all sources are supplied, so the review treats S1 as complete.
  - The survey instrument behind S3. This matters for the 27% figure's validity, but not for the citation findings.

COVERAGE:
- **Scope:** the whole work (brief.md) against its four sources.
- **Checked:**
  - all three brief claims (27% lift, staffing cut within a quarter, market leader)
  - each citation chain end to end
  - the S2 "paid for itself" quote, which the brief does not use
  - fit against the request
- **Not checked:** facts outside the sources (out of scope; the request restricts the brief to sources/).

SEATS AND GATE: one same-session reviewer, no tools, not cross-vendor. No subagent was available. The sensitivity gate found nothing sensitive (public-style sources, no personal data).

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | C | brief.md line 3: "teams that adopt it cut staffing needs within a quarter [2]" | S2's claim and its source don't support this. S2 says only "Staffing needs fell for early adopters, the report says," crediting Meridian. S1, the Meridian report, contains no staffing claim at all. "Within a quarter" appears in no source. "Early adopters" has also been widened to "teams that adopt it." | Leadership cuts support staffing on the expectation of a reduction within one quarter. No source supports either the reduction or the timeline. | Remove the claim, or find a primary source that measures staffing change, with method and timeframe. State plainly that the supplied sources do not support any staffing impact. | y/y/y/y |
| F2 | High | CONFIRMED | C | brief.md line 3: "raises first-contact resolution by 27% [1]" | **Not independent.** The chain is: brief → S1 (sponsored by SupportPilot; "We have not independently verified vendor figures"), which cites the SupportPilot press release. That release, S3, is a self-survey of "41 current customers." S2 credits the same number to Meridian, so all three citations come from one vendor figure.<br>**Not causal.** The figure is self-reported, from current customers only (unhappy customers who left are excluded), with no control group. "Raises" turns that into proof of cause. | Readers see three citations and take the figure as independently corroborated and causal. They expect a 27% gain that has never been measured independently. | Attribute the figure to its origin: "SupportPilot's own survey of 41 current customers reported a 27% lift." Note the sponsorship and the lack of verification. Say it is a reported lift, not one shown to be caused by the tool. | y/y/n/y |
| F3 | High | CONFIRMED | C | brief.md line 4: "widely considered the market leader [3]" | The only support is the vendor describing itself: "SupportPilot is the leading support AI." The title "named leader" names no one who named it. One party's self-description is not "widely considered." | The decision-maker gives weight to market consensus that does not exist in the sources. | Delete the claim, or say "SupportPilot describes itself as the leading support AI (vendor press release)." | y/y/n/y |
| F4 | High | CONFIRMED | A (outside the requested Track C) | brief.md as a whole, against request.md ("whether the support team should adopt") | The brief lists only claimed benefits. It gives no recommendation, costs, risks or alternatives. It also leaves out the limits its own sources state: S1's sponsorship and non-verification, and S3's sample of n=41 current customers. | The reader takes a one-sided summary as a balanced briefing and makes a staffing decision without the counter-case. | State the recommendation and the strength of the evidence, which is weak and vendor-originated. Carry the sources' own caveats into the brief. Name what evidence is missing, such as an independent study or a pilot. | y/y/n/y |
| F5 | Low | CONFIRMED | C | sources/S2-hbr-article.md: "AI support tools such as SupportPilot raise ... by 27%" | S2 misreports S1. S1 gives the figure for SupportPilot customers only, not for AI support tools in general. The brief does not repeat this error, but it shows S2 is not a careful secondary source. | Someone reuses S2 for a category-wide claim. | Do not use S2 as support for the figure. Cite the origin, S3, with its caveats. | y/y/n/n |

Siblings and boundaries (F1 to F4):
- **What was searched:** every claim in the brief, checked for the same root cause (a vendor-originated or unsupported claim presented as independent).
- **What was found:** all three claims share it. Each has its own finding: F1, F2, F3.
- **Security:** none of these are security findings. No trust boundary is crossed.

**NEEDS VALIDATION**
- Whether S1 is the full Meridian report or an excerpt. If the full report contains a staffing finding, F1's "no source" becomes "a sponsored, unverified source." It would not become support.
- Whether the "SupportPilot press release, March 2026" that S1 cites is S3. The date and the figure match, so this is probable. Confirm with the publisher.

**REFUTED**
- *Candidate:* the brief invents the 27% figure. *Refuted:* S1 states "a 27% lift in first-contact resolution." The figure is quoted accurately; the problem is how it is framed and attributed (F2).

**WHAT HOLDS UP**
- Every cited source exists in sources/, and each citation number points to the right file.
- The 27% figure is transcribed correctly.
- The brief stays within the supplied sources, as the request requires. It brings in no outside material.

**UNVERIFIED CLAIMS**
- The 27% lift: needs an independent study with a control group, or a pilot measured in-house.
- Any staffing reduction: needs a primary measurement.
- Market leadership: needs a third-party analyst ranking.

**QUESTIONS FOR THE AUTHOR**
1. What source, if any, supports "cut staffing needs within a quarter"?
2. Is S1 the complete report?

**DECISION-MAKER SUMMARY**
Do not base a staffing decision on this briefing. Its staffing claim has no source. Its 27% figure is the vendor's own survey of 41 current customers, repeated by a report the vendor sponsored and an article citing that report. If you need evidence, run a measured pilot first. Proceeding now risks cutting staff on the strength of vendor marketing.

**OWNER SUMMARY**
The briefing makes the tool look proven, but every supporting source traces back to the vendor's own small customer survey. Its claim that teams need fewer staff does not appear in any of the sources at all. A fair trial run should come before any staffing changes.

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
    {"item": "Full Meridian report (if S1 is an excerpt)", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "brief.md", "kind": "document"},
      {"unit": "sources/S1-trend-report.md", "kind": "document"},
      {"unit": "sources/S2-hbr-article.md", "kind": "document"},
      {"unit": "sources/S3-press-release.md", "kind": "document"},
      {"unit": "brief.md claim: 27% first-contact resolution lift", "kind": "claim"},
      {"unit": "brief.md claim: staffing cut within a quarter", "kind": "claim"},
      {"unit": "brief.md claim: widely considered market leader", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "Full Meridian report beyond S1 text", "reason": "not_supplied"},
      {"unit": "Facts outside sources/", "reason": "out_of_scope"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "brief.md line 3: 'teams that adopt it cut staffing needs within a quarter [2]'",
     "scenario": "Leadership cuts support staffing expecting a reduction within a quarter; S2 only says 'staffing needs fell for early adopters, the report says', S1 (the Meridian report) has no staffing claim, and 'within a quarter' appears in no source.",
     "fix": "Remove the claim or source it to a primary measurement of staffing change; state that the supplied sources do not support a staffing impact.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "every claim in brief.md against its full citation chain", "found": "F2 and F3 share the unsupported or vendor-originated root cause"}},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "C",
     "location": "brief.md line 3: 'raises first-contact resolution by 27% [1]'",
     "scenario": "Readers take three citations as independent corroboration of a causal 27% gain; all trace to a SupportPilot self-survey of 41 current customers, repeated by a SupportPilot-sponsored report that says it did not verify vendor figures.",
     "fix": "Attribute to origin: 'SupportPilot's own survey of 41 current customers reported a 27% lift'; disclose sponsorship and non-verification; drop the causal 'raises'.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "security": false,
     "siblings_searched": {"searched": "every claim in brief.md for vendor-origin chains", "found": "F3 (market-leader claim) has the same vendor-origin root cause"}},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "C",
     "location": "brief.md line 4: 'widely considered the market leader [3]'",
     "scenario": "The decision-maker credits a market consensus that exists only as the vendor's self-description in its own press release.",
     "fix": "Delete, or reword to 'SupportPilot describes itself as the leading support AI (vendor press release)'.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "security": false,
     "siblings_searched": {"searched": "every claim in brief.md for self-asserted support", "found": "F2 shares the vendor-origin root cause"}},
    {"id": "F4", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "A",
     "location": "brief.md (whole) against request.md 'whether the support team should adopt'",
     "scenario": "A one-sided list of benefits with no recommendation, costs, risks, alternatives or the sources' own caveats is taken as a balanced briefing for a staffing decision.",
     "fix": "State a recommendation and the strength of the evidence; carry S1's sponsorship and non-verification and S3's n=41 current-customer caveat; name the missing evidence (independent study or pilot).",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "security": false,
     "siblings_searched": {"searched": "brief.md for any statement of risk, cost, caveat or recommendation", "found": "none present"}},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "C",
     "location": "sources/S2-hbr-article.md: 'AI support tools such as SupportPilot raise ... by 27%'",
     "scenario": "S2 generalises a SupportPilot-only figure from S1 to all AI support tools; anyone reusing S2 makes a category claim no source supports.",
     "fix": "Do not use S2 as support for the figure; cite S3 with its caveats.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "C", "location": "sources/S1-trend-report.md",
     "suspicion": "S1 may be an excerpt of a longer report that contains a staffing finding.",
     "unresolved_fact": "Whether S1 is the complete Meridian report."},
    {"id": "S2", "status": "needs_validation", "track": "C", "location": "sources/S1-trend-report.md: '(SupportPilot press release, March 2026)'",
     "suspicion": "The press release S1 cites is probably S3, but this is not confirmed.",
     "unresolved_fact": "Whether the March 2026 release cited by S1 is the document in S3."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The brief invents the 27% figure.",
     "evidence": "S1 states 'a 27% lift in first-contact resolution'; the figure is accurately transcribed. The defect is framing and attribution (F2)."}
  ]
}
```

I had no tools in this session, so I could not run `tools/validate_findings.py` against this block.