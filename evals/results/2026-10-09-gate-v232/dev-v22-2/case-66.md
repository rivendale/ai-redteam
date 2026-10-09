VERDICT: **REWORK.** All three citations trace back to one vendor self-survey of 41 customers. The staffing claim, the one the decision rests on, is not supported by any source.

CONFIDENCE: **high** for the claims findings, which are short quotes from supplied files. Limits: single reviewer with no subagent and no tools. The work was not written in this conversation, so the anchoring risk is lower, but re-run in a fresh session before the staffing decision.

INPUTS LEDGER:
- **Seen:** request.md, context.md, brief.md, and sources S1, S2 and S3, all in full.
- **Not seen:** the full Meridian report (S1 may be an excerpt), the original SupportPilot survey and its method, and any non-vendor evidence. The context says all sources the author used are in sources/, so these gaps limit what *could* be known, not this review's conclusions.

COVERAGE:
- **Checked:** the brief's three claims and three citations; every sentence of S1, S2 and S3; the attribution chain S2 → S1 → S3; the brief against the request.
- **Not checked:** anything outside sources/ (out of scope by request).

SEATS AND GATE: one local reviewer ran. No cross-vendor seats (none requested; no tools). Sensitivity gate: nothing sensitive (no personal, financial or confidential data).

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | C | brief.md L3, "teams that adopt it cut staffing needs within a quarter [2]" | The cited source does not support the claim. S2 says only "Staffing needs fell for early adopters, the report says." It does not say "within a quarter" or "cut". It refers to "AI support tools" in general, not SupportPilot. It attributes the point to "the report" (Meridian, S1), but S1 contains no staffing claim at all. The chain dead-ends, and "within a quarter" appears in no source. | Leadership cuts or freezes support headcount expecting a one-quarter payoff that no source states. Customers and staff bear the gap. | Remove the claim or state "no source in the set supports a staffing reduction". Reproduction: search S1, S2 and S3 for "quarter" (zero hits) and "staff" (one hit, S2, unattributed and generic). Positive control: the same read finds "27%" in all three. | a✓ b✓ c✓ d✓ |
| F2 | High | CONFIRMED | C | brief.md L3, "raises first-contact resolution by 27% [1]"; Sources list | The brief presents circular, vendor-originated evidence as independent research. S1 takes the 27% figure from "SupportPilot press release, March 2026", states "We have not independently verified vendor figures", and is "Sponsored by SupportPilot". S2 cites Meridian (S1). S3 is the press release: "a survey of our own customers… asked 41 current customers." All three sources therefore rest on one self-reported vendor survey. The brief also upgrades "users reported a … lift" (S3) to a causal "raises". | A reader sees three sources and concludes the figure is corroborated. In fact it is a self-selected survey of 41 current customers (survivorship bias, no baseline or control). The brief also drops every caveat the sources state. | Cite S3 as the origin. State the n=41 self-report, the sponsorship and the "not independently verified" caveat. Use "the vendor reports" instead of "raises". Reproduction: follow each citation to its stated origin; all three end at S3. | a✓ b✓ c✗ d✓ |
| F3 | High | CONFIRMED | C | brief.md L4, "widely considered the market leader [3]" | The only source is the vendor's own press release: "SupportPilot is the leading support AI." That is one self-assertion, not wide consideration. No source reports any third-party ranking. | A reader treats vendor marketing as industry consensus and skips evaluating competitors. | Replace with "SupportPilot describes itself as the leading support AI [3]", or delete. | a✓ b✓ c✗ d✓ |
| F4 | High | CONFIRMED | A | brief.md, whole document vs request.md "whether the support team should adopt" | The brief does not answer the question asked. It gives no recommendation, costs, risks, alternatives or statement of evidence quality. It lists three favorable claims, which reads as an implicit endorsement. Given the sources, the honest answer is "evidence insufficient: vendor-originated only". | A decision-maker reads the brief as a yes and acts on it. | Add an explicit answer, including the limits of the evidence and what independent data (for example a pilot with a baseline) would be needed. | a✓ b✓ c✗ d✓ |
| F5 | Low | CONFIRMED | C | brief.md Sources #2, file path "S2-hbr-article.md" | The abbreviation "HBR" for Harlow Business Review invites confusion with Harvard Business Review and lends borrowed authority. | A reader skimming the file name credits a more authoritative outlet. | Use the full publication name and avoid "HBR". | a✓ b✓ c✗ d✗ |

**NEEDS VALIDATION**
- **S1:** whether the full Meridian report says anything about staffing. Settled by whether S1 as supplied is the complete report or an excerpt. If it is an excerpt, F1's "S1 contains no staffing claim" applies to the supplied text only. F1 still stands, because S2's statement is generic, unattributed and has no time frame.

**REFUTED**
- **"Cited sources do not exist."** All three are present in sources/ under the cited titles.
- **"27% is misquoted."** The figure matches in S1, S2 and S3. The problem is its origin and framing (F2), not the number.
- **"Citation [1] points to the wrong document."** S1 does contain the 27% statement.

**WHAT HOLDS UP:** every claim carries a citation, the citations resolve to real files, and the 27% figure is transcribed accurately.

