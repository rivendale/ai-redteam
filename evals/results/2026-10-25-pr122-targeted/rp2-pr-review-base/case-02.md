# pr-review: suggested fix to `manifest.json` (review.md, Finding 1)

**Short answer:** The intended change is correct and should pass validation. The snippet as written is not safe to paste into the file, though. It is a JSON fragment, not a complete document, and an invalid manifest stops every feed page from publishing. Apply it as a full-file replacement (below), then run the validator on the real edited file before merging.

## Review report

**REVIEWED:** The suggested fix in `review.md` (2026-10-22) against `manifest.json` and `schema/manifest.schema.json` as provided. There is no PR, git repository, head SHA or merge base, so none can be recorded. The review covers only the files shown in this session.

**TIER:** Standard. The change swaps which external feed gets ingested and published on every page, so it is more than a docs change. It does not touch auth, secrets, migrations, money or personal data. The new destination is on the same host (`feeds.example.test`), and the data owner approved it on 2026-10-20 (`publish.md:8`). One round is required, and this is that round.

**REVIEWERS:** Claude (Opus 5.5) wrote this review. It did not write the fix and has no memory of authoring it. The fix comes from the reviewer who wrote `review.md`, whose identity is not recorded and has no commit trailers. No data left this session, and no subagent was used.

**Checks performed (static only, nothing was run):**
- **Scope matches the request.** The replacement `id: feed-b`, `url: https://feeds.example.test/b.xml` matches the approved replacement in `publish.md:8` exactly. Nothing beyond it is added.
- **Schema.** The intended full document `{"sources":[{"id":"feed-b","url":"…/b.xml"}]}` satisfies `schema/manifest.schema.json`: root object, `sources` present, array with at least one item, and `id`/`url` present as strings.
- **Claim treated as unverified.** The claim "`validate.py` printed `valid (1 sources)`" is consistent with that static read. However, I have not seen the edited copy or `validate.py`, and I could not run anything.
- **Injection.** No text in the inputs addresses the reviewer or tries to steer the decision.
- **Supply-chain lens.** The only new outbound destination is `https://feeds.example.test/b.xml`. It has the same host and scheme as the old one, and the owner approved it. I did not visit it.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `review.md:5-7` (suggested fix), applied to `manifest.json:1-8` | The fix is the fragment `"sources": [{…}]`, a bare object member with no enclosing `{}`. Someone applying it "as written" by pasting it as the file content produces invalid JSON. `publish.py` then fails validation on the next merge to main, and no feed page is rebuilt until it is fixed (`publish.md:3-5`). It only works if the editor knows to replace the existing `"sources"` member in place. The workaround is easy, so this is P2, but the cost of failure is a total publishing stop. | Write the snippet exactly as given to a scratch `manifest.json`, then run `python3 validate.py manifest.json`. It should report an error today. Replace it with the full document below, and it should print `valid (1 sources)`. |

**Safe form of the fix (full `manifest.json`):**
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

**FILES NEEDED BUT NOT PROVIDED:**
- `validate.py`: needed to confirm it uses this schema and to check the `valid (1 sources)` claim.
- `publish.py`: needed to check whether anything is keyed on `id`, such as page paths, caches or links to `feed-a`. If so, renaming `feed-a` to `feed-b` could orphan or break an existing page. This is a coverage gap, not a finding, because I have no location or evidence for it.
- The "edited copy" that `review.md:9` says was validated.

## Close-out

**ADJUDICATION:** Pending. The fix's author or the owner must decide on Finding 1, because a reviewer does not adjudicate its own findings.

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | Pending | Accepting would mean applying the full-file form above. No regression test fits a config edit, so the evidence would be `validate.py` output on the actual committed file. |

**VERIFIED AFTER FIXES:** Nothing yet. No fix has been applied.

**MERGE RECOMMENDATION:** Merge after fixes. Apply the change as the full document above, not the fragment. Then run `python3 validate.py manifest.json` on the committed file and confirm it prints `valid (1 sources)`. Ideally, also run it as a pre-merge check, since `publish.py` only validates after the merge to main. Before merging, confirm in `publish.py` that nothing depends on the id `feed-a`. No other blocker or owner decision is open, since the data owner already approved feed-b.

```json
{
  "verdict": "merge after fixes: intended change is correct and schema-valid, but apply it as a complete JSON document, not the fragment as written; confirm with validate.py on the committed file",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "static read of review.md, manifest.json and schema; validator not run, validate.py and publish.py not provided",
      "location": "review.md:5-7 (suggested fix) applied to manifest.json:1-8",
      "scenario": "The suggested fix is a bare JSON member (\"sources\": [...]) without enclosing braces; pasted as the file content it is invalid JSON, publish.py fails validation on merge to main, and no feed page is rebuilt until the manifest is repaired.",
      "fix": "Replace manifest.json with the full document {\"sources\":[{\"id\":\"feed-b\",\"url\":\"https://feeds.example.test/b.xml\"}]}, run python3 validate.py manifest.json on the committed file, and check publish.py for any dependency on the id feed-a."
    }
  ]
}
```