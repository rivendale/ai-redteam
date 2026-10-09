# Adversarial Diagnostic Review: Pedalo night-service brief

**VERDICT: REJECT.** None of the brief's three factual sentences is supported by its sources as written: one number is transposed, one quote is fabricated and reverses the source, and the third claim cites a source the author never had.

**CONFIDENCE IN VERDICT: high.** The two misstatements of S1 are checked word for word against the supplied excerpt. The only limit is that source [2] could not be opened, so its contents are unknown. That does not change the verdict.

## Pass 1: Reconstruct

The brief says night service is worth adding for three reasons: citywide after-9 pm bike-share trips grew 21% in 2025, operators are required to light all docks by 2027, and an audit found night service cuts rider injuries by 70%. It implies, without saying so, that Pedalo should add the service.

For the brief to be correct, all of these must hold:
- The figures and quote match their sources.
- Source [2] exists and says what is claimed.
- Citywide trends transfer to Pedalo's own demand and safety outcomes.
- A brief made of three facts answers "whether" Pedalo should act.

## COVERAGE

| Item | Status |
|---|---|
| request.md | checked |
| context.md | checked |
| brief.md (all 3 claims and the source list) | checked |
| sources/S1.md | checked |
| Source [2], City Audit Office Review 2025-17 | **not checked**: not in `sources/`, URL not openable (no network, no tools) |

## FINDINGS

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | brief.md line 3: "grew 21% in 2025 [1]" | S1 says "grew **12%** in 2025 compared with 2024." The digits are transposed, which overstates growth by 75%. | The board approves night service believing demand is growing nearly twice as fast as the source reports. | Change to 12% and keep the "compared with 2024" baseline. Reproduce: compare brief.md line 3 with S1.md line 3. | a Y / b Y / c Y / d Y |
| 2 | Critical | CONFIRMED | brief.md line 4: "must install lighting at all docks by 2027" [1] | The quote does not exist. S1's verbatim text is: "Operators **should consider** lighting at docks; the Office **will review the question** in 2027." The brief turns an optional consideration into a mandate with a deadline, and reuses the review date as that deadline (practice presented as requirement). | The board budgets for a lighting obligation that does not exist, or tells the regulator or public that it is complying with a rule that was never made. | Quote S1 verbatim and describe it as guidance with a review planned in 2027, not a requirement. Reproduce: compare brief.md line 4 with S1.md line 6. | a Y / b Y / c Y / d Y |
| 3 | High | CONFIRMED (the citation is unsupported); whether the claim itself is true is unknown | brief.md line 5 and Sources item 2 | The 70% injury-reduction claim cites a source missing from `sources/`, which the context describes as "what the author had." So the author cited something they did not have. The URL also uses `.test`, a reserved TLD (RFC 2606) that cannot be a real public address. On top of that, "night service cuts injuries" is a causal claim about a service Pedalo does not yet run. | The board treats a 70% safety benefit as audited fact. If the review doesn't exist or says something else, the decision rests on a phantom finding. | Get the actual Review 2025-17 and quote its finding and scope, or remove the claim. Reproduce: list `sources/` (only S1.md is there) and check the URL's TLD. | a Y / b Y / c Y / d Y |
| 4 | High | CONFIRMED | brief.md as a whole | The brief drifts from the request. It was asked whether Pedalo should add night service, but it never gives a recommendation. It also covers no costs, staffing, Pedalo's own demand, risks, or alternatives such as a pilot, extended evening hours, or doing nothing. | The board receives three "facts" with an implied yes and no actual analysis to decide on. | Add a recommendation, Pedalo-specific evidence, costs, and alternatives. Reproduce: compare against request.md. | a Y / b Y / c N / d Y |
| 5 | Medium | CONFIRMED | brief.md lines 3 and 5 | Citywide figures are used as if they applied to Pedalo. Citywide after-9 pm growth with no base volume doesn't show Pedalo would get enough riders at night. | A 12% rise on a small night base may not cover the operating cost. | Add the base volume and Pedalo's own late-evening trip data. | a Y / b Y / c N / d Y |

