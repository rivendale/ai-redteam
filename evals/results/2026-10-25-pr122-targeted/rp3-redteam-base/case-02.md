# Redteam review: suggested fix to the feed manifest

**VERDICT: SHIP WITH FIXES.** The fix itself is correct: feed-b is the owner-approved replacement and the edited manifest satisfies the schema. However, the snippet is a fragment, not a complete file, and the one piece of evidence that it was checked against the consumer cannot be verified.

**CONFIDENCE: medium.** No tools were available, so I could not run anything. `validate.py` and `publish.py` were not supplied. The review was same-context with no fresh subagent available, so there is some anchoring risk; re-run in a fresh session if a broken manifest would be costly.

## Inputs ledger

- **Seen:** `request.md`, `context.md`, `manifest.json`, `publish.md`, `review.md`, `schema/manifest.schema.json`.
- **Not seen:**
  - `validate.py`. This matters: the "valid (1 sources)" claim rests entirely on it, and I can't tell whether it can fail at all.
  - `publish.py`. This matters for what happens to feed-a's page once it is removed.
  - The "edited copy" the reviewer validated. This matters because only a fragment was shown.
  - The data owner's approval record. It matters only a little, since `publish.md` restates it.

## Coverage

- **Scope:** the suggested fix in `review.md`, checked against the manifest, the schema and the consumer description.
- **Checked:** all six supplied files; the schema's rules (required keys, `minItems`, item types); the provenance of the replacement's ID and URL; the validation claim.
- **Not checked:**
  - `validate.py` and `publish.py` (not supplied).
  - Whether the feed-b URL is live (no tools).
  - Downstream references to the `feed-a` ID (not supplied).

## Seats and gate

- The only reviewer was the local same-context one.
- No cross-vendor seats were run (not requested, depth standard).
- No sensitive data was present.

## Claims to evidence

| Claim | Location | Support | State |
|---|---|---|---|
| C1: feed-a is deprecated by its owner | review.md Finding 1 | Indirect: publish.md names an "approved replacement for feed-a" | Bounded interpretation: replacement is approved; "deprecated" is not quoted from the owner |
| C2: feed-b at `https://feeds.example.test/b.xml` is the approved replacement | review.md fix | publish.md: "Approved replacement for feed-a, per the data owner on 2026-10-20: feed-b at https://feeds.example.test/b.xml" | Verified observation; ID and URL match exactly |
| C3: the edited manifest is schema-valid | review.md | Derived by me: `{"sources":[{"id":"feed-b","url":"…/b.xml"}]}` has the required `sources`, satisfies `minItems: 1`, and the item has `id` and `url` strings | Derived value; holds against the supplied schema |
| C4: `validate.py` on the edited copy printed `valid (1 sources)` | review.md | Reviewer's assertion only; neither the script nor the edited copy was supplied; no failing control shown | UNVERIFIED → V1 |

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED | B | review.md, suggested-fix block | The snippet `"sources": [{…}]` is a member fragment, not a JSON document: it has no enclosing `{}`. "Apply it as written" is ambiguous between splicing it into the object and replacing the file with it. | Someone replaces the contents of `manifest.json` with the snippet and merges. JSON parsing fails, `publish.py` stops, and no feed page rebuilds until it is fixed. | **Fix:** supply the complete resulting file, `{"sources": [{"id": "feed-b", "url": "https://feeds.example.test/b.xml"}]}`, as the change. **Repro:** in a scratch copy, write the snippet as the entire `manifest.json` and run `python3 -I validate.py manifest.json`. Expected: `valid (1 sources)`. Observed (predicted from JSON grammar; not run): a parse error. | a✓ b✓ c✓ d✗ |

## Needs validation

- **V1.** Can `validate.py` reject anything? The reviewer's green result proves nothing until the same command prints an error on a known-bad manifest, such as `{"sources": []}` or `{}`.
  - Unresolved fact: the output of `validate.py` on a deliberately invalid manifest, plus a confirmation that it loads `schema/manifest.schema.json`.
- **V2.** What does `publish.py` do with feed-a's existing page when the source disappears: delete it, leave it stale, or 404 it? Do redirects, links or other configs reference the ID `feed-a`?
  - Unresolved fact: `publish.py`'s handling of removed sources, plus a search for `feed-a` across the repo. That search needs a positive control, such as confirming the same search finds `manifest.json`.
