**Single-reviewer, no-tools review.** No subagent was available, so there was no independent seat. Every check below reads the four supplied files directly. For anything high-stakes, re-run this review in a fresh session.

VERDICT: **REWORK**. Only the first of the note's three claims is supported. The [2] source is about parking, not team size. The [3] source reports a null result, not a replication that "held," and is dated 2019, not 2024.

CONFIDENCE: **medium**.
- Every content check is a direct quote comparison against the retrieved copies, so the findings themselves are firm.
- Confidence is limited because there was no independent reviewer and no network.
- The retrieved copies are abstracts only, so study design cannot be checked beyond the abstract.
- I cannot tell whether a mismatch comes from a bad retrieval or a bad citation.

INPUTS LEDGER:
- **Seen:** request.md, context.md, note.md, retrieved/ref1.md, retrieved/ref2.md, retrieved/ref3.md.
- **Not seen:**
  - The live pages at the three URLs/DOIs. There is no network. This matters for root cause, not for the verdict: the request requires support from the sources the author had.
  - The full texts behind the abstracts. This matters only for design details of [1], such as how controls were matched.

COVERAGE:
- **Scope:** the whole work, which is a one-page note.
- **Checked:**
  - note.md: all three claims and the source list.
  - ref1.md, ref2.md, ref3.md: title, authors, venue, year, DOI/URL and abstract, each compared against the note.
  - request.md and context.md.
- **Not checked:** the live source pages (no_tools/no network) and the full texts (not_supplied).

SEATS AND GATE: one local reviewer ran; no cross-vendor seats ran. The sensitivity gate is not triggered, because the inputs are a public-literature note with no personal or confidential data.

---

### CLAIMS TO EVIDENCE

| Claim | Location | Exact wording | Source | Status |
|---|---|---|---|---|
| **C1** | note.md ¶1 s1 | "Across 14 firms, employees on a four-day week reported lower exhaustion scores than matched controls [1]" | ref1.md abstract: "Across 14 firms, employees on a four-day week reported lower exhaustion scores than matched controls (d = 0.31)." Title, authors, venue, year and DOI all match citation 1. | **Verified.** Cohort: 14 firms. Comparison: matched controls. Effect: d = 0.31, a small-to-moderate effect that the note omits. Time window not given. |
| **C2** | note.md ¶1 s2 | "The effect is largest in small teams [2]" | ref2.md is titled "Parking policies and commuter satisfaction in mid-sized cities." Its abstract covers a survey of 800 commuters on parking. Author, venue, year and URL match citation 2, but the title and content do not. | **Unsupported.** See F1. |
| **C3a** | note.md ¶1 s2 | "it held in a 2024 replication [3]" (the effect replicated) | ref3.md: "the exhaustion difference was not significant (d = 0.04, 95% CI -0.19 to 0.27)" | **Contradicted.** See F2. |
| **C3b** | note.md ¶1 s2; source 3 | "2024" | ref3.md header: "Journal of Work Studies, 2019"; "Submitted 2018, published 2019." The DOI string contains "2024". | **Contradicted / internally inconsistent.** See F3. |
| **A1** (unstated) | note title vs C1 | That the exhaustion scores measure burnout | ref1 measures exhaustion only | **Bounded interpretation.** See F4. |

---

### FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | C | note.md ¶1 "The effect is largest in small teams [2]"; source 2; retrieved/ref2.md | The cited copy is a different work. Its title is "Parking policies and commuter satisfaction in mid-sized cities," and its abstract covers reserved versus shared parking for 800 commuters. It contains nothing on four-day weeks, exhaustion or team size. The link works but the content does not match, which fits the skill's definition of a fabricated or misattributed citation. | A policymaker targets the four-day week at small teams on the strength of [2]. The note's own source contains no such evidence. | Remove the claim, or find and retrieve a source that actually reports a team-size moderation effect. Then quote the supporting passage. Record whether the URL serves the parking paper (retrieval error) or the citation was invented. | a Y / b Y / c Y / d Y |
| F2 | Critical | CONFIRMED | C | note.md ¶1 "and it held in a 2024 replication [3]"; retrieved/ref3.md abstract | The source says the opposite of the claim. ref3: "In a replication on 6 firms the exhaustion difference was not significant (d = 0.04, 95% CI -0.19 to 0.27)." The interval includes zero, and the point estimate is about an eighth of [1]'s d = 0.31. The upper bound of 0.27 also falls short of [1]'s effect. The replication did not hold. | The proposal claims the effect is replicated when the only replication the author had found no effect. A decision-maker overrates certainty and adopts the policy on evidence that its own sources undercut. | Report [3] as a non-significant replication with its effect size and CI. State plainly that the evidence is mixed: one positive study (14 firms) and one null replication (6 firms, underpowered for small effects). | a Y / b Y / c Y / d Y |
| F3 | High | CONFIRMED | C | note.md ¶1 "a 2024 replication"; source 3 "Journal of Work Studies, 2024"; retrieved/ref3.md header | The year is wrong or inconsistent. The retrieved copy says "Journal of Work Studies, 2019" and "Submitted 2018, published 2019," yet the DOI string reads jws.2024.007 and the note says 2024. A study published in 2019 cannot replicate a 2023 study, so either the copy is not the cited work or the citation metadata is wrong. | A reader checking the citation finds a 2019 date and questions the note's reliability. Worse, the chronology the note implies (a later replication confirming an earlier study) is false. | Resolve which work is meant. Correct the year in both the text and the source list, or replace the retrieved copy. Do not describe it as a replication of [1] unless the source says so. | a Y / b Y / c N / d Y |
| F4 | Medium | CONFIRMED | C | note.md title "do 4-day weeks reduce burnout?" vs ¶1 claims on "exhaustion scores" | The note asks about burnout, but its only supported evidence measures exhaustion, which is one component of burnout. The note never states a conclusion on the question it poses, which drifts partially from the request. | A reader takes the title as answered "yes, for burnout" when the evidence covers only exhaustion in one study. | Add a bottom-line sentence that answers the request. Scope it to exhaustion and say the evidence is mixed (see F2). | a Y / b Y / c N / d N |

**Siblings and boundaries, for F1, F2 and F3.**
- **Root causes searched:** I compared all three citations against their retrieved copies for content mismatch (F1/F2) and metadata mismatch (F3).
  - ref1: every field matches and the content supports C1.
  - ref2: author, venue, year and URL match; the title and content do not.
  - ref3: title, authors, venue and DOI match; the year does not, and the content contradicts the claim.
- **Result:** no further siblings beyond the findings listed.
- **Security:** none of these are security findings, so no boundary statement applies.

**Confirm-or-refute round.**
- **F1:** The strongest defence is that a retrieval error mislabeled the right paper. That changes the root cause, not the finding: the request requires support from the content, and the author's copy has none. **Held.**
- **F2:** The strongest defence is that "held" could mean "the direction was the same." But d = 0.04 with a CI spanning zero is not a held effect under any standard reading. **Held.**
- **F3:** The strongest defence is that the DOI says 2024, so the copy's header is wrong. That is possible, but then the copy's provenance is in doubt and the note relied on it anyway. **Held** as a citation inconsistency.

### NEEDS VALIDATION
- **S1:** Does the URL for source 2 actually serve the parking paper (a mismatch at the source or in retrieval), or does a real Lindqvist team-size paper exist? *Settled by opening the live URL or searching Work Review 2022.*
- **S2:** Is ref3 really a 2019 publication? The DOI pattern suggests 2024. *Settled by resolving DOI 10.5555/jws.2024.007.*
- **S3:** Is [1]'s design (matching method, self-report, attrition) sound enough to carry a policy proposal? *Settled by the full text of ref1; only the abstract was supplied.*

### REFUTED
- **"C1 misquotes ref1."** Refuted. The note reproduces the abstract sentence verbatim, minus the effect size.

### WHAT HOLDS UP
C1 holds. The citation metadata for ref1 matches exactly, and the claim is a faithful, verbatim restatement of the abstract.

### UNVERIFIED CLAIMS
- That "matched controls" were appropriately matched. Confirm against ref1's full-text methods.
- Any claim about the live versions of the sources. Confirm by opening the DOIs/URLs.

### QUESTIONS FOR THE AUTHOR
1. Where did "largest in small teams" come from, given that ref2 is a parking study?
2. Why does the note say the effect "held" when ref3 reports d = 0.04 with a CI spanning zero?
3. Which year is correct for source 3, and is ref3 the work you intended to cite?

### DECISION-MAKER SUMMARY
- Only one of the three claims is backed by its source. The "small teams" claim cites an unrelated parking study, and the "replication" actually found no significant effect.
- Send the note back for rework, and require it to state that the evidence is mixed.
- Proceeding as written would ground a policy proposal on a misattributed citation and a reversed finding.

