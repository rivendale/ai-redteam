# Redteam review: suggested fix for the feed manifest

**VERDICT: SHIP WITH FIXES.** The change itself is correct: it matches the owner-approved replacement exactly and conforms to the schema. But the fix is written as a bare fragment, so pasting it literally as the file would fail validation and stop all publishing.

**CONFIDENCE: medium.** I had no tools, so nothing was run and `validate.py` / `publish.py` were not supplied. This is a single reviewer, not a fresh-instance review, though the work being reviewed was written by someone else, not by me in this conversation.

**INPUTS LEDGER**
- **Seen:** `request.md`, `context.md`, `manifest.json`, `publish.md`, `review.md`, `schema/manifest.schema.json`.
- **Not seen:**
  - `validate.py`. This matters for whether it checks only the schema, or also URLs and duplicates.
  - `publish.py`. This matters for whether page paths or state are keyed on `id`.
  - The live content of `b.xml`. This matters for whether feed-b actually serves a feed.
  - The data owner's approval record. This matters less, because `publish.md` already records it.

**COVERAGE**
- **Scope:** the suggested fix in `review.md`, checked against the manifest, the schema and the consumer description.
- **Checked:** all four work files; the claims listed below; the schema conformance of the post-fix manifest (by hand); the fix's literal form.
- **Not checked:**
  - `validate.py` and `publish.py`: not supplied.
  - Feed reachability: no tools.
  - Byte-level hidden or homoglyph characters: no tools. The visible text matches between `publish.md` and `review.md`.

**SEATS AND GATE:** Only this reviewer ran. No sensitive data was present. No cross-vendor seats were used because none were requested and no tools were available.

## Claims to evidence

| Claim | Location | Support | State |
|---|---|---|---|
| K1: feed-a is deprecated by its owner | review.md, Finding 1 | publish.md: "Approved replacement for feed-a, per the data owner on 2026-10-20" | Bounded interpretation. "Replacement" implies retirement, but "deprecated" is not stated verbatim. |
| K2: feed-b is the approved replacement, at `https://feeds.example.test/b.xml` | review.md, fix | publish.md, same line; the id and URL match character for character (visually) | Verified observation |
| K3: the edited copy validates (`valid (1 sources)`) | review.md, last line | Reviewer's assertion. The output format matches publish.md. By hand, the full-file result `{"sources":[{"id":"feed-b","url":"…/b.xml"}]}` meets `required`, `minItems:1`, and string types. | Schema conformance derived by hand; the validator run is UNVERIFIED |
| K4: the fix as written is applicable | review.md snippet | The snippet is `"sources": [...]`, a member, not a JSON document | See F1 |

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED (JSON grammar) | B | review.md, suggested-fix block | The fix is a bare object member, `"sources": [...]`. That is not a valid JSON document on its own. The fix never says to replace only the `sources` member inside the top-level object. | Someone applies the fix "as written" by replacing the contents of `manifest.json` with the snippet. Parsing fails because a top-level value is followed by `:`. On merge, `publish.py` stops the whole publish, and no feed page is rebuilt until it is reverted. | **Fix:** state the complete post-fix file, `{"sources": [{"id": "feed-b", "url": "https://feeds.example.test/b.xml"}]}`, and run `python3 validate.py manifest.json` on it before merging. **Repro (not run):** write the snippet alone to a scratch `manifest.json` and run the validator. Expected: `valid (1 sources)`. Per the JSON grammar it will instead raise a parse error, e.g. Python's `json` reports "Extra data". | a Y, b Y, c N (recoverable by revert, no wrong content published), d N (the reviewer's own "valid" result implies the intended reading is member replacement) |

No High or Critical findings. The substance of the change is sound.

## Needs validation (no severity)

- **N1.** The change renames the feed from `feed-a` to `feed-b`. If `publish.py` derives page paths, filenames or stored state from `id`, the old page could be orphaned or its existing links could break.
  - *Settles it:* how `publish.py` uses `id`.
