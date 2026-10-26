# pr-review: suggested fix to `manifest.json` (from `review.md`, 2026-10-22)

**Short answer: no, it is not safe to apply as written.** `"sources": []` fails the manifest schema (`minItems: 1`). Per `publish.md`, any validation error stops the whole publish, so applying it would stop every feed page from rebuilding. The fix the data owner already approved is to replace feed-a with feed-b, not to empty the list.

## Review report

**REVIEWED:** The suggested one-line fix in `review.md` (Finding 1), applied to `work/manifest.json`. No PR, head SHA or merge base was provided, and this is not a git repository, so **no SHAs can be recorded**. This review covers only the file contents shown in the inputs. If the manifest or schema differ at the commit where the fix would land, this review does not cover that commit.

**TIER:** Standard. It is a config change that does not touch auth, secrets, network exposure or personal data, which would normally be Low. But it controls whether *any* feed publishes, so a bad value is an outage of all publishing. I took the higher tier as Step 2 directs when unsure. One round is required, and this report is that round.

**DATA HANDLING (Step 3):** Nothing was sent outside this session. No subagent or external endpoint was used.

**REVIEWERS:**
- Reviewer: this session (Claude, `claude-opus-5-5`), independent of the change. It did not write the manifest or the suggested fix.
- Author of the suggested fix: the unnamed reviewer of `review.md` (2026-10-22). There are no commit trailers to read authorship from.

**METHOD AND LIMITS:**
- I had no tools in this session, so I did **not** run `python3 validate.py`.
- I checked the fix statically against its consumer, `schema/manifest.schema.json`, using the behavior described in `publish.md`.
- "Ready to apply" in `review.md` is an author's claim. It is not addressed to this reviewer and is not an injection. It is treated as unverified and is contradicted below.

### FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | **P0** | `review.md` suggested fix, applied to `manifest.json:2` (`"sources"`), checked against `schema/manifest.schema.json` (`properties.sources.minItems: 1`) | 1. The fix sets `"sources": []`, which is an array of length 0.<br>2. The schema requires `minItems: 1`, so validation fails.<br>3. `publish.md` says `publish.py` runs on every merge to main and "stops the whole publish on any validation error: no feed page is rebuilt".<br>4. The first merge after applying the fix halts publishing for **every** feed until someone corrects the manifest.<br>Separately, even if the schema allowed it, removing feed-a with nothing in its place drops the feed. That contradicts the data owner's approved replacement (`publish.md`, 2026-10-20: feed-b at `https://feeds.example.test/b.xml`). | Add a CI check that runs `python3 validate.py manifest.json` on every manifest change and requires output `valid (N sources)` with N ≥ 1. Add a fixture test: validating `{"sources": []}` must fail with a `minItems` error. With the suggested fix applied, the manifest check fails today. With the corrected fix below, it passes. |

**Corrected fix (checked against the consumer, the schema; not run):**

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

Schema check, field by field:
- `sources` is present, as `required` demands.
- `sources` has 1 item, which satisfies `minItems: 1`.
- The item has `id` and `url`, as `required` demands.
- Both are strings, as `type: string` demands.

Status: **verified against the schema by reading only.** Execution through `validate.py` is UNVERIFIED because I could not run it.

Caveats on the corrected fix:
- The id `feed-b` is inferred from the owner's wording "feed-b at …". Confirm it matches whatever id `publish.py` or the feed pages expect.
- The URL comes from `publish.md`. I did not visit it, by design.

**FILES NEEDED BUT NOT PROVIDED:**
- `validate.py`, to confirm it enforces the schema exactly, including `minItems`.
- `publish.py`, to confirm the stop-on-error behavior described in `publish.md` and whether feed ids are referenced elsewhere.
- The PR or commit the fix would land on, with head and merge-base SHAs.

## Close-out

*Not written by this reviewer. Per the skill, a reviewer never adjudicates its own findings. The author or the person closing the change fills this in.*

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | *pending* | P0, so it cannot be Deferred. It must be Accepted (fix plus validator check, with fix commit named) or Rejected with evidence. |

**VERIFIED AFTER FIXES:** Nothing yet. When the corrected fix lands, verify it with a targeted read of that diff plus a passing `python3 validate.py manifest.json` (expected: `valid (1 sources)`). No further full review round is needed.

**MERGE RECOMMENDATION:** **Do not apply the suggested fix as written.**
- It fails the schema's `"minItems": 1` on `sources`.
- Per `publish.md`, a validation error means "no feed page is rebuilt until the manifest validates again".
- Step 8 requires "no unresolved blocker remains", and Finding 1 is an unresolved P0 blocker.
- Instead, apply the feed-b replacement after confirming its id, and run the validator before merging.
- A green validator check is required. A missing check is not green.

```json
{
  "verdict": "do_not_apply",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "static check against schema/manifest.schema.json and publish.md; validator not executed (no tools)",
      "location": "manifest.json:2 (sources) via review.md suggested fix; schema/manifest.schema.json properties.sources.minItems",
      "scenario": "Suggested fix sets \"sources\": []; schema requires minItems 1, so validation fails; publish.py stops the whole publish on any validation error, so no feed page is rebuilt after the next merge to main. It also drops feed-a without the owner-approved replacement (feed-b, 2026-10-20).",
      "fix": "Replace feed-a with {\"id\": \"feed-b\", \"url\": \"https://feeds.example.test/b.xml\"} (confirm id matches publish.py expectations), and gate merges on `python3 validate.py manifest.json` returning `valid (N sources)` with N >= 1."
    }
  ]
}
```