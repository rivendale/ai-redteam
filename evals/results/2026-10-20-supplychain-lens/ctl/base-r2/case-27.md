# PR #70 Review: harden slugify

## Review report

**REVIEWED:** PR #70 "harden slugify". The head is `9d4e1a7` and the merge base is `c82f0b3`, both as stated in `PR.md`.
- I had no tools, so I could not check these SHAs against a repository or check out a worktree.
- I reviewed `change.patch` as given, applied by reading to `base/slug.py`.
- If `9d4e1a7` does not match this patch, or the head has moved since, this review does not cover the difference.

**TIER:** Standard.
- This is an ordinary library function that builds URL slugs.
- It does not touch auth, permissions, secrets, network exposure, migrations, money or stored personal data.
- One model round is required, and this report is that round.

**DATA:** The code is a small library function with no secrets or personal data. I reviewed it in this session only and sent nothing to any other endpoint.

**REVIEWERS:**
- Reviewer: one fresh instance of claude-opus-5-5, which had no part in writing this change.
- Author: unknown. No commits or `Co-Authored-By` trailers were provided.

**NOT RUN:**
- I could not run anything. The claim "Six tests, all pass" is unverified.
- I traced each test by hand against the code, and each one passes on that reading.

### What checks out

| Requirement | How the change meets it |
|---|---|
| Only a-z, 0-9 and single hyphens | `re.sub(r"[^a-z0-9]+", "-", ...)` turns every run of other characters into one hyphen. |
| No leading or trailing hyphen | `.strip("-")` removes both ends. |
| Length cap | `slug[:MAX_LEN].rstrip("-")` keeps the result at 80 characters or fewer. Trimming after the cut cannot leave an empty string, because the first character is never a hyphen. |
| Hyphen trimming after the cut is tested | `"word " * 40` cuts to 16 copies of `"word-"`, so the `rstrip` path really runs. |
| Clear error for non-strings | `TypeError` for non-strings, including `bytes`. |
| Nothing extra | The change adds nothing beyond the request. |

### FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `slug.py:13` (`re.sub(...)`) | The docstring and PR say letters outside a-z are **dropped**. In fact they are **replaced by a word separator**. A non-ASCII letter inside a word splits that word: `"Zürich"` → `"z-rich"`, `"naïve"` → `"na-ve"`, `"résumé"` → `"r-sum"`. `test_non_ascii_dropped` only puts `é` at the end of a word, where the extra hyphen gets merged away, so the test hides this. The result: user-visible slugs for ordinary European titles have stray hyphens, and the code does not match its documented contract. | `assertEqual(slugify("Zürich"), "zrich")` and `assertEqual(slugify("naïve café"), "nave-caf")`. Both fail today. Alternatively, if the owner decides the split is intended, fix the docstring and assert `"z-rich"` instead. |
| 2 | P3 | `slug.py:13` (`text.lower()` runs before filtering) | `str.lower()` turns some non-ASCII characters into ASCII before the filter sees them. This contradicts "dropped, not transliterated". The KELVIN SIGN `"\u212a"` becomes `"k"`, so `slugify("5\u212a run")` gives `"5k-run"`. `"İstanbul"` (U+0130) lowercases to `"i"` + U+0307, which gives `"i-stanbul"`. Output is still valid. Only the stated contract breaks. | `assertEqual(slugify("\u212a"), "")` and `assertEqual(slugify("İstanbul"), "stanbul")`. Both fail today. |
| 3 | P2 (inferred; callers not provided) | `slug.py:14` (`return`) | A title made only of non-Latin script or symbols gives `""`. Examples: `"你好世界"`, `"Привет"`, `"!!!"`. The docstring says this happens, but the request asks for slugify to be safe for *user-supplied* titles. A caller that builds `/posts/<slug>` would then produce `/posts/` for every such title. These URLs collide, or they resolve to the index route. How bad this is depends on callers I was not given. | A caller-level test: create two items titled `"你好"` and `"Привет"` and assert their URLs are distinct and non-empty. Or, if the function should own this, `assertRaises(ValueError, slugify, "你好")` or a defined fallback. |

