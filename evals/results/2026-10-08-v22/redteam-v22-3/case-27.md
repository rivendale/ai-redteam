# Redteam review: PR #70 "harden slugify"

**Note:** This is a same-context review with no tools. I could not run code or tests, so every trace below was done by reading. Anchoring risk is lower than usual because I did not write this work. For anything high-stakes, re-run in a session that can execute the tests.

**VERDICT: SHIP.** The patch meets every part of the request (a-z, 0-9, single hyphens, an 80-character cap, TypeError for non-strings), and the only confirmed problems are Low: docstring and PR wording, plus one test gap.

**CONFIDENCE: medium.** Three things limit it:
- I could not run the tests, so the claim "six tests, all pass" is unverified.
- The callers of `slugify` were not supplied.
- I could not open the head or base commits.

**INPUTS LEDGER**

| Item | Status | Matters? |
|---|---|---|
| request.md (verbatim request) | seen | yes |
| context.md | seen | yes |
| PR.md | seen | yes |
| change.patch | seen | yes |
| base/slug.py, base/README.md | seen | yes |
| Commits 9d4e1a7 and c82f0b3 | not openable | low: the patch and base are supplied |
| Test run output or CI result | not supplied | medium: "all pass" cannot be confirmed |
| Callers of `slugify` and stored slugs | not supplied | medium: decides whether changed output breaks existing URLs |

**COVERAGE**
- **Checked:**
  - `slug.py:slugify`, traced on the main path and on these inputs: empty, all symbols, leading and trailing junk, runs of separators, 200 characters, non-ASCII, `None`.
  - All six tests in `tests/test_slug.py`, each with a mental mutation check.
  - Every claim in PR.md.
- **Not checked:**
  - Callers and stored slugs (not supplied).
  - An actual test run (no tools).
  - How the test runner is invoked: `tests/` has no `__init__.py`, and the test file uses a bare `from slug import ...`.

**SEATS AND GATE**
- Sensitivity gate: passed. The work contains no personal or confidential data.
- Seats: only the local reviewer (this session) ran. No subagent and no cross-vendor seats were available; none were refused.

## Pass 1: Reconstruct

The PR replaces a naive `lower()` plus space-to-hyphen slugify with this:
1. A type check.
2. A regex that turns every run of characters other than `[a-z0-9]` into one hyphen.
3. A strip of leading and trailing hyphens.
4. A cut to 80 characters, then a strip of trailing hyphens.

For it to be correct, these must hold:
- `str.lower()` must not introduce characters outside a-z that survive the regex. The regex guarantees this.
- Truncating must not create a double or trailing hyphen. The `rstrip` handles the trailing case. A double hyphen cannot occur because the regex already collapsed runs.
- Callers must tolerate both the new output and an empty-string result.

This is Track B.

## Pass 2: Attack

**Hostile inputs I traced:**

| Input | Result | Correct? |
|---|---|---|
| `""` | `""` | yes |
| `"!!!"` | `""` | yes |
| `"  a   b -- c  "` | `"a-b-c"` | yes |
| `"word " * 40` | joined slug is 199 characters; `[:80]` ends in `-`; after `rstrip` it is 79 characters | yes |
| `None` | `TypeError` | yes |
| `b"x"` | `TypeError` from the `isinstance` check | yes |
| A huge string | the regex has no nested quantifiers, so there is no catastrophic backtracking; cost grows linearly with input | yes |

**Invariants:**
- Output is always within `[a-z0-9-]`.
- No leading hyphen, because of the first `strip`.
- No trailing hyphen, because of the final `rstrip`.
- No double hyphen anywhere.
- Length is at most `MAX_LEN`.

All of these hold.

**Mutation reasoning on the tests:**

| Mutation | Test that goes red |
|---|---|
| Remove the type check | `test_type_error`: `None.lower()` raises AttributeError instead |
| Remove the cap | `test_length_cap_never_ends_in_hyphen`: length 199 |
| Remove the final `rstrip` | same test: the cut lands exactly after a hyphen |
| Remove the first `strip` | `test_collapses_and_strips` |
| Change `[:MAX_LEN]` to `[:MAX_LEN-1]` | **none**; this mutation survives (see F3) |

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Low | CONFIRMED (regex trace) | B | `slug.py` docstring; PR.md "Letters outside a-z are dropped" | A non-ASCII letter inside a word is not dropped. It becomes a word break. | `slugify("naïve")` returns `"na-ve"`, while the docstring implies `"nave"`. A maintainer relying on the docstring is misled. | Reword to: "characters outside a-z and 0-9 act as separators." Repro: `assert slugify("naïve") == "na-ve"`. | a:Y b:Y c:N d:N |
| F2 | Low | PROBABLE (Unicode case mapping; not run) | B | `slug.py`, `text.lower()` | `lower()` maps some non-ASCII characters to ASCII. This contradicts "not transliterated". The output is still safe. | `"\u212A"` (Kelvin sign) becomes `"k"`. `"İstanbul"` becomes `"i\u0307stanbul"`, then `"i-stanbul"`. | Either document this, or call `.lower()` after an ASCII filter. Repro: `slugify("\u212A")`, expect `""`, observe `"k"`. | a:Y b:N c:N d:N |
| F3 | Low | CONFIRMED (mutation trace) | B | `tests/test_slug.py`, `test_length_cap_never_ends_in_hyphen` | The test checks only that length is at most the cap, so a slug that is cut too short still passes. | Changing to `slug[:MAX_LEN-1]` leaves all tests green. | Add `assertEqual(slugify("a" * 200), "a" * MAX_LEN)`. That test fails under the mutation. | a:Y b:Y c:N d:N |

