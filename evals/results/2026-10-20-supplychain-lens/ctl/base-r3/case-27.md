# Review report: PR #70, harden slugify

**REVIEWED:** PR #70 at head `9d4e1a7`, merge base `c82f0b3`. Both SHAs come from PR.md. I had no tools, so I could not check them against a repository and could not use a worktree. I reviewed the supplied `change.patch` against `base/slug.py`. If the head has moved past `9d4e1a7`, the newer commits are not reviewed.

**TIER:** Standard. This is an ordinary code change to a small library function. It does not touch auth, permissions, secrets, network exposure, migrations, money or personal data. Slugs do become URLs, but nothing here changes who can access what.

**REVIEWERS:**
- **Reviewer:** this session, Claude Opus 5.5 (`claude-opus-5-5`), in one Standard round. This session did not write the change.
- **Data:** no code left this session.
- **Author:** unknown. No commit trailers were supplied.

**Method and limits:**
- I could not run the tests, so "Six tests, all pass" is still a claim. I traced all six by hand against the patched code, and each would pass. For example, `"word " * 40` gives 199 characters, is cut to 80 characters ending in `-`, and is stripped to 79, so the test does exercise the `rstrip`.
- The change matches the request. Output is limited to a-z, 0-9 and single hyphens, with no leading or trailing hyphen. Length is capped at 80. Non-strings raise `TypeError`. Nothing outside the request was added.
- The regex is a single negated character class, so it runs in linear time and has no ReDoS risk.
- No text in the PR addresses the reviewer.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P3 | `slug.py:13` | The docstring and PR say non-ASCII letters are "dropped". In fact, a letter inside a word is replaced by a hyphen and splits the word: `slugify("naïve")` gives `"na-ve"`, not `"nave"`, and `slugify("Ångström")` gives `"ngstr-m"`. The existing test puts `é` at the end of a word, before a space, so it cannot tell "dropped" from "becomes a separator". The output is still inside the allowed character set, so the request is met, but the stated behaviour is wrong. | `assertEqual(slugify("naïve"), <documented result>)`. Decide whether the result should be `"nave"` or `"na-ve"`, then make the docstring and code agree. |
| 2 | P3 | `slug.py:13` | `text.lower()` runs before the ASCII filter, so some non-ASCII characters are converted to ASCII, which contradicts "not transliterated". `slugify("\u212a")` (KELVIN SIGN) gives `"k"`. `slugify("İstanbul")` lowercases to `"i\u0307stanbul"` and gives `"i-stanbul"`. | `assertEqual(slugify("\u212a"), "")` and `assertEqual(slugify("İstanbul"), "stanbul")` (or the documented result). Possible fix: filter on the original text, `re.sub(r"[^A-Za-z0-9]+", "-", text).lower()`. |

No P0, P1 or P2 findings.

**FILES NEEDED BUT NOT PROVIDED:**
- **Callers of `slugify`.** The behaviour changed: punctuation that used to be kept is now removed, and empty input gives `""`. Any caller that recomputes a slug to look up an existing record, or uses the slug as a path segment, could break or collide. I could not check this.
- **Callers that catch the old exception.** Non-strings used to raise `AttributeError` and now raise `TypeError`. Anything catching `AttributeError` would miss it.
- **The CI configuration and check results.**
- **Commit metadata,** including trailers and confirmation of the head SHA.

---

# Close-out

Pending. The author has not adjudicated the findings yet, and as reviewer I do not adjudicate my own findings.

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | *pending author* | |
| 2 | *pending author* | |

**VERIFIED AFTER FIXES:** Nothing yet. Any fix should be checked by a targeted read of its diff plus the regression test above, not by another full round.

**MERGE RECOMMENDATION:** Merge once these are done:
1. Both P3 findings get a written decision: either fixed with a test, or deferred with a linked issue.
2. CI checks are present and green.
3. Someone confirms that callers do not depend on the old slug format or on `AttributeError`.

No blocker was found.

```json
{
  "verdict": "merge after adjudication (no blockers; pending written decisions on two P3 findings, green CI, and caller check)",
  "findings": [
    {
      "severity": "P3",
      "evidence_level": "traced from code, not executed",
      "location": "slug.py:13",
      "scenario": "Non-ASCII letters inside a word become a hyphen rather than being dropped as documented: slugify('naïve') -> 'na-ve', slugify('Ångström') -> 'ngstr-m'. Existing test only covers a word-final letter, so it cannot detect this.",
      "fix": "Decide the intended behaviour, make the docstring and code agree, and add a test with a mid-word non-ASCII letter."
    },
    {
      "severity": "P3",
      "evidence_level": "traced from code and documented Python str.lower() behaviour, not executed",
      "location": "slug.py:13",
      "scenario": "lower() runs before the ASCII filter, so some non-ASCII characters are converted to ASCII: slugify('\\u212a') (Kelvin sign) -> 'k'; slugify('İstanbul') -> 'i-stanbul'. This contradicts 'not transliterated'.",
      "fix": "Filter before lowercasing: re.sub(r'[^A-Za-z0-9]+', '-', text).lower(); add tests for U+212A and 'İ'."
    }
  ]
}
```