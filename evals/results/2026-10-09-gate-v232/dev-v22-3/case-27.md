# Redteam review: PR #70, "harden slugify"

**Review conditions:** No tools were available, so nothing was run and the validator was not executed. Every result below comes from reading the code by hand. This was a single-reviewer pass with no subagent or other-vendor seats. Anything that depends on Python runtime behaviour is labelled PROBABLE, not CONFIRMED.

**VERDICT: SHIP.** The patch meets all four requirements in the request. The only confirmed problem is a Low mismatch between the docstring and actual behaviour for a few Unicode characters, which does not break the safety contract.

**CONFIDENCE: medium.** Three things limit it:
- No code or tests were run.
- The callers of `slugify` were not supplied.
- How "all pass" was produced is unknown.

**INPUTS LEDGER**

| Item | Status | Matters? |
|---|---|---|
| request.md, context.md | seen | yes |
| PR.md | seen | yes |
| change.patch | seen | yes |
| base/slug.py, base/README.md | seen | yes |
| Callers of `slugify` (URL creation, stored slugs, lookups) | not supplied | yes, for blast radius (S2, S3) |
| Test runner or CI config and the "all pass" output | not supplied | yes, for the PR's claim that tests pass (S1) |
| Head 9d4e1a7 and merge base c82f0b3 | not openable | no; the patch applies cleanly to base/slug.py as shown |

**COVERAGE**
- **Checked:**
  - `slug.py:slugify`: main path plus hostile inputs (empty string, symbols only, long input, non-ASCII, None, bytes, leading and trailing separators).
  - All six tests in `tests/test_slug.py`: traced each one, and for each asked whether it would fail if the code it guards were removed.
  - Every claim in PR.md.
- **Not checked:** callers, the test runner configuration, and runtime execution.

**SEATS AND GATE:** One reviewer only (same-vendor, no subagent). The sensitivity gate passed: there is no personal or confidential data in the work. No other-vendor seats ran, because none were requested and the stakes are standard.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Low | PROBABLE | B | `slug.py`: `re.sub(r"[^a-z0-9]+", "-", text.lower())` and the docstring "Letters outside a-z … are dropped" | `lower()` runs *before* the ASCII filter. A few non-ASCII characters therefore lowercase into ASCII and are kept rather than dropped. | A title containing the Kelvin sign "K" (U+212A) gives `"k"`, not `""`. "İstanbul" (U+0130) lowercases to "i" plus a combining dot, which gives `"i-stanbul"`, a garbled slug with a stray hyphen. The output is still only a-z, 0-9 and single hyphens, so the safety contract holds. Only the documented behaviour is wrong. | Filter before lowercasing: `re.sub(r"[^A-Za-z0-9]+", "-", text).lower().strip("-")`. Alternatively, change the docstring to match the current behaviour. Tests to add: `assertEqual(slugify("\u212a"), "")` and `assertEqual(slugify("\u0130stanbul"), "stanbul")`. Both should fail on the current code. | a: yes, b: no, c: no, d: no |

## Needs validation

- **S1, the "Six tests, all pass" claim.** `tests/test_slug.py` sits in `tests/`, and the patch adds no `tests/__init__.py`. Running `python -m unittest discover` from the repo root may then report "Ran 0 tests … OK", which looks identical to a real pass. Running with `-s tests` from the root should work, because the root is on `sys.path`.
  - **What would settle it:** the exact command used and its output showing "Ran 6 tests".
- **S2, empty slug.** Inputs such as `"!!!"`, `""` or an all-CJK title return `""`. That behaviour is documented and tested. If a caller builds a URL as `/posts/{slug}`, though, an empty slug could collide with or route to the index page.
  - **What would settle it:** whether the callers reject or replace an empty slug.
- **S3, changed output for existing titles.** The old code mapped `"foo_bar"` to `"foo_bar"` and `"Hello, World"` to `"hello,-world"`. The new code gives `"foo-bar"` and `"hello-world"`. If a caller looks up existing records by recomputing `slugify(title)`, links created under the old slugs would stop resolving.
  - **What would settle it:** whether slugs are stored once or recomputed, and whether existing data uses the old format.

## Refuted

- **R1, "Truncation can leave a trailing hyphen or exceed the cap."** Refuted. `slug[:MAX_LEN].rstrip("-")` gives a length of at most 80 that never ends in a hyphen. A leading hyphen is impossible because `.strip("-")` runs before the slice.
- **R2, "Double hyphens can survive."** Refuted. The `+` in `[^a-z0-9]+` collapses each run of separators into one hyphen. Original hyphens are themselves non-allowed characters, so they get merged into those runs too.
- **R3, "The length-cap test is vacuous."** Refuted.
  - The input `"word " * 40` becomes `"word-…-word"`, which is 199 characters.
  - Slicing to 80 characters gives exactly 16 copies of `"word-"`, ending in `-`.
  - The test therefore goes red if either the cap or the `rstrip` is removed.