**UNVERIFIED CLAIMS**
- **27% FCR lift:** a vendor self-survey of 41 current customers, with no method, baseline or control. Confirming it needs an independent study or an internal pilot measured against baseline.
- **Staffing reductions:** no source supports this. Confirming it needs adopter data on headcount before and after adoption.
- **Market leadership:** vendor assertion only. Confirming it needs an independent analyst ranking.

**QUESTIONS FOR THE AUTHOR**
1. Where does "within a quarter" come from?
2. Did you see that S1 and S2 both trace back to S3?
3. What is your actual recommendation, given that all the evidence comes from the vendor?

**DECISION-MAKER SUMMARY:** Do not base a staffing decision on this brief. Its three citations collapse into one vendor survey of 41 customers, and the staffing-cut claim has no source. If you proceed, headcount may be cut on a benefit no one has independently shown. Run a measured pilot first.

**OWNER SUMMARY:** The briefing looks well sourced, but all its evidence comes from the vendor's own survey of a small group of existing customers. The claim that the tool lets teams reduce staff is not backed by any of the sources. The briefing should be rewritten to say how weak the evidence is and give a clear recommendation, such as running a trial first.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "brief.md", "status": "seen", "matters": true},
    {"item": "sources/S1-trend-report.md", "status": "seen", "matters": true},
    {"item": "sources/S2-hbr-article.md", "status": "seen", "matters": true},
    {"item": "sources/S3-press-release.md", "status": "seen", "matters": true},
    {"item": "full Meridian report beyond S1 excerpt", "status": "not_seen", "matters": false},
    {"item": "underlying SupportPilot survey (method, data)", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "brief.md", "kind": "file"},
      {"unit": "sources/S1-trend-report.md", "kind": "file"},
      {"unit": "sources/S2-hbr-article.md", "kind": "file"},
      {"unit": "sources/S3-press-release.md", "kind": "file"},
      {"unit": "27% first-contact resolution claim", "kind": "claim"},
      {"unit": "staffing reduction within a quarter claim", "kind": "claim"},
      {"unit": "widely considered market leader claim", "kind": "claim"},
      {"unit": "sources are independent", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "evidence outside sources/", "reason": "out of scope per request; no tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "brief.md line 3: 'teams that adopt it cut staffing needs within a quarter [2]'",
     "scenario": "Leadership cuts support headcount expecting a one-quarter payoff; S2 only says 'Staffing needs fell for early adopters, the report says' about AI tools generally, S1 contains no staffing claim, and 'within a quarter' appears in no source.",
     "fix": "Remove the claim or state that no source supports a staffing reduction.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Search S1-S3 for 'quarter' (0 hits) and 'staff' (1 hit in S2, generic, attributed to S1 which lacks it); positive control: '27%' found in all three."},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "C",
     "location": "brief.md line 3: 'raises first-contact resolution by 27% [1]'; Sources list",
     "scenario": "Reader treats three citations as corroboration, but S2 cites S1, S1 cites the vendor press release (S3) and is vendor-sponsored and unverified, and S3 is a self-survey of 41 current customers; the brief also states a self-reported lift as causal.",
     "fix": "Cite S3 as origin, disclose n=41 self-report, sponsorship and 'not independently verified', and use 'the vendor reports' instead of 'raises'.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Follow each citation to its stated origin; all terminate at S3."},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "C",
     "location": "brief.md line 4: 'widely considered the market leader [3]'",
     "scenario": "Vendor's own press-release self-description ('SupportPilot is the leading support AI') is presented as industry consensus, so competitors go unevaluated.",
     "fix": "Rephrase as 'SupportPilot describes itself as the leading support AI [3]' or delete.",
     "answers": {"a": true, "b": true, "c": false, "d": true}},
    {"id": "F4", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "A",
     "location": "brief.md whole document vs request.md 'whether the support team should adopt SupportPilot'",
     "scenario": "Brief gives no recommendation, costs, risks or evidence-quality assessment, so a decision-maker reads three favorable claims as an implicit yes.",
     "fix": "Add an explicit recommendation, including evidence limits and the independent data (e.g. a baselined pilot) needed.",
     "answers": {"a": true, "b": true, "c": false, "d": true}},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "C",
     "location": "brief.md Sources #2, path 'sources/S2-hbr-article.md'",
     "scenario": "'HBR' abbreviation for Harlow Business Review leads a skimming reader to assume Harvard Business Review.",
     "fix": "Use the full publication name and avoid 'HBR'.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "C", "location": "sources/S1-trend-report.md",
     "suspicion": "The full Meridian report might contain a staffing claim not in the supplied file.",
     "unresolved_fact": "Whether S1 as supplied is the complete report or an excerpt."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Cited sources do not exist.", "evidence": "All three files exist in sources/ with matching titles."},
    {"id": "C2", "candidate": "The 27% figure is misquoted.", "evidence": "27% appears verbatim in S1, S2 and S3."},
    {"id": "C3", "candidate": "Citation [1] points to a document lacking the claim.", "evidence": "S1 states 'SupportPilot customers see a 27% lift in first-contact resolution'."}
  ]
}
```