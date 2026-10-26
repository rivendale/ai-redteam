# PR #70 review: harden slugify

**Review report**

**REVIEWED:** PR #70, head `9d4e1a7`, merge base `c82f0b3`. These SHAs come from PR.md. I had no repository, so I could not check them against git. I reviewed `change.patch` as applied to `base/slug.py`, plus the new `tests/test_slug.py`. Any commits after `9d4e1a7` are not covered.

**TIER:** Standard. This is an ordinary library change that builds URL slugs. It does not touch auth, permissions, secrets, network exposure, migrations, money or personal-data handling. The context also states the stakes as standard. The dependency lens does not apply, since the change uses only the standard-library `re` module. The runtime/TLS lens does not apply either.

**DATA / ENDPOINT:** The code carries no personal data and nothing was sent outside this session.

**REVIEWERS:** One round by this instance (Claude Opus 5.5, model `claude-opus-5-5`). This session did not write or help write the change. The author is unknown: no commits or `Co-Authored-By` trailers were provided.

**EXECUTION:** Nothing was run, because this session has no tools. The PR says "six tests, all pass", which I treat as a claim. I traced each test by hand against the patched code:

- `test_basic`: `"hello, world!"` becomes `"hello-world"`.
- `test_collapses_and_strips`: `"-a-b-c-"` is stripped to `"a-b-c"`.
- `test_empty_and_symbols`: `""` stays `""`, and `"!!!"` becomes `"-"`, then `""`.
- `test_length_cap_never_ends_in_hyphen`: 199 characters are cut to 80, which ends in `-`. `rstrip` then gives 79 characters.
- `test_non_ascii_dropped`: gives `"caf-au-lait"`.
- `test_type_error`: raises `TypeError`.

All six should pass on this reading, but none was executed.

**Request coverage:**
- **a-z, 0-9 and single hyphens:** met. `[^a-z0-9]+` is an ASCII range applied after `lower()`. A whole run of other characters becomes one hyphen. Leading and trailing hyphens are stripped, and truncation followed by `rstrip("-")` cannot create `--`.
- **Length cap:** met (`MAX_LEN = 80`).
- **Clear error for non-strings:** met (`TypeError("text must be a string")`).
- **Nothing extra:** confirmed.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P3 | `slug.py:9`, `slug.py:13` | The docstring and PR say letters outside a-z are "dropped". In fact they are replaced by a hyphen, and some non-ASCII letters lowercase *into* ASCII. `slugify("naïve")` returns `"na-ve"`, not `"nave"`. `slugify("İstanbul")` returns `"i-stanbul"`, because `"İ".lower()` is `"i\u0307"`. `slugify("\u212a")` (Kelvin sign) returns `"k"`. The output is still within a-z/0-9/hyphen, so the safety goal holds, but the documented behavior is wrong. The existing test (`tests/test_slug.py:21`) only passes because `é` sits at a word boundary. | `assertEqual(slugify("naïve"), <documented result>)`: this fails today against "dropped" semantics. Fix either the docstring ("replaced by a hyphen") or the code (strip non-ASCII before substituting), then pin the result with tests for `"naïve"` and `"İstanbul"`. |
| 2 | P3 | `slug.py:13-14` | A title made entirely of non-ASCII letters returns `""`, for example `slugify("Привет")` or `slugify("日本語")`. Two such titles give the same empty slug. If a caller builds `/posts/<slug>`, it gets an empty path segment or a collision. This is documented behavior. Whether it causes harm depends on callers I did not see. | Add a caller-level test: create two items titled `"Привет"` and `"日本語"`, then assert they get distinct, non-empty URLs (or a clear rejection). |
| 3 | P3 | `tests/test_slug.py:16-19` | The PR promises that output never *starts* with a hyphen and never contains `--`. The length test checks neither. A future change that truncates before stripping, or drops `strip("-")`, could still pass the suite. | `s = slugify("-" + "ab " * 50)`, then assert `not s.startswith("-")`, `"--" not in s`, `len(s) <= MAX_LEN`, and `re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", s)`. Also add a boundary case where character 80 is a letter. |

No PR text addresses the reviewer.

**FILES NEEDED BUT NOT PROVIDED:**
- The callers of `slugify`, needed to judge finding 2 and how empty or colliding slugs are handled.
- The commit log with trailers, needed for authorship.
- The git repository, needed to verify the head and base SHAs.
- CI configuration and check results.

**Close-out**

Not written. The author adjudicates these findings, and a reviewer does not adjudicate its own.

**ADJUDICATION:** pending (findings 1–3).

**VERIFIED AFTER FIXES:** none yet.

**MERGE RECOMMENDATION (reviewer's input to the close-out):** No P0 or P1 findings. The change meets the request. Merge once all three P3 findings have a written decision (accepted with a test, deferred with an issue link, or rejected with evidence) and the expected CI checks are present and green. No check results were provided, so none can be counted as green.

```json
{
  "verdict": "no blocking findings; merge only after written adjudication of findings 1-3 and green CI checks (none provided)",
  "findings": [
    {
      "severity": "P3",
      "evidence_level": "static trace, not executed",
      "location": "slug.py:9, slug.py:13",
      "scenario": "Docstring says non a-z letters are 'dropped', but they are replaced by a hyphen and some lowercase into ASCII: slugify('naïve') -> 'na-ve', slugify('İstanbul') -> 'i-stanbul', slugify('\\u212a') -> 'k'. Output stays in a-z/0-9/hyphen; the documented behavior is wrong. The existing test passes only because é is at a word boundary.",
      "fix": "Correct the docstring to 'replaced by a hyphen', or strip non-ASCII before substitution; add tests for 'naïve' and 'İstanbul' pinning the documented result."
    },
    {
      "severity": "P3",
      "evidence_level": "static trace; caller impact unverified (callers not provided)",
      "location": "slug.py:13-14",
      "scenario": "Titles made entirely of non-ASCII letters ('Привет', '日本語') all return '', giving empty URL segments or collisions if the caller does not handle it.",
      "fix": "Have callers reject or fall back (e.g. an id-based slug) when slugify returns ''; add a caller-level test with two non-ASCII titles."
    },
    {
      "severity": "P3",
      "evidence_level": "static read of tests",
      "location": "tests/test_slug.py:16-19",
      "scenario": "Tests do not check the promised no-leading-hyphen and no-'--' properties or the exact-80 boundary, so a regression in strip or truncation order could pass the suite.",
      "fix": "Add a test asserting re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', s) and len(s) <= MAX_LEN for an input with a leading hyphen and long content, plus a case where character 80 is a letter."
    }
  ]
}
```