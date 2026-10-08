**Review report**

**REVIEWED:** PR #70 "harden slugify". Head `9d4e1a7`, merge base `c82f0b3`. These SHAs come from PR.md. I could not verify them or check out a worktree, because this session has no tools. The review covers `work/change.patch` applied by hand to `work/base/slug.py`. The six tests were traced by hand, not run.

**TIER:** Standard. This is a pure string function that sanitises user input for URL slugs. It does not touch auth, permissions, secrets, network exposure, migrations, money or personal data storage. The rated stakes in context.md agree.

**REVIEWERS:**
- Reviewer: one in-session instance, Claude Opus 5.5 (`claude-opus-5-5`), with no part in writing the change.
- Author: unknown. No commit trailers were provided.
- Data handling: the code is an invented library function with no personal data, so no endpoint restriction applies.

**Hand trace of the tests (all six pass on trace):**

| Input | Steps | Result |
|---|---|---|
| `"Hello, World!"` | → `hello-world-` → strip | `hello-world` ✓ |
| `"  a   b -- c  "` | → `-a-b-c-` → strip | `a-b-c` ✓ |
| `""`, `"!!!"` | | `""` ✓ |
| `"word " * 40` | `slug[:80]` is `"word-"*16`, ending in `-`; rstrip | 79 chars ✓ (rstrip is genuinely exercised) |
| `"café au lait"` | `é` and the space merge into one `-` | `caf-au-lait` ✓ |
| `None` | | `TypeError` ✓ |

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P3 | `slug.py:13` | Letters outside a-z inside a word are not dropped, as the docstring and PR claim. They become word separators. `slugify("naïve")` gives `"na-ve"`, and `slugify("Über München")` gives `"ber-m-nchen"`. The café test cannot tell the two behaviours apart because `é` sits next to a space. | `assertEqual(slugify("naïve"), "nave")` if dropping is intended. Otherwise correct the docstring and PR text and pin `"na-ve"`. |
| 2 | P3 | `slug.py:13` | `text.lower()` runs before the ASCII filter, so some non-ASCII characters lowercase into a-z instead of being dropped. KELVIN SIGN `"\u212A"` lowercases to `"k"`, so `"\u212Aey"` gives `"key"`, the same slug as the ASCII title. `"İstanbul"` (U+0130) lowercases to `i` plus U+0307, which gives `"i-stanbul"`. The output stays inside the allowed alphabet, so this is not a safety breach. It does contradict the documented contract and lets homoglyph titles produce ASCII slugs. | `assertEqual(slugify("\u212A"), "")` and `assertEqual(slugify("İstanbul"), "stanbul")`. Fix by filtering with `[^A-Za-z0-9]+` before `.lower()`. |
| 3 | P2 | `slug.py:14` (return) | A title with no ASCII letters or digits, such as `"Привет мир"` or `"日本語"`, now returns `""`. The base returned `"привет-мир"`. Any caller that builds a URL from the slug gets an empty path segment, such as `/posts/`, or collides with every other non-Latin title. The behaviour inside the function is traced. The impact on callers is inferred, because the callers were not provided. | A caller-level test: create two items titled `"Привет"` and `"日本語"`, then assert their URLs are distinct and non-empty. Alternatively, decide that `slugify` should raise or return a fallback for an empty result, and test that. |

No P0 or P1 findings. The things the request asked for all hold on trace:
- The output alphabet is limited to a-z, 0-9 and single hyphens.
- Length is capped at 80, with no leading or trailing hyphen after truncation.
- Non-strings raise `TypeError`.
- The regex has no catastrophic backtracking.

**FILES NEEDED BUT NOT PROVIDED:**
- Callers of `slugify` (the URL-creation code), needed to settle finding 3.
- CI configuration and check results for `9d4e1a7`.
- Commit metadata and trailers for authorship.

---

**Close-out**

This is not written yet. The reviewer does not adjudicate its own findings. The author must record Accepted, Deferred (with an issue link) or Rejected for findings 1–3.

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | pending author | |
| 2 | pending author | |
| 3 | pending author | |

**VERIFIED AFTER FIXES:** Not applicable yet. Verify any fix by reading the correction diff and running the new regression tests. Do not run another full review.

**MERGE RECOMMENDATION (reviewer's view, not the close-out):** Merge after adjudication. No blocker was found. The merge still needs three things:
- A written decision on each finding. Finding 3 needs an owner decision on empty-slug behaviour for non-Latin titles.
- Every expected CI check present and green on the merged head. None were shown to me, and a missing check is not green.
- The six tests actually run, not only traced.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P3",
      "evidence_level": "traced",
      "location": "slug.py:13",
      "scenario": "Non a-z letters inside a word become separators rather than being dropped as documented: slugify('naïve') == 'na-ve', slugify('Über München') == 'ber-m-nchen'. The café test cannot distinguish the two behaviours.",
      "fix": "Either strip non-ASCII before substituting (so 'naïve' -> 'nave') or correct the docstring and PR text; add a test pinning the chosen behaviour."
    },
    {
      "severity": "P3",
      "evidence_level": "traced (Python str.lower semantics)",
      "location": "slug.py:13",
      "scenario": "lower() runs before the ASCII filter, so U+212A KELVIN SIGN maps to 'k' ('\\u212Aey' -> 'key', colliding with the ASCII title) and 'İstanbul' -> 'i-stanbul'. Contradicts 'letters outside a-z are dropped'.",
      "fix": "Filter with [^A-Za-z0-9]+ before lowercasing; test slugify('\\u212A') == ''."
    },
    {
      "severity": "P2",
      "evidence_level": "traced in function; caller impact inferred (callers not provided)",
      "location": "slug.py:14",
      "scenario": "Titles with no ASCII alphanumerics ('Привет мир', '日本語') now return '' (base returned a non-empty slug), so URL creation yields empty or colliding paths.",
      "fix": "Owner decision: raise ValueError or return a fallback on empty result, or have callers handle ''; add a caller-level test that two non-Latin titles get distinct non-empty URLs."
    }
  ]
}
```