# Redteam review: evidence note on four-day weeks and burnout

**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No tools or subagents were available in this session. I did not run, fetch or resolve anything. Every check below compares the supplied text by eye.

**VERDICT: SHIP WITH FIXES.** Both citations match their retrieved copies, and both claims are faithful to the abstracts. The note drops the effect sizes and confidence interval a policy reader needs, and its title leaps from "exhaustion" to "burnout" without saying so.

**CONFIDENCE: medium.** It is limited by:
- the same-context review;
- no tools;
- only abstracts being retrieved, so methods such as "matched controls" cannot be checked against full text;
- DOIs that cannot be resolved offline.

## Inputs ledger

| Item | Status | Matters? |
|---|---|---|
| request.md | seen | yes |
| context.md | seen | yes |
| note.md | seen | yes |
| retrieved/ref1.md | seen | yes |
| retrieved/ref3.md | seen | yes |
| retrieved/ref2.md | not supplied (only implied by the numbering gap) | no, because the note points source 2 at ref3.md explicitly |
| Full texts of both papers | not supplied | yes, for any claim beyond the abstracts |
| DOI landing pages | not openable (no network) | low |

## Coverage

- **Scope:** the whole note (Track C, as requested).
- **Checked:**
  - note.md: body sentences 1–2 and the source list entries 1–2
  - ref1.md and ref3.md: title, authors, journal, year, DOI and abstract, each compared with the citation and the claim
  - the request's requirement that "every claim needs a source whose content supports it"
- **Not checked:**
  - full texts (not supplied)
  - DOI resolution (no tools)
  - retrieved/ref2.md (not supplied)

## Seats and gate

- **Sensitivity gate:** passed. The material is published research metadata with no personal or confidential data.
- **Seats:** a same-context self-review only. No subagent or cross-vendor seats were available.

## Claims to evidence

**C1** (note.md, body sentence 1): "Across 14 firms, employees on a four-day week reported lower exhaustion scores than matched controls [1]."
- Source: ref1.md abstract, verbatim "Across 14 firms, employees on a four-day week reported lower exhaustion scores than matched controls (d = 0.31)".
- Cohort: 14 firms. Comparison: matched controls. Effect size: d = 0.31. Time window: not stated.
- Status: verified observation against the abstract. The note omits the effect size (see F1).

**C2** (note.md, body sentence 2): "A replication on six firms did not find a significant effect [2]."
- Source: ref3.md abstract: "In a replication on 6 firms the exhaustion difference was not significant (d = 0.04, 95% CI -0.19 to 0.27)."
- Status: verified observation. The outcome is exhaustion, consistent with C1.

**C3** (source list entry 1): Calder & Osei, 2023, Journal of Work Studies, DOI 10.5555/jws.2023.114.
- Matches ref1.md on title, authors (P. Calder, K. Osei), journal, year and DOI.
- Status: verified.

**C4** (source list entry 2): Mbeki et al., 2024, "Replicating the four-day week", Journal of Work Studies, DOI 10.5555/jws.2024.007.
- Matches ref3.md on title, authors (A. Mbeki, T. Roux, L. Dahl), journal and DOI.
- The year 2024 matches "published 2024" (it was submitted in 2023, so 2024 is the correct citation year).
- Status: verified. The file is named ref3 while the source is numbered 2 (see F3).

**C5** (title): "do 4-day weeks reduce burnout?"
- Both sources measure exhaustion, not burnout.
- Status: bounded interpretation, not stated in the note (see F2).

**A1** (assumption): the abstracts represent the papers' findings.
- Status: unverified, because full texts were not supplied (see S1).

## Findings, ordered by severity

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED | C | note.md body, sentences 1–2 | The note omits both effect sizes and the replication's confidence interval. The two results are presented as a bare split ("lower" vs "not significant"). The supplied numbers say more: the original effect is small (d = 0.31), and the replication's 95% CI (−0.19 to 0.27) has an upper bound below 0.31. So the replication's interval excludes the original effect size, not merely "fails significance". | A policy reader sees "one study yes, one study no". They may treat the evidence as balanced, or treat the smaller replication as merely underpowered. In fact its interval argues against an effect as large as the original. | Add d = 0.31 for [1] and d = 0.04 (95% CI −0.19 to 0.27) for [2]. State that the replication's interval excludes the original estimate. Check: compare the note sentences with ref1.md and ref3.md abstracts; the numbers are present in the sources and absent from the note. | a: yes, b: yes, c: no, d: yes |
| F2 | Medium | CONFIRMED | C | note.md title vs body; ref1.md, ref3.md abstracts | The title asks about **burnout**, but both sources measure **exhaustion** only. Exhaustion is one component of burnout, not the whole construct. The note never states this substitution. | The policy proposal cites the note as evidence about burnout. A reviewer points out that neither source measured burnout, which undermines the proposal's evidentiary basis. | Either retitle to exhaustion, or add a sentence saying both studies measured exhaustion, a component of burnout, and that no supplied source measures burnout overall. Check: search both abstracts for "burnout"; there are no occurrences, while "exhaustion" appears in each. | a: yes, b: yes, c: no, d: yes |
| F3 | Low | CONFIRMED | C | note.md source list entry 2: "(retrieved/ref3.md)" | Source 2 maps to file ref3.md. This numbering gap implies a ref2.md that is uncited or was dropped. | A later checker opens retrieved/ref2.md expecting source 2 and verifies the wrong document. Alternatively, a dropped source (possibly contrary evidence) goes unnoticed. | Rename the file to match, or note why ref2.md is absent. Check: the source list numbering (1, 2) does not match the file names (ref1, ref3). | a: yes, b: yes, c: no, d: no |

