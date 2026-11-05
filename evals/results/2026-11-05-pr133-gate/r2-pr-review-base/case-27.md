# PR #70 review report: harden slugify

**REVIEWED:** PR #70, head `9d4e1a7`, merge base `c82f0b3` (short SHAs as given in PR.md). I had no git access, so I could not confirm that `change.patch` matches that head. I reviewed the patch as supplied and checked its hunk counts against `base/slug.py` (they are consistent).

**TIER:** Standard. It is ordinary library code, and the output feeds URLs but touches no auth, secrets, personal data or permissions. One model round is the budget.

**REVIEWERS:** Reviewed by a fresh Claude Sonnet 5.5 instance with no memory of writing the change. The author is not stated, because no commit trailers were supplied. No data-handling restriction applies, since the code carries no personal data. I had no tools, so nothing was run. "Six tests, all pass" is an unverified claim. I counted six tests and read each one.

**Request check:** The patch covers all four requirements and adds nothing extra:
- **Charset:** output is only `a-z`, `0-9` and hyphens.
- **Single hyphens:** runs collapse to one hyphen.
- **Length cap:** at most 80 characters.
- **Non-strings:** they raise `TypeError`.

Output is always `[a-z0-9-]` with no leading or trailing hyphen, so there is no path-traversal or injection risk. The regex is linear, so there is no ReDoS.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `slug.py:14` (`re.sub(r"[^a-z0-9]+", ...)`) | Titles with no ASCII letters or digits, such as `"日本語"`, `"Привет"` or `"!!!"`, all return `""`. A caller building `/posts/<slug>` gets an empty segment, and every such title collides. This is documented, but the request said "safe for user-supplied titles" and the callers are not shown. | `slugify("日本語") == ""` documents the behaviour. The real fix is a caller-side test: creating two posts with non-Latin titles must not yield the same URL. |
| 2 | P2 | `slug.py:14` (whole function) | Output changes for inputs that previously passed through. `"a_b"` gave `"a_b"` and now gives `"a-b"`. `"Hi!"` gave `"hi!"` and now gives `"hi"`. If callers recompute slugs from titles rather than reading stored ones, existing URLs change and old links break. | Using fixtures of existing titles, assert that recomputed slugs equal the stored ones, or that a redirect or migration exists. |
| 3 | P3 | `slug.py:14` (`text.lower()`) | Some non-ASCII characters survive via Unicode lowercasing. `"\u212a"` (Kelvin sign) lowercases to `"k"`, so `slugify("\u212aelvin") == "kelvin"`, which contradicts the docstring's claim that letters outside a-z are dropped. The output is still safe. | `assertEqual(slugify("\u212a"), "k")` pins the behaviour, or the docstring is reworded. |
| 4 | P3 | `tests/test_slug.py:2` | `from slug import ...` assumes the repo root is on `sys.path`. `python tests/test_slug.py` gives `ModuleNotFoundError`. Plain `python -m unittest` skips `tests/` on Python 3.11+ because it has no `__init__.py`. Only `python -m unittest tests.test_slug` from the root is certain to work. CI wiring is not shown (UNVERIFIED). | Run the documented test command from a clean checkout and confirm it reports 6 tests. |
| 5 | P3 | `tests/test_slug.py:25` | Only `None` is tested for the `TypeError` path. `bytes` is the likeliest real-world non-string, and `int` is another. The code handles them, since it uses `isinstance`, but nothing pins that. | `for v in (b"x", 5, ["a"]): assertRaises(TypeError, slugify, v)` |

**FILES NEEDED BUT NOT PROVIDED:**
- Callers of `slugify` and how they store or recompute slugs, which findings 1 and 2 depend on.
- The CI or test configuration, to confirm the checks run and are green.
- Commit trailers, to record the author.

**Close-out:** not written. It follows the author's adjudication, and a reviewer does not adjudicate its own findings. Merge gates not yet met are the written decision on each finding and confirmation that the expected checks are green. There is no P0 or P1. The P2 items are owner decisions, so deferring them with a tracking issue is allowed, as are P3s.

```json
{
  "verdict": "merge_after_adjudication",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "confirmed_by_reading",
      "location": "slug.py:14",
      "scenario": "Titles with no ASCII alphanumerics (e.g. '日本語', '!!!') all return '', so URLs built from the slug are empty or collide.",
      "fix": "Have callers fall back to an id or other disambiguator when the slug is empty, or document and enforce non-empty slugs at the call site. Add a caller-level test."
    },
    {
      "severity": "P2",
      "evidence_level": "inferred_callers_not_seen",
      "location": "slug.py:14",
      "scenario": "Behaviour change for previously passed-through inputs ('a_b' -> 'a-b', 'Hi!' -> 'hi'). If slugs are recomputed from titles, existing URLs change.",
      "fix": "Confirm slugs are stored rather than recomputed, or add redirects or a migration. Test with fixtures of existing titles."
    },
    {
      "severity": "P3",
      "evidence_level": "confirmed_by_reading",
      "location": "slug.py:14",
      "scenario": "text.lower() maps U+212A (Kelvin sign) to 'k', so non-a-z input yields ASCII output, contradicting the docstring.",
      "fix": "Pin the behaviour with a test or reword the docstring; optionally lowercase only after an ASCII filter."
    },
    {
      "severity": "P3",
      "evidence_level": "unverified_not_run",
      "location": "tests/test_slug.py:2",
      "scenario": "'from slug import ...' fails when run as 'python tests/test_slug.py', and plain 'python -m unittest' may not discover tests/ (no __init__.py) on Python 3.11+.",
      "fix": "Add tests/__init__.py or configure the runner, then verify the 6 tests are reported by the CI command."
    },
    {
      "severity": "P3",
      "evidence_level": "confirmed_by_reading",
      "location": "tests/test_slug.py:25",
      "scenario": "The TypeError test covers only None; bytes, int and list are not pinned.",
      "fix": "Parametrize the test over b'x', 5 and ['a']."
    }
  ]
}
```