VERDICT: **REWORK.** Two of the note's three claims are contradicted by the retrieved copies of their own sources: [2] is about parking, and [3] reports the opposite of what the note says.

CONFIDENCE: **high** for the findings below, because each one rests on a direct quote from a short retrieved copy. Three things limit it:
- I had no tools or network access, so I could only read the retrieved copies quoted inline.
- Only the abstracts were retrieved, not the full texts.
- I was a single reviewer, although I did not write the note.

INPUTS LEDGER:
- **Seen:** request.md, context.md, note.md, retrieved/ref1.md, retrieved/ref2.md, retrieved/ref3.md.
- **Not seen:**
  - The live DOI and URL targets. No network was available. This matters for [2] and [3]: it is not known whether the copy or the citation is wrong. Either way, the note is currently unsupported.
  - The full texts beyond the abstracts. This matters slightly for [1] and [3], where body text could qualify the abstract.

COVERAGE:
- **Checked:**
  - All three claims in note.md, each against its retrieved copy.
  - Citation metadata (title, authors, venue, year, DOI or URL) for all three sources.
  - Whether the note answers the request.
- **Not checked:**
  - Live sources.
  - Full papers.
  - Whether other literature exists that the note should have cited.

SEATS AND GATE: Same-context review only, with no subagent or tools available in this session. The sensitivity gate was not triggered because the material is published research metadata with no personal or confidential data. No cross-vendor seats were run.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | C | note.md ¶1 "The effect is largest in small teams [2]"; retrieved/ref2.md | The retrieved copy at the cited URL is titled "Parking policies and commuter satisfaction in mid-sized cities". Its abstract covers "reserved and shared parking", not team size or four-day weeks. The cited title "Team size and the shorter week" does not match the copy. | The policy proposal states that the four-day week works best in small teams, citing a parking survey. Anyone who checks the source finds no support, and the proposal's credibility falls with it. | Remove the claim, or find and retrieve a source that actually reports team-size moderation. Repro: open retrieved/ref2.md and compare its Title line with source 2 in note.md. | y/y/y/y |
| F2 | Critical | CONFIRMED | C | note.md ¶1 "it held in a 2024 replication [3]"; retrieved/ref3.md | The source says the opposite: "the exhaustion difference was not significant (d = 0.04, 95% CI -0.19 to 0.27)". The note reports a null replication as a successful one. | Decision-makers adopt the policy believing the effect has been replicated, when the only replication found no significant effect. This is the exact misstatement the request forbids. | Restate the claim: "a replication in 6 firms found no significant difference (d = 0.04, 95% CI −0.19 to 0.27)". Then weigh it against [1] in the note's conclusion. Repro: compare the note's sentence with ref3's abstract. | y/y/y/y |
| F3 | Medium | CONFIRMED | C | note.md source 3 ("Journal of Work Studies, 2024"); retrieved/ref3.md lines 1 and 4 | The citation gives 2024, and the DOI suffix reads jws.2024.007. The copy says "2019" and "Submitted 2018, published 2019". That would make the "replication" predate the 2023 study it replicates, which is impossible. Either the citation or the retrieved copy is not the work it claims to be. | A reviewer of the proposal finds the date inconsistency and cannot tell which paper was actually relied on. The note's "2024" is unsupported either way. | Resolve the DOI to the actual record and retrieve that copy. Correct the year in the note and drop "2024" from the claim unless the record supports it. Repro: compare the year fields in the note and in ref3.md. | y/y/n/n |
| F4 | Low | PROBABLE | A/C | note.md title vs ¶1 | The note asks whether four-day weeks reduce burnout, but its only supported evidence ([1]) measures exhaustion, which is one component of burnout. The note never states a conclusion or flags this gap. | Once F1 and F2 are corrected, the evidence is one study (d = 0.31) and one null replication. A reader may still take the note as showing that burnout falls. | Add an explicit conclusion that names the measure (exhaustion), the effect size, and the conflicting replication. | y/n/n/n |

**NEEDS VALIDATION:**
- **S1:** Whether the real Lindqvist 2022 paper at the cited URL exists and reports team-size effects. To settle it: open the live URL. If the paper exists and supports the claim, F1 becomes a retrieval error rather than a citation error. The claim stays unsupported by what the author had either way.
- **S2:** Whether the full text of ref1 qualifies the abstract (for example, limitations or self-selection of firms). To settle it: retrieve and read the full paper.

**REFUTED:**
- **C1:** "Claim [1] misstates its source." The note's sentence matches ref1's abstract almost verbatim ("Across 14 firms, employees on a four-day week reported lower exhaustion scores than matched controls"). The title, authors, venue, year and DOI all match.

## WHAT HOLDS UP
Claim [1] and its citation hold up. The source matches on every metadata field, and the abstract states the claim as written.

