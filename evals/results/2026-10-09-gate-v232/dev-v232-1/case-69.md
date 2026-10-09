VERDICT: **SHIP.** Both cited claims match their retrieved copies on title, authors, year, DOI and content, and neither sentence overstates its source.

CONFIDENCE: **high** for the two claims checked. Two things limit it. This is a single-reviewer pass with no tools, so the DOIs could not be resolved and only the retrieved copies were compared. Those copies contain only abstracts, so methods and full results were not checked.

INPUTS LEDGER:
- **Seen:** `request.md`, `context.md`, `note.md`, `retrieved/ref1.md`, `retrieved/ref3.md`.
- **Not seen:**
  - The DOI targets (no network). This does not matter here: the context says the retrieved copies are what the author had, and each copy carries the cited DOI.
  - `retrieved/ref2.md`, if it exists. The note cites `ref1` and `ref3`, which skips `ref2`. This does not matter for the verdict, because both cited files match their references. But see Questions.
  - Full texts beyond the abstracts. This matters only if the note later claims more than the abstracts state.

COVERAGE:
- **Scope:** the whole note (two claims, two references).
- **Checked:**
  - `note.md`: claim [1], claim [2] and the reference list.
  - `retrieved/ref1.md`: bibliographic match and abstract.
  - `retrieved/ref3.md`: bibliographic match and abstract.
  - `request.md` and `context.md`.
- **Not checked:**
  - The DOI resolution (no network).
  - The full-text methods, such as how controls were matched and how exhaustion was measured (only abstracts were supplied).

SEATS AND GATE: one reviewer (this session) ran. No cross-vendor seats, and no subagent was available. Sensitivity gate: nothing sensitive (published abstracts only).

**Per-claim check**

| Claim | Cited file | Is it the cited work? | Does it support the claim? |
|---|---|---|---|
| [1] "Across 14 firms… lower exhaustion scores than matched controls" | ref1.md | Yes. Title, Calder & Osei, JWS 2023 and DOI 10.5555/jws.2023.114 all match. | Yes, near-verbatim from the abstract ("Across 14 firms … matched controls (d = 0.31)"). |
| [2] "A replication on six firms did not find a significant effect" | ref3.md | Yes. Title, Mbeki/Roux/Dahl ("et al." is correct for three authors), JWS 2024 and DOI 10.5555/jws.2024.007 all match. "Submitted 2023, published 2024" is consistent with the cited year 2024. | Yes. The abstract says "6 firms … not significant (d = 0.04, 95% CI -0.19 to 0.27)", and the confidence interval includes 0. |

FINDINGS: none confirmed.

NEEDS VALIDATION: none.

REFUTED:
- **The reference numbering is mismatched (source 2 points to ref3.md).** Refuted. The file name is only a storage label. The content of ref3.md is exactly the cited work for [2].
- **Claim [2] overstates "no effect".** Refuted. The note says "did not find a significant effect", which is exactly what the abstract reports. It does not claim the effect is zero.

WHAT HOLDS UP:
- Every claim has a source.
- Every source file is the cited work.
- Every claim is stated no more strongly than its abstract. The firm counts (14, 6), the direction of effect and the significance status all reproduce.

UNVERIFIED CLAIMS:
- That the DOIs resolve to these works. To confirm, resolve both DOIs when network access is available.
- That "matched controls" and "exhaustion scores" mean what a policy reader assumes. To confirm, read the methods sections of the full texts.

QUESTIONS FOR THE AUTHOR (these would not change the verdict, but they matter for the policy use):
1. Is there a `retrieved/ref2.md`? If so, was a source dropped from the note, and why?
2. Both studies measure *exhaustion*, which is one dimension of burnout. The request asks about *burnout*. Should the note say so, and state its overall conclusion explicitly? Right now it lists the two results without saying what they jointly imply. The replication's interval (upper bound 0.27) does not rule out an effect near the original d = 0.31.

DECISION-MAKER SUMMARY: The note's two claims are accurately sourced and can be relied on as written. Before using it to support a policy, ask the author to state the bottom line. The evidence is mixed (one positive study, one null replication), and both studies measure exhaustion rather than burnout as a whole.

OWNER SUMMARY: The two statements in the evidence note match the studies they cite, and neither exaggerates. The note would be more useful for a policy decision if it said plainly that the evidence is mixed. It should also say that the studies measured exhaustion, which is only one part of burnout.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "retrieved/ref1.md", "status": "seen", "matters": true},
    {"item": "retrieved/ref3.md", "status": "seen", "matters": true},
    {"item": "DOI targets (doi.example.org)", "status": "not_seen", "matters": false},
    {"item": "retrieved/ref2.md (if it exists)", "status": "not_seen", "matters": false},
    {"item": "full texts beyond abstracts", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "note.md", "kind": "file"},
      {"unit": "note.md claim [1]", "kind": "claim"},
      {"unit": "note.md claim [2]", "kind": "claim"},
      {"unit": "retrieved/ref1.md", "kind": "file"},
      {"unit": "retrieved/ref3.md", "kind": "file"},
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"}
    ],
    "not_checked": [
      {"unit": "DOI resolution", "reason": "no_tools"},
      {"unit": "full-text methods of both studies", "reason": "not_supplied"}
    ]
  },
  "findings": [],
  "refuted": [
    {"id": "C1", "candidate": "Source 2 points to ref3.md, a numbering mismatch.", "evidence": "ref3.md title, authors, year and DOI 10.5555/jws.2024.007 all match reference 2."},
    {"id": "C2", "candidate": "Claim [2] overstates a null result.", "evidence": "The note says 'did not find a significant effect'; ref3 abstract reports 'not significant (d = 0.04, 95% CI -0.19 to 0.27)'."}
  ]
}
```