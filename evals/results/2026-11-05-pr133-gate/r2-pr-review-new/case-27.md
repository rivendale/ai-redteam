# Review report: PR #70, harden slugify

**REVIEWED:** PR #70, head `9d4e1a7`, merge base `c82f0b3`. Both SHAs come from PR.md. I could not check them against a repository, so the review covers the patch and `base/` as supplied.

**TIER:** Standard. This is an ordinary code change to a small pure function. It touches no auth, secrets, migrations or money. The function's output ends up in URLs, but the change narrows the output set rather than widening exposure. One model round applies.

**REVIEWERS:**
- Reviewer: a fresh Claude instance (Sonnet 5.5) with no part in writing the change.
- Author: unknown, because no commit trailers were supplied.
- Process: no code was run (no tools in this session) and no code left the session. No instruction files from a checkout were loaded. The PR text contains nothing addressed to the reviewer.

**What I checked by reading**
- **Output invariant:** `re.sub(r"[^a-z0-9]+", "-", text.lower())` can only emit `[a-z0-9-]` with hyphen runs collapsed. `.strip("-")` removes leading and trailing hyphens. `slug[:80].rstrip("-")` cannot create a double hyphen or a trailing hyphen. The length is at most 80 and a leading hyphen is impossible. All of this meets the request.
- **Type check:** `isinstance(text, str)` raises `TypeError("text must be a string")` for `None`, bytes and ints. That is a clear error.
- **Patch mechanics:** the hunk headers match the line counts (`-1,2 +1,14` and `+1,30`). The PR's "six tests" matches the six tests in the patch.
- **"All pass":** this is an unverified claim, since I could not run the tests.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `slug.py:13-14` | A title with no a-z or 0-9 characters, such as `"日本語"` or `"🎉🎉"`, returns `""`. A caller building `/posts/<slug>` gets an empty path segment, and all such titles collide. The docstring mentions `""`, but the PR gives no caller handling or fallback. Callers were not provided. | `assertEqual(slugify("日本語"), "")` documents the behavior. A caller-level test should show that creating a URL from an empty slug is rejected or given a fallback. |
| 2 | P3 | `slug.py:9`, `tests/test_slug.py:21-22` | The docstring and PR say non-a-z letters are "dropped". In fact each one acts as a separator. `"naïve"` gives `"na-ve"` and `"Zoë"` gives `"zo"`. The only test (`"café au lait"`) hides this because a space follows the dropped letter. Unicode lowercasing also maps some characters into ASCII: Kelvin sign `K` becomes `k`, and `İ` becomes `i` plus a dropped combining mark, so `"İstanbul"` gives `"i-stanbul"`. The safety invariant still holds. The documentation and the test coverage are wrong. | `assertEqual(slugify("na\u00efve"), "na-ve")` and `assertEqual(slugify("\u212a"), "k")`. Alternatively, fix the docstring to say "treated as separators". |
| 3 | P3 | `slug.py:14`, `tests/test_slug.py:16-19` | The cap test only uses `"word " * 40`, where the cut falls right after a hyphen. The path where the cut leaves a trailing hyphen after a mid-word position is untested: `"a"*79 + " b"` is cut to `"a"*79 + "-"` and must come back as 79 characters. A regression that drops the `rstrip` after slicing would pass the current test only by luck. Exact-boundary cases (79, 80 and 81 characters) are also missing. | `assertEqual(slugify("a"*79 + " b"), "a"*79)` and `assertEqual(len(slugify("a"*80)), 80)`. |
| 4 | P3 | `tests/test_slug.py:2` | `from slug import ...` works only when the repository root is on `sys.path`. `python tests/test_slug.py` fails with `ImportError`. Plain `python -m unittest` may not discover `tests/` because there is no `__init__.py`. No CI or run command was supplied, so "six tests, all pass" cannot be matched to a check. | Run the documented test command from a clean checkout and show 6 tests found. Add `tests/__init__.py`, or document `python -m unittest tests.test_slug`. |

**FILES NEEDED BUT NOT PROVIDED:**
- Every caller of `slugify`. They are needed to judge compatibility, because the old function kept non-ASCII characters and underscores and the new one does not. Existing stored slugs that are regenerated would change. They would also show how the empty-slug case is handled (finding 1).
- The CI configuration and check results, to confirm that the expected checks are present and green.
- Commit metadata, for the author trailers.

**Close-out (pending):** this report is the reviewer's output only. The author needs to adjudicate findings 1–4 (Accepted with a test and fix commit, Deferred with an issue link for P2/P3, or Rejected with evidence). Whoever closes the PR then fills in the adjudication.

**Provisional merge recommendation:** merge after fixes. The core requirements are met by reading the code: the character set, single hyphens, the 80-character cap, and `TypeError` for non-strings. No P0 or P1 findings remain. Under Step 8 the merge still waits on three things:
- finding 1 gets a written decision (caller handling for the empty slug, or a documented deferral with an issue link);
- the tests are shown to run and pass in CI (finding 4);
- the callers are checked for compatibility.

No written rule was supplied that settles these questions, so I cite none.

```json
{
  "verdict": "merge_after_fixes",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "reasoned from code, not run",
      "location": "slug.py:13-14",
      "scenario": "Titles with no a-z/0-9 characters (e.g. '日本語', emoji) return '', so a URL built from the slug has an empty segment and all such titles collide. No caller handling is shown.",
      "fix": "Have callers reject or fall back on an empty slug (or add an explicit default); add tests for the empty-slug case at the caller."
    },
    {
      "severity": "P3",
      "evidence_level": "reasoned from code, not run",
      "location": "slug.py:9; tests/test_slug.py:21-22",
      "scenario": "Docstring says non-a-z letters are dropped, but they act as separators: 'naïve' -> 'na-ve'. Unicode lowercasing maps Kelvin sign to 'k' and 'İstanbul' to 'i-stanbul'. The only non-ASCII test hides this because a space follows the dropped letter.",
      "fix": "Correct the docstring to say 'treated as separators' and add tests for 'naïve' and the Kelvin sign."
    },
    {
      "severity": "P3",
      "evidence_level": "reasoned from code, not run",
      "location": "slug.py:14; tests/test_slug.py:16-19",
      "scenario": "The cap test cuts right after a hyphen; the case where the cut leaves a trailing hyphen mid-word ('a'*79 + ' b') and the 79/80/81 boundaries are untested, so removing the post-slice rstrip could go unnoticed.",
      "fix": "Add assertEqual(slugify('a'*79 + ' b'), 'a'*79) and boundary-length tests."
    },
    {
      "severity": "P3",
      "evidence_level": "reasoned from code, not run",
      "location": "tests/test_slug.py:2",
      "scenario": "'from slug import' only works with the repo root on sys.path; running the file directly fails and plain unittest discovery may skip tests/ (no __init__.py). 'Six tests, all pass' is unverified and no run command is given.",
      "fix": "Show the test command passing 6 tests from a clean checkout; add tests/__init__.py or document 'python -m unittest tests.test_slug'."
    }
  ]
}
```