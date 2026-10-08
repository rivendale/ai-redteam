# Redteam Review: PR #70 "harden slugify"

**Review setup:** This session has no tools, so nothing was executed. Every behavioural claim below comes from reading and tracing the patch by hand. The work was not written in this conversation, so the review is not anchored to the author's reasoning.

**VERDICT: SHIP WITH FIXES.** The function meets all four requirements: a-z/0-9 and single hyphens only, a length cap, and a TypeError for non-strings. However, the PR and docstring describe the handling of non-ASCII letters wrongly, and the test written to prove that handling cannot tell the right behaviour from the wrong one.

**CONFIDENCE IN VERDICT: medium.** No code or tests were run. Unicode case-mapping results are recalled from knowledge, not executed. How callers use the result (stored slugs, empty-slug handling) is unknown.

## Pass 1: Reconstruct

The PR replaces `lower().replace(" ", "-")` with a regex that lowercases the input, turns every run of characters outside `[a-z0-9]` into one hyphen, strips leading and trailing hyphens, cuts the result to 80 characters, and strips any hyphen the cut leaves at the end. Non-strings raise TypeError. The PR claims that non-ASCII letters are "dropped, not transliterated", that six tests exist, and that all pass.

For this to be correct, the following must hold:
- `str.lower()` never produces a-z from a non-ASCII character.
- "Dropped" accurately describes what happens.
- Callers accept `""` as a valid slug.
- Changing the slug output does not break slugs that already exist.
- The tests actually run under the repo's test command.

## Findings

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Medium | CONFIRMED (traced) | `slug.py` docstring "Letters outside a-z and digits are dropped"; PR.md "dropped, not transliterated (... tested)"; `test_non_ascii_dropped` | Non-ASCII letters are **replaced by a hyphen**, not dropped. The regex `[^a-z0-9]+` → `"-"` treats them as word separators. The only test puts `é` at the end of a word, where dropping it and hyphenating it give the same output. | `slugify("naïve")` → `"na-ve"`, `slugify("Straße")` → `"stra-e"`, `slugify("Ångström")` → `"ngstr-m"`. The test passes either way, so the "tested" claim does not cover the behaviour it describes. | Choose one behaviour. (a) To really drop: `re.sub(r"[^a-z0-9\s-]", "", ...)` first, then collapse separators. (b) To keep current behaviour: change the docstring and PR to "replaced by a separator". Either way, add `assertEqual(slugify("naïve"), ...)` with the intended output. |
| 2 | Low | PROBABLE (Unicode mapping recalled, not run) | `text.lower()` before the ASCII filter | Some non-ASCII characters lowercase into ASCII, which contradicts "letters outside a-z are dropped". The output still satisfies the a-z requirement. | `"\u212A"` (KELVIN SIGN) `.lower()` → `"k"`, so it survives as an ASCII `k`. `"İstanbul"` (U+0130) lowercases to `"i\u0307stanbul"`, and the combining dot becomes a hyphen, giving `"i-stanbul"`. | Filter or normalise before lowercasing, e.g. `unicodedata.normalize("NFKD", text)` plus an ASCII filter, or run the regex on the original text with `re.I` and lowercase afterwards. Add tests for `"\u212A"` and `"İstanbul"`. |
| 3 | Low | UNVERIFIED | Return value `""` (docstring: "Input with no usable characters gives \"\"") | The function correctly returns an empty string, but the request is about creating URLs, and nothing shows that callers reject an empty slug. | A title written entirely in a non-Latin script (`"日本語"`, `"Привет"`) or entirely in emoji gives `""`. That can produce `/posts/` or make different posts collide on the same URL. | Confirm that callers handle `""`, for example by falling back to an id. Or raise `ValueError` and document it. |
| 4 | Low | PROBABLE | `tests/test_slug.py`: `from slug import slugify` with no `tests/__init__.py` | "Six tests, all pass" depends on how the tests were run. `python tests/test_slug.py` puts only `tests/` on `sys.path`, so the import fails. On Python 3.11+, `python -m unittest` from the root does not discover tests in a directory without `__init__.py`. | CI runs a command that collects 0 tests, which looks green, or fails at import. | State the exact command used. Add `tests/__init__.py` or test config so CI collects these tests. |
| 5 | Low | UNVERIFIED | Behaviour change from base `slugify` | The output changes for any input that contains punctuation. Base kept punctuation; the new version strips it. | If slugs are recomputed from titles to look records up (rather than stored once), old URLs stop resolving. Example: `"C++ tips"` was `"c++-tips"` and is now `"c-tips"`. | Confirm that slugs are only generated at creation time and then stored. If not, plan a migration or redirect. |

## What holds up

