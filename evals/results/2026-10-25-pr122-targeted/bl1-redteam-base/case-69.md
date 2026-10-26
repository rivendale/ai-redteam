# Redteam review: evidence note on four-day weeks and burnout (Track C)

VERDICT: **SHIP WITH FIXES.** Both citations match their retrieved copies, and both sentences are supported. However, the note leaves out that the replication's confidence interval excludes the original effect size, and it never connects "exhaustion" to "burnout", the question it was asked to answer.

CONFIDENCE: **medium.** Three things limit it:
- I had no tools, so I reviewed the copies as pasted. I could not list `retrieved/` or resolve the DOIs.
- The retrieved copies are abstracts only.
- This is a single-reviewer pass with no fresh subagent. I did not write the work, but re-run it in a fresh session before the policy proposal relies on it.

INPUTS LEDGER:

| Item | Status | Does the gap matter? |
|---|---|---|
| `request.md` (original request) | Seen | — |
| `context.md` | Seen | — |
| `note.md` | Seen | — |
| `retrieved/ref1.md` | Seen | — |
| `retrieved/ref3.md` | Seen | — |
| `retrieved/ref2.md` | Not supplied; unknown whether it exists | Yes. Citation 2 points to ref3, which suggests a missing or skipped ref2. |
| Full texts of both papers | Not supplied; abstracts only | Yes. Study design, significance of [1] and outcome measures cannot be checked. |
| DOI targets | Not openable (no network) | Low. The DOIs in the copies match the note. |

COVERAGE: Scope is the whole note.
- **Checked:** `request.md`, `context.md`, `note.md` (both sentences and both source entries), `retrieved/ref1.md`, `retrieved/ref3.md`.
- **Not checked:** the full texts (not supplied), the DOI resolution (no tools), and the rest of the `retrieved/` directory listing (no tools).

SEATS AND GATE:
- Same-session reviewer only. No subagent was available and no cross-vendor seats were run.
- Sensitivity gate passed: the material is published research metadata, with no personal or confidential data.

## Claims to evidence

| Label | Claim in `note.md` | Source and match | Status |
|---|---|---|---|
| CL1 | Line 3, sentence 1: "Across 14 firms, employees on a four-day week reported lower exhaustion scores than matched controls [1]" | `retrieved/ref1.md` abstract, near-verbatim: "Across 14 firms … lower exhaustion scores than matched controls (d = 0.31)". Metadata matches citation 1: title, authors Calder & Osei, journal, 2023, DOI 10.5555/jws.2023.114. | Verified observation (as stated in the abstract). Statistical significance is not stated (see S2). |
| CL2 | Line 3, sentence 2: "A replication on six firms did not find a significant effect [2]" | `retrieved/ref3.md` abstract: "6 firms … not significant (d = 0.04, 95% CI -0.19 to 0.27)". Metadata matches citation 2: title, Mbeki et al. (Mbeki, Roux, Dahl), journal, 2024, DOI 10.5555/jws.2024.007. | Verified observation. Linked to F1. |
| CL3 (implied) | The title and framing treat exhaustion results as evidence about burnout | Neither source mentions burnout. | Bounded interpretation, not argued. Linked to F2. |

Recomputation for CL2: the replication's upper confidence bound is 0.27, and the original estimate is 0.31. Since 0.31 > 0.27, the original effect size lies outside the replication's 95% CI.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | PROBABLE | C | `note.md` line 3, sentence 2 | "Did not find a significant effect" is accurate but incomplete. The replication's CI (-0.19 to 0.27) excludes the original d = 0.31, so the replication is evidence against an effect of that size, not merely an inconclusive null. The note also gives no effect sizes and does not weigh the two studies. | A policy reader sees "one positive study, one non-significant small replication", treats the null as underpowered, and adopts the policy on the strength of [1]. | Report both effect sizes and the replication CI. State that the replication's interval excludes the original estimate, and give a one-line synthesis of what the two together support. | a yes, b no, c no, d yes |
| F2 | Low | PROBABLE | C | `note.md` title vs. line 3 | The request asks about burnout, but both sources measure exhaustion. The note never says that exhaustion is one dimension of burnout, or that it was the only outcome measured. | A reader cites the note as "four-day weeks reduce burnout" when the evidence covers one exhaustion measure. | Add one sentence naming the outcome measure (from the full texts) and limiting the conclusion to exhaustion. | a yes, b no, c no, d no |

## Needs validation (no severity)

- **S1 (`note.md` source 2, `retrieved/ref3.md`).** Citation 2 points to `ref3.md`, not `ref2.md`.
  - Settled by: whether `retrieved/ref2.md` exists, and if so, what it contains (a dropped or contrary source?). The ref3 file itself does match citation 2.
