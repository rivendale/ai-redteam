# Review report: PR #70, harden slugify

**REVIEWED:** PR #70. Head `9d4e1a7`, merge base `c82f0b3`, both taken from PR.md. change.patch carries no SHAs, so I could not confirm it matches that head. I reviewed the patch against `base/slug.py`.

**TIER:** Standard. It is an ordinary code change to a small pure function, with no auth, secrets, network, migration or personal-data handling. The output goes into URLs, but the function only restricts characters. No data left this session, so Step 3 does not apply.

**REVIEWERS:** this is a single read-only review by a fresh instance (Sonnet 5.5) that did not write the change. No commit trailers were provided, so the author is **unknown**. I had no tools, so nothing was run. The "Six tests, all pass" claim is hand-traced, not executed.

**Requirements check:** the patch meets all three parts of the request and adds nothing extra. Output is only `[a-z0-9]` with single hyphens, capped at 80 characters, and non-strings raise `TypeError("text must be a string")`.

Hand trace of the six tests:
- `"Hello, World!"` gives `hello-world`.
- `"  a   b -- c  "` gives `a-b-c`.
- `""` and `"!!!"` both give `""`.
- `"word " * 40` is cut to 80 characters ending in `-`, then `rstrip` leaves 79. That is ≤ 80 and does not end in a hyphen.
- `café au lait` gives `caf-au-lait`.
- `None` raises `TypeError`.

All six should pass. The invariants (no leading, trailing or double hyphen, only `[a-z0-9]`) hold by construction. The regex collapses runs, `strip("-")` runs before the cut, and `rstrip("-")` runs after it.

There was no text addressed to the reviewer in the PR, and there are no cited sources, dependencies or consent wording.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P3 | `slug.py:9` (docstring) and `slug.py:13` | The docstring and PR.md say non-a-z letters are "dropped". The code replaces each run of them with a hyphen, so they act as separators. `slugify("naïve")` gives `na-ve`, not `nave`, and `slugify("über")` gives `ber`. `test_non_ascii_dropped` cannot tell the two behaviours apart, because the é in `café au lait` sits next to a space and both readings give `caf-au-lait`. The claim "stated and tested" is therefore only half true. | `assertEqual(slugify("na\u00efve"), "na-ve")`, or `"nave"` if dropping is the intended behaviour, with the code changed to match. |
| 2 | P3 | `slug.py:13` (`text.lower()`) | Unicode lowercasing runs before the filter. `"\u0130stanbul"` (İ) lowercases to `i` plus a combining dot, giving `i-stanbul`. `"\u212a"` (Kelvin sign) lowercases to ASCII `k`, so it is kept rather than dropped. Neither is a security issue, but both contradict the documented rule that letters outside a-z are dropped. This is from my knowledge of Python's `str.lower`, not a run. | `assertEqual(slugify("\u0130stanbul"), "i-stanbul")` and `assertEqual(slugify("\u212a"), "k")`, to pin the behaviour or fail until it is changed. |
| 3 | P3 | `tests/test_slug.py:19-22` | The cap test only checks `len ≤ 80` and "no trailing hyphen". A cap changed to 10 or 0 would still pass. The hard cut inside a word is untested. | `slugify("a"*100) == "a"*80` and `slugify("a"*79 + " b") == "a"*79`. |
| 4 | P3 (UNVERIFIED) | `tests/test_slug.py:2` | `from slug import ...` only works if the repo root is on `sys.path`. Running `python tests/test_slug.py` or `unittest discover -s tests` puts `tests/` on the path instead and would raise `ImportError`. I cannot see the repo's test runner or CI config. | Run the suite the way CI does, from a clean checkout. |

**Observation, not a finding:** a title with no a-z or 0-9 characters (for example all CJK) returns `""`. This is documented, but callers building URLs must handle an empty slug. Truncation and dropping also make slugs non-unique. Both are caller concerns outside this diff.

**FILES NEEDED BUT NOT PROVIDED:** CI or check status, the repo's test-runner config, the commit trailers, and callers of `slugify`. Only `slug.py` and `README.md` were in `base/`.

**Close-out:** not written. The author adjudicates the findings and whoever closes the PR writes it (Step 7).

**Preliminary merge view:** there are no P0 or P1 findings. Findings #1 and #2 are cheap to fix in this PR (align the docstring, or fix the code, and add the pin tests). Merge should wait for each finding to have a written decision, and for CI to be shown present and green, which I cannot see.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P3",
      "evidence_level": "read from code and test; not executed",
      "location": "slug.py:9, slug.py:13",
      "scenario": "Docstring and PR say non-a-z letters are dropped, but re.sub turns each run into a hyphen separator: slugify('naïve') -> 'na-ve', not 'nave'. test_non_ascii_dropped passes under either behavior because the é is adjacent to a space.",
      "fix": "Either change the docstring/PR text to say such characters act as separators, or drop them before collapsing; add assertEqual(slugify('na\\u00efve'), <chosen result>)."
    },
    {
      "severity": "P3",
      "evidence_level": "reasoned from Python str.lower semantics; not executed",
      "location": "slug.py:13",
      "scenario": "text.lower() runs before the a-z filter: 'İstanbul' -> 'i\\u0307stanbul' -> 'i-stanbul'; Kelvin sign U+212A lowercases to ASCII 'k' and is kept, contradicting 'letters outside a-z are dropped'.",
      "fix": "Decide the intended behavior and pin it with tests; optionally filter on the original text with re.IGNORECASE or ASCII-only lowercasing."
    },
    {
      "severity": "P3",
      "evidence_level": "read from test file",
      "location": "tests/test_slug.py:19-22",
      "scenario": "Cap test asserts only len <= MAX_LEN and no trailing hyphen, so a wrong or zero cap still passes; hard mid-word cut is untested.",
      "fix": "Add assertEqual(slugify('a'*100), 'a'*80) and assertEqual(slugify('a'*79 + ' b'), 'a'*79)."
    },
    {
      "severity": "P3",
      "evidence_level": "UNVERIFIED; test runner config not provided",
      "location": "tests/test_slug.py:2",
      "scenario": "'from slug import ...' needs the repo root on sys.path; running the file directly or 'unittest discover -s tests' would raise ImportError.",
      "fix": "Confirm CI's invocation from a clean checkout; add tests/__init__.py or document 'python -m unittest' from the repo root if needed."
    }
  ]
}
```