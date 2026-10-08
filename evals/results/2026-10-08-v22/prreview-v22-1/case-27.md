# PR #70 review: harden slugify

**Review report**

**REVIEWED:** PR #70 "harden slugify", head `9d4e1a7`, merge base `c82f0b3`. Both SHAs come from PR.md; I could not check them against a repository. This session has no tools, so I reviewed the supplied `change.patch` against `base/slug.py` rather than a checkout of the head. I could not run anything, so every behaviour below was traced by hand.

**TIER:** Standard. This is an ordinary code change to a small library function that builds URL slugs. It does not touch auth, permissions, secrets, network exposure, migrations, money or stored personal data. One round is required, and this is that round.

**REVIEWERS:**
- Reviewer: this session (Claude Opus 5.5, `claude-opus-5-5`), a separate instance that did not write the change.
- Author: unknown. No commit trailers were provided.
- Data: the code carries no sensitive data, and nothing was sent to any other endpoint.

**Checked against the request:**
- **Only a-z, 0-9 and single hyphens: met.**
  - `[^a-z0-9]+` collapses each run of other characters to one `-`.
  - `.strip("-")` removes leading and trailing hyphens.
  - Truncation is followed by `.rstrip("-")`.
  - So the output never has doubled, leading or trailing hyphens.
- **Length cap: met.** `slug[:MAX_LEN]` limits the output to at most 80 characters.
- **Clear error for non-strings: met.** It raises `TypeError("text must be a string")`.
- **Nothing extra added.** No ReDoS risk: the pattern is a single negated class with no nested quantifiers.

**Tests traced by hand (not run):**
- All six pass:
  - `"Hello, World!"` gives `hello-world`.
  - `"  a   b -- c  "` gives `a-b-c`.
  - `""` and `"!!!"` give `""`.
  - The 199-character input truncates to 80 characters ending in `-`, and `rstrip` leaves 79. The test does exercise the trailing-hyphen path.
  - `"café au lait"` gives `caf-au-lait`.
  - `None` raises `TypeError`.
- The claim "six tests" is accurate.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `slug.py:13-14` (`re.sub(...)`/`return`), docstring line 10 | A title with no a-z/0-9 characters returns `""`. Examples: `"日本語"`, `"Ünïcödé"` (gives `n-c-d`, shown only for contrast), `"!!!"`, or all-emoji titles. Two such posts both get the empty slug. If the caller builds `/posts/<slug>`, they collide on the same URL or produce `/posts/`. The docstring states this behaviour, but nothing in the PR guards against it, and the request says "safe for user-supplied titles". Whether this actually breaks depends on the caller, which was not provided. | `slugify("日本語")` should return a non-empty value or raise `ValueError`, once the owner decides which. Today it returns `""`. |
| 2 | P3 | `slug.py:13` (`text.lower()` before the ASCII filter) | The docstring says letters outside a-z are dropped, not transliterated. But `str.lower()` maps some non-ASCII characters to ASCII before the filter runs. `"\u212A"` (Kelvin sign) becomes `"k"`, and `"\u0130"` (İ) becomes `"i"` plus a combining dot, which is then dropped. So `slugify("\u212Aelvin")` returns `"kelvin"`, not `"elvin"`. The output is still safe, but the documented contract is wrong and the result looks like a lookalike-letter slug. | `assertEqual(slugify("\u212Aelvin"), "elvin")` fails today. Fix by filtering before lowercasing, e.g. `re.sub(r"[^A-Za-z0-9]+", "-", text).lower()`, or by correcting the docstring. |

**FILES NEEDED BUT NOT PROVIDED:**
- The callers of `slugify`. These are needed to judge two things:
  - how an empty slug is handled (finding 1);
  - whether slugs are stored when a URL is created or recomputed when looking one up. If they are recomputed, existing URLs containing punctuation that the old function kept, such as `c++`, would stop resolving.
- The CI configuration and check results.
- The commit log for `9d4e1a7`, for the author trailers.

**Close-out** (pending: written after the author adjudicates; the reviewer does not adjudicate its own findings)

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | pending | |
| 2 | pending | |

**VERIFIED AFTER FIXES:** none yet.

**MERGE RECOMMENDATION:** No P0 or P1 findings, so nothing in the code blocks merge. Recommend merge once all of these hold:
- findings 1 and 2 have written decisions (both may be deferred with an issue link);
- the CI checks are confirmed present and green, which I could not see;
- someone has confirmed from the callers that an empty slug is handled and that slugs are not recomputed for lookups.

```json
{
  "verdict": "merge after adjudication: no blockers found; findings 1-2 need written decisions, CI checks and callers not seen",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "traced by hand; impact depends on the caller, which was not provided",
      "location": "slug.py:13-14",
      "scenario": "Titles with no a-z/0-9 characters (e.g. \"日本語\", all emoji, \"!!!\") all return \"\"; two such posts collide on the same URL or produce an empty path segment.",
      "fix": "Decide the contract: raise ValueError on an empty result, or have the caller supply a fallback (id or hash). Add a test that slugify(\"日本語\") does not silently return \"\"."
    },
    {
      "severity": "P3",
      "evidence_level": "traced by hand (Python str.lower semantics)",
      "location": "slug.py:13",
      "scenario": "lower() runs before the ASCII filter, so U+212A (Kelvin sign) becomes 'k' and U+0130 becomes 'i'; slugify(\"\\u212Aelvin\") returns \"kelvin\", contradicting the docstring's 'dropped, not transliterated'.",
      "fix": "Filter before lowercasing: re.sub(r\"[^A-Za-z0-9]+\", \"-\", text).lower(), or correct the docstring. Add a test that slugify(\"\\u212Aelvin\") == \"elvin\"."
    }
  ]
}
```