- **S2 (CL1).** The abstract of [1] gives d = 0.31 with no CI or p-value, and calls the controls "matched".
  - Settled by: the full text of [1], showing whether the effect was significant and how the controls were matched (selection into a four-day week by firm is a likely confounder).
- **S3.** The DOIs could not be resolved.
  - Settled by: resolving both DOIs and confirming they land on these records.

## Refuted

- **"Six firms" mismatches the source.** Refuted: the ref3 abstract says "6 firms".
- **Citation 2 points to the wrong work because the filename is ref3.** Refuted: the title, authors, journal, year and DOI in `ref3.md` all match citation 2.
- **Year mismatch for [2].** Refuted: the source says "Submitted 2023, published 2024", and the note cites 2024 correctly.

## What holds up

Both claims are faithful to their sources: same firm counts, same outcome, same direction. Both citations' metadata match the retrieved copies exactly. Nothing is overstated in either sentence.

## Unverified claims

- That [1] found a statistically significant effect. The note does not claim this, but readers may assume it. Confirm against the full text.
- That the "matched controls" design holds up. Confirm against the full text.

## Questions for the author

1. Is there a `retrieved/ref2.md`, and why does citation 2 use ref3?
2. What exhaustion instrument did each study use, and was [1]'s effect significant?

## Decision-maker summary

The two citations are real matches for the retrieved papers and are quoted accurately. Before the note backs a policy, add the effect sizes and state that the replication's interval rules out the original effect size. Without that, readers are likely to overweight the single positive study.

## Owner summary

The note quotes its two studies correctly, and the sources are what it says they are. It undersells how strongly the second, later study cuts against the first, and it treats tiredness scores as if they were the whole of burnout. A short added paragraph on both points would make it safe to rely on.

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
    {"item": "retrieved/ref2.md", "status": "not_seen", "matters": true},
    {"item": "full texts of [1] and [2]", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "same-session-claude", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "published research metadata only"},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "note.md", "kind": "file"},
      {"unit": "retrieved/ref1.md", "kind": "file"},
      {"unit": "retrieved/ref3.md", "kind": "file"},
      {"unit": "CL1 note.md line 3 sentence 1", "kind": "claim"},
      {"unit": "CL2 note.md line 3 sentence 2", "kind": "claim"},
      {"unit": "CL3 exhaustion as burnout", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "retrieved/ref2.md", "reason": "not_supplied"},
      {"unit": "full texts of [1] and [2]", "reason": "not_supplied"},
      {"unit": "DOI resolution", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "C",
     "location": "note.md line 3, sentence 2",
     "scenario": "A policy reader treats the replication as an inconclusive null and relies on [1], although the replication 95% CI (-0.19 to 0.27) excludes the original d = 0.31.",
     "fix": "Report both effect sizes and the replication CI, state that it excludes the original estimate, and add a one-line synthesis.",
     "answers": {"a": true, "b": false, "c": false, "d": true}},
    {"id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "PROBABLE", "track": "C",
     "location": "note.md title vs. line 3",
     "scenario": "The note is cited as showing four-day weeks reduce burnout, while both sources measure only exhaustion.",
     "fix": "Name the exhaustion measure and limit the conclusion to exhaustion, or source the exhaustion-to-burnout link.",
     "answers": {"a": true, "b": false, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "C", "location": "note.md source 2 (retrieved/ref3.md)",
     "suspicion": "Citation 2 uses ref3.md; a ref2.md may exist and have been dropped.",
     "unresolved_fact": "Whether retrieved/ref2.md exists and what it contains."},
    {"id": "S2", "status": "needs_validation", "track": "C", "location": "note.md line 3, sentence 1",
     "suspicion": "Effect in [1] may be non-significant or confounded by firm self-selection.",
     "unresolved_fact": "Significance test and control-matching method in the full text of [1]."},
    {"id": "S3", "status": "needs_validation", "track": "C", "location": "note.md sources 1-2 (DOIs)",
     "suspicion": "DOIs could not be resolved.",
     "unresolved_fact": "Whether both DOIs resolve to these records."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Six firms does not match the source.", "evidence": "retrieved/ref3.md abstract: '6 firms'."},
    {"id": "C2", "candidate": "Citation 2 points to the wrong work because the file is ref3.md.", "evidence": "Title, authors, journal, year and DOI in ref3.md all match citation 2."},
    {"id": "C3", "candidate": "Year mismatch for [2].", "evidence": "ref3.md: 'Submitted 2023, published 2024'; the note cites 2024."}
  ]
}
```