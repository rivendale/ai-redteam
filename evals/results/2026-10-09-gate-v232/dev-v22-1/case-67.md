**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No tools were available in this session, so nothing was fetched or run. The sources were checked only as supplied inline.

VERDICT: **SHIP WITH FIXES.** Every number in the brief matches its source, but the brief presents the study as a check on SupportPilot that the study does not support, and the four-week trial it recommends is probably too small to settle anything.

CONFIDENCE: **medium.** Three things limit it:
- This is a same-context review.
- No tools were available.
- The source files are numbered S3 and S4, which suggests S1 and S2 exist, but they were not supplied.

INPUTS LEDGER:
- Seen: request.md, context.md, brief.md, sources/S3-press-release.md, sources/S4-nine-team-study.md.
- Not seen: a listing of sources/. S1 and S2 may exist. This matters if they hold evidence the brief left out.
- Not seen: anything outside the S4 text that would confirm the Public Service Analytics Unit is independent. This matters because "independent" is load-bearing in the brief.

COVERAGE:
- Checked:
  - every sentence of brief.md, including the sources list;
  - S3 in full;
  - S4 in full;
  - every number (41, 27%, 9, 6%, quarter, 2025, March 2026) against its source.
- Not checked:
  - the contents of sources/ beyond S3 and S4;
  - S4's methods and funding beyond its own statement.

SEATS AND GATE: Only the local same-context reviewer ran; no subagent was available. The sensitivity gate found no personal, client or confidential data. No cross-vendor seats were requested.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED | C | brief.md ¶1, sentence 3: "a similar tool" | S4 says only "an AI support assistant". It never names the tool or compares it to SupportPilot. "Similar" is the author's word, and it is not in [2]. | A decision-maker treats S4 as independent evidence about SupportPilot itself and discounts the vendor's figure on that basis. The study may have used a very different product. | Replace with "an unnamed AI support assistant". Add that its relevance to SupportPilot is unknown. Check: search S4 for "SupportPilot" or "similar"; neither appears. | a Y, b Y, c N, d N |
| F2 | Medium | PROBABLE | A | brief.md ¶1, final sentence: "a four-week trial on one queue" | S4 tested nine teams over a full quarter and could not separate a 6% change from about 8% normal variation. One queue over four weeks will almost certainly be noisier, and the brief defines no metric, baseline or success threshold. | The trial ends, the result sits inside normal variation, and the staffing decision is made on noise. That is the very decision the brief says should wait for the trial. | Set out before the trial: the metric (FCR, resolution time, or both), the baseline variation for that queue, and the effect size that counts as success. If four weeks cannot detect that effect, say so or lengthen the trial. | a Y, b N, c N, d Y |
| F3 | Low | CONFIRMED | C | brief.md ¶1 juxtaposition of [1] and [2] | The 27% figure measures first-contact resolution. The 6% figure measures median resolution time. These are different metrics, yet "The independent figure we have" invites a reader to compare them directly. | A reader concludes the vendor overstated by about 4x, or that the two sources contradict each other. Neither conclusion follows. | Add one clause stating that the two sources measure different outcomes and neither replicates the other. | a Y, b Y, c N, d N |
| F4 | Low | CONFIRMED | C | brief.md ¶1, sentence 2: "not a controlled comparison [1]" | The citation suggests the press release says this. The source only says "a survey of our own customers"; "not a controlled comparison" is the author's fair inference. | A reader who checks the citation finds the wording missing and starts to doubt the other citations. | Phrase it as the author's assessment, e.g. "this is a self-selected survey [1], not a controlled comparison". | a Y, b Y, c N, d N |

**Confirm-or-refute round:**
- **F1:** Under the four questions it was first a High candidate. The strongest defence is that S3 calls SupportPilot "support AI", so "similar" holds at the level of product category. Also, the brief's recommendation (trial before any staffing decision) does not rest on the study being about a similar product. So a wrong decision caused by this word is unlikely, and d = N. The finding is kept at Medium, because the source's lack of specificity is real and the brief hides it.
- **F2:** The finding is an inference from S4's variance figure, not a calculation; queue volume is unknown. It stays PROBABLE, which caps it at Medium.

## NEEDS VALIDATION
- **S1, possible omitted sources.** The files are numbered S3 and S4, which implies S1 and S2. *Unresolved fact:* a listing of sources/ and the contents of any other files. If they bear on SupportPilot and were left out, the request to use only the sources in sources/ was met selectively.
- **S2, independence of the study.** "No funding from any vendor" is the study's own statement. *Unresolved fact:* who the Public Service Analytics Unit is, and whether it has any tie to SupportPilot or a competitor.

## REFUTED
- **"The 27% / 41 customers figures are misquoted."** S3 states both exactly: "27% lift in first-contact resolution" and "The survey asked 41 current customers."
- **"The 6% and 'indistinguishable' claims overstate S4."** S4 says "Median resolution time fell 6%; … variation … about 8%, so the effect cannot be told apart from it." The brief matches this.
- **"The brief repeats vendor puffery."** S3's "the leading support AI" and "named leader" are not repeated anywhere in the brief.
- **"The 2025 date for [2] is unsupported."** The S4 header reads "(Public Service Analytics Unit, 2025)."

