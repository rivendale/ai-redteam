# PR Review: suggested fix to `manifest.json` (review.md, Finding 1)

**Is it safe to apply as written?** No. The substance is right: feed-b is the approved replacement, and the corrected manifest passes the schema. But the snippet as written is a fragment, not a manifest, and pasting it as the file content would stop all publishing. Apply the full-document version given under Finding 1 instead.

## Review report

**REVIEWED:** The suggested fix in `review.md` (dated 2026-10-22) against `manifest.json`, `schema/manifest.schema.json` and `publish.md` as provided.
- **Head SHA:** not available.
- **Merge base SHA:** not available.
- There is no git repository and no PR. This review covers the file contents shown above. If any of them change, this review does not cover the new contents.

**TIER:** Standard.
- The change is to a config file, not docs or tests only.
- A bad manifest stops publishing of every feed page (`publish.md`), so it is above Low.
- It does not touch auth, secrets, personal data or money. The new URL is on the same host as the old one (`feeds.example.test`), so there is no new outbound destination.
- Budget is one round, and this is that round.

**REVIEWERS:**
- Reviewer: this session (claude-opus-5-5). It did not write the change or the suggested fix. It had no tools, so it ran nothing and opened no links.
- Author of the fix: the unnamed reviewer of `review.md`. No commit trailers were available, so authorship cannot be confirmed.

### What I checked

**Against the original request.** The fix replaces feed-a with feed-b.
- `publish.md` names this exact replacement: "Approved replacement for feed-a, per the data owner on 2026-10-20: feed-b at https://feeds.example.test/b.xml".
- The fix's id and URL match it character for character.
- Nothing extra is added.

**Against the consumer.** I checked the fix by reading `schema/manifest.schema.json`, since I could not run the validator. If the snippet replaces only the value of the existing `sources` key:
- The result is an object with the required `sources` key.
- `sources` is an array with 1 item, which meets `minItems: 1`.
- The item has the required `id` and `url`, both strings.
- **Result:** it passes.

**Claim that the validator printed `valid (1 sources)`.**
- **UNVERIFIED.** `validate.py` and the "edited copy" are not provided, and I could not run anything.
- The output is consistent with the spliced form, but it says nothing about the literal fragment.

**Record or living document.**
- `review.md` is a dated record (2026-10-22). `publish.md` contains a dated approval (2026-10-20).
- `manifest.json` and the schema are living documents. Editing the manifest is appropriate.

**Cited sources.**
- **Data-owner approval.** The quote is present in `publish.md` and dated 2026-10-20. It reads as binding ("approved, per the data owner"). The underlying owner communication was not provided, so it is UNVERIFIED beyond `publish.md`.
- **"feed-a is deprecated by its owner"** (review.md). No direct source is given. The 2026-10-20 approved replacement supports it indirectly.

**Text addressing the reviewer.** None found.

### FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 | `review.md:7` (the suggested-fix snippet) → `manifest.json:1-8` | The fix is written as `"sources": [{...}]`, a bare key/value pair with no enclosing `{ }`. That is not a valid JSON document. If someone applies it "as written" by replacing the file contents, the next merge to main fails to parse or validate. Per `publish.md`, that halts the whole publish and no feed page is rebuilt until it is repaired. It only works if spliced in place of the existing `sources` value, and the review does not say so. **Fix:** apply the full document `{"sources": [{"id": "feed-b", "url": "https://feeds.example.test/b.xml"}]}`. This was checked against the schema by reading; it was not run (UNVERIFIED by execution). | Write the literal snippet as `manifest.json` and run `python3 validate.py manifest.json`. Expect a parse error today. Then write the full-document form and expect `valid (1 sources)`. Adding a CI check that runs the validator on any change to `manifest.json` would catch this before merge. |
| 2 | P3 | `review.md:9` | The evidence "validate.py printed valid" refers to an edited copy that is not shown. A reader cannot tell whether the validated file was the full document or something else. The claim therefore does not show that the fix as written is valid. | Attach the exact edited file, or its diff, with the validator output, and re-run the validator on that exact file. |

Not a finding: the schema does not check URL format, uniqueness of `id`, or extra properties. That predates this fix and does not change whether the fix is safe.

**FILES NEEDED BUT NOT PROVIDED:**
- `validate.py`, to confirm it uses this schema and how it handles JSON parse errors.
- `publish.py`.
- The "edited copy" that the review says it validated.
- The data owner's original approval and deprecation notice.
- Git history, SHAs and commit trailers.

## Close-out

The close-out is not written here. Under the skill, a reviewer never adjudicates its own findings. The author or owner should record a decision of Accepted, Deferred or Rejected for each finding. Finding 1 is a P1, so it cannot be deferred.

**MERGE RECOMMENDATION:** Merge after fixes.
- Apply the full-document form from Finding 1, not the literal snippet.
- Run `python3 validate.py manifest.json` on that exact file and confirm it prints `valid (1 sources)` before merging to main.
- Step 8 requires that "every finding has a written decision" and that "every expected check is present and green". Neither holds yet: the validator run on the final file is missing, and Findings 1 and 2 have no decision.

```json
{
  "verdict": "merge after fixes: suggested fix is correct in substance but not safe to apply as written; apply the full-document manifest and run the validator on that exact file first",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "verified by reading: the snippet is a bare key/value pair, not a JSON document; consequence per publish.md; validator not run",
      "location": "review.md:7 -> manifest.json:1-8",
      "scenario": "Pasting the literal snippet '\"sources\": [{...}]' as manifest.json produces invalid JSON; publish.py's validation fails on the next merge to main and halts publishing of every feed page.",
      "fix": "Write manifest.json as {\"sources\": [{\"id\": \"feed-b\", \"url\": \"https://feeds.example.test/b.xml\"}]}. Checked against schema/manifest.schema.json by reading (object, required sources, minItems 1, id/url strings); not executed, so UNVERIFIED by run. Then run python3 validate.py manifest.json on that exact file."
    },
    {
      "severity": "P3",
      "evidence_level": "UNVERIFIED: validate.py and the edited copy were not provided",
      "location": "review.md:9",
      "scenario": "The 'valid (1 sources)' evidence refers to an unseen edited copy, so it does not show that the snippet as written validates.",
      "fix": "Attach the exact edited file or diff with the validator output, and re-run the validator on it."
    }
  ]
}
```