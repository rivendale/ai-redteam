VERDICT: **SHIP WITH FIXES.** The patch meets every requested property (only a-z, 0-9 and single hyphens, an 80-character cap, a clear TypeError), but the docstring and PR say non-ASCII letters are "dropped", and the code does not do exactly that.

CONFIDENCE: **medium.** I had no tools, so I could not run the code or the tests. Every behavior below comes from reading the code and tracing Python's `str.lower` and `re.sub` by hand. No independent subagent was available. The work was not written in this conversation, so anchoring risk is low.

INPUTS LEDGER:
- **Seen:** request.md, context.md, PR.md, base/README.md, base/slug.py, change.patch (slug.py and tests/test_slug.py).
- **Not seen:**
  - The callers of `slugify`. This matters for the blast-radius questions under NEEDS VALIDATION.
  - CI or test output for head 9d4e1a7. This matters a little: "six tests, all pass" is UNVERIFIED.
  - Any slugs already stored. This matters if slugs are recomputed on lookup.

COVERAGE:
- **Checked:**
  - slug.py `slugify`: type check, lowercasing, regex, strip, truncation and rstrip.
  - All 6 tests in tests/test_slug.py, read against the code.
  - Every claim in PR.md.
  - The three requirements in the request.
- **Not checked:** callers, the test runner and CI configuration, and runtime behavior (no tools).

SEATS AND GATE: one local reviewer ran (this session; no subagent, no cross-vendor seats). Gate: not sensitive. The work is a public-style utility function with no personal data.

FINDINGS:

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED (traced) | B | slug.py docstring; PR.md "Letters outside a-z are dropped"; tests/test_slug.py `test_non_ascii_dropped` | A non-ASCII letter in the middle of a word is replaced by a hyphen and splits the word. The test only covers a letter at the end of a word, where the hyphen merges with the following space. | `slugify("résumé")` returns `"r-sum"` and `slugify("naïve")` returns `"na-ve"`, not the `"rsum"` / `"nave"` that "dropped" implies. A maintainer relying on the docstring gets a surprise. The output is still valid. | Either change the docstring and PR text to "replaced by a hyphen", or drop non-ASCII before collapsing (e.g. `re.sub(r"[^a-z0-9\s-]", "", ...)` first). Add a test with the expected output stated: `assertEqual(slugify("naïve"), ...)`. | a Y, b Y, c N, d N |
| F2 | Low | CONFIRMED (traced) | B | slug.py `text.lower()` | `str.lower()` maps some non-ASCII code points into a-z, so they are transliterated, not dropped. This contradicts the docstring. | `slugify("\u212A")` (Kelvin sign) returns `"k"`. `slugify("İstanbul")` returns `"i-stanbul"`, because `"İ".lower()` is `"i"` plus U+0307. | Document this, or filter to ASCII before lowercasing. Add tests for both inputs. | a Y, b Y, c N, d N |
| F3 | Low | CONFIRMED (traced) | B | slug.py `re.sub(...)` before `slug[:MAX_LEN]` | The whole input is lowercased and regex-processed before the cap is applied. The regex is linear (no catastrophic backtracking), so cost grows only with input size. | A multi-megabyte "title" costs O(n) CPU and memory per call. The impact depends on whether there is an upstream size limit. | Optionally cap the raw input (e.g. `text[:MAX_LEN * 4]`) before processing. Add a test with a 10 MB input and expect `len <= 80`. | a Y, b Y, c N, d N |

NEEDS VALIDATION:
- **S1, empty slug.** `""` is returned for `""`, `"!!!"` or all-non-ASCII titles such as `"日本語"`. Unresolved fact: do callers reject or fall back on an empty slug, or would they create the URL `/posts/` and collide with other empty slugs?
- **S2, behavior change for existing data.** The old function kept punctuation and non-ASCII, so old and new slugs differ for the same title. Unresolved fact: are slugs stored, or recomputed on lookup? If recomputed, existing links break.
- **S3, exception type changed.** `None` used to raise AttributeError and now raises TypeError. Unresolved fact: does any caller catch AttributeError around `slugify`?

REFUTED:
- **"Truncation can leave a trailing hyphen."** `.rstrip("-")` runs after the slice. The cap test (`"word " * 40`) slices at index 80, which lands on a hyphen, so the test really exercises the rstrip.
- **"Truncation or strip can produce a double hyphen."** Runs are collapsed by `+` before slicing, and slicing cannot join two hyphens.
- **"Unicode digits pass through `0-9`."** An explicit `[a-z0-9]` range in a str pattern is ASCII-only, unlike `\d`.

WHAT HOLDS UP:
- The output alphabet is enforced by a single negated class.
- Leading and trailing hyphens are stripped both before and after truncation.
- The length cap is correct, and the cap test would go red if the cap or the rstrip were removed.
- The type check comes first and raises a clear `TypeError`. `bytes` is also rejected.
- The regex has no backtracking risk.

