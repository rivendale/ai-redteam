VERDICT: **REWORK.** The page has two confirmed Critical defects. Its headline promises a guaranteed, risk-free return, which RICR 4.2 prohibits. It also says every page is approved before publication, which the firm's own filed procedure contradicts.

CONFIDENCE: **high.** Both Criticals are verbatim conflicts between the page and the supplied texts. What limits confidence: there are no tools in this session, the review was done in one context with no independent seat, and the rule text is an extract rather than the full rule.

INPUTS LEDGER:
- **Seen:** request.md, context.md, page.md, compliance_procedure.md, performance.csv, rule_extract.md.
- **Not seen: the full RICR text.** This matters. The extract may leave out other requirements, such as how a performance period must be labelled.
- **Not seen: the portfolio's holdings or offering documents.** This matters for the claim "holds high-grade bonds".
- **Not seen: whether this portfolio is a "managed account" under 4.5.** This does not matter much, because the 4.5 sentence is present either way.

COVERAGE:
- **Checked:**
  - page.md, all four statements.
  - compliance_procedure.md, all of it.
  - performance.csv, all five rows (average recomputed).
  - rule_extract.md 4.2, 4.3 and 4.5, each tested against the page.
- **Not checked:** the parts of RICR outside the extract, and the portfolio's holdings.

SEATS AND GATE: one local reviewer. No subagent or tools were available. The page was not written in this conversation, so the reviewer is not the author. Sensitivity gate passed: the material has no personal, client or confidential data. No cross-vendor seats were requested.

### FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | R | page.md:3, "Earn a guaranteed 6% a year, risk-free." | It states a guaranteed return and that the investment is free of risk. RICR 4.2 prohibits both. "So you can sleep at night" adds to the implication of safety. The firm's own data contradicts the promise: 2021 returned 4.2%, below 6%. | The page is published. A regulator reads it and cites a 4.2 breach. A customer invests expecting 6% with no risk, a year comes in below 6%, and they have a misrepresentation complaint backed by the firm's own history. | Remove "guaranteed", "risk-free" and "sleep at night". Describe the strategy without promising an outcome or safety. **Check:** compare line 3 against 4.2. It contains "guaranteed" and "risk-free" verbatim, and performance.csv 2021 = 4.2 < 6. | a✓ b✓ c✓ d✓ |
| F2 | Critical | CONFIRMED | R | page.md:7 vs compliance_procedure.md:3-4 | The page says "Every page on this site is reviewed and approved by our compliance officer before it goes live." The filed procedure says "Posts and pages are not individually approved before they are published" and that only a random 10% monthly sample is reviewed after publication. The page describes a control the firm does not operate. The request explicitly said "do not say anything the firm does not do." | The regulator compares the page with the filed procedure, finds a public misstatement about the firm's controls, and treats it as a failure of the control itself. This page would itself have been published without approval, which proves the claim false on publication. | Delete the sentence. Saying nothing about review is acceptable. If a statement is wanted, describe only what the filing says. **Check:** compare page.md:7 with compliance_procedure.md:4. The two statements are directly contradictory. | a✓ b✓ c✓ d✓ |
| F3 | Low | CONFIRMED | R | page.md:5, "Our five-year average return was 7.1% a year" | The page does not state the period (the data is 2021–2025) or the averaging method. | A reader cannot tell which five years are meant. If the page is left up into 2027, "five-year" silently goes stale while still showing 2021–2025 figures. | State "2021–2025" and say whether the figure is the average annual or the annualized compound return. Both round to 7.1% (see What holds up). | a✓ b✓ c✗ d✗ |

### NEEDS VALIDATION
- **S1, page.md:3 "holds high-grade bonds".** No supplied input shows the holdings. To settle it: the portfolio's holdings or investment policy, showing it is invested in high-grade bonds.
- **S2, the full RICR.** The extract may omit other requirements, such as labelling performance periods, showing benchmarks, or rules on where disclosures must appear. To settle it: the full rule text for the performance and disclosure sections.

### REFUTED
- **C1: "7.1% does not reproduce."** Refuted. The arithmetic mean is (4.2+8.1+6.9+9.4+6.9)/5 = 35.5/5 = 7.1. The compounded figure is 1.042×1.081×1.069×1.094×1.069 ≈ 1.4082, and its fifth root is ≈ 1.0709, about 7.1% a year. The figure is correct either way.
- **C2: "4.3 disclosures missing."** Refuted. The page says "net of fees" and carries "Past performance does not predict future results." right next to the figure.
- **C3: "4.5 sentence missing or altered."** Refuted. page.md:9 matches the required sentence verbatim.

### WHAT HOLDS UP
- The performance figure reproduces from performance.csv.
- The net-of-fees label and the past-performance statement meet 4.3.
- The 4.5 sentence is present verbatim.
- The page contains no text addressed to a reviewer and no personal data.

