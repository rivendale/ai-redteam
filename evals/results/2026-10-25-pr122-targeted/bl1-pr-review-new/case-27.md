# PR #70 review: harden slugify

**REVIEWED:** PR #70, head `9d4e1a7`, merge base `c82f0b3` (both from PR.md; I could not confirm them against a repository). The review covers `change.patch` applied to `base/slug.py`. I had no tools, so I did not run anything. All test results below come from tracing the code by hand.

**TIER:** Standard. This is ordinary code in a small library function that builds URLs. It does not touch authentication, secrets, network exposure, migrations, money or personal data. There are no dependency or runtime changes, so the supply-chain and TLS lenses do not apply.

**DATA / ENDPOINT:** The code carries no personal data or secrets, so reviewing it in this session is acceptable.

**REVIEWERS:** Reviewed by Claude Opus 5.5 (`claude-opus-5-5`), a fresh instance that did not write the change. The author is unknown: no commit trailers were provided.

## Checked against the request

| Requirement | Result |
|---|---|
| Only a-z, 0-9 and single hyphens | Met. The output passes through `[^a-z0-9]+ → "-"`, then `.strip("-")`, so runs collapse to one hyphen and there are no leading or trailing hyphens. See F1 for a docstring mismatch. |
| Length cap | Met. `slug[:80].rstrip("-")` gives at most 80 characters and cannot end in a hyphen. |
| Clear error for non-strings | Met. `None`, `bytes`, `int` and similar raise `TypeError("text must be a string")`. |
| Nothing extra | Met. No scope creep. |

**Tests traced by hand (not run):**
- `"Hello, World!"` → `"hello-world"`
- `"  a   b -- c  "` → `"a-b-c"`
- `""` and `"!!!"` → `""`
- `"word "*40` → 79 characters, ending in `d`
- `"café au lait"` → `"caf-au-lait"`
- `None` → `TypeError`

All six assertions should pass. The claim "six tests, all pass" is still unverified because no run output or CI result was provided.

## Findings

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| F1 | P3 | `slug.py:13` (new) | `text.lower()` runs before the ASCII filter, so some non-ASCII characters become ASCII letters instead of being dropped. The Kelvin sign `"\u212A"` returns `"k"`. `"İstanbul"` (U+0130) lowercases to `"i\u0307stanbul"` and returns `"istanbul"`. Meanwhile `"Ölçü"` returns `"l-"` → `"l"`. This contradicts the docstring and PR.md ("letters outside a-z are dropped, not transliterated"). The output stays within a-z, so this is not a safety break, but the documented contract is false. Fix: filter first, then lowercase, with `re.sub(r"[^A-Za-z0-9]+", "-", text).lower()`. Python `str` patterns match `[A-Za-z]` as ASCII only. The alternative is to document the behavior. | `assertEqual(slugify("\u212A"), "")` and `assertEqual(slugify("\u0130stanbul"), "stanbul")`. Both fail today, returning `"k"` and `"istanbul"`. |
| F2 | P2 (inferred; callers not provided) | `slug.py:14` (new) | Any title with no ASCII letters or digits, such as `"你好"`, `"Привет"` or `"!!!"`, returns `""`. If a caller uses the slug directly in a URL, every such title gets the same empty slug. That causes URL collisions or an empty path segment for non-Latin users. The PR documents this, but the request ("safe for user-supplied titles, used when creating URLs") does not say how empty results should be handled. Whether this fails in real use depends on callers I could not see. | A caller-level test: two titles `"你好"` and `"Привет"` must produce distinct, non-empty URL paths. Alternatively, a unit test asserting the chosen contract, such as `slugify("你好")` raising `ValueError`. |
| F3 | P3 (inferred) | `tests/test_slug.py:2` | The test sits in `tests/` with no `tests/__init__.py` in the patch and does `from slug import ...`. Running `python tests/test_slug.py` puts `tests/` on `sys.path` and fails with `ImportError`. On Python 3.11+, `python -m unittest` discovery from the repo root may not descend into a non-package `tests/`. That would run 0 tests: "OK" before 3.12, exit code 5 from 3.12 on. CI could then report green without exercising slugify. This depends on the CI command, which was not provided. | A CI run whose log shows `Ran 6 tests`. Alternatively, add `tests/__init__.py` and confirm `python -m unittest` from the root reports 6. |

No reviewer-directed instructions appeared in the PR text.

**FILES NEEDED BUT NOT PROVIDED:**
- Callers of `slugify`, to assess F2 and check whether the changed output alters existing stored slugs or URLs.
- CI config and the CI run for `9d4e1a7`.
- Commit metadata (author and trailers).

## Close-out

A reviewer does not adjudicate its own findings, so this section stays open for the author or whoever closes the PR.

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| F1 | Pending author | — |
| F2 | Pending author. As a P2 it may be Deferred with a linked issue. | — |
| F3 | Pending author | — |

**VERIFIED AFTER FIXES:** None yet. The head has not moved as far as I know.

**MERGE RECOMMENDATION:** Not yet. I found no P0 or P1 issues, so once the merge gates are met this should be a straightforward merge. The relevant gates are Step 8, which requires *"every round the tier requires has run, and every finding has a written decision"* and *"every expected check is present and green (a missing check is not green, and a red check is never overridden)."* The Standard round has run. Still open:
- Written decisions on F1, F2 and F3.
- A CI result for `9d4e1a7` showing the six tests actually ran (see F3).

```json
{
  "verdict": "merge after adjudication and green CI; no blockers found",
  "findings": [
    {
      "severity": "P3",
      "evidence_level": "traced by reading code (Python str.lower Unicode mappings); not executed",
      "location": "slug.py:13",
      "scenario": "lower() before the ASCII filter maps some non-ASCII letters to ASCII: '\\u212A' -> 'k', 'İstanbul' -> 'istanbul', contradicting the docstring/PR claim that letters outside a-z are dropped, not transliterated",
      "fix": "Filter then lowercase: re.sub(r'[^A-Za-z0-9]+', '-', text).lower(); or document the behavior. Test: slugify('\\u212A') == '' and slugify('\\u0130stanbul') == 'stanbul'"
    },
    {
      "severity": "P2",
      "evidence_level": "inferred; callers not provided",
      "location": "slug.py:14",
      "scenario": "Titles with no ASCII alphanumerics ('你好', 'Привет', '!!!') all return '', so URL creation can collide or produce an empty path segment unless callers handle it",
      "fix": "Decide the contract (raise ValueError, or require a caller fallback such as an id suffix) and add a test for it; or defer with a tracking issue"
    },
    {
      "severity": "P3",
      "evidence_level": "inferred; CI config not provided",
      "location": "tests/test_slug.py:2",
      "scenario": "tests/ has no __init__.py; depending on the CI command, discovery may run 0 tests, or direct execution fails with ImportError on 'from slug import', so CI could be green without testing slugify",
      "fix": "Add tests/__init__.py (or configure discovery) and confirm the CI log shows 'Ran 6 tests'"
    }
  ]
}
```