# Redteam report: evidence note on four-day weeks and burnout

**Review conditions:** this was a single reviewer with no tools. I did not use a subagent, cross-vendor seats, or any network access. I compared the supplied texts by reading them. The note was not written in this conversation, so anchoring risk is lower, but it is not zero. For a policy decision, re-run this review in a fresh session.

**VERDICT: REWORK.** Of the note's three claims, one is supported. One cites a paper about parking policy. The third cites a replication that found no significant effect, which contradicts what the note says about it.

**CONFIDENCE: high** that the comparison between each claim and its retrieved copy is right, because the mismatches can be read directly from the text. Two things limit confidence:
- I only had abstracts, not full papers.
- I could not open the DOIs or URLs to check whether each retrieved copy is what those links actually return.

## Inputs ledger

**Seen:**
- request.md
- context.md
- note.md
- retrieved/ref1.md
- retrieved/ref2.md
- retrieved/ref3.md

**Not seen:**

| Item | Why not | Does the gap matter? |
|---|---|---|
| Full texts of all three references | Only abstracts were supplied | Yes, for study design and for the burnout-versus-exhaustion construct |
| Live DOI and URL targets | No network access | Partly. The author relied on the retrieved copies, but whether ref2 and ref3 are the wrong documents or wrongly cited works cannot be settled offline |

## Coverage

**Scope:** the whole note, which is three claims and three citations.

**Checked:**
- Claims 1, 2 and 3, each against its retrieved copy.
- Each citation's metadata (authors, title, venue, year, DOI or URL) against its retrieved copy.
- The note's title, against what the sources actually measure.
- request.md and context.md.

**Not checked:**
- Live link resolution (`no_tools`).
- Full-paper methods and limitations (`not_supplied`).

## Seats and sensitivity gate

- **Seats:** one local reviewer ran. No cross-vendor seats ran; none were requested and none were available.
- **Sensitivity gate:** passed. The material is public research citations with no personal or confidential data.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | C | note.md claim 2 ("largest in small teams [2]"); retrieved/ref2.md Title/Abstract | Ref [2] is a different work. The note cites it as "Team size and the shorter week". The retrieved copy at the same URL is titled "Parking policies and commuter satisfaction in mid-sized cities", and its abstract covers reserved versus shared parking for 800 commuters. It says nothing about four-day weeks, team size or exhaustion. | A policy reader relies on "largest in small teams" to target a pilot at small teams. Nothing supports that targeting. | Remove the claim, or find and retrieve a source that actually reports a team-size moderation effect and quote it. | a✓ b✓ c✓ d✓ |
| F2 | Critical | CONFIRMED | C | note.md claim 3 ("it held in a 2024 replication [3]"); retrieved/ref3.md Abstract | The cited source contradicts the claim. Ref3 reports that "the exhaustion difference was not significant (d = 0.04, 95% CI -0.19 to 0.27)". The confidence interval includes zero, and the point estimate is about an eighth of the original d = 0.31. The effect did not "hold". | The proposal presents the finding as replicated, when the only replication supplied failed to replicate it. Decision-makers would overrate the evidence. | Report the failed replication accurately, for example: "a 6-firm replication found no significant difference (d = 0.04, 95% CI -0.19 to 0.27)". Then restate the overall conclusion as uncertain. | a✓ b✓ c✓ d✓ |
| F3 | High | CONFIRMED | C | note.md claim 3 and source list item 3 ("2024"); retrieved/ref3.md line 1 ("Journal of Work Studies, 2019") and Abstract ("Submitted 2018, published 2019") | The citation's year is wrong. The note says 2024 twice. The retrieved copy says it was published in 2019, which is before the 2023 study it supposedly replicates. Its DOI suffix, `jws.2024.007`, also conflicts with its own 2019 date. | A reader treats the replication as recent and as a follow-up to Calder & Osei 2023. On the copy supplied, neither is true, so either the citation or the retrieved document is wrong. | Correct the year to match the source, or retrieve the correct 2024 work. State which study ref3 actually replicates. | a✓ b✓ c✗ d✓ |
| F4 | Medium | PROBABLE | C | note.md title ("reduce burnout") versus ref1 ("exhaustion scores") | The construct is narrowed without saying so. The sources measure exhaustion, which is one dimension of burnout. The title and question treat that as burnout. | The proposal claims a burnout reduction, but the evidence covers at most a single dimension of it, measured by self-report. | Phrase the conclusion in terms of "exhaustion", or cite evidence on the other burnout dimensions. | a✓ b✗ c✗ d✓ |

**Severity check on the Critical and High findings (confirm or refute):**
- **F1 survives:** the title and abstract topic are unrelated to the claim. The only overlaps are the author surname, the venue and the URL.
- **F2 survives:** a non-significant d = 0.04 with a confidence interval spanning zero cannot be read as "held".
- **F3 survives:** "published 2019" is stated in the source in plain words.

**Sibling search (the same root cause, a source not supporting its claim, checked across every citation):**
- [1] holds.
- [2] is F1.
- [3] is F2.

**Sibling search (citation metadata, checked across every citation):**
- [1] matches on authors, title, venue, year and DOI.
- [2] has a title mismatch, which is part of F1.
- [3] has a year mismatch, which is F3.

None of the findings are security findings.

## Needs validation

