VERDICT: **REWORK.** Two of the note's three claims are contradicted or unsupported by their own retrieved sources. One retrieved copy is a different work entirely, and the "replication" reports a null result that the note presents as confirmation.

CONFIDENCE: **medium.** Same-context review with no tools (anchoring risk; re-run in a fresh session for anything high-stakes). Only abstracts were supplied, and I could not open DOIs or URLs. The core findings, however, rest on exact quotes from the supplied copies, so they do not depend on the missing material.

INPUTS LEDGER:
- Seen: `request.md`, `context.md`, `note.md`, `retrieved/ref1.md`, `retrieved/ref2.md`, `retrieved/ref3.md`.
- Not seen: the full texts behind refs 1–3 (only abstract-level copies exist) and the live DOI/URL targets (no network). This matters for method-level questions (how controls were matched, which exhaustion instrument was used, whether the ref3 copy is the right record). It does not matter for F1–F3, which are contradictions visible in the supplied copies.

COVERAGE:
- Scope: the whole note and all three retrieved copies.
- Checked: three claims (C1–C3), three citations (bibliographic metadata compared against each retrieved copy), and the note's framing against the original request.
- Not checked: full texts (not supplied) and live links (no network).

SEATS AND GATE: No subagent or cross-vendor seats were available, so this was a single same-context review. Sensitivity gate passed: the material is published research metadata, with no personal or confidential data.

## CLAIMS TO EVIDENCE

| Claim | Location | Source / derivation | Status | Link |
|---|---|---|---|---|
| C1: "Across 14 firms, employees on a four-day week reported lower exhaustion scores than matched controls" | note.md ¶1, sentence 1, [1] | ref1.md abstract: "Across 14 firms, employees on a four-day week reported lower exhaustion scores than matched controls (d = 0.31)." Cohort: 14 firms. Metric: exhaustion score. Baseline: matched controls. Effect size d = 0.31. Time window not stated. | Verified observation (abstract level). The metadata (title, authors, journal, year, DOI) matches the citation. | F4, N1 |
| C2: "The effect is largest in small teams" | note.md ¶1, sentence 2, [2] | ref2.md is titled "Parking policies and commuter satisfaction in mid-sized cities". It covers 800 commuters and parking, and says nothing about team size or work schedules. | UNSUPPORTED. The retrieved copy is a different work. | F1 |
| C3: "it held in a 2024 replication" | note.md ¶1, sentence 2, [3] | ref3.md: "the exhaustion difference was not significant (d = 0.04, 95% CI -0.19 to 0.27)"; "Submitted 2018, published 2019." Cohort: 6 firms. | CONTRADICTED on the result. Year conflicts with the citation. | F2, F3, N2 |

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | C | note.md ¶1 "largest in small teams [2]"; Sources item 2 vs retrieved/ref2.md | The citation is to "Team size and the shorter week". The retrieved copy at the same URL is "Parking policies and commuter satisfaction in mid-sized cities", a commuter parking survey. The cited content does not support the claim, so the citation is fabricated or mismatched. | Policy designers target small teams on the strength of a moderation effect that no supplied source reports. Anyone who checks the link finds a parking study, which undermines the whole proposal. | Locate the actual work that reports a team-size effect and retrieve it. If none exists, delete the claim. | a✓ b✓ c✓ d✓ |
| F2 | Critical | CONFIRMED | C | note.md ¶1 "it held in a 2024 replication [3]" vs retrieved/ref3.md abstract | The source states that the effect was *not* replicated: "not significant (d = 0.04, 95% CI -0.19 to 0.27)". The interval includes zero, and the point estimate is about an eighth of ref1's d = 0.31. The note inverts the finding. | Decision-makers read the evidence as replicated when the only replication on file is null. They adopt the policy with unwarranted confidence. | State the null replication accurately. Revise the overall conclusion to something like "one study found a small-to-moderate reduction in exhaustion; a smaller replication did not". | a✓ b✓ c✓ d✓ |
| F3 | Medium | CONFIRMED | C | note.md "2024 replication"; Sources item 3 "2024" vs ref3.md "Journal of Work Studies, 2019 … Submitted 2018, published 2019" | Citation year and copy year disagree. A 2019 paper cannot replicate a 2023 study. Either the copy is the wrong record (despite the matching DOI string `jws.2024.007`) or the citation metadata is wrong. | A reader cannot tell which study the replication claim rests on, and the citation fails verification. | Resolve which record DOI 10.5555/jws.2024.007 actually resolves to, then correct either the year or the retrieved copy. | a✓ b✓ c✗ d✓ |
| F4 | Medium | CONFIRMED | C | note.md title "do 4-day weeks reduce burnout?" vs C1's evidence (exhaustion scores, matched controls) | The only supporting evidence measures exhaustion, which is one dimension of burnout, in an observational matched-control comparison. The framing implies a causal effect on burnout overall. The note also omits the effect size (d = 0.31). | Readers take "reduces burnout" as established and causal when the evidence shows lower exhaustion in a non-randomized comparison of 14 firms. | Say "lower exhaustion (one burnout dimension), d = 0.31, matched observational design". Avoid causal and burnout-wide wording unless a source supports it. | a✓ b✓ c✗ d✓ |

