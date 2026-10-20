# Review report: PR #70, "harden slugify"

**REVIEWED:** PR #70, head `9d4e1a7`, merge base `c82f0b3`. Both SHAs come from PR.md as abbreviated hashes. I had no checkout to confirm them against. The review covers only `change.patch` applied to `base/slug.py`.

**TIER:** Standard. This is an ordinary code change to a library function that builds URL slugs. It touches no auth, permissions, secrets, network exposure, migrations, money or personal data. One round is required, and this report is that round.

**REVIEWERS:** Claude (Opus 5.5, `claude-opus-5-5`), a fresh instance in this session that did not write the change. The author is unknown because no commit trailers were provided.

**Limits of this review:** There were no tools in this session. I did not run the six tests. "Six tests, all pass" is the author's claim and is unverified. Every behaviour below comes from reading the code against Python's `str.lower` and `re` semantics.

**Against the request:**
- **Only a-z, 0-9 and single hyphens:** met. `[^a-z0-9]+` collapses each run into one hyphen, `strip("-")` trims the ends, and `rstrip("-")` after truncation stops a trailing hyphen.
- **Length cap:** met (`MAX_LEN = 80`). The cap test does exercise the `rstrip`, because 16 × `"word-"` puts a hyphen at index 79.
- **Clear TypeError for non-strings:** met.
- **Scope:** nothing extra was added.

## FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P3 | `slug.py:13` (`text.lower()` before the ASCII filter) | `str.lower()` maps some non-ASCII letters into ASCII before filtering, which contradicts the docstring's "letters outside a-z … are dropped". `slugify("\u212a")` (Kelvin sign) returns `"k"`, not `""`. `slugify("İstanbul")` lowers to `"i\u0307stanbul"` and returns `"i-stanbul"`, which splits the word. The output still meets the character-set rule, so this is wrong behaviour and docs, not a safety problem. | `assertEqual(slugify("\u212a"), "")` and `assertEqual(slugify("İstanbul"), "stanbul")`. Both fail today and pass if non-`[A-Za-z0-9]` is replaced before lowering, e.g. `re.sub(r"[^A-Za-z0-9]+", "-", text).lower()`. |
| 2 | P3 | `slug.py:9` (docstring) and `tests/test_slug.py:21` | The docstring and PR.md say non-ASCII letters are "dropped", but they are actually *replaced by a hyphen*. `slugify("naïve")` returns `"na-ve"`, not `"nave"`. The only test puts the non-ASCII letter at a word boundary (`"café au lait"`), where both readings give the same answer, so the test cannot tell them apart. | `assertEqual(slugify("naïve"), "na-ve")`, with the docstring changed to say "replaced by a hyphen". Alternatively choose `"nave"`, but either way pin the mid-word case. |
| 3 | P2 | `slug.py:13-14` (callers not provided) | A title made only of non-Latin script, such as `"Привет мир"` or `"東京"`, returns `""`. The docstring documents this, but for a function used "when creating URLs" from user-supplied titles, any caller that builds `/posts/<slug>` without its own fallback will produce an empty path segment, and those slugs will collide with each other. Whether this bites depends on callers I could not see. | A caller-level test: create two items titled `"東京"` and `"Привет"` and assert their URLs differ and are non-empty. Or, if the library should own it, `assertNotEqual(slugify("東京"), "")` after adding a fallback. |

**Note (not a finding):** `tests/test_slug.py` does `from slug import slugify` with no `tests/__init__.py` and no shown pytest/path config. Whether the tests import cleanly depends on the runner and the working directory. This is part of why "all pass" is unverified.

**FILES NEEDED BUT NOT PROVIDED:** the callers of `slugify` (needed to settle #3), the CI/check configuration and its results, test runner config (`pyproject.toml`/`setup.cfg`/`pytest.ini`), and the commit log with trailers (for authorship).

## Close-out

Pending. The author must adjudicate #1–#3; a reviewer does not adjudicate its own findings. All three are P2/P3, so each can be Accepted, Deferred with a tracking issue, or Rejected with evidence.

**ADJUDICATION:** not yet written.

**VERIFIED AFTER FIXES:** none yet.

**MERGE RECOMMENDATION:** do not merge yet. There is no blocker in the code: no P0/P1, and the request is met. Two things are still open:
1. Written decisions on findings #1–#3.
2. Evidence that the expected checks are present and green. I have seen no check results, and a missing check is not green. Someone needs to actually run the six tests.

Once both are done, this is a merge.

```json
{
  "verdict": "do not merge yet: no P0/P1; pending written adjudication of 3 P2/P3 findings and evidence of green checks (tests not run in this review)",
  "findings": [
    {
      "severity": "P3",
      "evidence_level": "code reading against documented Python str.lower semantics; not executed",
      "location": "slug.py:13",
      "scenario": "str.lower() runs before the ASCII filter, so slugify('\\u212a') (Kelvin sign) returns 'k' and slugify('İstanbul') returns 'i-stanbul', contradicting the docstring that letters outside a-z are dropped",
      "fix": "Filter before lowering: re.sub(r'[^A-Za-z0-9]+', '-', text).lower(); add tests for '\\u212a' -> '' and 'İstanbul' -> 'stanbul'"
    },
    {
      "severity": "P3",
      "evidence_level": "code reading; not executed",
      "location": "slug.py:9 and tests/test_slug.py:21",
      "scenario": "Non-ASCII letters are replaced by a hyphen, not dropped: slugify('naïve') returns 'na-ve'. The only test places the letter at a word boundary, so it cannot distinguish the documented behaviour from the actual one",
      "fix": "Correct the docstring (and PR text) to 'replaced by a hyphen', or change behaviour; add a mid-word test such as slugify('naïve')"
    },
    {
      "severity": "P2",
      "evidence_level": "inferred; callers not provided",
      "location": "slug.py:13-14",
      "scenario": "Titles entirely in non-Latin script ('Привет мир', '東京') return ''. Callers that build URLs from the slug without a fallback get empty path segments and collisions between items",
      "fix": "Confirm callers handle '' (e.g. fall back to an ID); otherwise add a fallback and a caller-level test that two such titles get distinct, non-empty URLs"
    }
  ]
}
```