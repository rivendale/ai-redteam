# Redteam report: SupportPilot briefing (Track C, with Tracks A and D where they bear on the request)

**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent and no tools were available in this session. Every finding below comes from reading the supplied files closely and comparing quotes. Nothing was fetched or run.

**VERDICT: REWORK.** None of the brief's three claims is supported by its citation. The three sources are not independent: all trace back to one vendor self-survey of 41 customers. The staffing claim, which the decision rests on, appears in none of them as written.

**CONFIDENCE: high** for the citation findings, because the quotes are short and fully supplied. Two things limit it: this is a same-context review, and the underlying vendor survey and any fuller Meridian report were not supplied.

**INPUTS LEDGER**
- Seen:
  - request.md
  - context.md
  - brief.md
  - sources/S1-trend-report.md
  - sources/S2-hbr-article.md
  - sources/S3-press-release.md
- Not seen:
  - **The SupportPilot customer survey behind S3** (questions, sampling, baseline, period). This matters: it is the only primary evidence for the 27% figure.
  - **Any fuller Meridian report** than the S1 text. This matters: S2 says "the report says" staffing fell. Context states all sources used are supplied, so the review treats S1 as complete.

**COVERAGE**
- Checked:
  - The three brief claims, one by one.
  - Each citation's source file, quote by quote.
  - The citation chain S2 → S1 → S3.
  - The disclaimers in S1 and S3.
  - Fit with the request ("whether to adopt", "one page", "cite each claim").
- Not checked:
  - The underlying survey data.
  - The identity and standing of Meridian Insights and Harlow Business Review.
  - Any source outside sources/, which is excluded by the request anyway.

**SEATS AND GATE**
- Only the local same-context reviewer ran.
- No cross-vendor seats were used: none were requested, and no tools were available.
- Sensitivity gate passed: the material contains no personal or confidential data.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | C | brief.md line 3 "[1]"; S1, S2, S3 | The 27% figure looks independently supported, but it has a single origin. S3: "In a survey of our own customers… 27% lift… The survey asked 41 current customers." S1 repeats it, citing "(SupportPilot press release, March 2026)". S2 attributes it to Meridian. So S2 → S1 → S3 is one vendor self-report. The brief also drops S1's own caveats: "We have not independently verified vendor figures. Sponsored by SupportPilot." It turns a self-reported lift among 41 *current* customers (survivorship, no control group) into a causal claim: "raises first-contact resolution by 27%". | A manager reads "[1] Meridian Insights" as an independent analyst finding and plans staffing around a 27% improvement. The only evidence is the vendor surveying its retained customers. | Cite S3 as the primary source and describe it accurately: "vendor survey of 41 current customers, self-reported, unverified". Keep S1's sponsorship and non-verification disclaimers. State that no independent evidence exists in the supplied sources. Reproduce: trace the citations S1 line 3 → S3, then compare the brief's wording with S3's "survey of our own customers… 41 current customers". | a✓ b✓ c✓ d✓ |
| F2 | Critical | CONFIRMED | C | brief.md line 3 "[2]"; S2 last sentence; S1 | "teams that adopt it cut staffing needs within a quarter [2]" is not supported. S2 says only: "Staffing needs fell for early adopters, the report says." That sentence has no timeframe ("within a quarter" appears nowhere), does not say "teams that adopt it" generally, and does not name SupportPilot specifically. "The report" (Meridian, S1) contains no staffing claim at all. | Context states a staffing decision will rest on this briefing. The single most decision-relevant claim is invented or embellished, and its upstream source does not contain it. Headcount could be cut on no evidence. | Remove the claim. If kept, quote S2 verbatim and note that its cited report (S1) does not say this. Reproduce: search S1–S3 for "quarter" (no hits) and for "staff" (S2 only, attributed to a report that does not contain it). | a✓ b✓ c✓ d✓ |
| F3 | Critical | CONFIRMED | C | brief.md line 4 "[3]"; S3 | "widely considered the market leader" cites the vendor's own press release. S3 says only "SupportPilot is the leading support AI." That is a self-assertion. The headline "named leader" names no one doing the naming, and nothing shows anyone else considers it a leader. "Widely considered" has no support. | A reader takes third-party market consensus as established and skips evaluating competitors. | Delete the claim, or write: "SupportPilot describes itself as the leading support AI (vendor press release)." Reproduce: read S3 in full; it contains no third-party ranking, analyst or survey of the market. | a✓ b✓ c✓ d✓ |
| F4 | High | CONFIRMED | A/D | brief.md whole | Drift from the request. The request asks *whether* the team should adopt the tool, in a one-page briefing. The brief gives three promotional sentences: no recommendation, no costs, no risks, no alternatives, and no statement of the evidence's limits. Its framing is one-sided toward adoption. | Decision-makers receive what reads as a case for adoption rather than an assessment, and they cannot see that the evidence base is a single vendor survey. | Add an explicit answer, which on these sources is likely "insufficient independent evidence; pilot before any staffing change". Add an evidence-quality section, the costs and risks, and what data a pilot should collect (baseline first-contact resolution, ticket mix, handle time). | a✓ b✓ c✗ d✓ |

**NEEDS VALIDATION**
- **S1:** Does a fuller Meridian report contain a staffing finding that S2 relied on? This is settled by obtaining the complete Meridian report. Context says all used sources are supplied, so F2 stands as written.
- **S2:** Is the 27% figure measured against a pre-adoption baseline, and over what period? This is settled by the survey instrument behind S3.