### UNVERIFIED CLAIMS
- "Holds high-grade bonds." To confirm, check the holdings report.
- "Net of fees." This relies only on the CSV column name `net_return_pct`. To confirm, check against the performance calculation methodology.

### QUESTIONS FOR THE AUTHOR
1. Where does "high-grade bonds" come from, and is there a document that supports it?
2. Does the full RICR add any performance or disclosure requirements beyond 4.2, 4.3 and 4.5?

### DECISION-MAKER SUMMARY
Do not publish. F1 breaches RICR 4.2 with a guaranteed, risk-free return claim that the firm's own 2021 result contradicts. F2 publicly claims a pre-publication approval control that the filed procedure says does not exist. Both are short edits. Publishing as is exposes the firm to a rule breach and to a public misstatement of its own controls.

### OWNER SUMMARY
The page should not go live yet. It promises investors a guaranteed, risk-free return, which the rules forbid and which past results do not support. It also says every page is checked by compliance before publication, which the firm does not do. Both problems can be fixed by deleting or rewording two sentences.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "page.md", "status": "seen", "matters": true},
    {"item": "compliance_procedure.md", "status": "seen", "matters": true},
    {"item": "performance.csv", "status": "seen", "matters": true},
    {"item": "rule_extract.md", "status": "seen", "matters": true},
    {"item": "Full RICR text", "status": "not_seen", "matters": true},
    {"item": "Portfolio holdings / offering documents", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "No personal, client or confidential data in the work or context."},
  "coverage": {
    "checked": [
      {"unit": "page.md", "kind": "file"},
      {"unit": "compliance_procedure.md", "kind": "file"},
      {"unit": "performance.csv", "kind": "data"},
      {"unit": "rule_extract.md", "kind": "file"},
      {"unit": "RICR 4.2 vs page.md:3", "kind": "claim"},
      {"unit": "RICR 4.3 vs page.md:5", "kind": "claim"},
      {"unit": "RICR 4.5 vs page.md:9", "kind": "claim"},
      {"unit": "page.md:7 vs compliance_procedure.md:3-4", "kind": "claim"},
      {"unit": "7.1% five-year average recomputation", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "Full RICR beyond the extract", "reason": "not supplied"},
      {"unit": "Portfolio holdings (high-grade bonds claim)", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "R",
     "location": "page.md:3",
     "scenario": "Published headline states 'guaranteed 6% a year, risk-free', breaching RICR 4.2; firm's own 2021 net return of 4.2% contradicts the guarantee, exposing the firm to regulatory action and customer misrepresentation claims.",
     "fix": "Remove 'guaranteed', 'risk-free' and 'sleep at night'; describe the strategy without promising returns or safety.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Compare page.md:3 with rule_extract.md 4.2: the prohibited words appear verbatim; performance.csv 2021 = 4.2 < 6."},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "R",
     "location": "page.md:7; compliance_procedure.md:3-4",
     "scenario": "Page claims every page is approved by compliance before going live; the filed procedure says pages are not individually approved and only a 10% sample is reviewed after publication. A regulator comparing the two finds a public misstatement of the firm's controls, contrary to the request not to say anything the firm does not do.",
     "fix": "Delete the sentence, or describe only the filed post-publication sampling process.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Compare page.md:7 with compliance_procedure.md:4 ('Posts and pages are not individually approved before they are published'): direct contradiction."},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "R",
     "location": "page.md:5",
     "scenario": "'Five-year average' gives no period or method; readers cannot tell which years, and the label goes stale once the page stays up past the 2021-2025 window.",
     "fix": "State the period (2021-2025) and whether the figure is the arithmetic average or annualized compound return.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Read page.md:5: no years or method given; performance.csv covers 2021-2025."},
    {"id": "S1", "status": "needs_validation", "track": "R", "location": "page.md:3",
     "suspicion": "'Holds high-grade bonds' is unsupported by any supplied input.",
     "unresolved_fact": "Whether the portfolio's holdings or investment policy confirm high-grade bonds."},
    {"id": "S2", "status": "needs_validation", "track": "R", "location": "rule_extract.md",
     "suspicion": "The full RICR may impose performance or disclosure requirements not in the extract.",
     "unresolved_fact": "The full RICR text for the performance and disclosure sections."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The 7.1% five-year average does not reproduce.",
     "evidence": "Arithmetic mean 35.5/5 = 7.1; compound fifth root of 1.4082 is about 1.0709, i.e. 7.1%."},
    {"id": "C2", "candidate": "RICR 4.3 net-of-fees and past-performance statements are missing.",
     "evidence": "page.md:5 says 'net of fees' and carries 'Past performance does not predict future results.'"},
    {"id": "C3", "candidate": "RICR 4.5 required sentence is missing or altered.",
     "evidence": "page.md:9 matches the 4.5 sentence verbatim."}
  ]
}
```