## UNVERIFIED CLAIMS
- Ref1's finding beyond its abstract. To confirm: read the full paper's methods and results.
- That a 2024 replication exists at all. To confirm: resolve DOI 10.5555/jws.2024.007.
- That Lindqvist 2022 "Team size and the shorter week" exists. To confirm: fetch the cited URL.

## QUESTIONS FOR THE AUTHOR
1. Did you read retrieved/ref2.md and ref3.md, or did you cite from titles or memory?
2. Is there a different source for the small-team claim, and a different replication that did succeed?

## DECISION-MAKER SUMMARY
Do not use this note to support the policy proposal yet. One of its three citations is about parking, and another is a replication that found no effect, while the note claims it confirmed the effect. If it is used as is, the proposal rests on one study with a modest effect and a misreported null result.

## OWNER SUMMARY
The note says four-day weeks reduce exhaustion, work best in small teams, and have been confirmed by a later study. Only the first point is backed by its source. The small-team source is actually about parking, and the follow-up study found no clear effect, so the note needs to be corrected before anyone relies on it.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "note.md", "status": "seen", "matters": true},
    {"item": "retrieved/ref1.md", "status": "seen", "matters": true},
    {"item": "retrieved/ref2.md", "status": "seen", "matters": true},
    {"item": "retrieved/ref3.md", "status": "seen", "matters": true},
    {"item": "live DOI/URL targets for sources 1-3", "status": "not_seen", "matters": true},
    {"item": "full texts beyond abstracts", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Published research metadata only; no personal or confidential data."},
  "coverage": {
    "checked": [
      {"unit": "note.md", "kind": "file"},
      {"unit": "retrieved/ref1.md", "kind": "file"},
      {"unit": "retrieved/ref2.md", "kind": "file"},
      {"unit": "retrieved/ref3.md", "kind": "file"},
      {"unit": "claim [1] lower exhaustion across 14 firms", "kind": "claim"},
      {"unit": "claim [2] effect largest in small teams", "kind": "claim"},
      {"unit": "claim [3] held in a 2024 replication", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "live source URLs and DOIs", "reason": "no network access"},
      {"unit": "full texts of sources", "reason": "only abstracts retrieved"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md para 1 'The effect is largest in small teams [2]'; retrieved/ref2.md Title/Abstract",
     "scenario": "The retrieved copy for [2] is 'Parking policies and commuter satisfaction in mid-sized cities' and says nothing about team size or four-day weeks; the policy proposal would cite a parking survey for a team-size effect.",
     "fix": "Remove the claim or replace it with a retrieved source that reports team-size moderation; correct the citation.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Open retrieved/ref2.md; expected title 'Team size and the shorter week', observed 'Parking policies and commuter satisfaction in mid-sized cities'."},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md para 1 'it held in a 2024 replication [3]'; retrieved/ref3.md Abstract",
     "scenario": "Source states 'the exhaustion difference was not significant (d = 0.04, 95% CI -0.19 to 0.27)'; decision-makers would believe the effect replicated when it did not.",
     "fix": "Report the replication as null with its effect size and CI, and weigh it against [1] in the note's conclusion.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Compare note.md claim 'it held' with ref3 abstract 'not significant (d = 0.04)'."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md source 3 '2024'; retrieved/ref3.md lines 1 and 4 ('2019', 'Submitted 2018, published 2019')",
     "scenario": "Citation says 2024 but the copy says 2019, which would predate the 2023 original it replicates; it cannot be determined which work was relied on, and the note's '2024' is unsupported.",
     "fix": "Resolve the DOI to the actual record, retrieve that copy, and correct the year in the note and claim.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Compare year fields in note.md source 3 and retrieved/ref3.md."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "PROBABLE", "track": "A",
     "location": "note.md title vs para 1",
     "scenario": "The note asks about burnout but its only supported evidence measures exhaustion (one burnout component) and it states no conclusion; readers may infer burnout reduction the evidence does not establish.",
     "fix": "Add an explicit conclusion naming the measure, the effect size (d = 0.31) and the conflicting null replication.",
     "answers": {"a": true, "b": false, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "C", "location": "note.md source 2",
     "suspicion": "The real Lindqvist 2022 paper may exist and differ from the retrieved copy.",
     "unresolved_fact": "What the live URL https://workreview.example.org/2022/team-size actually serves."},
    {"id": "S2", "status": "needs_validation", "track": "C", "location": "retrieved/ref1.md",
     "suspicion": "Full text may qualify the abstract's finding (e.g., firm self-selection).",
     "unresolved_fact": "Contents of the full paper's methods and limitations."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Claim [1] misstates its source.",
     "evidence": "ref1 abstract: 'Across 14 firms, employees on a four-day week reported lower exhaustion scores than matched controls (d = 0.31)'; title, authors, venue, year and DOI match the citation."}
  ]
}
```