# pr-review: suggested fix to `manifest.json` (from `review.md`, 2026-10-22)

**Answer: No, the fix is not safe to apply as written.** `"sources": []` fails the manifest's own schema (`minItems: 1`). Per `publish.md`, any validation error stops the whole publish, so applying this fix would stop every feed page from rebuilding. The underlying finding (feed-a is deprecated) looks correct. The fix should replace feed-a with the approved feed-b, not empty the list.

## Review report

**REVIEWED:** The suggested fix in `review.md` (Finding 1), applied to `work/manifest.json`. There is no PR, head SHA or merge base: the workspace is not a git repository and this session has no tools. I reviewed the file contents as supplied. If the manifest or schema change before the fix is applied, this review does not cover the new contents.

**TIER:** Standard. The change is config and touches no auth, secrets, network exposure or personal data. A bad manifest can still stop all publishing, though, so I did not treat it as Low. One round, this one.

**REVIEWERS:** This session (Claude Opus 5.5) reviewed. It did not write the manifest or the suggested fix. The fix's author is "the reviewer" named in `review.md`; no commit trailers exist to name them further. No code left this session.

**Method and limits:** I read the fix statically against its consumer, `schema/manifest.schema.json`, and against the consumption contract in `publish.md`. I could not run `python3 validate.py manifest.json`, so nothing here was executed. `review.md` says "Ready to apply." That is a claim, and the schema contradicts it.

### FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | **P0** (outage) | `review.md` suggested fix → `manifest.json:2`, checked against `schema/manifest.schema.json:9-10` (`"type": "array", "minItems": 1`) | 1. The fix sets `"sources": []`. 2. The next merge to main runs `publish.py`, which validates the manifest. 3. The empty array violates `minItems: 1` and validation fails. 4. Per `publish.md`, the publish stops: "no feed page is rebuilt until the manifest validates again." Every feed page stops updating, not just feed-a. | Apply the fix in a scratch copy and run `python3 validate.py manifest.json`. Expected today: an error about `minItems` / empty array, where a passing fix prints `valid (1 sources)`. Add a CI check that runs the validator on every change to `manifest.json`. |
| 2 | P1 | `review.md` suggested fix vs `publish.md` ("Approved replacement for feed-a, per the data owner on 2026-10-20: feed-b at https://feeds.example.test/b.xml") | The fix drops feed-a and adds nothing in its place. The data owner already approved feed-b as the replacement. Even if the schema allowed an empty list, the feed content would silently disappear instead of moving to the approved source. | Assert that `manifest.json` contains a source with `id == "feed-b"` and `url == "https://feeds.example.test/b.xml"`, and none with `id == "feed-a"`. |

**Corrected fix (verified statically against the schema, not run):**

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

Checked against `schema/manifest.schema.json`:
- The object has the required `sources` key.
- The array has 1 item, which satisfies `minItems: 1`.
- The item has the required `id` and `url`, both strings.
- The URL and id match `publish.md`'s 2026-10-20 approval.

Before merging, still run `python3 validate.py manifest.json` and expect `valid (1 sources)`. `validate.py` may enforce more than the schema shows.

**FILES NEEDED BUT NOT PROVIDED:**
- `validate.py`: needed to confirm it enforces exactly this schema.
- `publish.py`: needed to confirm the stop-on-error behaviour that `publish.md` describes.
- The data owner's deprecation/approval record for feed-a/feed-b: `publish.md` states it, but I could not open the original.

## Close-out

Pending. The author or the closer adjudicates these findings; the reviewer does not.

ADJUDICATION: — (pending)
VERIFIED AFTER FIXES: — (none yet)

**MERGE RECOMMENDATION: Do not merge the suggested fix as written.** Finding 1 is an unresolved P0 blocker, and under Step 8 a merge requires "no unresolved blocker remains." Apply the corrected feed-b entry instead. Run the validator and get a green result before merging, because Step 8 also requires that "every expected check is present and green."

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "static read against schema consumer; validator not run",
      "location": "review.md suggested fix -> manifest.json:2; schema/manifest.schema.json:9-10",
      "scenario": "Fix sets \"sources\": []; schema requires minItems: 1; publish.py validation fails on next merge to main and, per publish.md, stops the whole publish so no feed page is rebuilt.",
      "fix": "Replace feed-a with the approved source: \"sources\": [{\"id\": \"feed-b\", \"url\": \"https://feeds.example.test/b.xml\"}]; confirm with python3 validate.py manifest.json -> valid (1 sources)."
    },
    {
      "severity": "P1",
      "evidence_level": "static read of publish.md; data-owner record not opened",
      "location": "review.md suggested fix vs publish.md (approved replacement, 2026-10-20)",
      "scenario": "Fix removes feed-a without adding the owner-approved replacement feed-b, so feed content is dropped instead of migrated.",
      "fix": "Add feed-b at https://feeds.example.test/b.xml in place of feed-a; add a test asserting feed-b present and feed-a absent."
    }
  ]
}
```