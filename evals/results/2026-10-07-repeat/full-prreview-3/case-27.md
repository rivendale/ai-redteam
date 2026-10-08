**Review report**

**REVIEWED:** PR #70 "harden slugify". Head `9d4e1a7`, merge base `c82f0b3`. Both SHAs are as stated in PR.md and are unverified.
- I had no tools, so there was no worktree checkout and no test run.
- I reviewed the supplied `change.patch` against `base/slug.py`.
- If the head has moved past `9d4e1a7`, the later commits were not reviewed.

**TIER:** Standard. The change is a pure string function used to build URLs. It does not touch auth, secrets, migrations, money or personal data, and the context gives the stakes as standard. That means one model round, and this report is that round.

**REVIEWERS:**
- Reviewer: a fresh instance of claude-opus-5-5 with no part in writing the change.
- Author: unknown. No commit trailers were provided.
- Data: the code carries no personal data, so this endpoint is acceptable under Step 3.

**What I checked (traced by hand, not run):**
- **Request coverage.** The request asks for four things, and the code delivers all four:
  - Output contains only a-z, 0-9 and hyphens. The regex `[^a-z0-9]+` uses an ASCII literal range, and `.lower()` runs first.
  - Hyphens are single. The `+` collapses each run into one hyphen.
  - The length is capped, and the slug never starts or ends with a hyphen. `strip("-")` runs, then the 80-character slice, then `rstrip("-")`.
  - Non-strings get a clear error. `isinstance(str)` raises TypeError for `None`, bytes and ints.
- **Nothing extra.** The change adds nothing beyond the request.
- **Tests.** I traced all six tests and each one should pass:
  - `"Hello, World!"` gives `hello-world`.
  - `"  a   b -- c  "` gives `a-b-c`.
  - `""` and `"!!!"` both give `""`.
  - `"word " * 40` slices to 80 characters ending in `-`, so `rstrip` gives 79 characters. The test genuinely exercises the trailing-hyphen path.
  - `café au lait` gives `caf-au-lait`.
  - `None` raises TypeError.
- **ReDoS.** None. The pattern is a single character class with `+`, so matching is linear.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P3 | `slug.py:9`, `slug.py:13`; `tests/test_slug.py:21-22` | The docstring and PR say non-ASCII letters are "dropped", but the code replaces each with a word separator. `slugify("naïve")` gives `"na-ve"`, not `"nave"`. `slugify("Müller")` gives `"m-ller"`. The only test (`café au lait`) puts the non-ASCII letter at a word end, where "dropped" and "replaced by a hyphen" give the same result, so the test cannot tell the two apart. Either the docstring or the code is wrong. The author must pick one. | `assertEqual(slugify("naïve"), "nave")` if "dropped" is intended. Otherwise `assertEqual(slugify("naïve"), "na-ve")`, with the docstring changed to "treated as separators". |
| 2 | P3 | `slug.py:13` (`text.lower()` before the ASCII filter) | `str.lower()` maps some non-ASCII characters to ASCII, which contradicts "not transliterated". `"\u212Aelvin"` (Kelvin sign) gives `"kelvin"`. `"İstanbul"` lowercases to `"i\u0307stanbul"` and so gives `"i-stanbul"`, with a spurious hyphen. The output is still valid a-z/0-9/hyphen, so this is a contract inaccuracy, not a safety hole. | `assertEqual(slugify("İstanbul"), "stanbul")` (or whatever result the author picks under finding 1). Fix it by filtering to ASCII before lowercasing, e.g. `re.sub(r"[^A-Za-z0-9]+", "-", text).lower()`. |
| 3 | P2 (inferred: callers not provided) | `slug.py:13-14` | For user-supplied titles, any title with no a-z/0-9 characters returns `""`. Examples: `"日本語"`, `"Привет"`, `"!!!"`. If a caller builds `/posts/<slug>` without a fallback, every such title maps to the same empty path, which causes a collision or a bad URL. The docstring documents this, so it may be the caller's job, but nothing in the PR shows that any caller handles it. | Caller-level: creating two items titled `"Привет"` and `"日本語"` yields two distinct, non-empty URLs. Library alternative: raise `ValueError` on an empty result and assert it. |

**FILES NEEDED BUT NOT PROVIDED:**
- The callers of `slugify`. These are needed to confirm finding 3, and to check whether existing stored slugs or URLs from the old function (which kept punctuation and did not strip) will now differ. That would matter for redirects and uniqueness.
- CI configuration and check results.

---

**Close-out:** Not written. Per the skill, the reviewer does not adjudicate its own findings. The author must give each finding a written decision: Accepted with a regression test, Deferred with an issue link (all three findings are P2/P3, so deferral is allowed), or Rejected with evidence. The decision must be posted on the PR against `9d4e1a7`.

**Merge recommendation (provisional):** I found no blockers, so the verdict is merge after adjudication. Three things are still open:
- written decisions on findings 1–3;
- the CI checks, which are not shown, and a missing check is not green;
- confirmation that the stated head is still `9d4e1a7`.

```json
{
  "verdict": "merge after adjudication (no P0/P1; three P2/P3 findings need written decisions; CI checks not shown; tests traced by hand, not run)",
  "findings": [
    {
      "severity": "P3",
      "evidence_level": "traced by reading code (not executed)",
      "location": "slug.py:9, slug.py:13; tests/test_slug.py:21-22",
      "scenario": "Docstring/PR say non-ASCII letters are 'dropped', but the regex replaces them with a hyphen: slugify('naïve') -> 'na-ve', slugify('Müller') -> 'm-ller'. The only test uses a word-final 'é', where both behaviours coincide, so it cannot detect the mismatch.",
      "fix": "Decide the intended behaviour. To drop: remove non-ASCII before the separator substitution and add assertEqual(slugify('naïve'), 'nave'). Otherwise change the docstring to 'treated as separators' and add assertEqual(slugify('naïve'), 'na-ve')."
    },
    {
      "severity": "P3",
      "evidence_level": "traced by reading code (relies on Python str.lower Unicode mappings; not executed)",
      "location": "slug.py:13",
      "scenario": "lower() runs before the ASCII filter, so some non-ASCII characters become ASCII: KELVIN SIGN U+212A -> 'k' (transliteration, contrary to the docstring), and 'İstanbul' -> 'i\\u0307stanbul' -> 'i-stanbul' (spurious hyphen).",
      "fix": "Filter on [^A-Za-z0-9]+ before lowercasing, e.g. re.sub(r'[^A-Za-z0-9]+', '-', text).lower().strip('-'); add a test for 'İstanbul'."
    },
    {
      "severity": "P2",
      "evidence_level": "inferred (callers not provided)",
      "location": "slug.py:13-14",
      "scenario": "Any user title with no a-z/0-9 characters (e.g. '日本語', 'Привет', '!!!') yields ''. A caller that builds /posts/<slug> without a fallback gets an empty path, and distinct titles collide.",
      "fix": "Either raise ValueError on an empty result in slugify, or require and test a caller-side fallback (e.g. an id-based slug); add a test that two non-Latin titles produce distinct, non-empty URLs."
    }
  ]
}
```