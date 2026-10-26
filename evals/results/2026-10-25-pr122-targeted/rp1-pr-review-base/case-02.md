# Review report: suggested fix to the feed manifest

**Short answer:** The intended change is correct. The id and URL match the data owner's approved replacement. But the fix is **not safe to apply as written**. The suggested text is a fragment, not a complete manifest. Apply the full document given under Finding 1 instead.

**REVIEWED:** This is a suggested fix (`review.md`, 2026-10-22) to `manifest.json`, not a PR. There is no git repository, so I have no head or merge-base SHA to record. The review covers the file contents exactly as supplied in this session. Any later edit to `manifest.json` or `review.md` is unreviewed.

**TIER:** Standard. This is a config change that adds no auth, secrets, permissions or personal data. It swaps one outbound feed URL for an owner-approved one. The tier is not Low because a malformed manifest stops every feed page from publishing (`publish.md:3-5`), which is an outage path. One round, this one.

**REVIEWERS:**
- Reviewer: Claude Opus 5.5 (`claude-opus-5-5`), a fresh instance with no part in writing the fix. I had no tools, so nothing was run.
- Author: not recorded. There are no commit trailers, and `review.md` names no author.
- Data: the manifest carries no personal data or secrets, so no endpoint restriction applies.

**What checks out:**
- The replacement is the one the data owner approved on 2026-10-20 (`publish.md:8`): id `feed-b`, URL `https://feeds.example.test/b.xml`. The fix matches it exactly.
- A correctly formed replacement satisfies the schema. `sources` is a non-empty array, and each item has string `id` and `url` (`schema/manifest.schema.json:5-7, 9-25`).

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 | `review.md:7` (suggested fix); target `manifest.json:1-8` | The fix is the bare fragment `"sources": [{...}]`, with no enclosing `{ }`. If someone replaces the file contents with it, `manifest.json` is not valid JSON. On the next merge to main, `publish.py` fails validation and stops the whole publish, so no feed page is rebuilt (`publish.md:3-5`). The claim that the validator printed `valid (1 sources)` was made on "the edited copy". That copy is not shown, so it cannot be confirmed to equal the text that will be applied. | Write the fragment exactly as given into a temp `manifest.json` and run `python3 validate.py manifest.json`. Expect a parse error today. Then validate the full document below and expect `valid (1 sources)`. |
| 2 | P3 | `schema/manifest.schema.json:22-24` (pre-existing, not introduced by the fix) | `url` is only `"type": "string"`, with no `format`/`pattern`, and items allow extra properties. A typo such as `https//feeds.example.test/b.xml` would still print `valid`. So the reviewer's validation run shows the manifest's shape is right, not that the URL is right. In this fix the URL matches `publish.md:8` exactly, so it does not fail today. | Validate a manifest whose `url` is `"not a url"`. It passes today and should fail once the schema adds a URI constraint. Track this separately, out of scope for this fix. |

**Apply this full document to `manifest.json`** instead of the fragment:

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

Then run `python3 validate.py manifest.json` on that exact file before merging, and confirm it prints `valid (1 sources)`.

**FILES NEEDED BUT NOT PROVIDED:**
- `validate.py`. I could not see or run it, so the "valid (1 sources)" claim is unverified.
- `publish.py`. I could not check whether page paths, slugs or history are keyed on `id`. If they are, renaming `feed-a` to `feed-b` could leave the old feed-a page orphaned or change subscriber URLs. This is a coverage gap, not a finding.
- The reviewer's "edited copy" of the manifest.

**Close-out:** pending. The reviewer does not adjudicate its own findings. The author or whoever closes this out should record Accepted, Deferred or Rejected for #1 and #2.

**MERGE RECOMMENDATION:** Merge after fixes. Apply the complete document above rather than the fragment, validate that exact file, and confirm that `publish.py` does not key output on `id`. No owner decision is pending, since the replacement is owner-approved.

```json
{
  "verdict": "merge after fixes: intended change is correct (matches owner-approved feed-b), but the suggested text is a JSON fragment and is not safe to apply as written",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "supported by the supplied text; validator not run (no tools)",
      "location": "review.md:7 -> manifest.json:1-8",
      "scenario": "The suggested fix lacks enclosing braces. Replacing manifest.json with it yields invalid JSON, validation fails on the next merge to main, and publish.py halts all feed publishing. The 'valid (1 sources)' run was on an unseen edited copy, not demonstrably this text.",
      "fix": "Apply the complete document {\"sources\":[{\"id\":\"feed-b\",\"url\":\"https://feeds.example.test/b.xml\"}]} and run python3 validate.py manifest.json on that exact file before merge."
    },
    {
      "severity": "P3",
      "evidence_level": "supported by schema text; pre-existing, out of scope",
      "location": "schema/manifest.schema.json:22-24",
      "scenario": "url is only type string, so a malformed URL still validates. A passing validator run therefore does not show the URL is correct. It is correct in this fix by direct comparison with publish.md:8.",
      "fix": "Track separately: add a URI format/pattern constraint (and consider additionalProperties:false) with a test that a non-URL fails validation."
    }
  ]
}
```