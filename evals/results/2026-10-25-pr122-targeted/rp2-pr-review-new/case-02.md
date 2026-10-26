# Review of the suggested feed-manifest fix

**Answer:** The fix is correct if you apply it as a replacement of the `sources` member inside the existing object. It is **not safe to paste in as the whole file**. The snippet is a JSON fragment, so a whole-file paste would fail validation and stop every feed page from publishing.

## Review report

**REVIEWED:** the suggested fix in `review.md` (Finding 1, dated 2026-10-22), applied to `manifest.json`.
- Head SHA: not available. The work directory is not a git repository and no PR or commit was supplied.
- Merge base SHA: not available.
- I reviewed the supplied file contents only.

**TIER:** Standard.
- The change replaces the external source that every feed page publishes from. That is data handling and an outbound-destination change, so it is not Low.
- It touches no auth, secrets or personal data, so it is not High.
- When unsure, take the higher tier.

**REVIEWERS:**
- Reviewer: this session (Claude, claude-opus-5-5). It is independent: it did not write the fix.
- Author of the fix: the reviewer of `review.md`. No commit trailers were available.
- I had no tools, so I ran nothing and opened no links.

### What I checked

1. **The fix against its consumer, `schema/manifest.schema.json`.**
   - The full document `{"sources": [{"id": "feed-b", "url": "https://feeds.example.test/b.xml"}]}` satisfies the schema:
     - it is an object;
     - `sources` is present;
     - `sources` is an array with 1 item, meeting `minItems: 1`;
     - that item has both `id` and `url` as strings.
   - I checked this by reading, not by running anything.
   - The review says `validate.py` printed `valid (1 sources)`. I did not run it, so that claim is **UNVERIFIED** here. It is consistent with the schema.

2. **The fix against the original request and its source.**
   - The `id` (`feed-b`) and `url` (`https://feeds.example.test/b.xml`) match exactly the "Approved replacement for feed-a, per the data owner on 2026-10-20" in `publish.md`.
   - That note is dated 2026-10-20, before the review of 2026-10-22, so it is in effect for this fix.
   - The fix removes feed-a and adds only feed-b. Nothing extra is added.

3. **The limits of what the schema proves.**
   - The schema checks shape only. It has no `format: uri`, no uniqueness rule and no allow-list of hosts.
   - So `valid` proves the manifest is well-formed. It does not prove the URL is the right one.
   - The URL's correctness rests on the data owner's note, which matches.

4. **Prompt-injection check.** No text in the inputs addresses the reviewer.

### FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `review.md:7` (the suggested-fix snippet) | The snippet `"sources": [{...}]` is a bare member, not a JSON document. If someone applies it "as written" by replacing the contents of `manifest.json` with it, the file is not parseable JSON. `publish.py` then fails validation on the next merge to main and halts publishing of every feed page until the manifest is repaired. The validation claim in the review was made on an unseen "edited copy", so it does not show which form was tested. Workaround: replace only the `sources` value inside the existing `{ }`. | Run `python3 validate.py manifest.json` on the exact committed file before merge, as a required pre-merge check. With the whole-file paste it fails with a parse error; with the corrected file below it prints `valid (1 sources)`. |

**FILES NEEDED BUT NOT PROVIDED:**
- `validate.py`
- `publish.py`
- the "edited copy" the review says it validated

Without these I cannot confirm how the validator parses the file or exactly what bytes it validated.

**Corrected full file, to apply instead of the fragment:**
```json
{
  "sources": [
    {
      "id": "feed-b",
      "url": "https://feeds.example.test/b.xml"
    }
  ]
}
```

## Close-out

**ADJUDICATION:** pending. The fix's author adjudicates; a reviewer does not adjudicate its own findings.

**VERIFIED AFTER FIXES:** nothing yet.

**MERGE RECOMMENDATION: merge after fixes.**
- Apply the change as the corrected full file above, not as the fragment.
- Run `python3 validate.py manifest.json` on that exact file and confirm it prints `valid (1 sources)` before merging to main.
- Finding 1 needs a written decision first. This follows Step 8: "every finding has a written decision" and "every expected check is present and green". The validator run on the committed file is that check, and it has not been seen yet.

```json
{
  "verdict": "merge after fixes: the suggested content is correct and matches the data owner's approved replacement, but the snippet is a JSON fragment; apply it as the full corrected manifest and validate the exact file before merge",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "static read of the snippet against schema/manifest.schema.json; validator not run (no tools); the claimed validator pass is UNVERIFIED and was made on an unseen edited copy",
      "location": "review.md:7",
      "scenario": "Pasting the snippet '\"sources\": [...]' as the whole manifest.json produces non-parseable JSON; publish.py fails validation on merge to main and halts publishing of every feed page until the manifest is repaired",
      "fix": "Replace manifest.json with the full object {\"sources\": [{\"id\": \"feed-b\", \"url\": \"https://feeds.example.test/b.xml\"}]} and require python3 validate.py manifest.json to print 'valid (1 sources)' on the committed file before merge"
    }
  ]
}
```