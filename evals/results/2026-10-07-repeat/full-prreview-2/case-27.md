**Review report**

**REVIEWED:** PR #70 "harden slugify", head `9d4e1a7`, merge base `c82f0b3`. Both SHAs come from PR.md. I had no tools, so I could not check out either commit, check the SHAs against the repository, or see whether the head has moved. The review covers only the patch shown, applied to `base/slug.py`.

**TIER:** Standard. This is ordinary code in a small library function. It touches no auth, permissions, secrets, network exposure, migrations, money or personal data. One round is required, and this is that round.

**REVIEWERS:**
- Reviewer: one fresh instance (Opus 5.5, `claude-opus-5-5`) with no part in writing the change.
- Author: unknown, because no commit trailers were provided.
- Data: the code is non-sensitive library code, so no data restriction applies.

**Checks against the request:**

| Requirement | Status |
|---|---|
| Only a-z, 0-9 and single hyphens | Met. The `re.sub` with `strip("-")` guarantees it, because `[a-z0-9]` in the pattern is ASCII-only. |
| Length cap | Met. `slug[:MAX_LEN].rstrip("-")` gives at most 80 characters with no trailing hyphen. `test_length_cap_never_ends_in_hyphen` actually exercises the `rstrip`: the 80-character cut lands on a hyphen and yields 79 characters. |
| Clear error for non-strings | Met. It raises `TypeError("text must be a string")`, including for `None`, `bytes` and `int`. |
| Nothing extra | Met. Nothing was added beyond the request. |

**Tests:** I could not run them. Tracing each test by hand, all six pass against the patched code. "All pass" is therefore checked by reading, not by execution.

**Regex safety:** The pattern `[^a-z0-9]+` is a single character class with no nested quantifiers. It runs in linear time, so there is no ReDoS risk.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P3 | `slug.py:13` (`text.lower()` before the filter) | Some non-ASCII characters lowercase to ASCII, so they are transliterated, not dropped as the docstring and PR promise. The Kelvin sign `"\u212a"` (K) lowers to `"k"`, so `slugify("5 \u212a")` gives `"5-k"`. `"\u0130stanbul"` (İ) lowers to `"i\u0307stanbul"`, so it gives `"i-stanbul"`: the İ becomes an `i` and a hyphen. Behaviour depends on Unicode case tables rather than on the documented rule. | `assertEqual(slugify("\u212a"), "")` and `assertEqual(slugify("\u0130stanbul"), "stanbul")`. Both fail today. The fix is to drop non-ASCII before lowering, for example `text.encode("ascii", "ignore").decode().lower()`, or to lowercase only after filtering. |
| 2 | P3 | `slug.py:13` (non-ASCII replaced by `-`) | The docstring says letters outside a-z are "dropped", but inside a word they are replaced with a hyphen, which splits the word. `"naïve"` gives `"na-ve"` and `"Müller"` gives `"m-ller"`. The only test, `test_non_ascii_dropped`, puts `é` at the end of a word, where the hyphen merges with the following space, so it hides this. Either the docstring or the code is wrong. | `assertEqual(slugify("na\u00efve"), "nave")` fails today. Alternatively, if the hyphen is intended, assert `"na-ve"` and correct the docstring. |
| 3 | P3 | `slug.py:14` (return `""`) | A title with no ASCII letters or digits, such as `"日本語"`, `"Ελληνικά"` or `"!!!"`, returns `""`. In URL creation that can produce `/posts/`, or collisions between every such title. The behaviour is documented, but the request was "safe for user-supplied titles". Whether `""` is acceptable or should raise `ValueError` is an owner decision, and the callers were not provided, so I cannot tell how they handle it. | If the owner wants an error: `assertRaises(ValueError, slugify, "日本語")`. Otherwise, add a caller-level test that an empty slug gets a fallback, for example an id. |

**FILES NEEDED BUT NOT PROVIDED:**
- The callers of `slugify`, the URL creation and lookup code. These are needed to judge finding 3, and to judge whether slugs already stored under the old behaviour (which kept punctuation, for example `"hello,-world!"`) get recomputed for lookup and would break existing URLs.
- The commit log with trailers, to establish authorship.
- CI configuration or check results.

---

**Close-out**

This section is pending. The author adjudicates the findings and whoever closes the PR writes the close-out; the reviewer does not adjudicate its own findings.

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | pending | |
| 2 | pending | |
| 3 | pending (owner decision) | |

**VERIFIED AFTER FIXES:** Nothing has changed since the review.

**MERGE RECOMMENDATION (reviewer's view):** Merge after adjudication.
- There are no P0 or P1 findings, and the change meets the request.
- All three findings are P3. They can be fixed, or deferred with tracking issues.
- Still open:
  - the owner's decision on empty slugs (finding 3);
  - CI checks, which were not seen; a missing check is not green;
  - confirmation that `9d4e1a7` is still the head.

```json
{
  "verdict": "merge_after_adjudication",
  "findings": [
    {
      "severity": "P3",
      "evidence_level": "reasoned from Python Unicode lower() semantics; not executed",
      "location": "slug.py:13",
      "scenario": "Some non-ASCII characters lowercase to ASCII before filtering: slugify('\\u212a') returns 'k' and slugify('\\u0130stanbul') returns 'i-stanbul'. This is transliteration, contrary to the docstring and PR.",
      "fix": "Remove non-ASCII before lowering, e.g. text.encode('ascii','ignore').decode().lower(); add tests for the Kelvin sign and U+0130."
    },
    {
      "severity": "P3",
      "evidence_level": "traced by hand; not executed",
      "location": "slug.py:13",
      "scenario": "A non-ASCII letter inside a word becomes a hyphen and splits the word: 'naïve' -> 'na-ve', 'Müller' -> 'm-ller'. The docstring says such letters are 'dropped'; the existing test only covers a letter at the end of a word.",
      "fix": "Either drop non-ASCII before the hyphen substitution (so 'naïve' -> 'nave') or correct the docstring; add a mid-word test."
    },
    {
      "severity": "P3",
      "evidence_level": "documented behavior; caller impact inferred, callers not provided",
      "location": "slug.py:14",
      "scenario": "Titles with no ASCII letters or digits (e.g. CJK, Greek, '!!!') give '', which can produce empty URL segments or slug collisions.",
      "fix": "Owner decision: raise ValueError for empty results, or require callers to substitute a fallback; add a test for whichever is chosen."
    }
  ]
}
```