**Suggested fix for 1 and 2:** filter out non-ASCII alphanumerics *before* lowercasing, and keep non-ASCII spaces and punctuation as separators:

```python
text = "".join(c for c in text if c.isascii() or not c.isalnum())
slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
```

- `"Zürich"` → `"zrich"`, the KELVIN SIGN is dropped, and `"İstanbul"` → `"stanbul"`.
- `"a\u00a0b"` (non-breaking space) still gives `"a-b"`.
- Whether to drop letters like this or transliterate them is the owner's call. The PR says it chose to drop them.

**Not a finding, but unverified:** `tests/test_slug.py` uses `from slug import ...` and there is no `tests/__init__.py`. Whether the tests are discovered and import correctly depends on how CI runs them, for example `python -m unittest discover -s tests` from the repo root. I did not see the CI config, so I cannot confirm the six tests run in CI.

**FILES NEEDED BUT NOT PROVIDED:**
- The callers of `slugify` (URL creation and routing), which I need to assess finding 3.
- The CI/test configuration and check results.
- Commit metadata (trailers) for the author's identity.

## Close-out

Adjudication is the author's job. As the reviewer, I do not adjudicate my own findings.

**ADJUDICATION:** Pending. All three findings need a written decision: Accepted (with a fix commit and a regression test), Deferred (with an issue link; allowed because all three are P2/P3), or Rejected (with evidence).

**VERIFIED AFTER FIXES:** Nothing yet. Any fix should get a targeted read of its own diff plus its new tests, not a second full round.

**MERGE RECOMMENDATION:** Not yet. Merge after adjudication.
- No P0 or P1 findings, so nothing blocks merge on severity.
- These are still open:
  - written decisions on findings 1–3;
  - an owner decision on how to handle non-ASCII letters (drop or separate) and empty slugs;
  - CI checks, which I have not seen and which must be present and green. "All pass" is a claim, not evidence.

```json
{
  "verdict": "merge after adjudication: no blockers; findings 1-3 need written decisions, CI checks unseen and must be present and green",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "traced by reading code; not executed",
      "location": "slug.py:13",
      "scenario": "Non-ASCII letters inside a word are replaced by a hyphen rather than dropped as documented: 'Zürich' -> 'z-rich', 'naïve' -> 'na-ve'. test_non_ascii_dropped only covers a word-final é, which hides this.",
      "fix": "Drop non-ASCII alphanumerics before lowercasing (keep non-ASCII whitespace/punctuation as separators), or change the docstring to say they act as separators; add tests for 'Zürich' and 'naïve café'."
    },
    {
      "severity": "P3",
      "evidence_level": "traced by reading code against documented str.lower() Unicode mappings; not executed",
      "location": "slug.py:13",
      "scenario": "lower() runs before filtering, so some non-ASCII characters become ASCII: KELVIN SIGN U+212A -> 'k'; 'İstanbul' -> 'i-stanbul'. Contradicts 'dropped, not transliterated'.",
      "fix": "Filter non-ASCII alphanumerics before calling lower(); add tests slugify('\\u212a') == '' and slugify('İstanbul') == 'stanbul'."
    },
    {
      "severity": "P2",
      "evidence_level": "inferred; callers not provided",
      "location": "slug.py:14",
      "scenario": "Titles made only of non-Latin script or symbols ('你好世界', 'Привет', '!!!') return '', so a URL builder would produce empty or colliding slugs such as /posts/ for user-supplied titles.",
      "fix": "Owner decision: raise ValueError on empty result, or have callers apply a fallback (id-based slug); add a caller-level test that such titles get distinct non-empty URLs."
    }
  ]
}
```