- **R4, "The TypeError test would pass without the check."** Refuted. Without the `isinstance` check, `None.lower()` raises `AttributeError`, so `assertRaises(TypeError)` would fail.
- **R5, "Regex DoS on huge input."** Refuted. The pattern is a single negated character class with no nesting, so matching is linear in the input length.

## What holds up

- The `isinstance` check runs first, and it rejects `None`, `int` and `bytes` with a clear message.
- The output alphabet, the single-hyphen rule, the edge-hyphen stripping and the 80-character cap are all correct by construction.
- PR.md matches the code: the test count really is six, and the "dropped, not transliterated" behaviour is both documented and tested, apart from the edge case in F1.
- The patch adds nothing beyond what the request asked for.

## Unverified claims

- **"All pass":** run the tests from the repo root (see S1) and confirm the output says "Ran 6 tests".
- **The Unicode lowercasing behaviour in F1:** run `"\u212a".lower() == "k"` in Python to confirm it.

## Questions for the author

1. What command produced "all pass"?
2. Do callers handle an empty slug?
3. Are slugs stored once, or recomputed from titles?

## Decision-maker summary

The change does what was asked and is safe to merge. Before or soon after merging, confirm that the tests were actually discovered and run, and that callers handle an empty slug and the changed slugs for existing titles. If you proceed without checking, the main risk is broken links or empty URL segments in callers, not unsafe output.

## Owner summary

The update makes web-address names built from titles safe and predictable, and it looks correct. A couple of unusual foreign letters behave slightly differently from what the code's notes say, which is cosmetic. Before relying on it, someone should confirm the tests really ran, and that titles with no usable letters, or titles that already have older addresses, are handled sensibly.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "callers of slugify", "status": "not_seen", "matters": true},
    {"item": "test runner command/output", "status": "not_seen", "matters": true},
    {"item": "commits 9d4e1a7 / c82f0b3", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "slug.py", "kind": "file"},
      {"unit": "slug.py:slugify", "kind": "function"},
      {"unit": "tests/test_slug.py", "kind": "file"},
      {"unit": "PR.md", "kind": "file"},
      {"unit": "base/README.md", "kind": "file"}
    ],
    "not_checked": [
      {"unit": "callers of slugify", "reason": "not supplied"},
      {"unit": "test execution", "reason": "no tools in session"}
    ]
  },
  "verdict_reason": "Meets all four requirements; only a Low docstring/behaviour mismatch on rare Unicode.",
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Low", "evidence_level": "PROBABLE", "track": "B",
     "location": "slug.py: re.sub(r\"[^a-z0-9]+\", \"-\", text.lower())",
     "scenario": "Kelvin sign U+212A lowercases to 'k' and is kept; 'İstanbul' becomes 'i-stanbul'. The docstring says non-a-z letters are dropped.",
     "fix": "Filter before lowercasing: re.sub(r\"[^A-Za-z0-9]+\", \"-\", text).lower().strip(\"-\"), or amend the docstring.",
     "answers": {"a": true, "b": false, "c": false, "d": false},
     "reproduction": "assertEqual(slugify('\\u212a'), ''); assertEqual(slugify('\\u0130stanbul'), 'stanbul'); both expected to fail on current code."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "tests/test_slug.py (no tests/__init__.py)",
     "suspicion": "Default unittest discovery from the repo root may run 0 tests and still report OK.",
     "unresolved_fact": "The exact test command and whether its output shows 'Ran 6 tests'."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "slug.py docstring: 'Input with no usable characters gives \"\"'",
     "suspicion": "An empty slug may yield a malformed or colliding URL in callers.",
     "unresolved_fact": "Whether callers reject or replace an empty slug."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "slug.py:slugify (behaviour change vs base)",
     "suspicion": "Recomputed slugs for existing titles differ from the old ones, which would break existing links.",
     "unresolved_fact": "Whether slugs are stored or recomputed, and whether data uses the old format."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Truncation can leave a trailing hyphen or exceed 80 characters.", "evidence": "slug[:MAX_LEN].rstrip('-') runs after strip('-')."},
    {"id": "R2", "candidate": "Double hyphens can survive.", "evidence": "[^a-z0-9]+ collapses every run of non-allowed characters, original hyphens included."},
    {"id": "R3", "candidate": "The length-cap test is vacuous.", "evidence": "'word '*40 gives 199 characters; [:80] ends in '-', so the test fails if either the cap or the rstrip is removed."},
    {"id": "R4", "candidate": "The TypeError test would pass without the check.", "evidence": "None.lower() raises AttributeError, not TypeError."},
    {"id": "R5", "candidate": "Regex DoS on huge input.", "evidence": "A single negated character class with no nesting matches in linear time."}
  ]
}
```