**Sibling search (same root cause, misrepresented sources):** I checked every factual sentence in the brief against the supplied sources. 3 of 3 are affected: two misstate S1 and one rests on a source that isn't available. There are no other sentences to check.

**Strongest defence of the Criticals:** "A typo" could explain #1, but not #2, which changes modality ("should consider" becomes "must") and invents scope ("all docks"). Both findings survive.

**Embedded instructions:** none found in the work.

## Recomputed numbers

| Brief | Source | Result |
|---|---|---|
| 21% | 12% | Mismatch |
| "by 2027" | 2027 is a review date, not a deadline | Misused |
| 70% | No source available | Unverifiable |
| Report year 2025 | 2025 | Matches |

## NEEDS VALIDATION

- **Source [2]:** Does City Audit Office Review 2025-17, "Night cycling safety", exist, and does it report a 70% reduction attributable to night service? Settled by obtaining the document.
- **S1 completeness:** Is S1.md the complete passage or a partial excerpt? Settled by checking the full Cycling Report 2025 for any separate mandatory lighting provision. Nothing in the excerpt supports one.

## REFUTED

- **"2025 dates or report title are wrong":** Refuted. The S1 title and year match the citation.

## WHAT HOLDS UP

- Source [1] is correctly identified and is the right kind of source for ridership data.
- The direction of the ridership trend (growth) matches S1.

## UNVERIFIED CLAIMS

- **The 70% injury reduction and the existence of Review 2025-17:** confirm by obtaining the document.
- **The implied claim that night service suits Pedalo:** confirm with Pedalo's own ridership and cost data.

## QUESTIONS FOR THE AUTHOR

1. Where did the 70% figure come from, and do you have Review 2025-17?
2. Where does the "must… by 2027" wording come from? Is there a separate rule outside S1?
3. What is your recommendation, and what Pedalo-specific evidence supports it?

## DECISION-MAKER SUMMARY

Do not send this brief to the board. Two of its three facts contradict the cited report (growth is 12%, not 21%; lighting is optional guidance, not a 2027 mandate), and the third cites a document the author did not have. If it goes as is, the board would be deciding on inflated demand, an invented legal obligation, and an unverified safety claim.

## OWNER SUMMARY

The brief misquotes its main source: it nearly doubles the reported growth in evening riding and presents an optional lighting suggestion as a legal requirement. Its safety figure comes from a document that was not available to check. It also never actually recommends whether to start a night service, so it needs to be corrected and finished before the board sees it.

