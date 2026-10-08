# Redteam review: PR #70 "harden slugify"

**VERDICT: SHIP WITH FIXES.** The change meets every part of the request by trace. The remaining issues are a docstring claim that is false for a few Unicode characters, a missing test for digits, and an unassessed effect on existing callers.

**CONFIDENCE: medium.** I had no tools, so nothing was run. Every behavior below comes from tracing the code by hand against Python's documented `str.lower()` and `re` semantics. I did not write this work, so this is not a same-context review, but no second seat ran.

**INPUTS LEDGER**
- **Seen:** request.md, context.md, PR.md, base/README.md, base/slug.py, change.patch (slug.py and the new tests/test_slug.py).
- **Not seen: callers of `slugify`.** This matters. The change narrows the output (non-Latin titles now give `""`), and its effect on URL creation and uniqueness depends on the callers.
- **Not seen: CI or test output.** This matters a little. "All pass" is unverified, but I traced all six tests and each should pass.

**SEATS AND GATE:** Local reviewer only. No subagent or cross-vendor seats were available. The sensitivity gate passed: this is invented library code with no personal or confidential data.

## Pass 1: Reconstruct

The PR claims `slugify` now returns lowercase `[a-z0-9]` joined by single hyphens, at most 80 characters, with no leading or trailing hyphen. It drops (does not transliterate) non a-z letters and raises `TypeError` for non-strings.

For this to be correct, all of the following must hold:
- `re.sub(r"[^a-z0-9]+", "-", ...)` turns every disallowed run into a single hyphen.
- `strip`, slice, then `rstrip` cannot leave an edge hyphen or exceed 80 characters.
- `str.lower()` cannot add a-z letters that were not in the input.
- Callers can handle `""`.

Tracks: B (code), with a light pass of A (blast radius).

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Medium | PROBABLE (callers not seen) | B/A | slug.py `re.sub(...)`; docstring "Input with no usable characters gives \"\"" | Titles written wholly in non-Latin scripts now give `""`. The base code returned the lowercased text. | A user creates "Привет мир" or "東京". The slug is `""`, so the URL becomes `/posts/` or collides with every other non-Latin title. Before this change the slug was non-empty (though unsafe). | Have callers reject or fall back on `""` (for example an id-based slug), and test that path. Or document this as a required caller check in the PR. | Not a Critical/High; round not required |
| 2 | Low | CONFIRMED (by documented `str.lower` mappings) | B | slug.py `text.lower()` before the regex; docstring "dropped, not transliterated" | Some non-ASCII characters lowercase into ASCII, so they are transliterated rather than dropped. | `"\u212A"` (KELVIN SIGN) lowercases to `"k"`, giving `"k"`. `"İstanbul"` lowercases to `"i\u0307stanbul"`, giving `"i-stanbul"`. The output is still within a-z/0-9/hyphen, so it stays safe, but the stated contract is false and lookalike input can produce an ASCII slug. | Make the docstring accurate. Or, if strict dropping is wanted, first remove non-ASCII characters (e.g. `re.sub(r"[^\x00-\x7f]+", " ", text)`) and then lowercase. Add tests for `"\u212A"` and `"İ"`. | n/a |
| 3 | Low | CONFIRMED (mutation reasoned) | B | tests/test_slug.py | No test contains a digit, so keeping 0-9 is unguarded. | Mutating the regex to `[^a-z]+` keeps all six tests green but turns "Top 10 Tips" into `"top-tips"`. | Add `assertEqual(slugify("Top 10 Tips"), "top-10-tips")`. | n/a |
| 4 | Low | PROBABLE | B | slug.py: no input-length bound before `lower()`/`re.sub` | The whole input is processed before truncation. | Multi-megabyte titles cost linear time and memory per call. There is no ReDoS (the pattern is a single class with `+`), so this is load, not a vulnerability. | Optionally slice the input first (e.g. `text[:MAX_LEN * 4]`) or enforce a title length limit upstream. | n/a |

## What holds up

- **Character set:** `[^a-z0-9]+` uses ASCII-only ranges, and runs collapse to one hyphen. `test_collapses_and_strips` confirms this, including an input `--` run.
- **Edge hyphens:** `strip("-")` runs before the slice and `rstrip("-")` after it, so truncation cannot leave a trailing hyphen. The length test exercises this:
  - `"word " * 40` gives a 199-character slug.
  - `[:80]` cuts it to exactly sixteen `"word-"` units, which ends in a hyphen.
  - `rstrip` turns that into 79 characters.
  - Removing the `rstrip` would turn this test red.
- **Length cap:** the result is at most 80 characters for any input.
- **TypeError:** raised for `None`, `bytes`, `int`, and so on, with a clear message. `str` subclasses are accepted, which is reasonable.
- **Traced test results:** all six expectations hold:
  - `"Hello, World!"` gives `"hello-world"`.
  - `"!!!"` gives `""`.
  - `"café au lait"` gives `"caf-au-lait"`.
- **Scope:** the change does what was asked with no extra features.

## Unverified claims

- **"Six tests, all pass":** run `python -m unittest discover -s tests` from the repo root. Note that `from slug import` relies on the root being on `sys.path`.
- **Behavior of existing callers on `""`:** grep for `slugify(` and check each call site.

## Questions for the author

1. What should a caller do when `slugify` returns `""`, and is that handled at every call site?
2. Is strict "dropped, not transliterated" a real requirement, or can the docstring just be loosened?

## Summaries

**DECISION-MAKER SUMMARY:** The function meets the request and is safe to merge once a digit test is added and the docstring is corrected. Before merging, confirm that callers handle an empty slug. Otherwise, titles in non-Latin scripts will produce empty or colliding URLs.

**OWNER SUMMARY:** The new URL-name cleaner does what was asked, and its tests look sound. Titles written entirely in other alphabets (for example Russian or Japanese) will now produce a blank web address, so the code that creates pages needs a fallback for that case. A couple of small test and documentation gaps should also be tidied before release.

```json
{
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "callers of slugify", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "local-reviewer", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "findings": [
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "B", "location": "slug.py re.sub line; docstring",
     "scenario": "Fully non-Latin titles (e.g. Cyrillic, CJK) now slug to \"\", producing empty or colliding URLs where the base code returned non-empty text.",
     "fix": "Callers reject or fall back (e.g. id-based slug) on empty result; add a test for that path.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "B", "location": "slug.py text.lower(); docstring 'dropped, not transliterated'",
     "scenario": "KELVIN SIGN U+212A lowercases to 'k' and 'İ' to 'i'+U+0307, giving 'k' and 'i-stanbul': non-ASCII is partly transliterated, contradicting the docstring.",
     "fix": "Correct the docstring, or strip non-ASCII before lower(); add tests for U+212A and 'İ'.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "B", "location": "tests/test_slug.py",
     "scenario": "No test has digits; mutating the regex to [^a-z]+ keeps all tests green while 'Top 10 Tips' becomes 'top-tips'.",
     "fix": "Add assertEqual(slugify('Top 10 Tips'), 'top-10-tips').", "status": "n/a"},
    {"severity": "Low", "evidence_level": "PROBABLE", "track": "B", "location": "slug.py: no pre-truncation of input",
     "scenario": "Very long titles are fully lowercased and regex-processed before the 80-char cut, costing linear CPU and memory per call (no ReDoS).",
     "fix": "Optionally slice input first (e.g. text[:MAX_LEN*4]) or bound title length upstream.", "status": "n/a"}
  ]
}
```