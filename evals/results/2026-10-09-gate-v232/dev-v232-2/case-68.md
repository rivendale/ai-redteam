VERDICT: **REWORK.** Two of the note's three claims fail against their own retrieved sources: one cites a paper about parking, and the other contradicts the replication it cites.

CONFIDENCE: **high** for the confirmed findings, because each rests on a direct quote from the supplied copies. Three things limit overall confidence:
- This session has no tools, so no DOI or URL could be resolved.
- Only abstracts were supplied.
- The review was done by this session rather than a fresh subagent. This session did not write the note, but there was no independent seat.

INPUTS LEDGER:
- **Seen:** request.md, context.md, note.md, retrieved/ref1.md, retrieved/ref2.md, retrieved/ref3.md.
- **Not seen:** the live records at the three DOIs/URLs (no network, no tools). This matters for whether ref3's metadata or the note's citation is wrong. It does not matter for F1 or F2, which fail on the copies the author had.
- **Not seen:** the full texts behind the abstracts. This matters for whether ref1's design ("matched controls") holds up, but not for the verdict.

COVERAGE:
- **Scope:** the whole work. It is small: one note and three retrieved copies.
- **Checked:**
  - request.md, context.md, note.md (all of it), ref1.md, ref2.md, ref3.md.
  - Claims C1 (14 firms, lower exhaustion), C2 (largest in small teams) and C3 (held in a 2024 replication).
  - The title, authors, venue, year and identifier for each citation.
  - The unstated assumption that "exhaustion" stands for "burnout".
- **Not checked:** live DOI/URL resolution (no_tools); full texts (not_supplied).

SEATS AND GATE:
- One seat ran: this reviewer, with no tools.
- No subagent or cross-vendor seats were available.
- Sensitivity gate: not sensitive. The material is published research metadata with no personal data.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | C | note.md:3 "The effect is largest in small teams [2]"; note.md:7; retrieved/ref2.md | The cited work is a different paper. The note cites "Team size and the shorter week". The retrieved copy at the same URL is "Parking policies and commuter satisfaction in mid-sized cities", which surveys 800 commuters about parking and says nothing about four-day weeks, team size or burnout. The claim has no support, and the citation is fabricated or mismatched. | A policy proposal targets the four-day week at small teams on the strength of [2]. Anyone who opens the source finds a parking survey, which discredits the proposal and the note. | Delete the small-teams claim, or find and retrieve a source that actually tests team size. Cite it with a copy that matches its title. | a Y, b Y, c Y, d Y |
| F2 | Critical | CONFIRMED | C | note.md:3 "it held in a 2024 replication [3]"; retrieved/ref3.md | The cited source says the opposite. Ref3's abstract reads: "the exhaustion difference was not significant (d = 0.04, 95% CI -0.19 to 0.27)". The interval includes zero, and its upper bound (0.27) is below the original d = 0.31. The replication did not reproduce the effect. | A reader of the policy proposal believes the result has been replicated. In fact, the only replication on record is null, so the proposal overstates the evidence. | Rewrite the claim as: "a replication on 6 firms found no significant difference (d = 0.04, 95% CI −0.19 to 0.27) [3]". Revise the note's overall conclusion to mixed or weak evidence. | a Y, b Y, c Y, d Y |
| F3 | Medium | CONFIRMED | C | note.md:3 "2024 replication"; note.md:8 "2024"; retrieved/ref3.md "Journal of Work Studies, 2019 … Submitted 2018, published 2019" | The citation metadata does not match the copy. The note says 2024, and the DOI string reads "jws.2024.007", but the copy says it was published in 2019. A 2019 paper also cannot replicate a 2023 study, so either the copy is not the cited work or its link to ref1 is wrong. | A checker sees the date conflict and cannot tell which replication the note means. The claimed sequence (2023 original, 2024 replication) may be false. | Resolve the DOI. Correct the year, or replace the copy with the work actually cited. State which study it replicates. | a Y, b Y, c N, d Y |
| F4 | Medium | CONFIRMED | C, A | note.md:1 title "reduce burnout" vs ref1.md and ref3.md, which measure "exhaustion" | Drift in the construct. The sources measure exhaustion scores only, which is one dimension of burnout. The note answers "do they reduce burnout?" from exhaustion data without saying so. | The policy proposal claims a burnout reduction. The evidence covers one subscale with a small effect (d = 0.31) that did not replicate. | State that the outcome is exhaustion, report d = 0.31 as a small effect, and avoid generalizing to burnout without a source that measures burnout. | a Y, b Y, c N, d Y |

## Needs validation

- **S1 (ref1, design quality):** whether ref1's full text supports "matched controls" and the stated sample. The deciding fact is the methods section of Calder & Osei 2023, which was not supplied.
- **S2 (ref3 identity):** whether DOI 10.5555/jws.2024.007 resolves to the 2019 Mbeki et al. record or to a different 2024 paper. The deciding fact is the DOI landing page.

## Refuted

- **Candidate: the C1 claim misstates ref1.** Refuted. ref1.md's abstract reads "Across 14 firms, employees on a four-day week reported lower exhaustion scores than matched controls". The note's wording is the same apart from omitting d.