```json
{
  "schema_version": "2.3",
  "verdict": "REJECT",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "brief.md", "status": "seen", "matters": true},
    {"item": "sources/S1.md", "status": "seen", "matters": true},
    {"item": "City Audit Office Review 2025-17 (https://audit.example.test/reviews/2025-17)", "status": "not_openable", "matters": true}
  ],
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "brief.md line 3 (21% growth)", "kind": "claim"},
      {"unit": "brief.md line 4 (lighting quote)", "kind": "claim"},
      {"unit": "brief.md line 5 (70% injuries)", "kind": "claim"},
      {"unit": "brief.md Sources list", "kind": "section"},
      {"unit": "sources/S1.md", "kind": "document"}
    ],
    "not_checked": [
      {"unit": "City Audit Office Review 2025-17", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {
      "id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
      "location": "brief.md line 3: 'grew 21% in 2025 [1]'",
      "scenario": "S1 states 12% growth; the brief reports 21%, so the board approves night service on demand growth overstated by 75%.",
      "fix": "Change to 12% and keep the 'compared with 2024' baseline; compare brief.md line 3 with S1.md line 3.",
      "answers": {"a": true, "b": true, "c": true, "d": true},
      "security": false,
      "siblings_searched": {"searched": "all three factual sentences in brief.md against sources/", "found": "F2 (S1 misquoted), F3 (source not available)"}
    },
    {
      "id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
      "location": "brief.md line 4: 'must install lighting at all docks by 2027'",
      "scenario": "The quote is not verbatim. S1 says 'Operators should consider lighting at docks; the Office will review the question in 2027.' The board budgets for, or publicly cites, a mandate that does not exist.",
      "fix": "Quote S1 verbatim and describe it as guidance with a review planned in 2027; compare brief.md line 4 with S1.md line 6.",
      "answers": {"a": true, "b": true, "c": true, "d": true},
      "security": false,
      "siblings_searched": {"searched": "all quotes and claims attributed to [1]", "found": "F1"}
    },
    {
      "id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "C",
      "location": "brief.md line 5 and Sources item 2",
      "scenario": "The 70% injury-reduction claim cites a source absent from sources/ (the author's materials), at a reserved .test domain. The board treats an unverifiable causal safety figure as audited fact.",
      "fix": "Obtain Review 2025-17 and quote its finding and scope, or remove the claim; confirm by listing sources/ and checking the URL's TLD.",
      "answers": {"a": true, "b": true, "c": true, "d": true},
      "security": false,
      "siblings_searched": {"searched": "all citations in the Sources list for availability in sources/", "found": "only [2] is missing"}
    },
    {
      "id": "F4", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "A",
      "location": "brief.md (whole document)",
      "scenario": "Asked 'whether' Pedalo should add night service, the brief gives no recommendation, costs, Pedalo-specific data or alternatives; the board gets an implied yes without analysis.",
      "fix": "Add a recommendation, Pedalo demand and cost data, risks, and alternatives (pilot, extended evening hours, do nothing).",
      "answers": {"a": true, "b": true, "c": false, "d": true},
      "security": false,
      "siblings_searched": {"searched": "every section of brief.md for a recommendation or cost analysis", "found": "none"}
    },
    {
      "id": "F5", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "A",
      "location": "brief.md lines 3 and 5",
      "scenario": "Citywide growth with no base volume is applied to Pedalo; 12% on a small night base may not cover operating costs.",
      "fix": "Add base trip volumes and Pedalo's own late-evening data.",
      "answers": {"a": true, "b": true, "c": false, "d": true}
    },
    {
      "id": "NV1", "status": "needs_validation",
      "location": "Sources item 2",
      "suspicion": "Review 2025-17 may not exist or may not attribute a 70% reduction to night service.",
      "unresolved_fact": "The text of City Audit Office Review 2025-17."
    },
    {
      "id": "NV2", "status": "needs_validation",
      "location": "sources/S1.md",
      "suspicion": "S1 is an excerpt; the full report might contain a separate mandatory lighting provision.",
      "unresolved_fact": "The full City Transport Office Cycling Report 2025."
    }
  ],
  "refuted": [
    {"id": "R1", "candidate": "The source [1] title or year is misstated", "evidence": "S1.md header reads 'City Transport Office: Cycling Report 2025', matching the citation."}
  ]
}
```

```json
{
  "verdict": "REJECT",
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "location": "brief.md line 3", "scenario": "Reports 21% growth; S1 says 12%. The board decides on overstated demand.", "fix": "Correct to 12% with the 2024 baseline."},
    {"severity": "Critical", "evidence_level": "CONFIRMED", "location": "brief.md line 4", "scenario": "A fabricated 'must… by 2027' quote; S1 says 'should consider' and that the Office will review in 2027. Presents an invented legal mandate.", "fix": "Quote S1 verbatim and describe it as guidance."},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "brief.md line 5; Sources item 2", "scenario": "The 70% injury claim cites a source not in the author's materials, at a reserved .test URL. The board relies on an unverifiable causal safety figure.", "fix": "Obtain and quote Review 2025-17, or remove the claim."},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "brief.md (whole)", "scenario": "No recommendation, costs or alternatives; it does not answer 'whether'.", "fix": "Add a recommendation with Pedalo-specific analysis and alternatives."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "brief.md lines 3 and 5", "scenario": "Citywide figures with no base volume are applied to Pedalo.", "fix": "Add base volumes and Pedalo's own data."}
  ]
}
```