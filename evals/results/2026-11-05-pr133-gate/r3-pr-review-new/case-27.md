# PR review: PR #70, harden slugify

**REVIEWED:** PR #70, head `9d4e1a7`, merge base `c82f0b3`. Both SHAs come from PR.md. I had no git access, so I could not confirm that `change.patch` is exactly the diff between them. No head movement was observed.

**TIER:** Standard. The change is a small pure function that builds URL path components. It touches no auth, secrets, personal data or network exposure. Delegation and data-protection steps do not apply: no code left this session, and this is the one round the tier requires.

**REVIEWERS:** Fresh instance (Sonnet 5.5, no memory of writing the change), working from the PR text, patch and base files only. The author is unknown because no commit trailers were provided.

I did not run the tests, so "six tests, all pass" is the PR's claim, not something I saw. By reading, all six should pass.

**Checked against the request**
- Allowed characters, single hyphens and no leading or trailing hyphen: met. The regex plus `strip("-")` gives only `[a-z0-9-]`, and `rstrip("-")` after the cut keeps the end clean.
- Length cap: met at 80 characters.
- Clear error for non-strings: met, `TypeError("text must be a string")`.
- Nothing extra was added.

No prompt-injection text, citations or consent wording appear in the PR. The patch touches no instruction files.

**FINDINGS**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `slug.py` (patch lines 14-15, the `re.sub` line) | The same visible title gives different slugs depending on Unicode form. Precomposed `"caf\u00e9"` gives `"caf"`, because `é` becomes a hyphen that is then stripped. Decomposed `"cafe\u0301"` gives `"cafe"`, because the combining mark is replaced and the `e` survives. Titles from different clients or OSes (NFC vs NFD) produce different or colliding URLs. | `assertEqual(slugify("caf\u00e9"), slugify("cafe\u0301"))` fails today. |
| 2 | P2 | Docstring in `slug.py` (patch lines 6-7); PR.md; `test_non_ascii_dropped` | The docs say non-a-z letters are "dropped", but the code turns each run of them into a separator. `slugify("na\u00efve")` gives `"na-ve"`, not `"nave"`. The only test input, `"caf\u00e9 au lait"`, has the non-ASCII letter next to a space, so it cannot tell dropping from splitting. The stated behavior is not actually tested. | `assertEqual(slugify("na\u00efve"), <documented result>)` fails today if the docstring is right. Otherwise fix the docstring to say "treated as separators". |
| 3 | P2 | `slug.py` return line; docstring "gives `""`" | Titles with no a-z or 0-9, such as `"日本語"` or `"!!!"`, return `""`. If the caller builds `/posts/{slug}`, every such title maps to the same empty or invalid URL and collides. The PR documents the behavior, but the request asked for a "clear error" only for non-strings, so the caller's handling is an open decision. Callers were not provided. | A caller-level test that creating two all-non-ASCII titles does not yield identical or empty URLs. Alternatively, `slugify("日本語")` raises or returns a defined fallback, per the owner's choice. |
| 4 | P3 | `slug.py`, `text.lower()` before the regex | There is no input length bound, so a very large string is fully lowercased and scanned before the 80-character cap applies. Impact is bounded memory and linear time, and it matters only if titles arrive unvalidated. Special-case lowercasing also changes characters: `"\u212a"` (Kelvin sign) becomes ASCII `k`, and `"\u0130"` becomes `i` plus a dropped mark. This is a minor deviation from "not transliterated". | `slugify("\u212a")` assertion matching the documented policy. Optionally, a test that a 10 MB input returns promptly. |
| 5 | P3 | `tests/test_slug.py:15-17` | The length test only asserts `<= MAX_LEN` and no trailing hyphen. It does not check the exact boundary or that the cap is hit. A mutation to a cap of 10 would pass. Digits and underscores are also untested. | `assertEqual(len(slugify("a" * 200)), MAX_LEN)` and `assertEqual(slugify("a" * 79 + " b"), "a" * 79)`. |

**Notes on fixes (UNVERIFIED)**
- For finding 1, normalizing with `unicodedata.normalize("NFKD", ...)` and dropping combining marks would make both forms agree. That is a transliteration, so it contradicts the documented policy. NFC normalization first is the smaller change. Both are unchecked against the URL-creating consumer, which was not provided.
- The base behavior (`lower().replace(" ", "-")`) is replaced entirely. Existing callers that relied on punctuation or non-ASCII passing through will see changed URLs. Callers were not provided, so migration or redirect needs are unassessed.

**FILES NEEDED BUT NOT PROVIDED:** callers of `slugify` and the URL-creation code (for findings 3 and the behavior-change note). Also the repo's test-runner configuration: `tests/` has no `__init__.py`, and `from slug import ...` works only when the runner's working directory is the repo root.

**Close-out (not written by the reviewer):** The author must adjudicate findings 1-5, and by the skill's rules the adjudication is posted against `9d4e1a7`. Nothing is decided yet.

**Recommended outcome:** merge after fixes. Findings 1 and 2 need the code or docstring aligned, and finding 3 needs an owner decision on empty slugs. This is a recommendation, not a close-out. I did not verify check status, which was not provided, and no written merge rule was provided to cite.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "read-from-code",
      "location": "slug.py:re.sub line (patch lines 14-15)",
      "scenario": "NFC 'caf\\u00e9' slugifies to 'caf' while NFD 'cafe\\u0301' slugifies to 'cafe', so the same visible title yields different or colliding URLs.",
      "fix": "Normalize input (NFC, or NFKD plus combining-mark removal) before the regex; add test asserting both forms give the same slug. UNVERIFIED against the consumer."
    },
    {
      "severity": "P2",
      "evidence_level": "read-from-code",
      "location": "slug.py docstring; tests/test_slug.py test_non_ascii_dropped",
      "scenario": "Docs say non-a-z letters are dropped, but they act as separators: 'na\\u00efve' -> 'na-ve'. The test input has the non-ASCII letter beside a space, so it cannot distinguish dropping from splitting.",
      "fix": "Either change the docstring/PR to say separators, or change the code to delete them; add a test with a mid-word non-ASCII letter."
    },
    {
      "severity": "P2",
      "evidence_level": "read-from-code",
      "location": "slug.py return line",
      "scenario": "Titles with no a-z/0-9 (e.g. '日本語', '!!!') return '', so URLs built from them collide or are malformed; callers were not provided.",
      "fix": "Owner decides: raise ValueError, or caller supplies a fallback (e.g. an id); add a caller-level test."
    },
    {
      "severity": "P3",
      "evidence_level": "inferred",
      "location": "slug.py text.lower()",
      "scenario": "No input length bound before lowercasing and scanning; special-case lowercasing maps Kelvin sign U+212A to 'k' and U+0130 to 'i', a minor deviation from 'not transliterated'.",
      "fix": "Optionally cap input length before processing; add a test pinning the intended policy for U+212A."
    },
    {
      "severity": "P3",
      "evidence_level": "read-from-code",
      "location": "tests/test_slug.py:15-17",
      "scenario": "Length test asserts only <= MAX_LEN and no trailing hyphen, so a cap of 10 would still pass; digits and the exact boundary are untested.",
      "fix": "Add assertEqual(len(slugify('a'*200)), MAX_LEN) and a boundary case where the cut lands just after a hyphen."
    }
  ]
}
```