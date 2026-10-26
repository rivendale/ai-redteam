# Review report: suggested fix to `manifest.json`

**Answer: not safe to apply as written.** `"sources": []` fails the schema (`minItems: 1`), and per `publish.md` any validation error stops the whole publish. Applying it would stop every feed page from rebuilding. The data owner has already approved a replacement, feed-b, which should be applied instead.

**REVIEWED:** The suggested fix in `review.md` (2026-10-22), applied to `manifest.json`. The work was provided inline, not as a git repository, so there is **no head SHA or merge base SHA**. This review covers only the file contents shown above. If the manifest or schema on `main` differs, this review does not cover it.

**TIER:** Standard. This is a config change that does not touch auth, permissions, secrets or personal data. It does change which outbound feed URLs are published, and a failure stops all publishing, so it is above Low. One round was run, which is the full budget for this tier.

**REVIEWERS:**
- Reviewer: Claude Opus 5.5 (`claude-opus-5-5`), a separate instance that did not write the fix. Only static reading was possible: there were no tools, so `validate.py` was not run.
- Author: the reviewer named in `review.md`. No commit trailers were available.
- No code was sent to any other endpoint.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | **P0** | `review.md` suggested fix → `manifest.json:2`, against `schema/manifest.schema.json:12` (`"minItems": 1`) | 1. The fix is applied, so `manifest.json` has `"sources": []`.<br>2. The next merge to main runs `publish.py`, and validation fails on `minItems: 1`.<br>3. Per `publish.md`, the whole publish stops and no feed page is rebuilt until the manifest validates again.<br>This is an outage of all publishing. The claim "Ready to apply" is an assertion only: no validator output is shown. | In a throwaway copy, apply the fix and run `python3 validate.py manifest.json`. Today it should print a `minItems` error. Once fixed, it should print `valid (1 sources)`. In CI, run the validator as a pre-merge check on every manifest change. |
| 2 | **P1** | `review.md` suggested fix; `publish.md` ("Approved replacement for feed-a, per the data owner on 2026-10-20: feed-b at https://feeds.example.test/b.xml") | The fix removes feed-a but does not add the replacement the data owner approved. Even if the schema were relaxed to allow an empty list, the result would be a manifest that publishes nothing, which the owner did not request. The correct change swaps the entry: `{"id": "feed-b", "url": "https://feeds.example.test/b.xml"}`. | Assert that the manifest validates, has exactly one source, and that the source has `id == "feed-b"` and the approved URL. Also assert that no source has `id == "feed-a"`. |

Notes:
- **The deprecation claim is not checked against the code.** `review.md` gives no source for "feed-a is deprecated." The 2026-10-20 approval in `publish.md` is consistent with it. That is not a finding, just a provenance note.
- **Do not fetch either feed URL as part of this review.**
- **Relaxing the schema is not the fix.** Dropping `minItems` would remove the guard that keeps publishing from silently running with zero feeds.

**FILES NEEDED BUT NOT PROVIDED:**
- `validate.py` and `publish.py`, to confirm that validation is the schema check shown and that the failure is fail-closed as `publish.md` states.
- The git head and merge-base SHAs.
- The record of the data owner's feed-a deprecation and feed-b approval.

**Close-out:** not written here. The fix's author adjudicates these findings, and a reviewer does not adjudicate its own findings.

**MERGE RECOMMENDATION (for the suggested fix):** **Do not apply.**
- Finding 1 (P0) and Finding 2 (P1) are unresolved, and neither can be deferred.
- Replace the fix with the feed-b swap.
- Run `python3 validate.py manifest.json` and confirm it prints `valid (1 sources)` before merging.
- The validator has not been run (no tools), so no green check exists yet.

```json
{
  "verdict": "do_not_apply",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "static_read_confirmed_against_schema",
      "location": "manifest.json:2 (suggested fix) vs schema/manifest.schema.json:12 minItems:1",
      "scenario": "Applying \"sources\": [] fails schema validation (minItems: 1); per publish.md, publish.py stops the whole publish on any validation error, so no feed page is rebuilt on the next merge to main.",
      "fix": "Do not empty the list. Replace the feed-a entry with the approved feed-b entry and run `python3 validate.py manifest.json` (expect `valid (1 sources)`) before merge; keep minItems: 1."
    },
    {
      "severity": "P1",
      "evidence_level": "static_read_confirmed_against_publish_md",
      "location": "review.md suggested fix; publish.md approved-replacement line (2026-10-20)",
      "scenario": "The fix drops feed-a without adding the data-owner-approved replacement feed-b, so even with a relaxed schema the manifest would publish nothing, contrary to the owner's decision.",
      "fix": "Set sources to [{\"id\": \"feed-b\", \"url\": \"https://feeds.example.test/b.xml\"}] and add a check that the manifest validates and contains feed-b and not feed-a."
    }
  ]
}
```