- **S1, ref2:** I cannot tell whether the cited URL resolves to the parking paper, or whether the wrong file was saved. Settled by opening the URL, or by finding whether a Lindqvist 2022 paper titled "Team size and the shorter week" exists.
- **S2, ref3:** I cannot tell whether DOI 10.5555/jws.2024.007 resolves to this 2019 document or to a different 2024 paper. Settled by resolving the DOI.
- **S3, ref1:** I cannot tell whether "matched controls" means a design that supports a causal reading, or how exhaustion was measured. Settled by reading the methods section of the full paper.

## Refuted

None.

## What holds up

Claim 1 is supported almost word for word by ref1's abstract: "Across 14 firms, employees on a four-day week reported lower exhaustion scores than matched controls". Every metadata field in citation [1] matches the retrieved copy.

## Unverified claims

- Whether the DOI and URL in each citation point to the retrieved copies. Confirm by resolving them with network access.
- The study design behind ref1's effect. Confirm from the full text.

## Questions for the author

1. Does a Lindqvist 2022 paper on team size and the four-day week exist? If so, where is it?
2. Is there a 2024 replication separate from the 2019 document that was retrieved?
3. Given ref3's null result, what conclusion does the note now support?

## Decision-maker summary

Only one study, with a modest effect (d = 0.31), supports the note's core claim. The "small teams" claim cites an unrelated paper, and the cited replication found no significant effect. Do not use this note to support the policy proposal until it is rewritten. As it stands, it overstates evidence that is actually mixed.

## Owner summary

The note says the research shows four-day weeks reduce burnout, but only one of its three sources says what the note claims. One source is about parking and has nothing to do with work schedules. Another found no real effect, while the note says it confirmed the result. The note needs to be rewritten to reflect that the evidence is mixed before anyone relies on it.

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
    {"item": "full texts of refs 1-3", "status": "not_seen", "matters": true},
    {"item": "live DOI/URL targets", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "public research citations only"},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "note.md", "kind": "document"},
      {"unit": "retrieved/ref1.md", "kind": "document"},
      {"unit": "retrieved/ref2.md", "kind": "document"},
      {"unit": "retrieved/ref3.md", "kind": "document"},
      {"unit": "note.md claim 1", "kind": "claim"},
      {"unit": "note.md claim 2", "kind": "claim"},
      {"unit": "note.md claim 3", "kind": "claim"},
      {"unit": "note.md title: exhaustion equals burnout", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "live DOI/URL resolution", "reason": "no_tools"},
      {"unit": "full texts of refs 1-3", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md claim 2 [2]; retrieved/ref2.md Title and Abstract",
     "scenario": "The note cites 'Team size and the shorter week' for 'largest in small teams', but the retrieved copy is 'Parking policies and commuter satisfaction in mid-sized cities' and says nothing about four-day weeks or team size; a policy targeting small teams would rest on no evidence.",
     "fix": "Remove the claim or retrieve and quote a source that reports team-size moderation.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "every citation [1]-[3] against its retrieved copy for content support", "found": "[3] contradicts its claim (F2); [1] supports its claim"}},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md claim 3 [3]; retrieved/ref3.md Abstract",
     "scenario": "The note says the effect 'held' in the replication, but ref3 reports a non-significant difference (d = 0.04, 95% CI -0.19 to 0.27); readers of the policy proposal would believe the finding was replicated when it was not.",
     "fix": "State the null replication result accurately and downgrade the note's overall conclusion to uncertain.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "every citation [1]-[3] against its retrieved copy for content support", "found": "[2] is an unrelated work (F1); [1] supports its claim"}},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md claim 3 and source 3 ('2024'); retrieved/ref3.md line 1 and Abstract ('published 2019')",
     "scenario": "The note dates the replication 2024, but the retrieved copy was published in 2019, before the 2023 study it supposedly replicates; readers are misled about recency and sequence, or the wrong document was retrieved.",
     "fix": "Correct the year to the source's, or retrieve the actual 2024 work, and state which study ref3 replicates.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "security": false,
     "siblings_searched": {"searched": "authors, title, venue, year and DOI/URL of citations [1]-[3] against retrieved copies", "found": "[2] title mismatch (part of F1); [1] all fields match"}},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "C",
     "location": "note.md title ('reduce burnout') vs retrieved/ref1.md ('exhaustion scores')",
     "scenario": "The proposal asserts a burnout reduction while the evidence measures only exhaustion, one dimension of burnout, by self-report.",
     "fix": "Phrase the conclusion in terms of exhaustion, or add evidence on the other burnout dimensions.",
     "answers": {"a": true, "b": false, "c": false, "d": true}},
    {"id": "S1", "status": "needs_validation", "track": "C", "location": "note.md source 2 URL",
     "suspicion": "The wrong file may have been saved, or the cited title may not exist.",
     "unresolved_fact": "What workreview.example.org/2022/team-size resolves to, and whether a Lindqvist 2022 team-size paper exists."},
    {"id": "S2", "status": "needs_validation", "track": "C", "location": "note.md source 3 DOI",
     "suspicion": "The DOI suffix says 2024 while the retrieved document says 2019.",
     "unresolved_fact": "What DOI 10.5555/jws.2024.007 resolves to."},
    {"id": "S3", "status": "needs_validation", "track": "C", "location": "retrieved/ref1.md Abstract",
     "suspicion": "The matched-control design may not support a causal reading.",
     "unresolved_fact": "The methods section of the full Calder & Osei 2023 paper."}
  ],
  "refuted": []
}
```