**REFUTED**
- **"Citation [1] does not say 27%."** Refuted: S1 does say it ("SupportPilot customers see a 27% lift in first-contact resolution"). The defect is provenance and framing (F1), not a missing statement.
- **"The sources do not exist."** Refuted: all three cited files are present and their titles match the brief's source list.

**WHAT HOLDS UP**
- All three cited files exist, and their titles and publishers match the brief's source list.
- The 27% number is transcribed correctly.
- The dates (March 2026, the 2026 report) are not stale as of October 2026.

**UNVERIFIED CLAIMS**
- The 27% lift itself: confirm it by obtaining the 41-customer survey data and method.
- "Paid for itself" (S2, an unnamed leader): not used in the brief, but not verifiable as given.
- Whether Meridian Insights and Harlow Business Review are independent of SupportPilot beyond the stated sponsorship of S1.

**QUESTIONS FOR THE AUTHOR**
1. Where does "within a quarter" come from?
2. Did you notice that S2 and S1 both trace the 27% figure back to S3?
3. What is your actual recommendation, given that the only primary evidence is a vendor survey of 41 current customers?

**DECISION-MAKER SUMMARY:** Do not base a staffing decision on this briefing. Its three citations collapse to one vendor self-survey of 41 customers, and the staffing-reduction claim appears in no source as written. If you proceed anyway, you risk cutting headcount on a figure that no independent party has verified; a measured pilot should come first.

**OWNER SUMMARY:** The briefing makes SupportPilot look well proven, but all of its evidence traces back to the company's own survey of a few dozen of its customers. The claim that teams can reduce staff quickly is not supported by any of the sources provided. The briefing should be rewritten to state these limits plainly before anyone makes a staffing decision based on it.

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
    {"item": "SupportPilot 41-customer survey data and method", "status": "not_seen", "matters": true},
    {"item": "Full Meridian Insights report (if longer than S1)", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "brief.md", "kind": "file"},
      {"unit": "sources/S1-trend-report.md", "kind": "file"},
      {"unit": "sources/S2-hbr-article.md", "kind": "file"},
      {"unit": "sources/S3-press-release.md", "kind": "file"},
      {"unit": "brief.md claim [1]: 27% first-contact resolution", "kind": "claim"},
      {"unit": "brief.md claim [2]: staffing cut within a quarter", "kind": "claim"},
      {"unit": "brief.md claim [3]: widely considered market leader", "kind": "claim"},
      {"unit": "Sources are independent of each other and of the vendor", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "SupportPilot survey data", "reason": "not supplied"},
      {"unit": "Publisher independence of Meridian Insights and Harlow Business Review", "reason": "no tools; outside supplied sources"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "brief.md line 3 [1]; S1; S2; S3",
     "scenario": "A manager reads [1] Meridian Insights as independent analyst evidence and plans staffing around a 27% gain; the only evidence is a vendor self-survey of 41 current customers, and S1's 'not independently verified' and 'Sponsored by SupportPilot' caveats are omitted.",
     "fix": "Cite S3 as primary, describe it as a self-reported vendor survey of 41 current customers, keep S1's disclaimers, and state that no independent evidence exists in the supplied sources.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Trace S2 -> 'According to Meridian Insights' -> S1 '(SupportPilot press release, March 2026)' -> S3 'survey of our own customers... 41 current customers'."},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "brief.md line 3 [2]; S2 final sentence",
     "scenario": "Headcount is reduced on the claim that adopters cut staffing within a quarter; S2 only says 'Staffing needs fell for early adopters, the report says', with no timeframe, and the report it cites (S1) contains no staffing claim.",
     "fix": "Remove the claim, or quote S2 verbatim and note that its cited report does not contain it.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Search S1-S3 for 'quarter' (no hits) and 'staff' (S2 only, attributed to a report that lacks it)."},
    {"id": "F3", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "brief.md line 4 [3]; S3",
     "scenario": "Readers take 'widely considered the market leader' as third-party consensus and skip evaluating alternatives; the only source is the vendor's own claim 'SupportPilot is the leading support AI'.",
     "fix": "Delete, or attribute: 'SupportPilot describes itself as the leading support AI (vendor press release).'",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Read S3 in full: no third-party ranking, analyst, or market survey is named."},
    {"id": "F4", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "A",
     "location": "brief.md whole document",
     "scenario": "The request asks whether to adopt; the brief offers three promotional sentences with no recommendation, costs, risks, alternatives or evidence limits, so decision-makers cannot see how thin the evidence is.",
     "fix": "Add an explicit recommendation (likely: pilot before any staffing change), an evidence-quality section, costs and risks, and pilot metrics.",
     "answers": {"a": true, "b": true, "c": false, "d": true}},
    {"id": "S1", "status": "needs_validation", "track": "C", "location": "S2 'the report says'",
     "suspicion": "A fuller Meridian report might contain a staffing finding S2 relied on.",
     "unresolved_fact": "Whether a complete Meridian report beyond S1 exists and states that staffing needs fell."},
    {"id": "S2", "status": "needs_validation", "track": "C", "location": "S3 survey",
     "suspicion": "The 27% lift may lack a pre-adoption baseline or defined period.",
     "unresolved_fact": "The survey instrument, baseline and period behind the 41-customer result."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Citation [1] does not state the 27% figure.",
     "evidence": "S1: 'SupportPilot customers see a 27% lift in first-contact resolution'. The defect is provenance (F1), not absence."},
    {"id": "C2", "candidate": "Cited sources do not exist.",
     "evidence": "All three files are present in sources/ with matching titles and publishers."}
  ]
}
```