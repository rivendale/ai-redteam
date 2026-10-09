# Redteam review: evidence note on four-day weeks and burnout

**VERDICT: REWORK.** Two of the note's three claims fail against their own retrieved sources. Source [2] is a different paper (about parking). Source [3] reports that the effect did *not* replicate, while the note says it "held".

**CONFIDENCE: high** for the source-content findings, because each one rests on a direct quote from the supplied copies. Three things limit it:
- This is a single reviewer with no subagent or fresh session. I did not author the note, but there was no independent second read.
- There are no tools or network access, so I could not check whether other versions of the cited works exist.
- Only abstracts were supplied, not full texts.

**INPUTS LEDGER**

| Item | Status | Matters? |
|---|---|---|
| request.md (original request) | seen | yes |
| context.md | seen | yes |
| note.md | seen | yes |
| retrieved/ref1.md, ref2.md, ref3.md | seen (abstracts only) | yes |
| Full texts of refs 1–3 | not supplied | yes for study design ("matched controls", firm counts, outcome measure); no for F1/F2, which the abstracts settle |
| Live DOIs and URLs | not openable (no network) | partly; this is why S1 and S2 stay open |

**COVERAGE**
- **Checked:**
  - note.md: the three claims in ¶1 and the three citation entries
  - Each retrieved copy: identity (title, authors, venue, year, DOI or URL) and whether its content supports the claim
- **Not checked:**
  - Full-text methods
  - Whether any other literature exists (out of scope for a claims review)
  - Live resolution of identifiers

**SEATS AND GATE**
- Sensitivity gate: passed. This is published research with no personal or confidential data.
- Reviewers: one local reviewer only. No subagent was available, and no cross-vendor seats were requested.

---

## Pass 1: Reconstruct

The note claims three things:
1. A 14-firm study found lower exhaustion on a four-day week versus matched controls [1].
2. The effect is largest in small teams [2].
3. The effect held in a 2024 replication [3].

Taken together, the note implies that four-day weeks reduce burnout and that this is robust. That is what makes it useful to a policy proposal.

For the note to be correct, all of the following must hold:
- Each retrieved copy is the cited work.
- Each copy says what is claimed.
- "Exhaustion" stands in for "burnout".
- A replication actually confirmed the original result.

Track: C.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | C | note.md ¶1 "The effect is largest in small teams [2]"; retrieved/ref2.md | The retrieved copy is not the cited work. The note cites *"Team size and the shorter week"*. The copy at the same URL is titled *"Parking policies and commuter satisfaction in mid-sized cities"* and covers "reserved and shared parking". Nothing in it concerns four-day weeks, team size or exhaustion. | The policy proposal argues for targeting small teams first, citing [2]. Anyone who checks the source finds a parking survey, and the note's credibility collapses. | Remove the claim, or find and retrieve the actual team-size work and quote the passage that supports it. **Reproduce:** compare the title in note.md source 2 with the `Title:` line in retrieved/ref2.md. | a✔ b✔ c✔ d✔ |
| F2 | Critical | CONFIRMED | C | note.md ¶1 "it held in a 2024 replication [3]"; retrieved/ref3.md | The source says the opposite: "the exhaustion difference was not significant (d = 0.04, 95% CI -0.19 to 0.27)". The interval spans zero, and the point estimate is about one eighth of the original d = 0.31. | Decision-makers read the result as replicated and robust. The only replication supplied actually failed, so the proposal overstates the evidence. | Rewrite: "a replication in 6 firms found no significant difference (d = 0.04, 95% CI −0.19 to 0.27)". Then revisit the note's overall conclusion. **Reproduce:** read the abstract of retrieved/ref3.md. | a✔ b✔ c✔ d✔ |
| F3 | Medium | CONFIRMED | C | note.md source 3 ("Journal of Work Studies, 2024"); retrieved/ref3.md lines 1 and 5 | The citation's metadata does not match the copy. The note says 2024. The copy's header says 2019 and "Submitted 2018, published 2019", yet its DOI contains "2024.007". A replication published in 2019 would also predate the 2023 original it replicates. | It is unclear which work is being cited. A reader cannot verify it, and the "2024" in the note's text may be invented. | Resolve the DOI and correct the year, or retrieve the correct version. If it is a 2019 study, it is not a replication of [1], so re-describe it. **Reproduce:** compare note.md source 3 with the header and last line of retrieved/ref3.md. | a✔ b✔ c✘ d✘ |
| F4 | Medium | CONFIRMED | C | note.md title "do 4-day weeks reduce burnout?" vs ref1 "exhaustion scores" | The only supporting source measures exhaustion. The note frames its answer as being about burnout. Exhaustion is one dimension of burnout, not the whole construct. | The proposal says "reduces burnout" on the strength of a single exhaustion measure, which overstates what was measured. | State the outcome as "exhaustion" or justify the proxy. Report the effect size (d = 0.31), and note that the evidence base is one study whose replication failed. | a✔ b✔ c✘ d✔ |