- **Character set and hyphens.** After `[^a-z0-9]+` → `-` and `strip("-")`, the output contains only a-z, 0-9 and single hyphens, with no hyphen at either end. Non-ASCII digits and fullwidth letters are excluded.
- **Length cap.** `slug[:80].rstrip("-")` is always ≤ 80. It cannot become empty, because character 0 is alphanumeric after the strip. I traced `test_length_cap_never_ends_in_hyphen`: the 80-character cut ends exactly on a hyphen, so the `rstrip` path is exercised.
- **Type check.** `None`, `bytes` and `int` all raise TypeError before any string method is called. The old version raised AttributeError, or for `bytes` it raised TypeError on `.replace`.
- **Regex safety.** The pattern is a single negated character class, so there is no catastrophic backtracking. Run time is linear.
- **Test traces.** By hand, all six tests produce their expected values: `"hello-world"`, `"a-b-c"`, `""`, `""`, a 79-character slug, `"caf-au-lait"`, and TypeError. The count of six matches the PR.

## Unverified claims

- **"All pass."** Not run here. To confirm, run the repo's actual test command and check that it reports 6 tests collected.
- **"Letters outside a-z are dropped."** False as worded (finding 1). To confirm, run `slugify("naïve")`.
- **Kelvin sign and İ behaviour (finding 2).** To confirm, run `"\u212A".lower()` and `"\u0130".lower()` in the target Python version.

## Questions for the author

1. Should a non-ASCII letter in the middle of a word be removed (`naïve` → `nave`) or act as a separator (`na-ve`)?
2. What should a caller do with `""`? Should the function raise instead?
3. Are slugs stored once at creation, or recomputed from titles on lookup?
4. What exact command produced "all pass"?

## Decision-maker summary

The hardening works: output is always URL-safe, capped at 80 characters, and rejects non-strings. Merge after making the docstring and PR match the real behaviour for non-ASCII letters (they become hyphens) and adding a mid-word test such as `naïve`. Two risks remain if merged as is: titles in non-Latin scripts produce empty slugs, and recomputed slugs could break old URLs. Neither can be checked from the PR alone.

```json
{
  "verdict": "SHIP WITH FIXES",
  "findings": [
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "slug.py docstring 'Letters outside a-z and digits are dropped'; PR.md 'dropped, not transliterated (... tested)'; test_non_ascii_dropped",
      "scenario": "Non-ASCII letters are replaced by a hyphen, not dropped: slugify('naïve') -> 'na-ve', slugify('Straße') -> 'stra-e'. The only test places é at a word end, where dropping and hyphenating produce the same output, so the test cannot detect the mismatch.",
      "fix": "Pick a behaviour: either strip non-[a-z0-9 separator] characters before collapsing separators, or reword the docstring and PR to 'replaced by a separator'. Add a mid-word test such as slugify('naïve') with the intended output."
    },
    {
      "severity": "Low",
      "evidence_level": "PROBABLE",
      "location": "slug.py: text.lower() applied before the ASCII filter",
      "scenario": "Some non-ASCII characters lowercase into ASCII: KELVIN SIGN U+212A becomes 'k'; 'İstanbul' (U+0130) becomes 'i' + U+0307, giving 'i-stanbul'. This contradicts the 'dropped' claim; output is still a-z only.",
      "fix": "Filter or NFKD-normalise before lowercasing, or match with re.I on the original text and lowercase afterwards. Add tests for U+212A and 'İstanbul'."
    },
    {
      "severity": "Low",
      "evidence_level": "UNVERIFIED",
      "location": "slug.py return value '' (docstring: 'Input with no usable characters gives \"\"')",
      "scenario": "Titles written entirely in a non-Latin script or in emoji yield '', which can produce an empty URL segment or slug collisions if callers do not guard against it.",
      "fix": "Confirm callers handle '' (for example, fall back to an id), or raise ValueError and document it."
    },
    {
      "severity": "Low",
      "evidence_level": "PROBABLE",
      "location": "tests/test_slug.py 'from slug import slugify'; no tests/__init__.py",
      "scenario": "Depending on the runner, the import fails (python tests/test_slug.py) or unittest discovery on Python 3.11+ collects 0 tests, so 'all pass' may be vacuous.",
      "fix": "State the exact test command; add tests/__init__.py or runner config so CI collects all six tests."
    },
    {
      "severity": "Low",
      "evidence_level": "UNVERIFIED",
      "location": "slug.py: behaviour change versus base slugify",
      "scenario": "Base kept punctuation ('C++ tips' -> 'c++-tips'); the new version gives 'c-tips'. If slugs are recomputed for lookup rather than stored once, existing URLs stop resolving.",
      "fix": "Confirm slugs are generated once at creation and stored; otherwise add a migration or redirects."
    }
  ]
}
```