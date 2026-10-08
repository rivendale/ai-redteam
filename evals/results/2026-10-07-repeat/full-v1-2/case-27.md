**Review mode:** I did this review myself, without tools. The work did not come from this conversation, so there is no anchoring from authorship. But I could not run anything. Every behavioral claim below comes from tracing the code by hand, and the PR's statement that the tests pass is unverified.

## Pass 1: Reconstruct

PR #70 replaces `text.lower().replace(" ", "-")` with a hardened version:
- It rejects non-`str` input with `TypeError`.
- It lowercases the input and collapses every run of characters outside `[a-z0-9]` into one hyphen.
- It strips hyphens from both ends, truncates to 80 characters, and strips trailing hyphens again.

The PR says letters outside a-z are "dropped, not transliterated" and that six tests pass. For the PR to be correct, three things must hold:
- `[^a-z0-9]` matches only ASCII ranges in Python's `re`. It does.
- Truncation cannot create a leading hyphen or a double hyphen. It cannot.
- The documented behavior for non-ASCII letters matches what the code actually does. This is the weak point.

There are also unstated assumptions:
- Callers can handle an empty-string result.
- No stored URLs depend on the old slug output.

## Pass 2: Attack (Track B)

**Correctness of the output contract against the request:**
- **Alphabet:** the pattern `[^a-z0-9]+` uses literal ASCII ranges, not `\w` or `\d`, so non-ASCII digits and letters cannot get through.
- **Single hyphens:** runs collapse to one hyphen, and slicing cannot create a new run.
- **Ends:** `.strip("-")` runs before truncation and `.rstrip("-")` runs after, so the result never starts or ends with a hyphen.
- **Length:** the result is at most 80 characters.
- **Type error:** `None`, `bytes` and numbers all raise `TypeError`.

All of these hold.

**Hostile inputs, traced by hand:**
- `"naïve"`: lowercases to `naïve`. The `ï` is one run of non-matching characters and becomes `-`, giving `"na-ve"`. The letter is **replaced by a separator**, not dropped, which contradicts the docstring and PR.md. The existing test only covers `é` at the end of a word (`café au lait`). There, the `é` and the following space merge into one run, so the test cannot tell the difference.
- `"İstanbul"`: `str.lower()` maps U+0130 to `i` plus U+0307 (combining dot). The combining dot then becomes a hyphen, giving `"i-stanbul"`. This is the same root cause. It depends on the Unicode case tables, so I rate it PROBABLE.
- `"word " * 40`: produces 199 characters. Slicing to 80 ends on `-`, and `rstrip` brings it to 79. The cap test does exercise the `rstrip` path.
- A very large input: the whole string is lowercased and regex-processed before truncation. The work is linear, so there is no catastrophic backtracking, just wasted effort. This is Low.

**Blast radius:**
- The old function kept every non-space character. For example, `"C++ Guide"` gave `"c++-guide"`, and the new version gives `"c-guide"`.
- If slugs are recomputed from titles rather than stored, existing URLs will change.
- The exception type changes from `AttributeError` to `TypeError`, which matters for any caller that catches the old one.
- The PR mentions none of this.

**Tests:**
- They assert real values, apart from the length test, which checks only bounds.
- No test covers a non-ASCII letter in the middle of a word.
- No test covers input that produces exactly 80 characters.
- `tests/` has no `__init__.py`. Running `python -m unittest` from the repository root may therefore discover zero tests, depending on the Python version. That makes "all pass" depend on how they were run.

## Output

**VERDICT: SHIP WITH FIXES.** The code meets every requirement in the request. However, its documented contract for non-ASCII letters ("dropped") does not match its behavior (they become word breaks), and the test suite is built in a way that hides this.

**CONFIDENCE IN VERDICT: medium.** I could not run the code or the tests, and the `İ` case relies on Unicode tables that I recalled rather than checked.

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Medium | CONFIRMED (trace) | `slug.py` docstring "Letters outside a-z … are dropped"; PR.md same claim; `re.sub(r"[^a-z0-9]+", "-", …)` | Non-ASCII letters are turned into hyphens, not dropped, so words are split. | `slugify("naïve")` returns `"na-ve"` where the documentation implies `"nave"`. `"Ångström"` returns `"ngstr-m"`. | Choose a behavior. To drop the letters, first run `re.sub(r"[^a-z0-9\s-]", "", …)` and then collapse whitespace and hyphens. Otherwise, rewrite the docstring and PR to say "act as separators". Add the test `assertEqual(slugify("naïve"), <chosen>)`. |
| 2 | Medium | PROBABLE | `test_non_ascii_dropped` | The only non-ASCII test puts the letter next to a space, where "dropped" and "replaced" give the same output. The test passes under either behavior, so it does not support the claim. | A future change, or the current mismatch, goes unnoticed. | Add cases with the letter mid-word (`"naïve"`) and at the start (`"école"`). |
| 3 | Medium | UNVERIFIED | Change from `base/slug.py` to the new `slugify` | Output changes for any title that contains punctuation other than spaces, or repeated spaces. The PR does not mention this. | If slugs are regenerated from titles, existing URLs such as `/c++-guide` return 404 after merge. | Confirm whether slugs are stored or recomputed. If recomputed, add redirects or a migration note. |
| 4 | Low | PROBABLE | `text.lower()` before the regex | Characters whose lowercase form contains several code points produce extra hyphens. | `slugify("İstanbul")` returns `"i-stanbul"`. | If finding #1 is fixed by removing the characters, this goes away too. Otherwise, apply `unicodedata.normalize("NFKD")` and strip combining marks, or document it. |
| 5 | Low | PROBABLE | `return slug[:MAX_LEN]…`; docstring 'gives ""' | An empty result is valid and documented, but URL construction downstream may not handle it. Different titles can also collide (`"C++"` and `"C#"` both give `"c"`). | A title made only of symbols or CJK characters produces the empty slug `""`, which may create the URL `/posts/`. | Confirm that callers reject or deduplicate empty and colliding slugs, or raise `ValueError` on an empty result. |
| 6 | Low | UNVERIFIED | `tests/test_slug.py` (no `tests/__init__.py`); PR.md "all pass" | The test run is not reproducible as described. Default discovery may skip `tests/`. | CI runs `python -m unittest`, collects 0 tests, and reports success. | State the exact command, for example `python -m unittest discover -s tests -t .`, or add `tests/__init__.py`. Then confirm the test count is 6. |
| 7 | Low | PROBABLE | `re.sub` on the full input before `[:MAX_LEN]` | Unbounded input is fully processed even though the output is capped. | A multi-megabyte "title" costs CPU and memory on every call. | Pre-truncate the input to a generous bound, such as `text[:MAX_LEN * 8]`, or enforce a limit on title length upstream. |

