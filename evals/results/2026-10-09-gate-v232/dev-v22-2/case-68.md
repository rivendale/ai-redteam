**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** I had no tools and no subagent. All three retrieved copies were supplied inline, so the source-versus-claim checks below rest on exact quotes. Nothing outside those copies could be opened.

VERDICT: **REWORK**. Two of the note's three claims are not supported by their retrieved sources. One source is a different paper, and one directly contradicts the claim it is cited for. A policy proposal built on this note would rest on one small-effect study.

CONFIDENCE: **high** for the source-versus-claim mismatches, because they are tied to verbatim text in the supplied copies. **Medium** overall, for three reasons: this was a same-context single reviewer, the copies are abstracts only, and I could not open the DOIs or URLs to see whether better versions of refs 2 and 3 exist.

INPUTS LEDGER:
- Seen: `request.md` (original request), `context.md`, `note.md`, `retrieved/ref1.md`, `retrieved/ref2.md`, `retrieved/ref3.md`.
- Not openable: the three DOIs and URLs (no network). This matters only for deciding whether the wrong copies were *retrieved* or the wrong works were *cited*. Either way the note as delivered fails the request: "every claim needs a source whose content supports it".
- Not seen: full texts beyond the abstracts. This matters for checking design details such as "matched controls", but the abstract states them.

COVERAGE:
- Checked: claim 1 ("Across 14 firms… lower exhaustion… matched controls") against ref1; claim 2 ("largest in small teams") against ref2; claim 3 ("held in a 2024 replication") against ref3; bibliographic metadata (title, author, venue, year, identifier) for each of the three references; the note's framing against the request's question ("burnout").
- Not checked: the live DOI and URL records; full-text methods; literature the note does not cite.

SEATS AND GATE: one same-context reviewer (self). No cross-vendor seats, because none were requested and no tools were available. Sensitivity gate: no personal, client, financial, health or credential data found, so the work is not sensitive. No reviewer-directed instructions were found in the work.

FINDINGS, ordered by severity:

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | C | note.md ¶1 "[3]"; Sources item 3; retrieved/ref3.md abstract | Claim 3 says the effect "held in a 2024 replication". The cited copy says the opposite: "the exhaustion difference was not significant (d = 0.04, 95% CI -0.19 to 0.27)". The copy is also dated 2019 ("Submitted 2018, published 2019"), not 2024. | A policy reader is told the finding replicated. The only replication in the evidence set found an effect near zero, with a CI that includes zero and excludes ref1's d = 0.31 (0.31 > 0.27). The proposal overstates the evidence. | Rewrite claim 3 to report the null replication, or remove it. Reproduce by comparing the note's "it held" with the ref3 abstract quote above. | a✓ b✓ c✓ d✓ |
| F2 | Critical | CONFIRMED | C | note.md ¶1 "[2]"; Sources item 2; retrieved/ref2.md | The copy behind [2] is a different work. Its title is "Parking policies and commuter satisfaction in mid-sized cities", about "reserved and shared parking". It says nothing about four-day weeks, team size or exhaustion. The URL and author match the citation, but the title does not ("Team size and the shorter week"). | The "largest in small teams" claim has no supporting source. A policy that targets small teams on the strength of [2] would rest on nothing. | Find and retrieve the actual "Team size and the shorter week" text and confirm it says this, or delete claim 2. Reproduce by comparing the citation title with the ref2 title and abstract. | a✓ b✓ c✓ d✓ |
| F3 | Medium | CONFIRMED | C | Sources item 3 vs retrieved/ref3.md header | Ref3's metadata is internally inconsistent. The DOI string is `jws.2024.007` and the citation year is 2024, but the copy says 2019. A 2019 paper also cannot replicate a 2023 study (ref1). | Either the retrieved copy is the wrong record, or the citation is wrong. A reader cannot tell which work the note relies on. | Resolve the DOI against the publisher record and cite the year and version actually read. | a✓ b✓ c✗ d✗ |
| F4 | Medium | CONFIRMED | C/A | note.md title vs ¶1; ref1 abstract | The note asks about "burnout", but its only supported evidence measures "exhaustion scores", which is one dimension of burnout. The note also omits ref1's effect size (d = 0.31), which is small. | A policy reader takes "reduces burnout" as established from a single small effect on one burnout dimension. | Say "exhaustion" rather than burnout, report d = 0.31, and state that the only replication was null. | a✓ b✓ c✗ d✓ |

NEEDS VALIDATION:
- S1: Whether a genuine Lindqvist 2022 paper on team size exists at the cited URL. The retrieved copy at that URL is the parking paper. Settled by: the live page or publisher record.
- S2: Whether a 2024 Mbeki et al. paper exists that differs from the retrieved 2019 copy and reports a different result. Settled by: resolving DOI 10.5555/jws.2024.007.

