# PR #70 review: harden slugify

**Review report**

**REVIEWED:** PR #70, head `9d4e1a7`, merge base `c82f0b3`. Both SHAs come from PR.md. I had no tools, so I could not check out the head. I reviewed the supplied `change.patch` against `base/slug.py` and could not confirm the patch matches `9d4e1a7` byte for byte. If the head has moved since `9d4e1a7`, the newer commits are not covered.

**TIER:** Standard. This is an ordinary code change to a URL helper. It touches no auth, secrets, network exposure, personal-data handling or dependencies, so the supply-chain lens does not apply. One round is required and this is that round.

**DATA (Step 3):** Nothing left this session. No subagent or external endpoint was used.

**REVIEWERS:** Reviewed by this instance (Claude Opus 5.5, `claude-opus-5-5`), which did not write or help write the change. No commit trailers were provided, so the author is unknown.

**Coverage and claims:**
- **Not run.** "Six tests, all pass" is the author's claim. I traced each test by hand instead:
  - `test_length_cap_never_ends_in_hyphen` does exercise the `rstrip`: 16 × `"word-"` = 80 characters, so the cut lands on a hyphen and the result is 79 characters.
  - The other five tests' expected values match the code as written.
- **Request coverage:** The change meets the request. Output is only a-z, 0-9 and single hyphens. It is capped at 80 characters, with no leading or trailing hyphen. Non-strings raise `TypeError`. Nothing outside the request was added.
- **Injection check (Step 5.4):** The PR contains no text addressed to the reviewer.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `slug.py:14` (`re.sub(r"[^a-z0-9]+", "-", …)`); docstring `slug.py:10`; PR.md | The docstring and PR say letters outside a-z are "dropped". In fact the regex replaces them with a hyphen, so they split words. `slugify("Résumé tips")` returns `"r-sum-tips"` and `slugify("naïve")` returns `"na-ve"`, not `"rsum-tips"` / `"nave"`. `test_non_ascii_dropped` puts `é` at the end of a word, so it cannot tell "dropped" from "replaced by a separator". Callers relying on the documented contract get fragmented slugs for most non-English titles. Fix either the code (delete non-ASCII letters before splitting) or the docs. | `assertEqual(slugify("naïve"), "nave")`, or, if the current behavior is intended, `assertEqual(slugify("naïve"), "na-ve")` with the docstring corrected. Today the first fails and the docstring is wrong. |
| 2 | P3 | `slug.py:14` (`text.lower()` before the ASCII filter) | `str.lower()` maps some non-ASCII characters to ASCII, contradicting "not transliterated". The Kelvin sign `"\u212a".lower()` is `"k"`, so `slugify("\u212aelvin")` returns `"kelvin"`. `"İstanbul"` lowers to `"i̇stanbul"` (i + U+0307), which gives `"i-stanbul"`. Output stays within a-z, 0-9 and hyphens, so this is not a safety break. It does contradict the documented contract and produces odd splits. Filtering to ASCII before lowering, or matching `[^A-Za-z0-9]` and lowering afterwards, makes the behavior match the docs. | `assertEqual(slugify("\u212a"), "")` and `assertEqual(slugify("İstanbul"), "stanbul")`, or whatever the documented rule says. Both differ today. |
| 3 | P2 (depends on unseen callers) | `slug.py:14–15` (empty result; docstring line 11) | Any title with no a-z or 0-9 characters returns `""`. Examples: `"日本語"`, `"Привет"`, `"!!!"`. Used directly "when creating URLs", these titles all map to the same empty slug. That can give paths like `/posts/` or slug collisions between unrelated items. The function documents the empty result, but the request is "safe for user-supplied titles", and I cannot see whether callers handle `""`. | A caller-level test: create two items titled `"日本語"` and `"Привет"`, then assert distinct, non-empty URLs. Or a unit test asserting `slugify` raises `ValueError` / returns a fallback when the result is empty, if that is the chosen contract. |

**FILES NEEDED BUT NOT PROVIDED:**
- **Callers of `slugify`:** needed to settle finding 3. They would also show whether stored or regenerated slugs change for existing titles. Base kept punctuation, the new code strips it, so links built from regenerated slugs could break.
- **CI and test-runner config:** `tests/` has no `__init__.py` and imports `from slug import …` from the repo root. Whether the tests are even collected and imported depends on how CI invokes them. Plain `python -m unittest` discovery from the root will not recurse into a non-package `tests/` directory.
- **Check results for `9d4e1a7`.**

---

**Close-out** (pending; the author adjudicates, not the reviewer)

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | Pending author | |
| 2 | Pending author | |
| 3 | Pending author | |

**VERIFIED AFTER FIXES:** None yet. Any fix should be verified by a targeted read of its diff plus its regression test, not another full round.

**MERGE RECOMMENDATION:** Merge after fixes, but not yet. No P0 or P1 was found. Findings 1–3 are P2/P3 and can be fixed or deferred with linked issues. Merge stays blocked until:
- every finding has a written decision;
- CI checks for `9d4e1a7` are shown present and green, with the test suite actually collected;
- the owner decides the empty-slug contract (finding 3).

```json
{
  "verdict": "merge after fixes (blocked pending adjudication, green checks for 9d4e1a7, and owner decision on empty-slug contract)",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "static trace of code; not executed",
      "location": "slug.py:14 (re.sub) and docstring slug.py:10",
      "scenario": "Non-ASCII letters are replaced by a hyphen rather than dropped as documented: slugify('naïve') -> 'na-ve', slugify('Résumé tips') -> 'r-sum-tips'. test_non_ascii_dropped only covers an end-of-word case and cannot distinguish the two behaviors.",
      "fix": "Delete non-ASCII characters before replacing separators (or correct the docstring/PR to say they act as word separators) and add a mid-word test such as slugify('naïve')."
    },
    {
      "severity": "P3",
      "evidence_level": "static trace of documented str.lower() Unicode behavior; not executed",
      "location": "slug.py:14 (text.lower() before ASCII filter)",
      "scenario": "str.lower() maps some non-ASCII characters to ASCII: Kelvin sign U+212A -> 'k', so slugify('\\u212aelvin') == 'kelvin'; 'İstanbul' -> 'i-stanbul'. Contradicts 'not transliterated'; output remains within the allowed alphabet.",
      "fix": "Filter on [^A-Za-z0-9] (ASCII) before lowercasing, and add tests for U+212A and U+0130."
    },
    {
      "severity": "P2",
      "evidence_level": "inferred; callers not provided",
      "location": "slug.py:14-15 (empty result, documented in docstring line 11)",
      "scenario": "Titles with no a-z/0-9 characters ('日本語', 'Привет', '!!!') all return '', so URLs built from them can be empty paths or collide.",
      "fix": "Owner decides the contract: raise ValueError on empty result or have callers supply a fallback/unique suffix; add a test for the chosen behavior."
    }
  ]
}
```