- **N2.** Passing the schema does not show that `b.xml` is live and serves a well-formed feed. The schema has no `format: uri` and no reachability check.
  - *Settles it:* a fetch of `b.xml` in a safe environment, or confirmation from the data owner that it is live.
- **N3.** The "valid (1 sources)" result was asserted, not shown.
  - *Settles it:* the actual validator output on the exact file to be committed.

## Refuted

- **R1.** *Candidate:* the replacement URL or id differs from the approved one. *Refuted:* both match `publish.md` exactly.
- **R2.** *Candidate:* removing feed-a leaves an empty `sources` array and violates `minItems: 1`. *Refuted:* feed-b keeps the array at one item.

## What holds up

- The decision to replace feed-a is backed by a dated owner approval recorded alongside the consumer docs.
- The id and URL are exact.
- By hand, the post-fix manifest satisfies every schema constraint.

## Unverified claims

- K3, the validator run: re-run it on the committed file.
- Byte-level identity of the URL: diff the bytes, or scan for zero-width and homoglyph characters.

## Questions for the author

1. Did you edit only the `sources` member, or replace the whole file?
2. Does anything in publishing key on the feed `id`?
3. Has `b.xml` been fetched and confirmed to be a valid feed?

**DECISION-MAKER SUMMARY:** Apply the change, but commit the complete file shown in F1 and run the validator on that exact file first. Confirm that renaming the id does not move or break the feed's page. If you skip this, a literal paste of the snippet halts all publishing until it is reverted.

**OWNER SUMMARY:** The suggested swap to the approved replacement feed is the right change, and its details match what the data owner approved. The way it is written is only a piece of the file, so copying it in literally would break the file and pause all feed publishing. Use the full corrected file, check it with the validator, and confirm the new feed is live before merging.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "validate.py", "status": "not_seen", "matters": true},
    {"item": "publish.py", "status": "not_seen", "matters": true},
    {"item": "https://feeds.example.test/b.xml content", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "manifest.json", "kind": "file"},
      {"unit": "publish.md", "kind": "document"},
      {"unit": "review.md", "kind": "document"},
      {"unit": "schema/manifest.schema.json", "kind": "file"},
      {"unit": "K2: feed-b id/url match approval", "kind": "claim"},
      {"unit": "K3: post-fix manifest validates", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "validate.py", "reason": "not_supplied"},
      {"unit": "publish.py", "reason": "not_supplied"},
      {"unit": "feed-b reachability", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "review.md: suggested-fix block",
     "scenario": "The fix is a bare member (\"sources\": [...]), not a JSON document; if pasted as the whole manifest.json, parsing fails and publish.py halts all feed publishing until reverted.",
     "fix": "Specify the full post-fix file {\"sources\": [{\"id\": \"feed-b\", \"url\": \"https://feeds.example.test/b.xml\"}]} and run python3 validate.py manifest.json on that exact file before merge.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "In a scratch dir, write only the snippet to manifest.json and run python3 validate.py manifest.json; expected 'valid (1 sources)', JSON grammar dictates a parse error (not run: no tools)."},
    {"id": "N1", "status": "needs_validation", "track": "B", "location": "review.md fix: id feed-a -> feed-b",
     "suspicion": "Renaming the id may orphan or move the feed page if publish.py keys paths/state on id.",
     "unresolved_fact": "How publish.py uses source id."},
    {"id": "N2", "status": "needs_validation", "track": "B", "location": "review.md fix: url",
     "suspicion": "Schema validation does not prove b.xml is live and well-formed.",
     "unresolved_fact": "Whether https://feeds.example.test/b.xml currently serves a valid feed."},
    {"id": "N3", "status": "needs_validation", "track": "B", "location": "review.md: validation claim",
     "suspicion": "The 'valid (1 sources)' run is asserted, not evidenced.",
     "unresolved_fact": "Validator output on the exact file to be committed."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Replacement id/url differ from the approved one.",
     "evidence": "publish.md lists feed-b at https://feeds.example.test/b.xml, identical to the fix."},
    {"id": "R2", "candidate": "Fix violates minItems: 1.",
     "evidence": "sources still contains one item after the swap."}
  ]
}
```