REFUTED:
- Candidate: claim 1 misstates ref1. Refuted: ref1's abstract reads "Across 14 firms, employees on a four-day week reported lower exhaustion scores than matched controls (d = 0.31)", which matches the note almost verbatim. Title, authors, venue, year and DOI all match the citation.

WHAT HOLDS UP: Claim 1 and its citation (ref1) are accurate, and the note correctly points each claim at a retrieved copy.

UNVERIFIED CLAIMS: ref1's "matched controls" design and its 14-firm sample are stated only in the abstract, so read the full text's methods to confirm them. The live DOI and URL records for all three references could not be checked.

QUESTIONS FOR THE AUTHOR:
1. Did you read a Lindqvist paper on team size? If so, where is it?
2. Which Mbeki et al. record did you rely on, the 2019 copy or a 2024 version, and what result did it report?

DECISION-MAKER SUMMARY: Do not use this note in the policy proposal as written. The "small teams" claim cites an unrelated parking study, and the "replication held" claim cites a study that found no significant effect. The supportable statement is that one 14-firm study found a small reduction in exhaustion and one smaller replication did not.

OWNER SUMMARY: The note says the evidence for four-day weeks reducing burnout is stronger than its own sources show. One source is about parking, not working hours, and the follow-up study it cites actually found no clear benefit. The note needs to be rewritten to reflect that only one study shows a small improvement before it supports any policy.

I could not run `tools/validate_findings.py` in this session, so the block below has not been validated.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "note.md", "status": "seen", "matters": true},
    {"item": "retrieved/ref1.md", "status": "seen", "matters": true},
    {"item": "retrieved/ref2.md", "status": "seen", "matters": true},
    {"item": "retrieved/ref3.md", "status": "seen", "matters": true},
    {"item": "live DOI/URL records for refs 1-3", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "same-context-self", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "note.md", "kind": "file"},
      {"unit": "retrieved/ref1.md", "kind": "file"},
      {"unit": "retrieved/ref2.md", "kind": "file"},
      {"unit": "retrieved/ref3.md", "kind": "file"},
      {"unit": "claim 1: 14 firms, lower exhaustion vs matched controls [1]", "kind": "claim"},
      {"unit": "claim 2: effect largest in small teams [2]", "kind": "claim"},
      {"unit": "claim 3: held in a 2024 replication [3]", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "live DOI/URL records", "reason": "no network access"},
      {"unit": "full-text methods of refs 1-3", "reason": "only abstracts supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md para 1 [3]; retrieved/ref3.md abstract",
     "scenario": "The note says the effect held in a 2024 replication; the cited copy reports a non-significant d = 0.04 (95% CI -0.19 to 0.27) and is dated 2019, so a policy proposal would claim replication where the only replication was null.",
     "fix": "Report the null replication or remove claim 3.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Compare note.md 'it held in a 2024 replication [3]' with ref3 abstract 'the exhaustion difference was not significant (d = 0.04...)'."},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md para 1 [2]; retrieved/ref2.md",
     "scenario": "The copy cited for 'effect largest in small teams' is a parking-policy commuter survey with no four-day-week or team-size content, so the claim has no supporting source.",
     "fix": "Retrieve the actual 'Team size and the shorter week' text and confirm it supports the claim, or delete claim 2.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Compare citation title 'Team size and the shorter week' with ref2 title 'Parking policies and commuter satisfaction in mid-sized cities'."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md Sources item 3; retrieved/ref3.md header",
     "scenario": "The citation says 2024 and the DOI reads jws.2024.007, but the copy says published 2019, which is earlier than the 2023 study it claims to replicate, so the work relied on cannot be identified.",
     "fix": "Resolve the DOI against the publisher record and cite the version actually read.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "C",
     "location": "note.md title vs para 1; retrieved/ref1.md abstract",
     "scenario": "The note frames the question as burnout while its only supported evidence is a small (d = 0.31) effect on exhaustion scores, so readers may infer a broader, larger effect.",
     "fix": "Say 'exhaustion', report d = 0.31, and state that the only replication was null.",
     "answers": {"a": true, "b": true, "c": false, "d": true}},
    {"id": "S1", "status": "needs_validation", "track": "C", "location": "note.md Sources item 2",
     "suspicion": "A genuine Lindqvist 2022 team-size paper may exist and the wrong page was retrieved.",
     "unresolved_fact": "The content of the live page at workreview.example.org/2022/team-size."},
    {"id": "S2", "status": "needs_validation", "track": "C", "location": "note.md Sources item 3",
     "suspicion": "A 2024 version of Mbeki et al. may exist with different results.",
     "unresolved_fact": "The publisher record for DOI 10.5555/jws.2024.007."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Claim 1 misstates ref1.",
     "evidence": "ref1 abstract: 'Across 14 firms, employees on a four-day week reported lower exhaustion scores than matched controls (d = 0.31)'; title, authors, venue, year and DOI match the citation."}
  ]
}
```