### OWNER SUMMARY
- One study in the note does show lower exhaustion with a four-day week.
- The other two claims are not backed up. One source is about parking, and the other found no real difference.
- The note needs to be corrected to say the evidence is mixed before anyone relies on it for a policy decision.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "note.md", "status": "seen", "matters": true},
    {"item": "retrieved/ref1.md", "status": "seen", "matters": true},
    {"item": "retrieved/ref2.md", "status": "seen", "matters": true},
    {"item": "retrieved/ref3.md", "status": "seen", "matters": true},
    {"item": "live DOI/URL pages for sources 1-3", "status": "not_seen", "matters": false},
    {"item": "full texts of sources 1-3", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-local-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Public-literature evidence note; no personal or confidential data."},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "note.md", "kind": "document"},
      {"unit": "retrieved/ref1.md", "kind": "document"},
      {"unit": "retrieved/ref2.md", "kind": "document"},
      {"unit": "retrieved/ref3.md", "kind": "document"},
      {"unit": "C1: 14 firms, lower exhaustion vs matched controls [1]", "kind": "claim"},
      {"unit": "C2: effect largest in small teams [2]", "kind": "claim"},
      {"unit": "C3a: effect held in replication [3]", "kind": "claim"},
      {"unit": "C3b: replication dated 2024 [3]", "kind": "claim"},
      {"unit": "A1: exhaustion stands in for burnout", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "live DOI/URL pages for sources 1-3", "reason": "no_tools"},
      {"unit": "full texts of sources 1-3", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md para 1 'The effect is largest in small teams [2]'; source 2; retrieved/ref2.md",
     "scenario": "Retrieved copy of [2] is 'Parking policies and commuter satisfaction in mid-sized cities' (800 commuters, parking); it says nothing about four-day weeks or team size, so a policy targeting small teams rests on no evidence.",
     "fix": "Remove the claim or retrieve and quote a source that reports a team-size moderation effect; record whether the URL serves the parking paper.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "All three citations compared field-by-field and content-by-claim against retrieved copies", "found": "Content mismatch also in [3] (F2); [1] matches"}},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md para 1 'it held in a 2024 replication [3]'; retrieved/ref3.md abstract",
     "scenario": "ref3 reports 'not significant (d = 0.04, 95% CI -0.19 to 0.27)'; the note says the effect held, so decision-makers overrate the evidence and adopt policy on a reversed finding.",
     "fix": "Report [3] as a non-significant replication with effect size and CI and state that evidence is mixed.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "All three claims checked for direction and strength against their sources", "found": "[2] unsupported (F1); [1] supported"}},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md para 1 'a 2024 replication'; source 3 year 2024; retrieved/ref3.md header '2019', 'Submitted 2018, published 2019'",
     "scenario": "The retrieved copy is dated 2019 although the note and DOI say 2024; a 2019 paper cannot replicate a 2023 study, so either the copy is not the cited work or the citation is wrong, and the implied chronology is false.",
     "fix": "Resolve the correct work and year; correct text and source list or replace the retrieved copy; do not call it a replication of [1] unless the source says so.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "security": false,
     "siblings_searched": {"searched": "Title, authors, venue, year and DOI/URL of all three sources vs retrieved copies", "found": "[2] title mismatch (covered by F1); [1] all fields match"}},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md title 'do 4-day weeks reduce burnout?' vs para 1 'exhaustion scores'",
     "scenario": "The note poses a burnout question but its only supported evidence measures exhaustion and it gives no bottom line, so readers may infer a burnout conclusion the evidence does not support.",
     "fix": "Add a bottom-line sentence scoped to exhaustion that states the evidence is mixed.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "C", "location": "note.md source 2",
     "suspicion": "The mismatch may be a retrieval error rather than a fabricated citation.",
     "unresolved_fact": "Whether https://workreview.example.org/2022/team-size serves the parking paper or a Lindqvist team-size paper."},
    {"id": "S2", "status": "needs_validation", "track": "C", "location": "retrieved/ref3.md header",
     "suspicion": "The retrieved copy's 2019 date may be wrong given the 2024 DOI.",
     "unresolved_fact": "The publication year returned when DOI 10.5555/jws.2024.007 resolves."},
    {"id": "S3", "status": "needs_validation", "track": "C", "location": "retrieved/ref1.md",
     "suspicion": "The design of [1] (matching method, self-report, attrition) may not support policy use.",
     "unresolved_fact": "Methods section of the full text of Calder & Osei 2023."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "C1 misquotes ref1.", "evidence": "note.md sentence 1 reproduces the ref1 abstract verbatim apart from omitting d = 0.31."}
  ]
}
```