**WHAT HOLDS UP**
- The output alphabet is strictly `[a-z0-9-]`, because the ranges are ASCII literals.
- Collapsing to single hyphens is correct, including runs that mix spaces and hyphens.
- There is never a leading or trailing hyphen, including after truncation.
- The cap of 80 or fewer characters is correct.
- Non-strings get a `TypeError` with a clear message.
- The regex cannot backtrack catastrophically.
- Tracing the five non-length tests by hand, each produces the asserted value.

**UNVERIFIED CLAIMS**
- "Six tests, all pass": run `python -m unittest discover -s tests -t . -v` and confirm that 6 tests run and all pass.
- The `İ` behavior: run `python -c 'print(len("İ".lower()))'`. If it prints 2, finding #4 is confirmed.
- No dependence on old slugs: search for the callers of `slugify` and check whether slugs are persisted.

**QUESTIONS FOR THE AUTHOR**
1. Should `naïve` become `nave` or `na-ve`? The answer decides whether you fix the code or the documentation.
2. Are slugs stored when an item is created, or regenerated from titles?
3. What command produced "all pass"?

**DECISION-MAKER SUMMARY**
The function meets every requirement that was asked for and can be merged safely once the non-ASCII behavior is made to match its documentation and covered by a mid-word test. Before merging, confirm that existing slugs are stored rather than recomputed. If you merge as is, the remaining risk is cosmetic slugs like `na-ve`, plus possibly broken URLs for any titles with punctuation that are regenerated.

```json
{
  "verdict": "SHIP WITH FIXES",
  "findings": [
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "slug.py docstring and PR.md 'Letters outside a-z ... are dropped'; re.sub(r\"[^a-z0-9]+\", \"-\", ...)",
      "scenario": "slugify(\"naïve\") returns \"na-ve\", not \"nave\"; non-ASCII letters act as word separators, contradicting the documented contract.",
      "fix": "Decide on the behavior: either strip non-[a-z0-9\\s-] characters before collapsing separators, or change the docstring/PR to say they act as separators; add assertEqual(slugify(\"naïve\"), <chosen>)."
    },
    {
      "severity": "Medium",
      "evidence_level": "PROBABLE",
      "location": "tests/test_slug.py test_non_ascii_dropped",
      "scenario": "The only non-ASCII case puts é before a space, where 'dropped' and 'replaced' give the same output, so the test cannot detect the mismatch.",
      "fix": "Add mid-word and leading non-ASCII cases (\"naïve\", \"école\")."
    },
    {
      "severity": "Medium",
      "evidence_level": "UNVERIFIED",
      "location": "base/slug.py -> new slugify (behavior change)",
      "scenario": "If slugs are regenerated from titles, '/c++-guide' becomes '/c-guide' and existing URLs 404; callers catching AttributeError now get TypeError.",
      "fix": "Confirm slugs are persisted; otherwise add redirects or a migration note to the PR."
    },
    {
      "severity": "Low",
      "evidence_level": "PROBABLE",
      "location": "text.lower() before the regex",
      "scenario": "slugify(\"İstanbul\") returns \"i-stanbul\" because U+0130 lowercases to i + U+0307 and the combining dot becomes a hyphen.",
      "fix": "Resolved by removing non-ASCII characters (finding 1), or NFKD-normalize and strip combining marks, or document it."
    },
    {
      "severity": "Low",
      "evidence_level": "PROBABLE",
      "location": "return value; docstring 'Input with no usable characters gives \"\"'",
      "scenario": "Titles made only of symbols or CJK give \"\", and distinct titles collide (\"C++\" and \"C#\" both give \"c\"); callers may build '/posts/' or duplicate URLs.",
      "fix": "Confirm callers reject or deduplicate empty and colliding slugs, or raise ValueError on an empty result."
    },
    {
      "severity": "Low",
      "evidence_level": "UNVERIFIED",
      "location": "tests/test_slug.py (no tests/__init__.py); PR.md 'Six tests, all pass'",
      "scenario": "Default 'python -m unittest' discovery may skip tests/ and report success with 0 tests.",
      "fix": "Document the run command (python -m unittest discover -s tests -t .) or add tests/__init__.py; confirm 6 tests run."
    },
    {
      "severity": "Low",
      "evidence_level": "PROBABLE",
      "location": "re.sub over full input before slug[:MAX_LEN]",
      "scenario": "A multi-megabyte title is fully lowercased and regex-processed even though the output is capped at 80 characters.",
      "fix": "Pre-truncate input (e.g. text[:MAX_LEN * 8]) or cap title length upstream."
    }
  ]
}
```