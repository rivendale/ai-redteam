# Review report: suggested fix to `manifest.json`

**Bottom line: do not apply the fix as written.** Replacing the sources with `"sources": []` fails schema validation (`minItems: 1`), and `publish.py` stops the entire publish on any validation error. Every feed page would stop rebuilding. The data owner already approved a replacement, feed-b, and the manifest should switch to it instead of being emptied.

**REVIEWED:** The suggested fix in `review.md` (2026-10-22), applied to `manifest.json`, against `schema/manifest.schema.json` and the consumption notes in `publish.md`.
- There is no PR, head SHA or merge base. The work is plain files in a directory that is not a git repository, so this review covers the file contents as given.
- I did not run `python3 validate.py`, because this session has no tools. The schema result below comes from reading the files, not from running the validator.

**TIER:** Standard.
- The change does not touch auth, secrets, network exposure or personal data.
- It is still not Low. It is config whose failure mode, per `publish.md:3-5`, is an outage of all publishing.

**REVIEWERS:**
- Reviewer: Claude (Opus 5.5, `claude-opus-5-5`), a fresh instance. It did not write the manifest, the original review or the suggested fix.
- Author of the fix: the unnamed reviewer of `review.md`. There are no commit trailers.
- Data handling: nothing was sent outside this session.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | **P0** | `review.md:7` (the fix `"sources": []`) against `schema/manifest.schema.json:11` (`"minItems": 1`), with consumer behavior at `publish.md:3-5` | 1. The fix is applied and merged to main. 2. `publish.py` loads the manifest and validates it, and the empty array violates `minItems: 1`. 3. The publish stops. 4. No feed page is rebuilt until someone writes a valid manifest. The fix trades one deprecated feed for an outage of every feed. | Apply the fix in a scratch copy and run `python3 validate.py manifest.json`. Today it should report a `minItems` error. With the corrected manifest below, it should print `valid (1 sources)`. |
| 2 | P1 | `review.md:7`, with the approval at `publish.md:8` | The fix drops feed-a and adds nothing in its place. The data owner approved feed-b (`https://feeds.example.test/b.xml`) as feed-a's replacement on 2026-10-20. So even if the schema allowed an empty list, the feed content would silently disappear from the site, which goes beyond the request to remove the deprecated feed. | After the fix, assert that the manifest contains exactly one source, with `id == "feed-b"` and `url == "https://feeds.example.test/b.xml"`, and no source with `id == "feed-a"`. |

The original finding itself, that feed-a is deprecated and should not be published, appears correct. `publish.md:8` records the owner-approved replacement.

**What the fix should be** (still to be checked with the validator before merging):

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
- `validate.py` and `publish.py`, to confirm the validator enforces `minItems` the way the schema says and that the publish halts as `publish.md` describes.
- Any CI check definition for the manifest.

**Unverified claim:** "Ready to apply" in `review.md` is an assertion. No validation run is shown for it.

---

**Close-out** (pending: findings are adjudicated by the author or whoever closes the change, not by this reviewer)

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | pending | — |
| 2 | pending | — |

**VERIFIED AFTER FIXES:** None yet.

**MERGE RECOMMENDATION:** **Do not merge the suggested fix as written.** It would merge a P0: a manifest that fails validation and halts all publishing.
- Apply the feed-b replacement above instead.
- Run `python3 validate.py manifest.json` and confirm it prints `valid (1 sources)`.
- Confirm that any expected CI check is present and green.
- Record the adjudication of both findings before merging.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "static: schema read, validator not run",
      "location": "review.md:7; schema/manifest.schema.json:11; publish.md:3-5",
      "scenario": "Suggested fix sets \"sources\": [], which violates the schema's minItems: 1. publish.py stops the whole publish on any validation error, so no feed page is rebuilt.",
      "fix": "Replace the feed-a entry with the owner-approved feed-b entry (id \"feed-b\", url https://feeds.example.test/b.xml) instead of emptying the list; confirm with python3 validate.py manifest.json."
    },
    {
      "severity": "P1",
      "evidence_level": "static: documented owner approval",
      "location": "review.md:7; publish.md:8",
      "scenario": "Removing feed-a without adding its approved replacement feed-b drops the feed's content from the site, beyond the requested removal of the deprecated feed.",
      "fix": "Add feed-b as the single source; test that the manifest contains feed-b and not feed-a."
    }
  ]
}
```