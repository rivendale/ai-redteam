VERDICT: **REWORK**. The staffing claim, which the decision rests on, appears in no supplied source. The 27% figure and the "market leader" claim both come from one vendor self-report, cited three ways so it looks like independent support.

CONFIDENCE: **high** for the findings, since each one is tied to verbatim text in the supplied files. Limits: there were no tools, so I took the pasted file contents as the files on disk. This was a single-reviewer, no-subagent review. It is not same-context, because the brief was not written in this conversation.

INPUTS LEDGER:
- Seen: `request.md` (verbatim request), `context.md`, `brief.md`, `sources/S1-trend-report.md`, `sources/S2-hbr-article.md`, `sources/S3-press-release.md`.
- Not seen: the full Meridian report and the full SupportPilot survey (questions, method, response rate). These matter only to rescue the claims. The request limits the brief to `sources/`, so the brief has to stand on what is supplied, and it does not.

COVERAGE:
- Scope: the whole work.
- Checked: all six files; each of the three claims in `brief.md`; each citation's mapping to its source; the citation chain S2 → S1 → S3; whether the brief answers the request.
- Not checked: hidden or zero-width characters, because there were no tools to scan bytes (`no_tools`). Whether these publications exist outside `sources/` (`out_of_scope`, because the request restricts the brief to `sources/`).

SEATS AND GATE:
- Sensitivity gate: passed. The files contain no personal, client, financial or credential data.
- Seats: local reviewer only. No subagent or cross-vendor seats were available, and none were requested.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | C | brief.md line 3: "teams that adopt it cut staffing needs within a quarter [2]" | No supplied source supports this. The cited source [2] says only "Staffing needs fell for early adopters, the report says". It gives no quarter and no "teams that adopt it", and it attributes the point to "the report" (Meridian). S1, the Meridian report, contains nothing about staffing. "Within a quarter" appears in no source at all. | Leadership cuts or freezes support headcount expecting a reduction within a quarter. The expectation rests on a sentence that traces to nothing, so the team ends up understaffed if the gain does not appear. | Remove the claim, or replace it with a source that measures staffing outcomes. If kept, quote S2 exactly and note that its attributed source (S1) does not contain the claim. | Y/Y/Y/Y |
| F2 | High | CONFIRMED | C | brief.md line 3: "SupportPilot raises first-contact resolution by 27% [1]" | The source is not independent, and the claim is overstated. S1 takes the figure from "SupportPilot press release, March 2026", says "We have not independently verified vendor figures", and is "Sponsored by SupportPilot". The figure's origin, S3, is a survey of "41 current customers" about what they "reported". The brief restates a self-reported figure from a sample of 41 current customers as a measured causal effect ("raises"). | A reader takes 27% as an expected outcome for this team. The real basis is self-selected, satisfied current customers answering the vendor's own survey, which carries survivorship and response bias. | Attribute the figure to its origin: "SupportPilot's own survey of 41 current customers reported a 27% lift (vendor press release, relayed by a SupportPilot-sponsored report)". State that it is unverified, and do not use "raises". | Y/Y/N/Y |
| F3 | High | CONFIRMED | C | brief.md line 4: "widely considered the market leader in its category [3]" | The cited source is the vendor describing itself: "SupportPilot is the leading support AI" (S3). The title "named leader" names no one who did the naming. Nothing in the sources shows the view is "widely" held. | A reader treats market leadership as an outside consensus and gives less weight to alternatives. | Remove the claim, or write "SupportPilot describes itself as the leading support AI (own press release)". | Y/Y/N/Y |
| F4 | High | CONFIRMED | A | brief.md, whole document | Drift from the request. The request asks *whether* the team should adopt. The brief gives no recommendation, no costs, no risks, no alternatives and no caveats. It omits the disclosures its own sources carry: S1 is sponsored and unverified, and S3 surveyed n=41 current customers. The result is a pitch, not a briefing. | The decision-maker reads a one-sided summary and approves without seeing that every figure goes back to the vendor. | Add an explicit recommendation, an evidence-quality section that states the sponsorship and sample, costs and risks, and the alternative of not adopting or piloting first. | Y/Y/N/Y |
| F5 | Medium | CONFIRMED | C | brief.md Sources list [1]–[3] | Three citations present one origin as three. S2 relays S1 ("According to Meridian Insights… the report says"). S1 relays S3. S3 is the vendor. The list reads as triangulation but holds a single vendor claim. | A reader counts three sources and assumes corroboration. | Mark S1 and S2 as secondary to S3, or cite S3 alone. | Y/Y/N/N |

**Sibling search (for F1–F4):** I checked all three brief claims and all three sources for the same root cause, a vendor origin presented as outside evidence.
- S2 repeats the 27% and widens it to "AI support tools such as SupportPilot". The brief does not use that sentence, so it is not a separate finding.
- S2's "paid for itself" is one unnamed anecdote. The brief does not use it either.
- None of these findings is a security finding.

## Needs validation
- Whether the full Meridian report (beyond the S1 excerpt) covers staffing. This would settle whether S2's "the report says" has any basis. Only the excerpt was supplied, and the brief may use only `sources/`.

## Refuted
- *The sources are fabricated or missing.* Refuted: all three cited files exist in `sources/`, and each title matches its file.
- *The 27% figure is misquoted.* Refuted: S1 and S3 both state 27% for first-contact resolution. The defect is how the figure is framed and where it comes from, not the number.

