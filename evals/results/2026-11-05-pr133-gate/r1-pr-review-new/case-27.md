# pr-review: PR #70 "harden slugify"

I could not run code, open links or check out the repo, so this is a read-only review of the supplied files.

**REVIEWED:** PR #70, head `9d4e1a7`, merge base `c82f0b3`. Both SHAs are taken from `PR.md`; I could not verify them against a repository. I reviewed `change.patch` applied to `base/slug.py`.

**TIER:** Standard. This is an ordinary code change to a small string function. It does not touch auth, secrets, migrations, money or personal data, and the output is used in URLs. Step 3 raises no data concern: the code is generic and I sent it nowhere. Step 1.4: no instruction files or reviewer-addressed text appeared in the PR description, patch or README.

**REVIEWERS:** A fresh Claude (Sonnet 5.5) instance with no memory of writing the change reviewed it. The author is unknown because no commit trailers were supplied.

**Original request check:** All four asks are met and nothing extra is added.
- The output charset is a-z, 0-9 and single hyphens.
- There is an 80-character cap.
- Non-strings raise `TypeError`.
- The hyphen rules hold, with no leading or trailing hyphen.

**Hand-trace of the six tests** (not run):

| Test | Result |
|---|---|
| `"Hello, World!"` | `"hello-world"` ✓ |
| `"  a   b -- c  "` | `"a-b-c"` ✓ |
| `""` and `"!!!"` | `""` ✓ |
| `"word " * 40` | 79 characters, no trailing hyphen ✓ |
| `"café au lait"` | `"caf-au-lait"` ✓ |
| `None` | `TypeError` ✓ |

"All pass" is therefore plausible but UNVERIFIED by execution.

## FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `slug.py:7-10` (docstring), `slug.py:13` | The docstring, PR text and test name say non-ASCII letters are "dropped". The code replaces each run of non-`[a-z0-9]` characters with a hyphen, so it splits words. `"naïve"` gives `"na-ve"`, `"cafés"` gives `"caf-s"`, and `"İstanbul"` gives `"i-stanbul"` (`lower()` yields `i` plus U+0307). The only non-ASCII test has `é` next to a space, so it cannot tell dropping from splitting. | Assert `slugify("na\u00efve")` equals the documented result. Either fix the docstring to say "treated as separators" and expect `"na-ve"`, or change the code to drop the characters and expect `"naive"`. |
| 2 | P3 | `slug.py:13` | `text.lower()` runs before the filter, so some non-ASCII characters map into a-z. The Kelvin sign U+212A becomes `"k"`. The output is still within the safe charset, but this contradicts "letters outside a-z are dropped". | Assert `slugify("\u212a")` equals the documented result. |
| 3 | P3 | `slug.py:14` | Titles with no ASCII alphanumerics (`"日本語"`, `"!!!"`) return `""`. A caller building URLs gets an empty path segment, and all such titles collide. This is documented and matches the request, but callers are not covered. | A caller-level test that creating a URL from `slugify("日本語")` is rejected or given a fallback. |
| 4 | P3 | `slug.py:13` | Behaviour change for existing callers. `_` and `.` were previously preserved and are now separators, so `"v1.2"` becomes `"v1-2"` and `"snake_case"` becomes `"snake-case"`. Slugs already stored or published would regenerate differently. | A test pinning the intended behaviour for `.` and `_`, plus a check of existing stored slugs. |

**Verified OK:**
- `bytes` and `None` input raise `TypeError`.
- The regex is linear and has no ReDoS risk.
- The cap-then-`rstrip("-")` ordering is correct. `slug[:80]` can end in a hyphen, and the length test would catch its removal.

**FILES NEEDED BUT NOT PROVIDED:**
- Commit trailers, to establish authorship.
- CI configuration and check results. Step 8 requires every expected check present and green, and none were supplied.
- Callers of `slugify`, to assess findings 3 and 4.

## Close-out (pending)

The author adjudicates the findings, and a reviewer does not adjudicate its own findings, so no adjudication or post-fix verification exists yet.

**MERGE RECOMMENDATION:** merge after fixes. There is no P0 or P1. Finding 1 (P2) needs a decision: fix the docstring and test, or fix the code. Findings 2 to 4 can be deferred with tracking issues. Before merging, confirm that CI is present and green, since "six tests, all pass" is unverified by me. No written merge rule was supplied, so I cite none.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "traced by reading code, not executed",
      "location": "slug.py:7-10, slug.py:13",
      "scenario": "Docstring, PR text and test name say non-ASCII letters are 'dropped', but the regex replaces each run of non-[a-z0-9] characters with a hyphen, which splits words: 'naïve' -> 'na-ve', 'cafés' -> 'caf-s', 'İstanbul' -> 'i-stanbul'. The only non-ASCII test has é adjacent to a space, so it cannot distinguish dropping from splitting.",
      "fix": "Decide the intended behaviour. Either correct the docstring and PR text to say separators and assert 'na-ve', or drop the characters and assert 'naive'. Add a mid-word non-ASCII test."
    },
    {
      "severity": "P3",
      "evidence_level": "reasoned from Python lower() semantics, not executed",
      "location": "slug.py:13",
      "scenario": "text.lower() runs before filtering, so some non-ASCII characters map into a-z (Kelvin sign U+212A -> 'k'), contradicting the claim that letters outside a-z are dropped. Output charset remains safe.",
      "fix": "Document the behaviour, or filter on the original text (for example, check ASCII before lowercasing), and add a test."
    },
    {
      "severity": "P3",
      "evidence_level": "traced by reading code, not executed",
      "location": "slug.py:14",
      "scenario": "Titles with no ASCII alphanumerics ('日本語', '!!!') return '', so URLs built from them get an empty segment and all such titles collide.",
      "fix": "Have callers reject or fall back on an empty slug; add a caller-level test."
    },
    {
      "severity": "P3",
      "evidence_level": "traced by reading code, not executed",
      "location": "slug.py:13",
      "scenario": "'.' and '_' were previously preserved and are now separators ('v1.2' -> 'v1-2'), so slugs already stored or published would regenerate differently.",
      "fix": "Pin the intended behaviour in a test and check existing stored slugs for regeneration differences."
    }
  ]
}
```