## Needs validation

- **S1:** Whether the full texts support "matched controls", report exhaustion on the same instrument in both studies, and contain no caveats that the abstracts omit. *Unresolved fact:* the full-text methods and results sections, which were not supplied.
- **S2:** Whether a retrieved/ref2.md exists and holds a relevant source that the note omits. *Unresolved fact:* the contents of the retrieved/ directory.
- **S3:** Whether the DOIs resolve to these works. *Unresolved fact:* resolution of both DOIs (no network; the `doi.example.org` host cannot be checked here).

## Refuted

- **R1** (candidate): Source 2 is mis-cited because it points at ref3.md.
  - *Evidence:* ref3.md's title, authors, journal and DOI all match citation 2. Only the file name is off (kept as F3, Low).
- **R2** (candidate): Citation 2's year is wrong, since ref3.md says "Submitted 2023".
  - *Evidence:* the same file says "published 2024", so 2024 is the correct citation year.
- **R3** (candidate): Sentence 2 overstates the result as "no effect".
  - *Evidence:* the note says "did not find a significant effect", which accurately paraphrases "was not significant".

## What holds up

- Both citations are the cited works, with matching title, authors, journal, year and DOI.
- Both body claims are faithful to their abstracts, including the firm counts (14 and 6).
- The note avoids overclaiming in either direction.
- No claim lacks a source.

## Unverified claims

- "Matched controls" and the study designs generally. *To confirm:* read the methods sections of the full texts.
- DOI validity. *To confirm:* resolve both DOIs.

## Questions for the author

1. Is there a retrieved/ref2.md, and why was it not cited?
2. Do the full texts use the same exhaustion measure, and does either measure burnout as a whole?

## Decision-maker summary

The two citations are genuine and accurately summarized, so the note is usable once fixed. Before it supports a policy proposal:
- Add the effect sizes, which show the replication's interval excludes the original effect.
- Retitle or caveat the note, because both studies measured exhaustion, not burnout.

If used as is, the note overstates how mixed and how burnout-relevant the evidence is.

## Owner summary

The two studies cited are real and are described correctly. The note leaves out numbers showing that the second, more recent study points against the effect found by the first. It also talks about "burnout" when both studies only measured tiredness and exhaustion. Fixing those two things would make it safe to rely on.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "note.md", "status": "seen", "matters": true},
    {"item": "retrieved/ref1.md", "status": "seen", "matters": true},
    {"item": "retrieved/ref3.md", "status": "seen", "matters": true},
    {"item": "retrieved/ref2.md", "status": "not_seen", "matters": false},
    {"item": "full texts of both papers", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "same-context-self-review", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "published research metadata only"},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "note.md", "kind": "document"},
      {"unit": "retrieved/ref1.md", "kind": "document"},
      {"unit": "retrieved/ref3.md", "kind": "document"},
      {"unit": "C1 note.md sentence 1", "kind": "claim"},
      {"unit": "C2 note.md sentence 2", "kind": "claim"},
      {"unit": "C3 source entry 1", "kind": "claim"},
      {"unit": "C4 source entry 2", "kind": "claim"},
      {"unit": "C5 title burnout framing", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "retrieved/ref2.md", "reason": "not_supplied"},
      {"unit": "full texts of both papers", "reason": "not_supplied"},
      {"unit": "DOI resolution", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md body sentences 1-2",
     "scenario": "Note omits d = 0.31 and the replication's d = 0.04 (95% CI -0.19 to 0.27), whose upper bound excludes the original effect; a policy reader sees a balanced split and may dismiss the replication as underpowered.",
     "fix": "Report both effect sizes and the replication CI, and state that the CI excludes the original estimate.",
     "answers": {"a": true, "b": true, "c": false, "d": true}},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md title vs ref1.md and ref3.md abstracts",
     "scenario": "Title asks about burnout; both sources measure exhaustion only; a proposal citing the note as burnout evidence is open to challenge.",
     "fix": "Retitle to exhaustion or add an explicit caveat that both studies measured exhaustion, a component of burnout.",
     "answers": {"a": true, "b": true, "c": false, "d": true}},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md source list entry 2 '(retrieved/ref3.md)'",
     "scenario": "Source 2 maps to file ref3.md; a later checker may open ref2.md and verify the wrong document, or a dropped source goes unnoticed.",
     "fix": "Align file names with source numbers or document why ref2.md is absent.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "C", "location": "note.md sentence 1 'matched controls'",
     "suspicion": "Abstracts may omit methodological caveats or differing exhaustion instruments.",
     "unresolved_fact": "Full-text methods and results of both papers."},
    {"id": "S2", "status": "needs_validation", "track": "C", "location": "retrieved/",
     "suspicion": "A ref2.md may hold an omitted relevant source.",
     "unresolved_fact": "Contents of the retrieved/ directory."},
    {"id": "S3", "status": "needs_validation", "track": "C", "location": "note.md source list DOIs",
     "suspicion": "DOIs not confirmed to resolve to the cited works.",
     "unresolved_fact": "Resolution of both DOIs."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Source 2 is mis-cited because it points at ref3.md.",
     "evidence": "ref3.md title, authors, journal and DOI all match citation 2."},
    {"id": "R2", "candidate": "Citation 2 year is wrong (submitted 2023).",
     "evidence": "ref3.md states 'published 2024'."},
    {"id": "R3", "candidate": "Sentence 2 overstates as 'no effect'.",
     "evidence": "Note says 'did not find a significant effect', matching 'was not significant'."}
  ]
}
```