## Needs validation (no severity)
- **S1:** Does a Lindqvist 2022 paper titled "Team size and the shorter week" exist, and does it support the small-teams claim? To settle it, resolve workreview.example.org/2022/team-size and find out whether the URL or the retrieved copy is wrong.
- **S2:** Is there a 2024 replication separate from the 2019 copy? To settle it, check what DOI 10.5555/jws.2024.007 resolves to.
- **S3:** Were ref1's "matched controls" actually matched, and on what variables? To settle it, read ref1's full-text methods.

## Refuted
- **"Ref1 may be a misattributed copy."** Refuted. The authors (Calder, Osei), title, journal, year (2023) and DOI (10.5555/jws.2023.114) all match, and the claim matches the abstract verbatim.

## What holds up
- **Claim [1] and its citation.** It is the right work and says what the note claims, word for word ("Across 14 firms … lower exhaustion scores than matched controls").

## Unverified claims
- **"Matched controls" design quality in [1].** This appears only in the abstract. Confirm it from the full-text methods.
- **Existence and content of the real sources behind [2] and [3].** Confirm by resolving the URL and DOI.

## Questions for the author
1. Where did "largest in small teams" come from, given that the retrieved [2] is a parking study?
2. Did you read ref3's result? If so, why does the note say the effect "held"?
3. Is source 3 from 2019 or 2024, and which document does the DOI resolve to?

## Decision-maker summary
Only one of the note's three claims is supported. The "small teams" source is an unrelated parking paper, and the cited replication found no effect. Do not attach this note to the policy proposal until it is rewritten. As it stands, it presents a single unreplicated exhaustion finding as robust evidence on burnout.

## Owner summary
One of the studies cited is real and says what the note claims. Another cited paper is actually about parking. The third found that the benefit did not show up when the study was repeated. The note needs to be rewritten to say honestly that the evidence is thin and mixed before anyone uses it to argue for a policy.

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
    {"item": "full texts of refs 1-3", "status": "not_seen", "matters": true},
    {"item": "live DOI/URL resolution", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "note.md", "kind": "file"},
      {"unit": "note.md: claim [1] 14 firms lower exhaustion", "kind": "claim"},
      {"unit": "note.md: claim [2] largest in small teams", "kind": "claim"},
      {"unit": "note.md: claim [3] held in 2024 replication", "kind": "claim"},
      {"unit": "retrieved/ref1.md", "kind": "file"},
      {"unit": "retrieved/ref2.md", "kind": "file"},
      {"unit": "retrieved/ref3.md", "kind": "file"},
      {"unit": "exhaustion as proxy for burnout", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "full texts of refs 1-3", "reason": "not supplied"},
      {"unit": "live DOI/URL resolution", "reason": "no network or tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md para 1 'largest in small teams [2]'; retrieved/ref2.md Title line",
     "scenario": "The proposal targets small teams citing [2]; the retrieved copy is 'Parking policies and commuter satisfaction in mid-sized cities' and says nothing about four-day weeks or team size.",
     "fix": "Remove the claim or retrieve the actual cited work and quote the supporting passage.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Compare note.md source 2 title with the Title line of retrieved/ref2.md; expect a match, observe a parking-policy paper."},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md para 1 'it held in a 2024 replication [3]'; retrieved/ref3.md Abstract",
     "scenario": "Readers take the effect as replicated; the source reports 'not significant (d = 0.04, 95% CI -0.19 to 0.27)', i.e. the replication failed.",
     "fix": "State that the replication found no significant difference with its effect size and CI, and revise the note's overall conclusion.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Read the retrieved/ref3.md abstract; expect support for 'held', observe a non-significant result."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md source 3 '2024'; retrieved/ref3.md header '2019' and 'Submitted 2018, published 2019'",
     "scenario": "Citation year (2024) contradicts the copy (2019, DOI containing 2024); a 2019 study cannot replicate a 2023 original, so the cited work cannot be verified.",
     "fix": "Resolve the DOI, correct the year, and re-describe the study if it is not a replication of [1].",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Compare note.md source 3 with the first and last lines of retrieved/ref3.md."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md title vs retrieved/ref1.md 'exhaustion scores'",
     "scenario": "The proposal claims reduced burnout based on one study measuring only exhaustion, overstating what was measured.",
     "fix": "Report the outcome as exhaustion (d = 0.31), or justify the proxy, and state the evidence base is one study with a failed replication.",
     "answers": {"a": true, "b": true, "c": false, "d": true}},
    {"id": "S1", "status": "needs_validation", "track": "C", "location": "note.md source 2",
     "suspicion": "The real Lindqvist team-size paper may exist and the wrong copy was retrieved.",
     "unresolved_fact": "What workreview.example.org/2022/team-size resolves to."},
    {"id": "S2", "status": "needs_validation", "track": "C", "location": "note.md source 3",
     "suspicion": "A distinct 2024 replication may exist.",
     "unresolved_fact": "What DOI 10.5555/jws.2024.007 resolves to."},
    {"id": "S3", "status": "needs_validation", "track": "C", "location": "retrieved/ref1.md Abstract",
     "suspicion": "The matched-controls design may be weaker than the abstract implies.",
     "unresolved_fact": "Matching variables and method in ref1's full-text methods."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "ref1 may be a misattributed copy.",
     "evidence": "Authors, title, journal, year 2023 and DOI 10.5555/jws.2023.114 all match the citation, and the claim is verbatim from the abstract."}
  ]
}
```