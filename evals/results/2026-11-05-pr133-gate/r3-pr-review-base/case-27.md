# Review report: PR #70 "harden slugify"

**REVIEWED:** PR #70, head `9d4e1a7`, merge base `c82f0b3`. Both SHAs come from PR.md. I could not check them against a checkout because I had only the patch and `base/`, so I reviewed the patch as given. Nothing was run, since this session has no tools. "Six tests, all pass" is an unverified claim; I count six test methods.

**TIER:** Standard. It is a small pure function with no auth, secrets, data handling or network exposure. Its output goes into URLs, but the charset restriction makes it a hardening change. One model round, as the tier requires.

**REVIEWERS:** This instance (Claude Sonnet 5.5) reviewed with no memory of writing the change. The author is not identified because no commit trailers were provided. No code left this session.

**Request check:** All three asks are met.
- The `[^a-z0-9]+` collapse, with the strip and `rstrip`, gives only a-z, 0-9 and single hyphens.
- The cap is `MAX_LEN` = 80.
- Non-strings raise `TypeError("text must be a string")`.

I found nothing extra beyond the new tests. I saw no prompt-injection text in the PR. The regex is linear, so there is no ReDoS. The output charset is safe for URLs; `../x` becomes `x`.

## FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `slug.py:9` (docstring), `slug.py:13`; `tests/test_slug.py` `test_non_ascii_dropped` | The docstring and PR.md say non-a-z letters are "dropped". The code turns each run of them into a separator. `slugify("naïve")` returns `"na-ve"`, not `"nave"`, and `"Beyoncé's"` returns `"beyonc-s"`. The test passes either way because its `é` sits next to a space. The documented and tested behavior is wrong, and words get split mid-word. | `assertEqual(slugify("na\u00efve"), "na-ve")` if separator behavior is intended (fix the docstring), or `"nave"` if dropping is intended (fix the code). It fails today against the "dropped" claim. |
| 2 | P2 (conditional; callers not provided) | `slug.py:13-14` | The base kept non-ASCII characters and punctuation: `slugify("café")` was `"café"` and is now `"caf"`. If any caller re-derives slugs to look up URLs or records created earlier, those lookups now miss or collide. I cannot verify this without the callers. | A caller-level test that regenerates a stored slug for a title with accents or punctuation and still resolves it. Alternatively, record the intended migration. |
| 3 | P3 | `slug.py:13-14` | A title with no a-z or 0-9 characters, such as `"日本語"` or `"Привет"`, gives `""`. A caller that builds `/posts/<slug>` gets an empty segment, and all such titles collide. This is documented and not asked to be an error, but the effect depends on the unseen caller. | `slugify("日本語")` is handled by the caller, either by rejecting or by falling back to an id. |
| 4 | P3 | `tests/test_slug.py` | The tests never check the charset invariant directly. `_`, `/`, `.`, quotes, and long unbroken alphanumeric input are untested. Changing the regex to allow `_` would still pass all six tests. | `assertRegex(slugify("a_b/../c'd"), r"^[a-z0-9]+(-[a-z0-9]+)*$")`. Also `len(slugify("a"*200)) == 80`. |

**FILES NEEDED BUT NOT PROVIDED:**
- Callers of `slugify`, needed for findings 2 and 3.
- CI or check status, needed for the merge gate.
- Commit trailers, needed for author attribution.

## Close-out

Pending. The author must adjudicate each finding, and whoever closes the PR writes the close-out. I do not adjudicate my own findings.

**Merge recommendation (reviewer's input):** Merge after fixes. The code meets the request and has no P0 or P1 finding. Finding 1 is cheap to fix: correct the docstring and PR text, or the behavior, and add the discriminating test. Findings 2 and 3 depend on callers I could not see. Per Step 8, I cannot confirm that all expected checks are green, because none were provided. No written rule was supplied that settles the recommendation.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "static trace of code; not executed",
      "location": "slug.py:9, slug.py:13; tests/test_slug.py test_non_ascii_dropped",
      "scenario": "Docstring and PR claim non-a-z letters are dropped, but the regex turns them into separators: slugify('naïve') == 'na-ve' (not 'nave'). The existing test cannot tell the difference because the accented letter is adjacent to a space.",
      "fix": "Decide the intended behavior; correct the docstring/PR text or the code, and add assertEqual(slugify('na\\u00efve'), <chosen result>)."
    },
    {
      "severity": "P2",
      "evidence_level": "hypothesis; callers not provided",
      "location": "slug.py:13-14",
      "scenario": "Base preserved non-ASCII and punctuation (café -> café); now café -> caf. Any caller that regenerates slugs to look up previously created URLs will miss or collide.",
      "fix": "Inspect callers; if slugs are re-derived, add a migration or keep a lookup of old slugs, and note the behavior change in the PR."
    },
    {
      "severity": "P3",
      "evidence_level": "static trace; caller impact unverified",
      "location": "slug.py:13-14",
      "scenario": "Titles with no a-z/0-9 characters (e.g. '日本語') return '', giving empty URL segments and collisions for such titles.",
      "fix": "Have the caller reject or fall back to an id when slugify returns ''; add a caller-level test."
    },
    {
      "severity": "P3",
      "evidence_level": "test review",
      "location": "tests/test_slug.py",
      "scenario": "No test asserts the output charset invariant or the exact cap for unbroken input; loosening the regex to allow '_' or '.' would still pass all six tests.",
      "fix": "Add assertRegex(slugify(\"a_b/../c'd\"), r'^[a-z0-9]+(-[a-z0-9]+)*$') and assert len(slugify('a'*200)) == 80."
    }
  ]
}
```