UNVERIFIED CLAIMS:
- "Six tests, all pass." Confirm with `python -m unittest discover -s tests -t .` from the repo root on 9d4e1a7.
- Whether the tests import `slug` correctly under the project's CI command. There is no `tests/__init__.py`, so this depends on `sys.path`.

QUESTIONS FOR THE AUTHOR:
1. Should `"naïve"` become `"nave"` or `"na-ve"`?
2. How do callers handle an empty slug?
3. Are slugs stored, or recomputed on lookup?

DECISION-MAKER SUMMARY: The function now meets all three requested safety properties and can merge after a docstring or behavior fix and one extra test for accented letters inside a word. The risk if it merges as is: the documented "dropped" behavior is wrong for some inputs, and empty slugs and existing links need a caller-side check.

OWNER SUMMARY: The change does what was asked: URL slugs now contain only safe characters, have a length limit, and give a clear error for bad input. One description is inaccurate, because accented letters in the middle of a word become a hyphen rather than disappearing, and that needs a wording fix or a small code change plus a test. Someone should also check what happens when a title produces an empty slug and whether existing links depend on the old format.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "PR.md", "status": "seen", "matters": true},
    {"item": "change.patch", "status": "seen", "matters": true},
    {"item": "base/slug.py", "status": "seen", "matters": true},
    {"item": "base/README.md", "status": "seen", "matters": false},
    {"item": "callers of slugify", "status": "not_seen", "matters": true},
    {"item": "CI/test output for 9d4e1a7", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "slug.py", "kind": "file"},
      {"unit": "slug.py:slugify", "kind": "function"},
      {"unit": "tests/test_slug.py", "kind": "file"},
      {"unit": "PR.md", "kind": "file"},
      {"unit": "base/README.md", "kind": "file"},
      {"unit": "PR.md: six tests, all pass", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "callers of slugify", "reason": "not supplied"},
      {"unit": "test execution", "reason": "no tools in session"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "slug.py docstring; PR.md; tests/test_slug.py:test_non_ascii_dropped",
     "scenario": "slugify('résumé') returns 'r-sum' and slugify('naïve') returns 'na-ve': mid-word non-ASCII letters become hyphens, contradicting the documented 'dropped' behavior; the test only covers an end-of-word letter.",
     "fix": "Correct the docstring/PR to say 'replaced by a hyphen', or remove non-ASCII before collapsing; add a mid-word test with the expected output.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "python -c \"from slug import slugify; print(slugify('naïve'))\"; documented expectation 'nave', observed 'na-ve'."},
    {"id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "slug.py:slugify text.lower()",
     "scenario": "str.lower maps U+212A KELVIN SIGN to 'k' and 'İ' to 'i'+U+0307, so slugify('İstanbul') returns 'i-stanbul': some non-ASCII is transliterated, not dropped.",
     "fix": "Filter to ASCII before lowercasing or document the behavior; add tests for '\\u212A' and 'İstanbul'.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "python -c \"from slug import slugify; print(slugify('\\u212A'))\"; docstring implies '', observed 'k'."},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "slug.py:slugify re.sub before slug[:MAX_LEN]",
     "scenario": "A multi-megabyte title is fully lowercased and regex-processed before truncation, costing O(n) CPU and memory per call.",
     "fix": "Cap raw input length (e.g. text[:MAX_LEN*4]) before processing.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Time slugify('a ' * 5_000_000); observe work proportional to input although output is at most 80 chars."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "slug.py:slugify return ''",
     "suspicion": "Empty slugs from symbol-only or non-Latin titles may produce colliding or empty URLs.",
     "unresolved_fact": "Whether callers reject or fall back on an empty slug."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "slug.py:slugify (behavior change vs base)",
     "suspicion": "Existing links break if slugs are recomputed from titles.",
     "unresolved_fact": "Whether slugs are persisted or recomputed on lookup."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "slug.py:slugify TypeError",
     "suspicion": "Callers catching AttributeError for None input would now miss the TypeError.",
     "unresolved_fact": "Whether any caller catches AttributeError around slugify."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Truncation can leave a trailing hyphen.",
     "evidence": "rstrip('-') runs after slug[:MAX_LEN]; the cap test slices at a hyphen and asserts no trailing hyphen."},
    {"id": "R2", "candidate": "Output can contain double hyphens.",
     "evidence": "[^a-z0-9]+ collapses runs before slicing; slicing cannot join hyphens."},
    {"id": "R3", "candidate": "Unicode digits pass the filter.",
     "evidence": "The explicit [a-z0-9] range is ASCII-only, unlike \\d."}
  ]
}
```