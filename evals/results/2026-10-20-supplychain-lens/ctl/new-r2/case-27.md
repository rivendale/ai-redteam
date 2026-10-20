# PR #70 review: harden slugify

## Review report

**REVIEWED:** PR #70, head `9d4e1a7`, merge base `c82f0b3`.
- Both SHAs come from PR.md and are short forms. I could not check them against a repository.
- I had no tools, so there was no throwaway checkout. I reviewed the supplied `change.patch` against `base/slug.py`. Nothing was executed. Every test result below comes from tracing the code by hand.

**TIER:** Standard. This is ordinary code: a pure string function with no auth, secrets, network, migrations or personal-data handling. That matches the stated stakes. Code was not sent outside this session.

**REVIEWERS:**
- Reviewer: this instance (Claude Opus 5.5, `claude-opus-5-5`), one round. This session did not write the change.
- Author: unknown. No commits or `Co-Authored-By` trailers were provided.

**Checked against the request and found correct:**
- **Character set:** output is limited to `a-z`, `0-9` and hyphens (`slug.py:13`).
- **Single hyphens:** runs of other characters collapse to one hyphen, and truncation cannot create a double hyphen.
- **No leading or trailing hyphen:** `strip("-")` runs before the slice and `rstrip("-")` after it.
- **Length:** output is at most 80 characters.
- **Non-strings:** `TypeError` is raised for `None`, `bytes` and `int` (`slug.py:11-12`).
- **Regex safety:** `[^a-z0-9]+` is linear, so there is no ReDoS risk.
- **Unicode lowercasing:** cases like `"\u212a".lower()` returning `"k"` still give ASCII output, so they are not a defect.
- **Tests:** tracing all six by hand, each should pass. For example, the cap test produces a 79-character slug, so it exercises the `rstrip`. I did not run them, so "all pass" remains the author's claim.
- **Scope:** there is nothing beyond what was requested.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P3 | `slug.py:13` (docstring at `slug.py:9`; PR.md) | **Claim:** the docstring and PR say non-a-z letters are "dropped". **Actual:** they are replaced by a hyphen, so a letter inside a word splits the word. `"naïve"` gives `"na-ve"`, `"Müller"` gives `"m-ller"`, `"São Paulo"` gives `"s-o-paulo"`. **Why tests miss it:** `test_non_ascii_dropped` (`tests/test_slug.py:21-22`) only places `é` at the end of a word, so it passes either way. **Result:** the slug still meets the request, but it is worse than documented and the doc is wrong. | `assertEqual(slugify("naïve"), "nave")`. This fails today with `"na-ve"`. If the hyphen behavior is intended, fix the docstring and PR text instead and assert `"na-ve"`. |
| 2 | P3 | `slug.py:14` (callers not provided) | Any title with no a-z or 0-9 characters returns `""`, for example `"Привет"`, `"日本語"` or `"🙂"`. This is documented. However, if the URL-creating caller uses the slug directly, every such title gets the same empty path segment, which causes collisions or a URL like `/posts/`. Severity depends on caller code I have not seen. | A caller-level test: create two items titled `"Привет"` and `"日本語"`, then assert their URLs are non-empty and distinct. Alternatively, decide that `slugify` raises `ValueError` on empty output and test for that. |
| 3 | P3 | `tests/test_slug.py:16-19` | The cap test only asserts `len <= 80` and no trailing hyphen. It does not check the boundary. An off-by-one regression would still pass, such as `slug[:MAX_LEN-1]`, or a cap that wrongly trims an exactly-80-character slug. | `assertEqual(slugify("a" * 80), "a" * 80)` and `assertEqual(slugify("a" * 81), "a" * 80)`. |

There are no P0 or P1 findings. No text in the PR addresses the reviewer.

**FILES NEEDED BUT NOT PROVIDED:**
- The callers of `slugify` that build URLs. Finding 2 depends on them.
- CI or check status for the head.
- The commit list with trailers, to record the author.

## Close-out

Per the skill, the reviewer does not adjudicate its own findings. The author must write the decisions below.

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | *pending author* | — |
| 2 | *pending author* (deferrable as P3, with a tracking issue) | — |
| 3 | *pending author* (deferrable as P3) | — |

**VERIFIED AFTER FIXES:** None yet. Verify each fix with a targeted read of its diff and its regression test, not another full round.

**MERGE RECOMMENDATION:** Merge after adjudication. There are no blockers. Merging still needs:
- a written decision on findings 1 to 3 (each can be fixed or deferred with an issue link);
- a confirmed green CI run at `9d4e1a7`, since check status is unknown and a missing check is not green;
- confirmation that the head has not moved since `9d4e1a7`.

```json
{
  "verdict": "merge after fixes (no blockers; pending author adjudication of three P3 findings and confirmation of green checks at 9d4e1a7)",
  "findings": [
    {
      "severity": "P3",
      "evidence_level": "code-traced (not executed)",
      "location": "slug.py:13 (docstring slug.py:9)",
      "scenario": "Non-a-z letters inside a word become a hyphen instead of being dropped as documented: 'naïve' -> 'na-ve', 'Müller' -> 'm-ller'. The existing test only covers a word-final 'é', so it passes either way.",
      "fix": "Either drop such characters before collapsing (e.g. remove [^a-z0-9\\s-] first, then collapse separators) and test slugify('naïve') == 'nave', or correct the docstring and PR text to say they act as separators."
    },
    {
      "severity": "P3",
      "evidence_level": "code-traced; caller impact unverified (callers not provided)",
      "location": "slug.py:14",
      "scenario": "Titles with no ASCII letters or digits ('Привет', '日本語', emoji) all return '', so URL creation may produce empty or colliding paths.",
      "fix": "Decide the contract: raise ValueError on empty output, or have the caller fall back to an ID-based slug; add a caller-level test for distinct non-empty URLs."
    },
    {
      "severity": "P3",
      "evidence_level": "test gap",
      "location": "tests/test_slug.py:16-19",
      "scenario": "The cap test only asserts len <= 80, so an off-by-one regression (slicing to 79, or trimming an exactly-80 slug) would still pass.",
      "fix": "Add assertEqual(slugify('a'*80), 'a'*80) and assertEqual(slugify('a'*81), 'a'*80)."
    }
  ]
}
```