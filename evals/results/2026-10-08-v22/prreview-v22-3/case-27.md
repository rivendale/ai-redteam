# PR #70 Review: harden slugify

## Review report

**REVIEWED:** PR #70, head `9d4e1a7`, merge base `c82f0b3`. Both SHAs come from PR.md. I had no checkout or worktree, so the review covers `work/change.patch` applied to `work/base/slug.py` as provided. I could not confirm that this patch is exactly what `9d4e1a7` contains.

**TIER:** Standard. This is an ordinary code change to a small library function that builds URL slugs. It touches no auth, permissions, secrets, network exposure, migrations, money or personal data. The context also states the stakes as standard. One model round, and this report is that round.

**DATA:** The code is a pure string function with no data, secrets or personal data. Reviewing it in this session sends nothing new anywhere.

**REVIEWERS:**
- Reviewer: this instance (Opus 5.5, `claude-opus-5-5`). It did not write or help write the change.
- Author: unknown. No commit trailers were provided.

**TESTS:** I could not run them because this session has no tools. "Six tests, all pass" is therefore the author's claim. I traced each test by hand against the patched code, and all six should pass:
- `test_length_cap_never_ends_in_hyphen`: `"word " * 40` gives 199 characters. The first 80 are `"word-"` × 16, and `rstrip` trims that to 79. So the test does exercise the trailing-hyphen path.

**AGAINST THE REQUEST:**
- Only a-z, 0-9 and single hyphens: met, via `[^a-z0-9]+` → `-`, then `strip("-")`.
- Length cap: met, via `[:MAX_LEN].rstrip("-")`.
- Clear error for non-strings: met, via `TypeError("text must be a string")`.
- Nothing extra was added beyond the docstring and tests.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P3 | `slug.py:13` (`re.sub(r"[^a-z0-9]+", "-", text.lower())`) | The code lowercases before filtering, so some non-ASCII characters lowercase into ASCII letters and survive. KELVIN SIGN `"\u212A"` lowercases to ASCII `"k"`, so `slugify("\u212Aey")` returns `"key"`. `"\u0130"` (İ) lowercases to `"i\u0307"`, so `slugify("\u0130stanbul")` returns `"istanbul"`. This contradicts the docstring and PR claim that "letters outside a-z are dropped, not transliterated." It also lets a lookalike title produce the same slug as an ASCII title. Output is still within a-z, 0-9 and hyphens, so the request itself is met; the documented contract is not. | `assertEqual(slugify("\u212A"), "")` and `assertEqual(slugify("\u0130x"), "x")`. Both fail today. Fix: filter on the original text first, then lowercase: `re.sub(r"[^A-Za-z0-9]+", "-", text).lower()`. |

No other defects found. I checked these specifically:
- Leading, trailing and doubled hyphens: handled.
- Truncation landing on a hyphen: handled.
- `bytes` and `None` input: both raise `TypeError`.
- Regex backtracking on large input: the pattern is linear.

**OPEN QUESTIONS (not findings, because the callers were not provided):**
- **Empty slugs.** `slugify("!!!")` returns `""` by design, and this is tested. If a caller builds `/posts/<slug>` from it, the result could be an empty or colliding URL. Whether that matters depends on the callers.
- **Changed slugs for existing titles.** The new algorithm produces different slugs for existing titles. Old: `"Hello, World!"` → `"hello,-world!"`. New: `"hello-world"`. Any slugs that are recomputed from titles for lookup, rather than stored, would break existing URLs.

**FILES NEEDED BUT NOT PROVIDED:**
- Callers of `slugify`, to check how empty slugs are handled and whether slugs are stored or recomputed.
- CI configuration and check results for `9d4e1a7`.
- Commit metadata and trailers for authorship.

## Close-out

Pending. The author adjudicates finding 1; a reviewer does not adjudicate its own findings.

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | Pending author | — |

**VERIFIED AFTER FIXES:** None yet. If the fix above lands, verify it with a targeted read of its diff plus the two new tests. It does not need another full round.

**MERGE RECOMMENDATION:** Merge after adjudication, not yet. Finding 1 is P3, so it can be fixed or deferred with a tracking issue. Two things are still open before merge:
- Check results for `9d4e1a7` have not been seen. A missing check is not green.
- The two caller questions above need an answer from someone who can see the callers.

There are no blockers.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P3",
      "evidence_level": "traced by reading code against Python str.lower() semantics; not executed (no tools)",
      "location": "slug.py:13",
      "scenario": "Lowercasing happens before ASCII filtering, so non-ASCII characters whose lowercase is ASCII survive: slugify('\\u212Aey') == 'key' (Kelvin sign), slugify('\\u0130stanbul') == 'istanbul'. This contradicts the documented 'letters outside a-z are dropped, not transliterated' and lets lookalike titles collide with ASCII slugs.",
      "fix": "Filter before lowercasing: re.sub(r\"[^A-Za-z0-9]+\", \"-\", text).lower().strip(\"-\"); add tests slugify('\\u212A') == '' and slugify('\\u0130x') == 'x'."
    }
  ]
}
```