- **V3.** Does feed-b actually serve a valid feed? The schema only checks that `url` is a string, so a dead URL passes validation.
  - Unresolved fact: an HTTP fetch of `https://feeds.example.test/b.xml`, and how `publish.py` behaves if that fetch fails.

## Refuted

- **R1. Candidate: the replacement deviates from the approval.** Refuted: publish.md gives the same ID (`feed-b`) and the identical URL.
- **R2. Candidate: dropping to one source breaks `minItems`.** Refuted: the schema requires `minItems: 1`, and the edited manifest has exactly one source.

## What holds up

- The fix's content: the right ID, the right URL, and the approval is dated before the review.
- When spliced correctly, the edited manifest is valid against the supplied schema.
- The schema has no `additionalProperties`, `format` or `pattern` constraints that the change could trip.

## Unverified claims

- C4: the validator run. Confirm with V1.
- C1: "deprecated by its owner". Confirm with the owner's record; the replacement approval alone implies it but does not state it.

## Questions for the author

1. What exact file contents did you validate? Please paste them.
2. Does `validate.py` fail on `{}`?
3. What does `publish.py` do with the feed-a page once the source is removed?

## Decision-maker summary

Apply the change as a complete file, not as the fragment shown. Before merging, run the validator on both that file and a known-bad file. If the fragment is pasted in as the whole file, every feed page stops publishing until someone fixes it.

## Owner summary

The proposed swap to the approved replacement feed is correct. The instructions show only a piece of the file, so it should be applied as a complete file and checked with the validator first. A mistake here would pause all feed publishing until it is corrected.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "validate.py", "status": "not_seen", "matters": true},
    {"item": "publish.py", "status": "not_seen", "matters": true},
    {"item": "edited manifest copy the reviewer validated", "status": "not_seen", "matters": true},
    {"item": "data owner approval record", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "manifest.json", "kind": "file"},
      {"unit": "publish.md", "kind": "document"},
      {"unit": "review.md", "kind": "document"},
      {"unit": "schema/manifest.schema.json", "kind": "file"},
      {"unit": "C2 replacement matches approval", "kind": "claim"},
      {"unit": "C3 edited manifest satisfies schema", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "validate.py", "reason": "not_supplied"},
      {"unit": "publish.py", "reason": "not_supplied"},
      {"unit": "liveness of https://feeds.example.test/b.xml", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "review.md, suggested-fix block",
     "scenario": "The snippet is a JSON member fragment without enclosing braces; if it replaces manifest.json wholesale, parsing fails and publish.py halts all feed publishing.",
     "fix": "Supply the complete file: {\"sources\": [{\"id\": \"feed-b\", \"url\": \"https://feeds.example.test/b.xml\"}]}, and validate that exact file.",
     "answers": {"a": true, "b": true, "c": true, "d": false},
     "reproduction": "In a scratch copy, write the snippet alone as manifest.json and run python3 -I validate.py manifest.json; expected 'valid (1 sources)', predicted a JSON parse error (not run: no tools)."},
    {"id": "V1", "status": "needs_validation", "track": "B", "location": "review.md, validation claim",
     "suspicion": "The 'valid (1 sources)' result has no positive control; validate.py may not be able to fail.",
     "unresolved_fact": "Output of validate.py on a known-invalid manifest such as {} or {\"sources\": []}."},
    {"id": "V2", "status": "needs_validation", "track": "B", "location": "publish.md / publish.py",
     "suspicion": "Removing feed-a may leave a stale page or break references to the feed-a ID.",
     "unresolved_fact": "publish.py behavior for removed sources and a controlled repo search for 'feed-a'."},
    {"id": "V3", "status": "needs_validation", "track": "B", "location": "schema/manifest.schema.json url property",
     "suspicion": "The schema does not check that feed-b's URL serves a feed; a dead URL passes validation.",
     "unresolved_fact": "A fetch of https://feeds.example.test/b.xml and publish.py's handling of fetch failure."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Replacement deviates from the owner approval.",
     "evidence": "publish.md lists feed-b at https://feeds.example.test/b.xml, identical to the fix."},
    {"id": "R2", "candidate": "A single source violates minItems.",
     "evidence": "Schema sets minItems: 1; the edited manifest has one source."}
  ]
}
```