**NEEDS VALIDATION** (no severity)
- **S1: Existing URLs.** Output changes for existing titles. For example, `"Hello, World!"` used to give `"hello,-world!"` and now gives `"hello-world"`. Unresolved fact: are slugs stored, or are they regenerated from titles at lookup time? If regenerated, old links break.
- **S2: Empty slug.** `"!!!"` and all-non-ASCII titles now return `""`. Unresolved fact: do callers reject an empty slug, or would they create a URL like `/posts/` or collide with other empty slugs?
- **S3: Exception type.** The exception changed from AttributeError to TypeError. Unresolved fact: does any caller catch AttributeError around `slugify`?
- **S4: Test run.** "Six tests, all pass" is unverified. Unresolved fact: the command and output. Note that `tests/` has no `__init__.py`, so `python -m unittest discover` from the repo root may find zero tests. A zero needs a positive control: confirm the run reports "Ran 6 tests".

**REFUTED**
- **"Truncation can leave a double hyphen."** Refuted: the regex collapses runs before the cut, and the cut only removes characters.
- **"The regex is a ReDoS risk."** Refuted: `[^a-z0-9]+` is a single character class with no nested quantifier, so matching is linear.
- **"A leading hyphen can survive."** Refuted: `.strip("-")` runs before the cut, and the cut keeps the start of the string.

**WHAT HOLDS UP**
- All four requirements are met.
- The type check comes before any string operation.
- The cap and the trailing-hyphen handling are both correct.
- The tests assert real behavior, and the length test happens to hit the exact boundary case (a cut at position 80 that lands just after a hyphen).
- No scope creep.

**UNVERIFIED CLAIMS**
- **"Six tests, all pass."** To confirm, run `python -m unittest tests.test_slug` from the repo root (or `discover -s tests -t .`) and check that it reports "Ran 6 tests, OK".

**QUESTIONS FOR THE AUTHOR**
1. Are slugs stored, or regenerated at lookup time? (S1)
2. What should a caller do with an empty slug? (S2)

**DECISION-MAKER SUMMARY:** Safe to merge. The function now does what was asked, and the remaining issues are wording and one missing boundary test. Before merging, confirm that existing URLs are not rebuilt from titles and that an empty slug is handled, or old links may break.

**OWNER SUMMARY:** The change makes web-address names from titles safe and predictable, and it does what was asked. A couple of comments describe the behavior slightly wrong, and one more test would make it sturdier. The one real question is whether existing page links depend on the old naming, because those names will change.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "PR.md", "status": "seen", "matters": true},
    {"item": "change.patch", "status": "seen", "matters": true},
    {"item": "base/slug.py", "status": "seen", "matters": true},
    {"item": "base/README.md", "status": "seen", "matters": false},
    {"item": "commits 9d4e1a7 / c82f0b3", "status": "not_seen", "matters": false},
    {"item": "test run output / CI", "status": "not_seen", "matters": true},
    {"item": "callers of slugify", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local-same-session", "status": "ran", "cross_vendor": false}],
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
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "slug.py docstring; PR.md 'Letters outside a-z are dropped'",
     "scenario": "slugify('naïve') returns 'na-ve', not 'nave'; non-ASCII letters act as separators, contrary to the docstring.",
     "fix": "Reword docstring/PR: characters outside a-z and 0-9 act as separators.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "assert slugify('naïve') == 'na-ve' passes; docstring implies 'nave'."},
    {"id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "PROBABLE", "track": "B",
     "location": "slug.py: text.lower()",
     "scenario": "Kelvin sign U+212A lowercases to 'k' and 'İ' to 'i'+U+0307, so some non-ASCII is transliterated despite the docstring.",
     "fix": "Document the behaviour, or filter to ASCII before lowercasing.",
     "answers": {"a": true, "b": false, "c": false, "d": false},
     "reproduction": "slugify('\u212a'): expect '' per docstring, observe 'k'."},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "tests/test_slug.py: test_length_cap_never_ends_in_hyphen",
     "scenario": "Mutating slug[:MAX_LEN] to slug[:MAX_LEN-1] leaves every test green, so over-truncation is undetected.",
     "fix": "Add assertEqual(slugify('a' * 200), 'a' * MAX_LEN).",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Apply the MAX_LEN-1 mutation in a scratch copy; current suite passes; new assertion fails."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "slug.py:slugify (callers)",
     "suspicion": "Changed output for existing titles may break existing URLs.",
     "unresolved_fact": "Whether slugs are stored or regenerated from titles at lookup."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "slug.py:slugify (callers)",
     "suspicion": "Empty slug for symbol-only or non-ASCII titles may yield bad or colliding URLs.",
     "unresolved_fact": "Whether callers reject or replace an empty slug."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "slug.py:slugify (callers)",
     "suspicion": "Exception type changed from AttributeError to TypeError.",
     "unresolved_fact": "Whether any caller catches AttributeError around slugify."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "PR.md 'Six tests, all pass'",
     "suspicion": "tests/ lacks __init__.py; discovery from root may run zero tests.",
     "unresolved_fact": "Test command and output showing 'Ran 6 tests ... OK'."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Truncation can produce a double hyphen.", "evidence": "Regex collapses runs before the cut; slicing only removes characters."},
    {"id": "C2", "candidate": "Regex is vulnerable to ReDoS.", "evidence": "[^a-z0-9]+ is a single character class with no nested quantifier; linear time."},
    {"id": "C3", "candidate": "A leading hyphen can survive.", "evidence": ".strip('-') runs before the cut, and the cut keeps the start of the string."}
  ]
}
```