Siblings for F1 and F2 (same root cause: the claim does not match the source content): I checked all three citations. Ref1 matches its citation and supports C1. No further siblings exist; the note makes only three claims. Neither finding is a security finding.

NEEDS VALIDATION:
- **N1:** Whether ref1's full text supports the abstract. Settled by the full paper: matching method, exhaustion instrument, and the firm-level versus employee-level unit of analysis.
- **N2:** Whether a genuine 2024 replication exists that is distinct from the 2019 record. Settled by resolving DOI 10.5555/jws.2024.007 with network access.

REFUTED: none.

WHAT HOLDS UP: C1 is quoted essentially verbatim from ref1. Ref1's title, authors, journal, year and DOI all match the citation.

UNVERIFIED CLAIMS: none beyond N1 and N2. Each claim was either confirmed or contradicted against its retrieved copy.

QUESTIONS FOR THE AUTHOR:
1. Where did "Team size and the shorter week" come from? Does a copy of it exist?
2. Did you read ref3's result? Is there a different 2024 replication you meant to cite?

DECISION-MAKER SUMMARY: Only one of the three claims is backed by its source. The small-teams claim cites a parking study, and the "replication held" claim reverses a null result. Do not use this note to support the policy proposal until it is rewritten. Proceeding risks a proposal built on a misreported replication and a citation that fails on first check.

OWNER SUMMARY: The note says a shorter week reliably lowers burnout, but its own sources do not back that up. One cited source is about parking, not work. The follow-up study the note calls a confirmation actually found no clear effect. The note needs rewriting before anyone relies on it.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "full texts of refs 1-3", "status": "not_seen", "matters": false},
    {"item": "live DOI/URL targets", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"}, {"unit": "context.md", "kind": "document"},
      {"unit": "note.md", "kind": "document"}, {"unit": "retrieved/ref1.md", "kind": "document"},
      {"unit": "retrieved/ref2.md", "kind": "document"}, {"unit": "retrieved/ref3.md", "kind": "document"},
      {"unit": "C1 exhaustion across 14 firms", "kind": "claim"},
      {"unit": "C2 largest in small teams", "kind": "claim"},
      {"unit": "C3 held in 2024 replication", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "full texts of refs 1-3", "reason": "not_supplied"},
      {"unit": "live DOI/URL resolution", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md para 1 'largest in small teams [2]'; Sources item 2 vs retrieved/ref2.md",
     "scenario": "Cited 'Team size and the shorter week' but the retrieved copy is 'Parking policies and commuter satisfaction in mid-sized cities'; policy targets small teams on an effect no source reports.",
     "fix": "Retrieve the actual team-size work or delete the claim.",
     "answers": {"a": true, "b": true, "c": true, "d": true}, "security": false,
     "siblings_searched": {"searched": "all three citations against their retrieved copies", "found": "ref1 matches; ref3 contradicted (F2)"}},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md para 1 'it held in a 2024 replication [3]' vs retrieved/ref3.md abstract",
     "scenario": "Source reports 'not significant (d = 0.04, 95% CI -0.19 to 0.27)'; note says the effect held, so decision-makers believe a null replication confirmed the effect.",
     "fix": "Report the null replication accurately and weaken the overall conclusion.",
     "answers": {"a": true, "b": true, "c": true, "d": true}, "security": false,
     "siblings_searched": {"searched": "all three claims for source-content mismatch", "found": "F1 (ref2); ref1 holds"}},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md Sources item 3 '2024' vs retrieved/ref3.md 'published 2019'",
     "scenario": "A 2019 paper cannot replicate a 2023 study; readers cannot verify which work the replication claim rests on.",
     "fix": "Resolve DOI 10.5555/jws.2024.007 and correct the year or the retrieved copy.",
     "answers": {"a": true, "b": true, "c": false, "d": true}},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md title vs ref1.md abstract (exhaustion, matched controls, d = 0.31)",
     "scenario": "Readers take 'reduces burnout' as causal and burnout-wide when evidence is lower exhaustion in an observational comparison.",
     "fix": "Narrow wording to exhaustion, state d = 0.31 and the matched observational design.",
     "answers": {"a": true, "b": true, "c": false, "d": true}},
    {"id": "N1", "status": "needs_validation", "track": "C", "location": "retrieved/ref1.md",
     "suspicion": "Abstract may overstate design or result relative to the full text.",
     "unresolved_fact": "Full-text matching method, exhaustion instrument and unit of analysis."},
    {"id": "N2", "status": "needs_validation", "track": "C", "location": "note.md Sources item 3",
     "suspicion": "A distinct 2024 replication may exist and the wrong record was retrieved.",
     "unresolved_fact": "What DOI 10.5555/jws.2024.007 resolves to."}
  ],
  "refuted": []
}
```