## What holds up
- Every claim carries a citation.
- Every citation resolves to a supplied file.
- The 27% number is reproduced correctly.

## Unverified claims
- **27% lift.** To confirm: the vendor survey instrument, plus an independent before-and-after measurement, ideally a pilot on this team.
- **Staffing reduction.** To confirm: any source with measured headcount outcomes.
- **Market leadership.** To confirm: an independent analyst ranking or market-share data.

## Questions for the author
1. Where does "within a quarter" come from?
2. Did you see that S1 is SupportPilot-sponsored and that S2 relays S1?
3. What is your recommendation, and what would change it?

## Decision-maker summary
Do not base a staffing decision on this brief. Its staffing claim has no support in the sources, and its only performance number is the vendor's own survey of 41 current customers, repeated through two secondary sources. If you proceed anyway, you risk cutting headcount for a gain that has never been measured independently. Commission a revised brief or a time-boxed pilot instead.

## Owner summary
The briefing's main points all trace back to the vendor's own marketing, and its claim about reducing staff is not backed by any of its sources. It reads as an endorsement rather than a balanced answer to whether the team should adopt the tool. It should be rewritten with honest caveats, or the tool should be trialled first, before any staffing decision.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "brief.md", "status": "seen", "matters": true},
    {"item": "sources/S1-trend-report.md", "status": "seen", "matters": true},
    {"item": "sources/S2-hbr-article.md", "status": "seen", "matters": true},
    {"item": "sources/S3-press-release.md", "status": "seen", "matters": true},
    {"item": "full Meridian report beyond S1 excerpt", "status": "not_seen", "matters": false}
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
      {"unit": "brief.md claim: 27% first-contact resolution", "kind": "claim"},
      {"unit": "brief.md claim: staffing cut within a quarter", "kind": "claim"},
      {"unit": "brief.md claim: widely considered market leader", "kind": "claim"},
      {"unit": "citation chain S2 -> S1 -> S3", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "hidden/zero-width characters in all files", "reason": "no_tools"},
      {"unit": "existence of publications outside sources/", "reason": "out_of_scope"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "brief.md line 3: 'cut staffing needs within a quarter [2]'",
     "scenario": "Leadership cuts support headcount expecting a reduction within a quarter; the claim appears in no supplied source (S2 attributes it to S1, which says nothing about staffing; 'within a quarter' appears nowhere), so the team is left understaffed if the gain does not materialize.",
     "fix": "Remove the claim or replace it with a source that measures staffing outcomes; if kept, quote S2 exactly and note that S1 does not contain it.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "all three brief claims against S1-S3 for unsupported or vendor-origin support", "found": "F2 and F3 share the root cause; S2's '27%' generalization and 'paid for itself' anecdote are not used by the brief"}},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "C",
     "location": "brief.md line 3: 'raises first-contact resolution by 27% [1]'",
     "scenario": "A reader treats 27% as a measured causal effect, when it is a self-reported figure from the vendor's survey of 41 current customers, relayed by a SupportPilot-sponsored report that says it did not verify it.",
     "fix": "Attribute the figure to the vendor survey (n=41 current customers), note the sponsorship and the lack of verification, and drop the causal 'raises'.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "security": false,
     "siblings_searched": {"searched": "all brief claims and sources for vendor-origin figures presented as independent", "found": "F3 (market leader) and F5 (citation chain)"}},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "C",
     "location": "brief.md line 4: 'widely considered the market leader in its category [3]'",
     "scenario": "A reader treats market leadership as outside consensus, when the only source is the vendor's own press release asserting 'SupportPilot is the leading support AI'.",
     "fix": "Remove the claim, or restate it as the vendor's self-description.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "security": false,
     "siblings_searched": {"searched": "all brief claims and sources for vendor self-assertion presented as consensus", "found": "F2 shares the root cause"}},
    {"id": "F4", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "A",
     "location": "brief.md, whole document",
     "scenario": "The request asks whether to adopt; the brief gives no recommendation, costs, risks, alternatives or source caveats, so the decision-maker approves on a one-sided summary.",
     "fix": "Add an explicit recommendation, an evidence-quality section (sponsorship, n=41, unverified), costs and risks, and a not-adopt or pilot alternative.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "security": false,
     "siblings_searched": {"searched": "brief.md for any recommendation, risk, cost or caveat sentence", "found": "none present"}},
    {"id": "F5", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "C",
     "location": "brief.md Sources list [1]-[3]",
     "scenario": "A reader counts three sources as corroboration, but S2 relays S1 and S1 relays S3 (the vendor): there is one origin.",
     "fix": "Mark S1 and S2 as secondary to S3, or cite S3 alone.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "C", "location": "sources/S2-hbr-article.md: 'Staffing needs fell for early adopters, the report says'",
     "suspicion": "S2 may misattribute the staffing claim to the Meridian report.",
     "unresolved_fact": "Whether the full Meridian report, beyond the S1 excerpt, mentions staffing."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The cited sources are fabricated or missing.", "evidence": "All three cited files exist in sources/ and their titles match the citations."},
    {"id": "C2", "candidate": "The 27% figure is misquoted.", "evidence": "S1 and S3 both state 27% for first-contact resolution; the defect is the framing and provenance, not the number."}
  ]
}
```

I had no tools, so this block has not been run through `tools/validate_findings.py`.