## WHAT HOLDS UP
- Every figure reproduces from its source.
- Both citations resolve to supplied files whose titles and dates match.
- The brief correctly labels the vendor figure as a self-survey and does not adopt the press release's superlatives.
- It uses only the supplied sources.
- It answers the question asked, adopt or not, with a cautious recommendation. There is no drift.
- No text in the sources tries to instruct the reviewer.

## UNVERIFIED CLAIMS
- **The study's independence.** Confirm it by checking who the Unit is and how it is funded, outside its own statement.
- **That S3 and S4 are the only relevant sources.** Confirm this from a listing of sources/.

## QUESTIONS FOR THE AUTHOR
1. Are there other files in sources/ (S1, S2), and why were they not used?
2. What metric and threshold would make the four-week trial a pass, and is one queue's four-week volume enough to detect it?

## DECISION-MAKER SUMMARY
The brief reports both sources accurately, and its "trial first" stance is sound. However, the study it calls independent was not about SupportPilot and measured a different outcome, and the proposed trial is probably too small to give a clear answer. Fix F1 to F3 in the wording and define the trial's metric and threshold before it starts. Otherwise the staffing decision may rest on noise.

## OWNER SUMMARY
The briefing quotes its two sources correctly and sensibly recommends trying the tool before changing staffing. It overstates how closely the outside study relates to this product, and it compares two different measures as if they were the same. The proposed four-week trial also needs a clear pass mark and enough volume, or it may not show anything either way.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "brief.md", "status": "seen", "matters": true},
    {"item": "sources/S3-press-release.md", "status": "seen", "matters": true},
    {"item": "sources/S4-nine-team-study.md", "status": "seen", "matters": true},
    {"item": "sources/ directory listing (possible S1, S2)", "status": "not_seen", "matters": true},
    {"item": "external record of Public Service Analytics Unit funding", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "brief.md", "kind": "file"},
      {"unit": "sources/S3-press-release.md", "kind": "file"},
      {"unit": "sources/S4-nine-team-study.md", "kind": "file"},
      {"unit": "brief.md: 27% FCR lift, 41 customers [1]", "kind": "claim"},
      {"unit": "brief.md: not a controlled comparison [1]", "kind": "claim"},
      {"unit": "brief.md: 9 teams, similar tool, quarter, 6%, indistinguishable [2]", "kind": "claim"},
      {"unit": "brief.md: four-week one-queue trial recommendation", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "sources/ (other files, if any)", "reason": "not supplied; no tools"},
      {"unit": "S4 methods and funding beyond self-statement", "reason": "no external source; no tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "C",
     "location": "brief.md para 1 sentence 3: \"a similar tool\"",
     "scenario": "S4 says only 'an AI support assistant'; a decision-maker treats it as independent evidence about SupportPilot and discounts the vendor figure, though the study tool may differ.",
     "fix": "Say 'an unnamed AI support assistant' and state that relevance to SupportPilot is unknown.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "A",
     "location": "brief.md para 1 final sentence: \"a four-week trial on one queue\"",
     "scenario": "Nine teams over a quarter could not separate 6% from ~8% variation; one queue over four weeks ends with a result inside noise and staffing is decided on it.",
     "fix": "Pre-register metric, baseline variation and success threshold; lengthen or caveat the trial if four weeks cannot detect it.",
     "answers": {"a": true, "b": false, "c": false, "d": true}},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "C",
     "location": "brief.md para 1, juxtaposition of [1] and [2]",
     "scenario": "Reader compares 27% first-contact resolution with 6% median resolution time and concludes the vendor overstated ~4x, though the metrics differ.",
     "fix": "State that the sources measure different outcomes and neither replicates the other.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "C",
     "location": "brief.md para 1 sentence 2: \"not a controlled comparison [1]\"",
     "scenario": "A reader checking [1] does not find this wording; it is the author's inference presented as cited.",
     "fix": "Phrase as the author's assessment: 'a self-selected survey [1], not a controlled comparison'.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "C", "location": "sources/ (file numbering S3, S4)",
     "suspicion": "Sources S1 and S2 may exist and were omitted from the brief.",
     "unresolved_fact": "A listing of sources/ and the contents of any other files."},
    {"id": "S2", "status": "needs_validation", "track": "C", "location": "sources/S4-nine-team-study.md: \"No funding from any vendor.\"",
     "suspicion": "Independence of the study rests on its own statement.",
     "unresolved_fact": "Who the Public Service Analytics Unit is and whether it has ties to any vendor."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "27% and 41-customer figures misquoted.", "evidence": "S3 states both verbatim."},
    {"id": "C2", "candidate": "6% and indistinguishable-from-variation claims overstate S4.", "evidence": "S4: 'Median resolution time fell 6%; ... about 8%, so the effect cannot be told apart from it.'"},
    {"id": "C3", "candidate": "Brief repeats vendor puffery.", "evidence": "'leading support AI' and 'named leader' do not appear in brief.md."},
    {"id": "C4", "candidate": "2025 date for [2] unsupported.", "evidence": "S4 header: '(Public Service Analytics Unit, 2025)'."}
  ]
}
```