## What holds up

- **Claim C1:** the note's wording matches ref1's abstract, apart from omitting the effect size.
- **Ref1's metadata:** the title, authors, venue, year (2023) and DOI all agree between the note and the copy.

## Unverified claims

- Whether the three DOIs/URLs resolve to the retrieved copies. Confirm by resolving each and comparing title and authors.
- Ref1's study design. Confirm from the full text.

## Questions for the author

1. Where did "Team size and the shorter week" come from, and does a copy of it exist?
2. Which replication did you mean by "2024 replication"? Did you read ref3's result?

## Decision-maker summary

Do not use this note to support the policy proposal yet. One citation points to an unrelated parking study, and the cited replication found no effect. Proceeding risks a proposal resting on a single small, unreplicated exhaustion result presented as replicated evidence on burnout.

## Owner summary

The note correctly reports one study that found less exhaustion on a four-day week. However, one of its sources is about parking, not working hours. Its "replication" actually found no effect, so the note needs to be rewritten before anyone relies on it.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "note.md", "status": "seen", "matters": true},
    {"item": "retrieved/ref1.md", "status": "seen", "matters": true},
    {"item": "retrieved/ref2.md", "status": "seen", "matters": true},
    {"item": "retrieved/ref3.md", "status": "seen", "matters": true},
    {"item": "live DOI/URL records for refs 1-3", "status": "not_seen", "matters": true},
    {"item": "full texts of refs 1 and 3", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Published research metadata only; no personal or confidential data."},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "note.md", "kind": "document"},
      {"unit": "retrieved/ref1.md", "kind": "document"},
      {"unit": "retrieved/ref2.md", "kind": "document"},
      {"unit": "retrieved/ref3.md", "kind": "document"},
      {"unit": "C1: 14 firms, lower exhaustion than matched controls [1]", "kind": "claim"},
      {"unit": "C2: effect largest in small teams [2]", "kind": "claim"},
      {"unit": "C3: held in a 2024 replication [3]", "kind": "claim"},
      {"unit": "exhaustion stands in for burnout", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "live DOI/URL resolution for refs 1-3", "reason": "no_tools"},
      {"unit": "full texts of refs 1 and 3", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md:3 and note.md:7; retrieved/ref2.md",
     "scenario": "The note cites 'Team size and the shorter week' for 'effect is largest in small teams', but the retrieved copy is 'Parking policies and commuter satisfaction in mid-sized cities' and says nothing about four-day weeks or team size; a policy targeting small teams would rest on an unrelated paper.",
     "fix": "Remove the small-teams claim or replace [2] with a retrieved source that actually tests team size and matches its citation.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "title, authors, venue and identifier of every citation (refs 1-3) against its retrieved copy",
                           "found": "ref1 matches; ref3 matches title and authors but not year (see F3)"}},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md:3 'it held in a 2024 replication [3]'; retrieved/ref3.md abstract",
     "scenario": "Ref3 reports 'the exhaustion difference was not significant (d = 0.04, 95% CI -0.19 to 0.27)'; the note says the effect held, so the policy proposal presents a null replication as confirmation.",
     "fix": "State the null result with its effect size and CI and revise the note's overall conclusion to mixed/weak evidence.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "every claim in note.md for direction or strength overstated relative to its source",
                           "found": "C2 is unsupported (F1); C1 matches ref1 but omits d = 0.31 (F4)"}},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md:3 and note.md:8 '2024'; retrieved/ref3.md 'Journal of Work Studies, 2019 ... Submitted 2018, published 2019'",
     "scenario": "The note dates the replication 2024 while the copy says 2019, which also predates the 2023 study it supposedly replicates; a checker cannot tell which work is cited.",
     "fix": "Resolve the DOI, correct the year or the retrieved copy, and state which study ref3 replicates.",
     "answers": {"a": true, "b": true, "c": false, "d": true}},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md:1 title 'reduce burnout' vs retrieved/ref1.md and ref3.md outcome 'exhaustion scores'",
     "scenario": "The proposal claims reduced burnout although the sources measure only exhaustion, with a small effect (d = 0.31) that did not replicate.",
     "fix": "Name the outcome as exhaustion, report d = 0.31 as small, and do not generalize to burnout without a source measuring burnout.",
     "answers": {"a": true, "b": true, "c": false, "d": true}},
    {"id": "S1", "status": "needs_validation", "track": "C", "location": "retrieved/ref1.md",
     "suspicion": "The abstract alone may overstate the design ('matched controls').",
     "unresolved_fact": "The methods section of Calder & Osei 2023 (full text not supplied)."},
    {"id": "S2", "status": "needs_validation", "track": "C", "location": "note.md:8; retrieved/ref3.md",
     "suspicion": "The retrieved ref3 may not be the work the note cites.",
     "unresolved_fact": "What DOI 10.5555/jws.2024.007 resolves to (no network)."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Claim C1 misstates ref1.",
     "evidence": "retrieved/ref1.md abstract: 'Across 14 firms, employees on a four-day week reported lower exhaustion scores than matched controls', the same wording as the note."}
  ]
}
```